"""MonitoringController 테스트.

docs/design/phase5.md §5, docs/FEATURES/monitoring.md "테스트 관점" 기준:
- count_by_status: RESERVED/CONFIRMED/PRODUCING/RELEASE 각 개수가 실제 데이터와 일치하는지,
  REJECTED가 집계에서 제외되는지
- stock_status: 미출고 수요(RESERVED+PRODUCING+CONFIRMED 수량 합) 기준 경계값 검증
  - 재고 0 -> "고갈"
  - 재고 > 0 이고 재고 < 수요 -> "부족"
  - 재고 > 0 이고 재고 >= 수요(수요 0 포함) -> "여유"
- 주문/시료 데이터가 전혀 없을 때 빈 결과(0건/빈 목록)로 정상 동작하는지
"""
import os

import pytest

from src.controller.monitoring_controller import MonitoringController
from src.model.order import Order, OrderStatus
from src.model.sample import Sample
from src.repository.order_repository import OrderRepository
from src.repository.sample_repository import SampleRepository


@pytest.fixture
def order_repository(tmp_path):
    repo_path = os.path.join(tmp_path, "orders.json")
    return OrderRepository(repo_path)


@pytest.fixture
def sample_repository(tmp_path):
    repo_path = os.path.join(tmp_path, "samples.json")
    return SampleRepository(repo_path)


@pytest.fixture
def controller(order_repository, sample_repository):
    return MonitoringController(order_repository, sample_repository)


def make_order(order_id, status, sample_id="S001", customer_name="Alice", quantity=3):
    return Order(
        order_id=order_id,
        sample_id=sample_id,
        customer_name=customer_name,
        quantity=quantity,
        status=status,
    )


def make_sample(sample_id="S001", name="WaferA", stock_quantity=10):
    return Sample(
        sample_id=sample_id,
        name=name,
        avg_production_time=2.5,
        yield_rate=0.9,
        stock_quantity=stock_quantity,
    )


# ---------------------------------------------------------------------------
# count_by_status
# ---------------------------------------------------------------------------

def test_count_by_status_matches_actual_data(controller, order_repository):
    order_repository.add(make_order("O001", OrderStatus.RESERVED))
    order_repository.add(make_order("O002", OrderStatus.RESERVED))
    order_repository.add(make_order("O003", OrderStatus.CONFIRMED))
    order_repository.add(make_order("O004", OrderStatus.PRODUCING))
    order_repository.add(make_order("O005", OrderStatus.PRODUCING))
    order_repository.add(make_order("O006", OrderStatus.PRODUCING))
    order_repository.add(make_order("O007", OrderStatus.RELEASE))

    result = controller.count_by_status()

    assert result == {
        "RESERVED": 2,
        "CONFIRMED": 1,
        "PRODUCING": 3,
        "RELEASE": 1,
    }


def test_count_by_status_excludes_rejected(controller, order_repository):
    order_repository.add(make_order("O001", OrderStatus.RESERVED))
    order_repository.add(make_order("O002", OrderStatus.REJECTED))
    order_repository.add(make_order("O003", OrderStatus.REJECTED))

    result = controller.count_by_status()

    assert result == {
        "RESERVED": 1,
        "CONFIRMED": 0,
        "PRODUCING": 0,
        "RELEASE": 0,
    }
    assert "REJECTED" not in result


def test_count_by_status_empty_when_no_orders(controller):
    result = controller.count_by_status()

    assert result == {
        "RESERVED": 0,
        "CONFIRMED": 0,
        "PRODUCING": 0,
        "RELEASE": 0,
    }


# ---------------------------------------------------------------------------
# orders_by_status
# ---------------------------------------------------------------------------

def test_orders_by_status_matches_actual_data(controller, order_repository):
    order_repository.add(make_order("O001", OrderStatus.RESERVED))
    order_repository.add(make_order("O002", OrderStatus.RESERVED))
    order_repository.add(make_order("O003", OrderStatus.CONFIRMED))
    order_repository.add(make_order("O004", OrderStatus.PRODUCING))
    order_repository.add(make_order("O005", OrderStatus.RELEASE))

    result = controller.orders_by_status()

    assert result == {
        "RESERVED": ["O001", "O002"],
        "CONFIRMED": ["O003"],
        "PRODUCING": ["O004"],
        "RELEASE": ["O005"],
    }


def test_orders_by_status_excludes_rejected(controller, order_repository):
    order_repository.add(make_order("O001", OrderStatus.RESERVED))
    order_repository.add(make_order("O002", OrderStatus.REJECTED))

    result = controller.orders_by_status()

    assert result["RESERVED"] == ["O001"]
    assert "REJECTED" not in result


