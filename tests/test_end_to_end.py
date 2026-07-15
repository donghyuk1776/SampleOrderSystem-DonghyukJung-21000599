"""전체 시나리오 통합 테스트.

docs/design/phase6.md §5 "통합 테스트" 기준:
1. 시료 등록
2. 재고보다 적은 수량으로 주문 생성 후 승인 -> CONFIRMED
3. 재고보다 많은 수량으로 주문 생성 후 승인 -> PRODUCING -> 생산 완료 처리 -> CONFIRMED
4. 두 CONFIRMED 주문 모두 출고 처리 -> RELEASE
5. 모니터링 집계 결과(count_by_status, stock_status)가 시나리오와 일치하는지

각 컨트롤러를 실제 Repository(임시 데이터 디렉터리)로 조립해 진짜 엔드투엔드로 동작하는지
검증한다 (tests/test_production_line_controller.py의 통합 테스트 조립 패턴 참고).
"""
import math
import os

import pytest

from src.controller.monitoring_controller import MonitoringController
from src.controller.order_controller import OrderController
from src.controller.production_line_controller import ProductionLineController
from src.controller.sample_controller import SampleController
from src.controller.shipment_controller import ShipmentController
from src.model.order import OrderStatus
from src.repository.order_repository import OrderRepository
from src.repository.production_queue_repository import ProductionQueueRepository
from src.repository.sample_repository import SampleRepository


@pytest.fixture
def sample_repository(tmp_path):
    return SampleRepository(os.path.join(tmp_path, "samples.json"))


@pytest.fixture
def order_repository(tmp_path):
    return OrderRepository(os.path.join(tmp_path, "orders.json"))


@pytest.fixture
def queue_repository(tmp_path):
    return ProductionQueueRepository(os.path.join(tmp_path, "production_queue.json"))


@pytest.fixture
def production_line_controller(sample_repository, order_repository, queue_repository):
    return ProductionLineController(sample_repository, order_repository, queue_repository)


@pytest.fixture
def order_controller(order_repository, sample_repository, production_line_controller):
    return OrderController(order_repository, sample_repository,
                            production_queue=production_line_controller)


@pytest.fixture
def sample_controller(sample_repository):
    return SampleController(sample_repository)


@pytest.fixture
def shipment_controller(order_repository):
    return ShipmentController(order_repository)


@pytest.fixture
def monitoring_controller(order_repository, sample_repository):
    return MonitoringController(order_repository, sample_repository)


