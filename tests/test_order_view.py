"""OrderView 사용성 회귀 테스트.

주문승인/거절 화면에서 "승인할 주문ID"/"거절할 주문ID" 입력 프롬프트에 지금 승인/거절
가능한(RESERVED) 주문ID 목록이 함께 표시되는지 확인한다. 사용자가 존재하지 않는
주문ID를 반복 입력해 헤매는 문제를 막기 위한 개선이다.
"""
import os

import pytest

from src.controller.order_controller import OrderController
from src.model.sample import Sample
from src.repository.order_repository import OrderRepository
from src.repository.sample_repository import SampleRepository
from src.view.order_view import OrderView


@pytest.fixture
def controller(tmp_path):
    sample_repository = SampleRepository(os.path.join(tmp_path, "samples.json"))
    order_repository = OrderRepository(os.path.join(tmp_path, "orders.json"))
    sample_repository.add(Sample(
        sample_id="S001", name="WaferA", avg_production_time=2.5,
        yield_rate=0.9, stock_quantity=10,
    ))
    return OrderController(order_repository, sample_repository)


def run_view_with_inputs(view, inputs, monkeypatch):
    values = iter(inputs)

    def fake_input(prompt: str = "") -> str:
        print(prompt, end="")  # 실제 input()처럼 프롬프트도 출력해야 capsys로 검증 가능
        return next(values)

    monkeypatch.setattr("builtins.input", fake_input)
    view.run_approval()


def test_approve_prompt_shows_reserved_order_ids(controller, monkeypatch, capsys):
    order = controller.create_order("S001", "Alice", 3)
    view = OrderView(controller)

    run_view_with_inputs(view, ["1", order.order_id, "0"], monkeypatch)

    output = capsys.readouterr().out
    assert f"승인할 주문ID (승인/거절 가능: {order.order_id})" in output


def test_reject_prompt_shows_reserved_order_ids(controller, monkeypatch, capsys):
    order = controller.create_order("S001", "Alice", 3)
    view = OrderView(controller)

    run_view_with_inputs(view, ["2", order.order_id, "0"], monkeypatch)

    output = capsys.readouterr().out
    assert f"거절할 주문ID (승인/거절 가능: {order.order_id})" in output


def test_approve_prompt_shows_multiple_reserved_ids(controller, monkeypatch, capsys):
    order1 = controller.create_order("S001", "Alice", 1)
    order2 = controller.create_order("S001", "Bob", 1)
    view = OrderView(controller)

    run_view_with_inputs(view, ["1", order1.order_id, "0"], monkeypatch)

    output = capsys.readouterr().out
    assert f"{order1.order_id}, {order2.order_id}" in output


def test_approve_prompt_has_no_hint_when_no_reserved_orders(controller, monkeypatch, capsys):
    view = OrderView(controller)

    run_view_with_inputs(view, ["1", "NOPE", "0"], monkeypatch)

    output = capsys.readouterr().out
    assert "승인할 주문ID: " in output
    assert "승인/거절 가능" not in output