def test_orders_by_status_empty_when_no_orders(controller):
    result = controller.orders_by_status()

    assert result == {
        "RESERVED": [],
        "CONFIRMED": [],
        "PRODUCING": [],
        "RELEASE": [],
    }


# ---------------------------------------------------------------------------
# stock_status
# ---------------------------------------------------------------------------

def test_stock_status_zero_stock_is_depleted(controller, sample_repository, order_repository):
    sample_repository.add(make_sample("S001", stock_quantity=0))
    order_repository.add(make_order("O001", OrderStatus.RESERVED, sample_id="S001", quantity=5))

    result = controller.stock_status()

    assert len(result) == 1
    assert result[0].sample_id == "S001"
    assert result[0].stock_quantity == 0
    assert result[0].status_label == "고갈"


def test_stock_status_zero_stock_with_no_demand_is_still_depleted(controller, sample_repository):
    sample_repository.add(make_sample("S001", stock_quantity=0))

    result = controller.stock_status()

    assert result[0].status_label == "고갈"


def test_stock_status_positive_stock_below_demand_is_shortage(controller, sample_repository, order_repository):
    sample_repository.add(make_sample("S001", stock_quantity=4))
    order_repository.add(make_order("O001", OrderStatus.RESERVED, sample_id="S001", quantity=3))
    order_repository.add(make_order("O002", OrderStatus.CONFIRMED, sample_id="S001", quantity=2))

    result = controller.stock_status()

    assert result[0].status_label == "부족"  # 재고 4 < 수요 5


def test_stock_status_stock_equal_to_demand_is_sufficient(controller, sample_repository, order_repository):
    sample_repository.add(make_sample("S001", stock_quantity=5))
    order_repository.add(make_order("O001", OrderStatus.PRODUCING, sample_id="S001", quantity=5))

    result = controller.stock_status()

    assert result[0].status_label == "여유"  # 재고 5 == 수요 5


def test_stock_status_stock_above_demand_is_sufficient(controller, sample_repository, order_repository):
    sample_repository.add(make_sample("S001", stock_quantity=10))
    order_repository.add(make_order("O001", OrderStatus.CONFIRMED, sample_id="S001", quantity=3))

    result = controller.stock_status()

    assert result[0].status_label == "여유"


def test_stock_status_positive_stock_no_demand_is_sufficient(controller, sample_repository):
    sample_repository.add(make_sample("S001", stock_quantity=10))

    result = controller.stock_status()

    assert result[0].status_label == "여유"  # 수요 0 포함


def test_stock_status_only_counts_unshipped_statuses(controller, sample_repository, order_repository):
    """RELEASE/REJECTED 주문은 미출고 수요에 포함되지 않아야 한다."""
    sample_repository.add(make_sample("S001", stock_quantity=3))
    order_repository.add(make_order("O001", OrderStatus.RELEASE, sample_id="S001", quantity=100))
    order_repository.add(make_order("O002", OrderStatus.REJECTED, sample_id="S001", quantity=100))

    result = controller.stock_status()

    # RELEASE/REJECTED는 수요에서 제외되므로 수요는 0 -> 재고 3 > 0 이면 여유
    assert result[0].status_label == "여유"


def test_stock_status_demand_sums_across_multiple_orders_and_statuses(controller, sample_repository, order_repository):
    sample_repository.add(make_sample("S001", stock_quantity=6))
    order_repository.add(make_order("O001", OrderStatus.RESERVED, sample_id="S001", quantity=2))
    order_repository.add(make_order("O002", OrderStatus.PRODUCING, sample_id="S001", quantity=2))
    order_repository.add(make_order("O003", OrderStatus.CONFIRMED, sample_id="S001", quantity=3))

    result = controller.stock_status()

    # 수요 = 2+2+3 = 7 > 재고 6 -> 부족
    assert result[0].status_label == "부족"


def test_stock_status_only_matches_orders_for_same_sample(controller, sample_repository, order_repository):
    sample_repository.add(make_sample("S001", stock_quantity=5))
    sample_repository.add(make_sample("S002", stock_quantity=5, name="WaferB"))
    order_repository.add(make_order("O001", OrderStatus.RESERVED, sample_id="S002", quantity=100))

    result = controller.stock_status()

    s001 = next(r for r in result if r.sample_id == "S001")
    assert s001.status_label == "여유"  # S002 주문은 S001 수요에 영향 없음


def test_stock_status_empty_when_no_samples(controller):
    result = controller.stock_status()

    assert result == []


def test_stock_status_empty_data_no_orders_and_no_samples(controller):
    assert controller.count_by_status() == {
        "RESERVED": 0,
        "CONFIRMED": 0,
        "PRODUCING": 0,
        "RELEASE": 0,
    }
    assert controller.stock_status() == []
