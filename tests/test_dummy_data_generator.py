"""Dummy 데이터 생성 도구 스모크 테스트.

Repository/Controller API를 통해 생성되는지, 요청한 개수만큼 생성되는지, 생성값이
검증 규칙(수율 범위 등)을 만족하는지, CLI 인자 파싱이 올바른지 확인한다.
"""
import os

from src.controller.order_controller import OrderController
from src.controller.sample_controller import SampleController
from src.repository.order_repository import OrderRepository
from src.repository.sample_repository import SampleRepository
from tools.dummy_data_generator import generate_orders, generate_samples, parse_args


def test_parse_args_defaults():
    args = parse_args([])
    assert args.samples == 5
    assert args.orders == 5


def test_parse_args_custom_values():
    args = parse_args(["--samples", "2", "--orders", "3"])
    assert args.samples == 2
    assert args.orders == 3


def test_generate_samples_creates_requested_count_with_valid_yield(tmp_path):
    sample_repository = SampleRepository(os.path.join(tmp_path, "samples.json"))
    sample_controller = SampleController(sample_repository)

    samples = generate_samples(sample_controller, sample_repository, count=4)

    assert len(samples) == 4
    assert len(sample_repository.get_all()) == 4
    for sample in samples:
        assert 0 < sample.yield_rate <= 1
        assert sample.avg_production_time > 0


def test_generate_samples_first_sample_has_stock_others_do_not(tmp_path):
    sample_repository = SampleRepository(os.path.join(tmp_path, "samples.json"))
    sample_controller = SampleController(sample_repository)

    samples = generate_samples(sample_controller, sample_repository, count=3)

    assert samples[0].stock_quantity > 0
    assert all(s.stock_quantity == 0 for s in samples[1:])


def test_generate_orders_creates_requested_count_referencing_existing_samples(tmp_path):
    sample_repository = SampleRepository(os.path.join(tmp_path, "samples.json"))
    sample_controller = SampleController(sample_repository)
    order_repository = OrderRepository(os.path.join(tmp_path, "orders.json"))
    order_controller = OrderController(order_repository, sample_repository)

    samples = generate_samples(sample_controller, sample_repository, count=2)
    orders = generate_orders(order_controller, samples, count=2)

    assert len(orders) == 2
    sample_ids = {s.sample_id for s in samples}
    assert all(order.sample_id in sample_ids for order in orders)


def test_generate_orders_first_two_orders_cover_in_stock_and_out_of_stock_cases(tmp_path):
    sample_repository = SampleRepository(os.path.join(tmp_path, "samples.json"))
    sample_controller = SampleController(sample_repository)
    order_repository = OrderRepository(os.path.join(tmp_path, "orders.json"))
    order_controller = OrderController(order_repository, sample_repository)

    samples = generate_samples(sample_controller, sample_repository, count=2)
    orders = generate_orders(order_controller, samples, count=2)

    in_stock_sample_id = samples[0].sample_id
    out_of_stock_sample_id = samples[1].sample_id
    assert orders[0].sample_id == in_stock_sample_id
    assert orders[0].quantity <= samples[0].stock_quantity
    assert orders[1].sample_id == out_of_stock_sample_id
