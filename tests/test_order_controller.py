"""OrderController 테스트.

docs/design/phase2.md §7, docs/FEATURES/sample-order.md /
docs/FEATURES/order-approval-rejection.md "테스트 관점" 기준:
- create_order: 존재하지 않는 시료ID / 수량 0·음수·실수 / 고객명 공백 -> ValidationError
- create_order: 정상 생성 시 RESERVED 상태
- approve: 재고 충분 -> CONFIRMED + 재고 차감, 재고 부족 -> PRODUCING + 부족분 계산 +
  생산 큐 등록, 경계값(재고 == 주문수량)
- approve/reject: RESERVED가 아닌 주문 재처리 시 ValidationError
- reject: REJECTED 전환
"""
import os

import pytest

from src.controller.order_controller import OrderController, ValidationError
from src.model.order import OrderStatus
from src.model.sample import Sample
from src.repository import json_storage
from src.repository.order_repository import OrderRepository
from src.repository.sample_repository import SampleRepository


class FakeProductionQueue:
    """Phase 3 ProductionLineController 대역: enqueue 호출 여부/인자 기록."""

    def __init__(self):
        self.calls = []

    def enqueue(self, order, shortage):
        self.calls.append((order, shortage))


@pytest.fixture
def sample_repository(tmp_path):
    repo_path = os.path.join(tmp_path, "samples.json")
    return SampleRepository(repo_path)


@pytest.fixture
def order_repository(tmp_path):
    repo_path = os.path.join(tmp_path, "orders.json")
    return OrderRepository(repo_path)


@pytest.fixture
def production_queue():
    return FakeProductionQueue()


@pytest.fixture
def controller(order_repository, sample_repository, production_queue):
    return OrderController(order_repository, sample_repository, production_queue)


def register_sample(sample_repository, sample_id="S001", stock_quantity=10):
    sample_repository.add(Sample(
        sample_id=sample_id,
        name="WaferA",
        avg_production_time=2.5,
        yield_rate=0.9,
        stock_quantity=stock_quantity,
    ))


# ---------------------------------------------------------------------------
# create_order
# ---------------------------------------------------------------------------

def test_create_order_happy_path_sets_reserved(controller, sample_repository):
    register_sample(sample_repository, stock_quantity=10)

    order = controller.create_order("S001", "Alice", 3)

    assert order.status == OrderStatus.RESERVED
    assert order.sample_id == "S001"
    assert order.customer_name == "Alice"
    assert order.quantity == 3

    assert len(controller.list_reserved()) == 1


def test_create_order_multiple_orders_for_same_sample_are_independent(controller, sample_repository):
    register_sample(sample_repository, stock_quantity=10)

    order1 = controller.create_order("S001", "Alice", 3)
    order2 = controller.create_order("S001", "Bob", 5)

    assert order1.order_id != order2.order_id
    assert order1.customer_name == "Alice"
    assert order2.customer_name == "Bob"
    assert len(controller.list_reserved()) == 2


def test_create_order_nonexistent_sample_id_raises_validation_error(controller, sample_repository):
    with pytest.raises(ValidationError):
        controller.create_order("NOPE", "Alice", 3)

    assert controller.list_reserved() == []


@pytest.mark.parametrize("invalid_quantity", [0, -1, -10])
def test_create_order_invalid_quantity_raises_validation_error(controller, sample_repository, invalid_quantity):
    register_sample(sample_repository)

    with pytest.raises(ValidationError):
        controller.create_order("S001", "Alice", invalid_quantity)

    assert controller.list_reserved() == []


def test_create_order_non_integer_quantity_raises_validation_error(controller, sample_repository):
    register_sample(sample_repository)

    with pytest.raises(ValidationError):
        controller.create_order("S001", "Alice", 2.5)

    assert controller.list_reserved() == []


@pytest.mark.parametrize("blank_name", ["", "   "])
def test_create_order_blank_customer_name_raises_validation_error(controller, sample_repository, blank_name):
    register_sample(sample_repository)

    with pytest.raises(ValidationError):
        controller.create_order("S001", blank_name, 3)

    assert controller.list_reserved() == []


# ---------------------------------------------------------------------------
# approve
# ---------------------------------------------------------------------------

def test_approve_sufficient_stock_confirms_and_deducts(controller, sample_repository, production_queue):
    register_sample(sample_repository, stock_quantity=10)
    order = controller.create_order("S001", "Alice", 3)

    result = controller.approve(order.order_id)

    assert result.status == OrderStatus.CONFIRMED
    updated_sample = sample_repository.find_by_id("S001")
    assert updated_sample.stock_quantity == 7
    assert production_queue.calls == []


def test_approve_boundary_stock_equals_quantity_confirms(controller, sample_repository, production_queue):
    register_sample(sample_repository, stock_quantity=5)
    order = controller.create_order("S001", "Alice", 5)

    result = controller.approve(order.order_id)

    assert result.status == OrderStatus.CONFIRMED
    updated_sample = sample_repository.find_by_id("S001")
    assert updated_sample.stock_quantity == 0
    assert production_queue.calls == []


