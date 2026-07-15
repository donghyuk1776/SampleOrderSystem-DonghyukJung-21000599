"""ProductionLineController 테스트.

docs/design/phase3.md §7 "테스트 계획", docs/FEATURES/production-line.md "테스트 관점" 기준:
- 실생산량 계산식 ceil(shortage/yield_rate) 검증 (나누어 떨어지지 않는 경우 포함)
- total_production_time = avg_production_time * actual_quantity 계산 검증
- 여러 건 enqueue 후 list_pending()이 등록 순서(FIFO)를 유지하는지
- process_next() 반복 호출 시 FIFO 순서로 처리되는지, 처리 후 큐에서 제거되는지
- 생산 완료 후 주문 상태 PRODUCING -> CONFIRMED 전환 및 재고 actual_quantity만큼 증가 검증
- 큐가 비어있을 때 process_next() 호출 시 크래시 없이 None 반환
- OrderController와 조립한 "승인 -> enqueue -> 생산완료 처리" 통합 시나리오
"""
import math
import os

import pytest

from src.controller.order_controller import OrderController
from src.controller.production_line_controller import ProductionLineController, ProductionLineError
from src.model.order import Order, OrderStatus
from src.model.sample import Sample
from src.repository import json_storage
from src.repository.order_repository import OrderRepository
from src.repository.production_queue_repository import ProductionQueueRepository
from src.repository.sample_repository import SampleRepository


@pytest.fixture
def sample_repository(tmp_path):
    repo_path = os.path.join(tmp_path, "samples.json")
    return SampleRepository(repo_path)


@pytest.fixture
def order_repository(tmp_path):
    repo_path = os.path.join(tmp_path, "orders.json")
    return OrderRepository(repo_path)


@pytest.fixture
def queue_repository(tmp_path):
    repo_path = os.path.join(tmp_path, "production_queue.json")
    return ProductionQueueRepository(repo_path)


@pytest.fixture
def controller(sample_repository, order_repository, queue_repository):
    return ProductionLineController(sample_repository, order_repository, queue_repository)


def register_sample(sample_repository, sample_id="S001", avg_production_time=2.5,
                     yield_rate=0.9, stock_quantity=0):
    sample_repository.add(Sample(
        sample_id=sample_id,
        name="WaferA",
        avg_production_time=avg_production_time,
        yield_rate=yield_rate,
        stock_quantity=stock_quantity,
    ))


def register_order(order_repository, order_id, sample_id="S001", quantity=10,
                    status=OrderStatus.PRODUCING):
    order = Order(
        order_id=order_id,
        sample_id=sample_id,
        customer_name="Alice",
        quantity=quantity,
        status=status,
    )
    order_repository.add(order)
    return order


# ---------------------------------------------------------------------------
# enqueue: 계산식 검증
# ---------------------------------------------------------------------------

def test_enqueue_actual_quantity_ceil_division_not_exact(controller, sample_repository, order_repository):
    """부족분 5, 수율 0.9 -> ceil(5/0.9) = ceil(5.555...) = 6"""
    register_sample(sample_repository, yield_rate=0.9)
    order = register_order(order_repository, "O001")

    job = controller.enqueue(order, shortage_quantity=5)

    assert job.actual_quantity == 6
    assert job.actual_quantity == math.ceil(5 / 0.9)


def test_enqueue_actual_quantity_exact_division(controller, sample_repository, order_repository):
    """부족분 9, 수율 0.9 -> ceil(9/0.9) = ceil(10.0) = 10 (나누어 떨어지는 경계값)"""
    register_sample(sample_repository, yield_rate=0.9)
    order = register_order(order_repository, "O001")

    job = controller.enqueue(order, shortage_quantity=9)

    assert job.actual_quantity == 10


def test_enqueue_total_production_time_calculation(controller, sample_repository, order_repository):
    register_sample(sample_repository, avg_production_time=2.5, yield_rate=0.9)
    order = register_order(order_repository, "O001")

    job = controller.enqueue(order, shortage_quantity=5)

    # actual_quantity = ceil(5/0.9) = 6, total_production_time = 2.5 * 6 = 15.0
    assert job.actual_quantity == 6
    assert job.total_production_time == pytest.approx(2.5 * 6)
    assert job.total_production_time == pytest.approx(15.0)


