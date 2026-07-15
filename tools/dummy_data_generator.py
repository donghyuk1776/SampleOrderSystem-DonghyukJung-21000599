"""Dummy 데이터 생성 도구.

`SampleController.register` / `OrderController.create_order` API를 통해서만 데이터를
생성한다 (JSON 파일 직접 조작 금지). 이렇게 해야 기존 검증 로직(중복 ID 금지, 수율/수량 범위
등)을 그대로 통과한 유효한 데이터만 생성된다.

실행 방법:

    python -m tools.dummy_data_generator --samples 5 --orders 5

생성 규칙:
- 수율은 0 초과 1 이하 범위에서 랜덤 생성한다 (실제 구현은 시연 편의상 0.5~1.0 구간만
  사용한다 — 수율이 매우 낮아 실생산량이 급증하는 극단적 케이스까지 시연하려면 이 구간을
  넓혀서 실행할 것).
- 평균 생산시간, 주문수량도 유효 범위 내에서 랜덤 생성한다.
- 재현 가능한 시연을 위해 random 시드를 고정한다.
- 최소 1개 이상의 시료는 등록 직후 재고를 채워 "재고 충분" 상태로 만들고, 최소 1개는 재고
  0(부족) 상태를 유지해, 이후 사람이 주문을 승인할 때 CONFIRMED/PRODUCING 두 분기를 모두
  시연할 수 있게 한다.
"""
import argparse
import random

from src.controller.errors import ValidationError
from src.controller.order_controller import OrderController
from src.controller.sample_controller import SampleController
from src.repository.sample_repository import SampleRepository

CUSTOMER_NAMES = ["가나전자", "다라반도체", "마바소재", "사아테크", "자차랩스"]


def _unique_sample_id(sample_repository: SampleRepository, index: int) -> str:
    """이미 존재하는 시료ID와 충돌하지 않는 더미 시료ID를 만든다."""
    while True:
        sample_id = f"DUMMY-S{index:03d}"
        if sample_repository.find_by_id(sample_id) is None:
            return sample_id
        index += 1


def generate_samples(sample_controller: SampleController, sample_repository: SampleRepository,
                      count: int) -> list:
    """더미 시료를 `count`개 등록한다. 첫 번째 시료는 등록 직후 재고를 채워 "재고 충분"
    케이스로 만들고, 나머지는 재고 0(재고 부족) 상태를 유지한다."""
    samples = []
    next_index = 1
    for i in range(count):
        sample_id = _unique_sample_id(sample_repository, next_index)
        next_index = int(sample_id.split("S")[-1]) + 1

        avg_production_time = round(random.uniform(0.5, 5.0), 2)
        yield_rate = round(random.uniform(0.5, 1.0), 2)
        sample = sample_controller.register(
            sample_id=sample_id,
            name=f"더미시료{i + 1}",
            avg_production_time=avg_production_time,
            yield_rate=yield_rate,
        )

        if i == 0:
            sample.stock_quantity = random.randint(20, 50)
            sample_repository.update(sample)

        samples.append(sample)
    return samples


def generate_orders(order_controller: OrderController, samples: list, count: int) -> list:
    """더미 주문을 `count`개 생성한다. 첫 번째 주문은 재고가 충분한 시료를 대상으로 재고보다
    적은 수량을 주문해 승인 시 CONFIRMED 분기를 유도하고, 두 번째 주문(가능하면)은 재고가
    부족한 시료를 대상으로 주문해 승인 시 PRODUCING 분기를 유도한다."""
    orders = []
    in_stock_sample = next((s for s in samples if s.stock_quantity > 0), None)
    out_of_stock_sample = next((s for s in samples if s.stock_quantity == 0), None)

    for i in range(count):
        if i == 0 and in_stock_sample is not None:
            sample = in_stock_sample
            quantity = random.randint(1, sample.stock_quantity)
        elif i == 1 and out_of_stock_sample is not None:
            sample = out_of_stock_sample
            quantity = random.randint(1, 10)
        else:
            sample = random.choice(samples)
            quantity = random.randint(1, 10)

        customer_name = random.choice(CUSTOMER_NAMES)
        order = order_controller.create_order(sample.sample_id, customer_name, quantity)
        orders.append(order)
    return orders


def parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="더미 시료/주문 데이터 생성 도구")
    parser.add_argument("--samples", type=int, default=5, help="생성할 더미 시료 개수 (기본 5)")
    parser.add_argument("--orders", type=int, default=5, help="생성할 더미 주문 개수 (기본 5)")
    return parser.parse_args(argv)


def main(argv=None) -> None:
    args = parse_args(argv)
    random.seed(42)

    sample_repository = SampleRepository()
    sample_controller = SampleController(sample_repository)
    order_controller = OrderController()

    samples = generate_samples(sample_controller, sample_repository, args.samples)
    print(f"더미 시료 {len(samples)}개를 등록했습니다.")

    try:
        orders = generate_orders(order_controller, samples, args.orders)
        print(f"더미 주문 {len(orders)}개를 생성했습니다.")
    except ValidationError as e:
        print(f"더미 주문 생성 중 오류가 발생했습니다: {e}")


if __name__ == "__main__":
    main()