def test_approve_insufficient_stock_producing_and_shortage_calculated(controller, sample_repository, production_queue):
    register_sample(sample_repository, stock_quantity=4)
    order = controller.create_order("S001", "Alice", 10)

    result = controller.approve(order.order_id)

    assert result.status == OrderStatus.PRODUCING
    # 재고 부족 시 재고 자체는 차감되지 않아야 한다.
    updated_sample = sample_repository.find_by_id("S001")
    assert updated_sample.stock_quantity == 4

    assert len(production_queue.calls) == 1
    queued_order, shortage = production_queue.calls[0]
    assert queued_order.order_id == order.order_id
    assert shortage == 6  # 10 - 4


def test_approve_zero_stock_full_shortage(controller, sample_repository, production_queue):
    register_sample(sample_repository, stock_quantity=0)
    order = controller.create_order("S001", "Alice", 7)

    result = controller.approve(order.order_id)

    assert result.status == OrderStatus.PRODUCING
    assert production_queue.calls[0][1] == 7


def test_approve_persists_status_change(controller, sample_repository, order_repository):
    register_sample(sample_repository, stock_quantity=10)
    order = controller.create_order("S001", "Alice", 3)
    controller.approve(order.order_id)

    reloaded = order_repository.find_by_id(order.order_id)
    assert reloaded.status == OrderStatus.CONFIRMED


def test_approve_non_reserved_order_raises_validation_error(controller, sample_repository):
    register_sample(sample_repository, stock_quantity=10)
    order = controller.create_order("S001", "Alice", 3)
    controller.approve(order.order_id)  # -> CONFIRMED

    with pytest.raises(ValidationError):
        controller.approve(order.order_id)


def test_approve_rejected_order_raises_validation_error(controller, sample_repository):
    register_sample(sample_repository, stock_quantity=10)
    order = controller.create_order("S001", "Alice", 3)
    controller.reject(order.order_id)  # -> REJECTED

    with pytest.raises(ValidationError):
        controller.approve(order.order_id)


def test_approve_nonexistent_order_id_raises_validation_error(controller):
    with pytest.raises(ValidationError):
        controller.approve("NOPE")


def test_approve_tolerates_zero_o_typo_in_order_id(controller, sample_repository):
    """사용자가 'O001'을 '0001'로 잘못 입력해도(0/O 혼동) 승인이 되어야 한다."""
    register_sample(sample_repository, stock_quantity=10)
    order = controller.create_order("S001", "Alice", 3)

    result = controller.approve(order.order_id.replace("O", "0"))

    assert result.status == OrderStatus.CONFIRMED


def test_approve_order_with_deleted_sample_raises_validation_error(controller, sample_repository, order_repository):
    """시료가 등록된 이후 삭제된 경우에도(현재는 삭제 기능이 없어 직접 조작으로 재현)
    approve()가 크래시하지 않고 ValidationError로 안내해야 한다."""
    register_sample(sample_repository, stock_quantity=10)
    order = controller.create_order("S001", "Alice", 3)

    json_storage.save(sample_repository._path, [])  # 시료 데이터를 강제로 비워 "삭제된 시료" 상황을 재현

    with pytest.raises(ValidationError):
        controller.approve(order.order_id)


def test_approve_insufficient_stock_without_production_queue_still_transitions(order_repository, sample_repository):
    """production_queue가 주입되지 않아도(Phase 3 미구현 상태) PRODUCING 전환은 동작해야 한다."""
    controller_without_queue = OrderController(order_repository, sample_repository, production_queue=None)
    register_sample(sample_repository, stock_quantity=2)
    order = controller_without_queue.create_order("S001", "Alice", 5)

    result = controller_without_queue.approve(order.order_id)

    assert result.status == OrderStatus.PRODUCING


# ---------------------------------------------------------------------------
# reject
# ---------------------------------------------------------------------------

def test_reject_transitions_to_rejected(controller, sample_repository, order_repository):
    register_sample(sample_repository, stock_quantity=10)
    order = controller.create_order("S001", "Alice", 3)

    result = controller.reject(order.order_id)

    assert result.status == OrderStatus.REJECTED
    reloaded = order_repository.find_by_id(order.order_id)
    assert reloaded.status == OrderStatus.REJECTED

    # 거절된 주문은 재고에 영향을 주지 않는다.
    assert sample_repository.find_by_id("S001").stock_quantity == 10


def test_reject_non_reserved_order_raises_validation_error(controller, sample_repository):
    register_sample(sample_repository, stock_quantity=10)
    order = controller.create_order("S001", "Alice", 3)
    controller.reject(order.order_id)  # -> REJECTED

    with pytest.raises(ValidationError):
        controller.reject(order.order_id)


def test_reject_confirmed_order_raises_validation_error(controller, sample_repository):
    register_sample(sample_repository, stock_quantity=10)
    order = controller.create_order("S001", "Alice", 3)
    controller.approve(order.order_id)  # -> CONFIRMED

    with pytest.raises(ValidationError):
        controller.reject(order.order_id)


def test_reject_nonexistent_order_id_raises_validation_error(controller):
    with pytest.raises(ValidationError):
        controller.reject("NOPE")


def test_reject_tolerates_zero_o_typo_in_order_id(controller, sample_repository):
    register_sample(sample_repository, stock_quantity=10)
    order = controller.create_order("S001", "Alice", 3)

    result = controller.reject(order.order_id.replace("O", "0"))

    assert result.status == OrderStatus.REJECTED