def test_enqueue_records_shortage_and_status_pending(controller, sample_repository, order_repository):
    register_sample(sample_repository)
    order = register_order(order_repository, "O001")

    job = controller.enqueue(order, shortage_quantity=5)

    assert job.order_id == "O001"
    assert job.sample_id == "S001"
    assert job.shortage_quantity == 5
    assert job.status == "PENDING"


# ---------------------------------------------------------------------------
# list_pending: FIFO 순서 유지
# ---------------------------------------------------------------------------

def test_list_pending_preserves_fifo_registration_order(controller, sample_repository, order_repository):
    register_sample(sample_repository)
    order1 = register_order(order_repository, "O001")
    order2 = register_order(order_repository, "O002")
    order3 = register_order(order_repository, "O003")

    controller.enqueue(order1, shortage_quantity=3)
    controller.enqueue(order2, shortage_quantity=5)
    controller.enqueue(order3, shortage_quantity=1)

    pending = controller.list_pending()

    assert [job.order_id for job in pending] == ["O001", "O002", "O003"]


def test_list_pending_empty_queue_returns_empty_list(controller):
    assert controller.list_pending() == []


# ---------------------------------------------------------------------------
# process_next: FIFO 처리 순서 + 큐에서 제거
# ---------------------------------------------------------------------------

def test_process_next_processes_in_fifo_order_and_removes_from_queue(controller, sample_repository, order_repository):
    register_sample(sample_repository)
    order1 = register_order(order_repository, "O001")
    order2 = register_order(order_repository, "O002")
    order3 = register_order(order_repository, "O003")

    controller.enqueue(order1, shortage_quantity=3)
    controller.enqueue(order2, shortage_quantity=5)
    controller.enqueue(order3, shortage_quantity=1)

    first = controller.process_next()
    assert first.order_id == "O001"
    assert [job.order_id for job in controller.list_pending()] == ["O002", "O003"]

    second = controller.process_next()
    assert second.order_id == "O002"
    assert [job.order_id for job in controller.list_pending()] == ["O003"]

    third = controller.process_next()
    assert third.order_id == "O003"
    assert controller.list_pending() == []


def test_enqueue_nonexistent_sample_raises_production_line_error(controller, order_repository):
    order = register_order(order_repository, "O001", sample_id="NOPE")

    with pytest.raises(ProductionLineError):
        controller.enqueue(order, shortage_quantity=5)


def test_process_next_nonexistent_sample_raises_production_line_error(
        controller, sample_repository, order_repository):
    register_sample(sample_repository)
    order = register_order(order_repository, "O001")
    controller.enqueue(order, shortage_quantity=5)

    json_storage.save(sample_repository._path, [])  # 시료가 삭제된 상황을 재현

    with pytest.raises(ProductionLineError):
        controller.process_next()


def test_process_next_empty_queue_returns_none_without_crash(controller):
    result = controller.process_next()
    assert result is None


def test_process_next_on_already_empty_queue_after_draining_returns_none(controller, sample_repository, order_repository):
    register_sample(sample_repository)
    order = register_order(order_repository, "O001")
    controller.enqueue(order, shortage_quantity=3)

    controller.process_next()  # drains the only job
    result = controller.process_next()  # queue now empty

    assert result is None


# ---------------------------------------------------------------------------
# process_next: 상태 전이 + 재고 반영
# ---------------------------------------------------------------------------

def test_process_next_transitions_order_status_and_increases_stock(
        controller, sample_repository, order_repository):
    register_sample(sample_repository, avg_production_time=2.5, yield_rate=0.9, stock_quantity=0)
    order = register_order(order_repository, "O001", quantity=10, status=OrderStatus.PRODUCING)

    job = controller.enqueue(order, shortage_quantity=5)  # actual_quantity == 6

    controller.process_next()

    reloaded_order = order_repository.find_by_id("O001")
    assert reloaded_order.status == OrderStatus.CONFIRMED

    reloaded_sample = sample_repository.find_by_id("S001")
    assert reloaded_sample.stock_quantity == job.actual_quantity == 6


