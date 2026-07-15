"""OrderRepository 테스트.

docs/design/phase2.md §7, docs/FEATURES/sample-order.md /
docs/FEATURES/order-approval-rejection.md "테스트 관점" 기준:
- 저장/조회 (add 후 get_all 반영)
- list_by_status로 상태별 필터링
- 저장 후 새 Repository 인스턴스로 다시 읽었을 때 데이터가 유지되는지 (JSON 영속성)
- update로 상태 변경이 영속화되는지
"""
import os

import pytest

from src.model.order import Order, OrderStatus
from src.repository.order_repository import OrderRepository


@pytest.fixture
def repo_path(tmp_path):
    return os.path.join(tmp_path, "orders.json")


def make_order(order_id="O001", sample_id="S001", customer_name="Alice",
               quantity=10, status=OrderStatus.RESERVED):
    return Order(
        order_id=order_id,
        sample_id=sample_id,
        customer_name=customer_name,
        quantity=quantity,
        status=status,
    )


def test_add_reflected_in_get_all(repo_path):
    repo = OrderRepository(repo_path)
    assert repo.get_all() == []

    order = make_order()
    repo.add(order)

    all_orders = repo.get_all()
    assert len(all_orders) == 1
    assert all_orders[0].order_id == "O001"
    assert all_orders[0].sample_id == "S001"
    assert all_orders[0].customer_name == "Alice"
    assert all_orders[0].quantity == 10
    assert all_orders[0].status == OrderStatus.RESERVED


def test_find_by_id(repo_path):
    repo = OrderRepository(repo_path)
    repo.add(make_order(order_id="O001"))

    found = repo.find_by_id("O001")
    assert found is not None
    assert found.customer_name == "Alice"

    assert repo.find_by_id("NOPE") is None


@pytest.mark.parametrize("typo_id", ["0001", "o001", " O001 ", "0001 "])
def test_find_by_id_tolerates_zero_o_typo_and_case(repo_path, typo_id):
    """'O'(대문자 오)와 '0'(숫자 영)을 헷갈려 입력하는 실수를 보정해야 한다."""
    repo = OrderRepository(repo_path)
    repo.add(make_order(order_id="O001"))

    found = repo.find_by_id(typo_id)

    assert found is not None
    assert found.order_id == "O001"


def test_find_by_id_does_not_falsely_match_unrelated_id(repo_path):
    repo = OrderRepository(repo_path)
    repo.add(make_order(order_id="O001"))

    assert repo.find_by_id("0002") is None


def test_list_by_status_filters_correctly(repo_path):
    repo = OrderRepository(repo_path)
    repo.add(make_order(order_id="O001", status=OrderStatus.RESERVED))
    repo.add(make_order(order_id="O002", status=OrderStatus.CONFIRMED))
    repo.add(make_order(order_id="O003", status=OrderStatus.RESERVED))
    repo.add(make_order(order_id="O004", status=OrderStatus.PRODUCING))
    repo.add(make_order(order_id="O005", status=OrderStatus.REJECTED))

    reserved = repo.list_by_status(OrderStatus.RESERVED)
    assert {o.order_id for o in reserved} == {"O001", "O003"}

    confirmed = repo.list_by_status(OrderStatus.CONFIRMED)
    assert {o.order_id for o in confirmed} == {"O002"}

    producing = repo.list_by_status(OrderStatus.PRODUCING)
    assert {o.order_id for o in producing} == {"O004"}

    rejected = repo.list_by_status(OrderStatus.REJECTED)
    assert {o.order_id for o in rejected} == {"O005"}


def test_persistence_across_new_repository_instance(repo_path):
    repo1 = OrderRepository(repo_path)
    repo1.add(make_order(order_id="O001", sample_id="S001", customer_name="Alice",
                          quantity=5, status=OrderStatus.RESERVED))

    assert os.path.exists(repo_path)

    # 새 인스턴스로 다시 읽었을 때 데이터가 유지되어야 한다.
    repo2 = OrderRepository(repo_path)
    all_orders = repo2.get_all()
    assert len(all_orders) == 1
    restored = all_orders[0]
    assert restored.order_id == "O001"
    assert restored.sample_id == "S001"
    assert restored.customer_name == "Alice"
    assert restored.quantity == 5
    assert restored.status == OrderStatus.RESERVED


def test_update_persists_status_change(repo_path):
    repo = OrderRepository(repo_path)
    repo.add(make_order(order_id="O001", status=OrderStatus.RESERVED))

    order = repo.find_by_id("O001")
    order.status = OrderStatus.CONFIRMED
    repo.update(order)

    repo2 = OrderRepository(repo_path)
    assert repo2.find_by_id("O001").status == OrderStatus.CONFIRMED


def test_update_nonexistent_raises_value_error(repo_path):
    repo = OrderRepository(repo_path)
    with pytest.raises(ValueError):
        repo.update(make_order(order_id="NOPE"))


def test_next_order_id_increments(repo_path):
    repo = OrderRepository(repo_path)
    assert repo.next_order_id() == "O001"

    repo.add(make_order(order_id="O001"))
    assert repo.next_order_id() == "O002"

    repo.add(make_order(order_id="O002"))
    assert repo.next_order_id() == "O003"
