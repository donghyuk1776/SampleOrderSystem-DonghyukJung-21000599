"""ShipmentController 테스트.

docs/design/phase4.md §6, docs/FEATURES/shipment.md "테스트 관점" 기준:
- list_confirmed: CONFIRMED 상태 주문만 반환 (다른 상태와 섞여있을 때 필터링 확인)
- ship: CONFIRMED 주문 출고 -> RELEASE 전환 + 영속화
- ship: CONFIRMED가 아닌 상태(RESERVED, PRODUCING, REJECTED, 이미 RELEASE) 각각에 대해
  ValidationError
- ship: 존재하지 않는 order_id -> ValidationError
"""
import os

import pytest

from src.controller.order_controller import ValidationError
from src.controller.shipment_controller import ShipmentController
from src.model.order import Order, OrderStatus
from src.repository.order_repository import OrderRepository


@pytest.fixture
def order_repository(tmp_path):
    repo_path = os.path.join(tmp_path, "orders.json")
    return OrderRepository(repo_path)


@pytest.fixture
def controller(order_repository):
    return ShipmentController(order_repository)


def make_order(order_id, status, sample_id="S001", customer_name="Alice", quantity=3):
    return Order(
        order_id=order_id,
        sample_id=sample_id,
        customer_name=customer_name,
        quantity=quantity,
        status=status,
    )


# ---------------------------------------------------------------------------
# list_confirmed
# ---------------------------------------------------------------------------

def test_list_confirmed_returns_only_confirmed_orders(controller, order_repository):
    order_repository.add(make_order("O001", OrderStatus.RESERVED))
    order_repository.add(make_order("O002", OrderStatus.CONFIRMED))
    order_repository.add(make_order("O003", OrderStatus.PRODUCING))
    order_repository.add(make_order("O004", OrderStatus.REJECTED))
    order_repository.add(make_order("O005", OrderStatus.RELEASE))
    order_repository.add(make_order("O006", OrderStatus.CONFIRMED))

    result = controller.list_confirmed()

    assert {o.order_id for o in result} == {"O002", "O006"}
    assert all(o.status == OrderStatus.CONFIRMED for o in result)


def test_list_confirmed_empty_when_none_confirmed(controller, order_repository):
    order_repository.add(make_order("O001", OrderStatus.RESERVED))
    order_repository.add(make_order("O002", OrderStatus.RELEASE))

    assert controller.list_confirmed() == []


# ---------------------------------------------------------------------------
# ship - happy path
# ---------------------------------------------------------------------------

def test_ship_confirmed_order_transitions_to_release(controller, order_repository):
    order_repository.add(make_order("O001", OrderStatus.CONFIRMED))

    result = controller.ship("O001")

    assert result.status == OrderStatus.RELEASE


def test_ship_persists_status_change(controller, order_repository):
    order_repository.add(make_order("O001", OrderStatus.CONFIRMED))

    controller.ship("O001")

    reloaded = order_repository.find_by_id("O001")
    assert reloaded.status == OrderStatus.RELEASE


def test_ship_removes_order_from_confirmed_list_after_shipping(controller, order_repository):
    order_repository.add(make_order("O001", OrderStatus.CONFIRMED))

    controller.ship("O001")

    assert controller.list_confirmed() == []


# ---------------------------------------------------------------------------
# ship - rejection cases
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("status", [
    OrderStatus.RESERVED,
    OrderStatus.PRODUCING,
    OrderStatus.REJECTED,
    OrderStatus.RELEASE,
])
def test_ship_non_confirmed_order_raises_validation_error(controller, order_repository, status):
    order_repository.add(make_order("O001", status))

    with pytest.raises(ValidationError):
        controller.ship("O001")

    # 상태가 변경되지 않아야 한다.
    reloaded = order_repository.find_by_id("O001")
    assert reloaded.status == status


def test_ship_nonexistent_order_id_raises_validation_error(controller, order_repository):
    with pytest.raises(ValidationError):
        controller.ship("NOPE")