def test_process_next_stock_increase_accumulates_over_existing_stock(
        controller, sample_repository, order_repository):
    register_sample(sample_repository, yield_rate=0.9, stock_quantity=4)
    order = register_order(order_repository, "O001", quantity=10, status=OrderStatus.PRODUCING)
    controller.enqueue(order, shortage_quantity=5)  # actual_quantity == 6

    controller.process_next()

    reloaded_sample = sample_repository.find_by_id("S001")
    assert reloaded_sample.stock_quantity == 4 + 6


def test_process_next_does_not_change_status_if_order_not_producing(
        controller, sample_repository, order_repository):
    """주문이 이미 다른 사유로 PRODUCING이 아니게 된 예외적인 경우, 상태를 강제로
    덮어쓰지 않아야 한다(방어적 동작 확인)."""
    register_sample(sample_repository)
    order = register_order(order_repository, "O001", status=OrderStatus.PRODUCING)
    controller.enqueue(order, shortage_quantity=3)

    # 큐에 등록된 이후 주문 상태가 외부 요인으로 REJECTED로 바뀌었다고 가정
    order.status = OrderStatus.REJECTED
    order_repository.update(order)

    controller.process_next()

    reloaded_order = order_repository.find_by_id("O001")
    assert reloaded_order.status == OrderStatus.REJECTED


# ---------------------------------------------------------------------------
# 통합 시나리오: 승인 -> enqueue -> 생산완료 처리
# ---------------------------------------------------------------------------

def test_integration_approve_enqueues_and_process_next_completes_production(
        sample_repository, order_repository, queue_repository):
    """OrderController(재고 부족 시 production_queue.enqueue 호출)와
    ProductionLineController를 함께 조립하여 승인부터 생산완료까지의 전체 흐름을 검증한다."""
    production_line_controller = ProductionLineController(
        sample_repository, order_repository, queue_repository)
    order_controller = OrderController(
        order_repository, sample_repository, production_queue=production_line_controller)

    register_sample(sample_repository, avg_production_time=2.5, yield_rate=0.9, stock_quantity=4)
    order = order_controller.create_order("S001", "Alice", 10)

    approved = order_controller.approve(order.order_id)

    # 재고(4) < 주문수량(10) -> PRODUCING 전환 + 생산 큐 등록 (부족분 = 6)
    assert approved.status == OrderStatus.PRODUCING
    pending = production_line_controller.list_pending()
    assert len(pending) == 1
    job = pending[0]
    assert job.order_id == order.order_id
    assert job.shortage_quantity == 6
    assert job.actual_quantity == math.ceil(6 / 0.9)  # ceil(6.666..) = 7
    assert job.total_production_time == pytest.approx(2.5 * job.actual_quantity)

    # 생산완료 처리
    processed_job = production_line_controller.process_next()
    assert processed_job.order_id == order.order_id
    assert production_line_controller.list_pending() == []

    final_order = order_repository.find_by_id(order.order_id)
    assert final_order.status == OrderStatus.CONFIRMED

    final_sample = sample_repository.find_by_id("S001")
    # 기존 재고 4 (승인 시 부족 분기라 차감되지 않음) + 실생산량
    assert final_sample.stock_quantity == 4 + processed_job.actual_quantity


def test_integration_multiple_orders_processed_in_fifo_across_two_approvals(
        sample_repository, order_repository, queue_repository):
    production_line_controller = ProductionLineController(
        sample_repository, order_repository, queue_repository)
    order_controller = OrderController(
        order_repository, sample_repository, production_queue=production_line_controller)

    register_sample(sample_repository, avg_production_time=1.0, yield_rate=0.5, stock_quantity=0)

    order_a = order_controller.create_order("S001", "Alice", 4)
    order_b = order_controller.create_order("S001", "Bob", 2)

    order_controller.approve(order_a.order_id)
    order_controller.approve(order_b.order_id)

    pending = production_line_controller.list_pending()
    assert [job.order_id for job in pending] == [order_a.order_id, order_b.order_id]

    first_processed = production_line_controller.process_next()
    assert first_processed.order_id == order_a.order_id
    assert order_repository.find_by_id(order_a.order_id).status == OrderStatus.CONFIRMED
    assert order_repository.find_by_id(order_b.order_id).status == OrderStatus.PRODUCING

    second_processed = production_line_controller.process_next()
    assert second_processed.order_id == order_b.order_id
    assert order_repository.find_by_id(order_b.order_id).status == OrderStatus.CONFIRMED

    assert production_line_controller.process_next() is None