def test_full_scenario_register_order_produce_ship_monitor(
        sample_controller, order_controller, production_line_controller,
        shipment_controller, monitoring_controller, sample_repository, order_repository):
    # 1. 시료 등록 (초기 재고 0)
    sample = sample_controller.register(
        sample_id="S001", name="WaferA", avg_production_time=2.0, yield_rate=0.8)
    assert sample.stock_quantity == 0

    # 승인 처리를 위해 재고를 늘려둔다 (Repository를 직접 통해 재고를 채우는 것은 테스트
    # 셋업 목적이며, 도메인 로직은 등록/승인/생산 컨트롤러만 사용한다).
    sample.stock_quantity = 10
    sample_repository.update(sample)

    # 2. 재고(10)보다 적은 수량(4)으로 주문 생성 후 승인 -> CONFIRMED
    small_order = order_controller.create_order("S001", "Alice", 4)
    approved_small = order_controller.approve(small_order.order_id)
    assert approved_small.status == OrderStatus.CONFIRMED

    reloaded_sample_after_small = sample_repository.find_by_id("S001")
    assert reloaded_sample_after_small.stock_quantity == 10 - 4  # == 6

    # 3. 재고(6)보다 많은 수량(10)으로 주문 생성 후 승인 -> PRODUCING
    large_order = order_controller.create_order("S001", "Bob", 10)
    approved_large = order_controller.approve(large_order.order_id)
    assert approved_large.status == OrderStatus.PRODUCING

    # 재고 부족분 = 10 - 6 = 4, 실생산량 = ceil(4/0.8) = 5
    pending_jobs = production_line_controller.list_pending()
    assert len(pending_jobs) == 1
    job = pending_jobs[0]
    assert job.order_id == large_order.order_id
    assert job.shortage_quantity == 4
    assert job.actual_quantity == math.ceil(4 / 0.8) == 5
    assert job.total_production_time == pytest.approx(2.0 * 5)

    # 승인 시 부족 분기이므로 재고는 차감되지 않고 그대로 유지된다.
    reloaded_sample_after_large_approval = sample_repository.find_by_id("S001")
    assert reloaded_sample_after_large_approval.stock_quantity == 6

    # 생산 완료 처리 -> PRODUCING -> CONFIRMED, 재고 +actual_quantity
    processed_job = production_line_controller.process_next()
    assert processed_job.order_id == large_order.order_id
    assert production_line_controller.list_pending() == []

    reloaded_large_order = order_repository.find_by_id(large_order.order_id)
    assert reloaded_large_order.status == OrderStatus.CONFIRMED

    # 기존 재고 6 + 생산량 5 - 주문수량 10 == 1 (주문에 소진되고 남는 수율 손실 버퍼만 재고로 남음)
    reloaded_sample_after_production = sample_repository.find_by_id("S001")
    assert reloaded_sample_after_production.stock_quantity == 6 + 5 - 10 == 1

    # 4. 두 CONFIRMED 주문 모두 출고 처리 -> RELEASE
    confirmed_before_shipment = shipment_controller.list_confirmed()
    confirmed_ids_before_shipment = {o.order_id for o in confirmed_before_shipment}
    assert confirmed_ids_before_shipment == {small_order.order_id, large_order.order_id}

    shipped_small = shipment_controller.ship(small_order.order_id)
    shipped_large = shipment_controller.ship(large_order.order_id)
    assert shipped_small.status == OrderStatus.RELEASE
    assert shipped_large.status == OrderStatus.RELEASE

    assert shipment_controller.list_confirmed() == []

    # 5. 모니터링 집계 결과가 시나리오와 일치하는지 확인
    counts = monitoring_controller.count_by_status()
    assert counts[OrderStatus.RESERVED.value] == 0
    assert counts[OrderStatus.PRODUCING.value] == 0
    assert counts[OrderStatus.CONFIRMED.value] == 0
    assert counts[OrderStatus.RELEASE.value] == 2

    stock_statuses = monitoring_controller.stock_status()
    assert len(stock_statuses) == 1
    stock_status = stock_statuses[0]
    assert stock_status.sample_id == "S001"
    # 출고된 물량은 더 이상 미출고 수요가 아니므로, 남은 재고(1) 전체가 "여유"로 표시된다.
    assert stock_status.stock_quantity == 1
    assert stock_status.status_label == "여유"


def test_full_scenario_reject_path_does_not_affect_stock_or_monitoring_counts(
        sample_controller, order_controller, monitoring_controller, sample_repository):
    """거절된 주문은 재고에 영향을 주지 않고, 모니터링 집계에도 CONFIRMED/RELEASE로 반영되지
    않아야 한다 (핵심 시나리오의 보조 확인용 회귀 테스트)."""
    sample_controller.register(
        sample_id="S002", name="WaferB", avg_production_time=1.0, yield_rate=1.0)

    order = order_controller.create_order("S002", "Carol", 3)
    order_controller.reject(order.order_id)

    reloaded_sample = sample_repository.find_by_id("S002")
    assert reloaded_sample.stock_quantity == 0

    counts = monitoring_controller.count_by_status()
    assert counts[OrderStatus.CONFIRMED.value] == 0
    assert counts[OrderStatus.RELEASE.value] == 0


# ---------------------------------------------------------------------------
# 회귀 방지: controller/errors.py 리팩터링 이후에도 각 컨트롤러 모듈에서
# ValidationError를 동일하게 재노출(re-export)하는지 확인한다.
# ---------------------------------------------------------------------------

def test_validation_error_is_reexported_and_identical_across_controllers():
    from src.controller.errors import ValidationError as CanonicalValidationError
    from src.controller.sample_controller import ValidationError as SampleValidationError
    from src.controller.order_controller import ValidationError as OrderValidationError
    from src.controller.shipment_controller import ValidationError as ShipmentValidationError

    assert SampleValidationError is CanonicalValidationError
    assert OrderValidationError is CanonicalValidationError
    assert ShipmentValidationError is CanonicalValidationError
