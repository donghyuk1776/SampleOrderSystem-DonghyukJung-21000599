"""데이터 모니터링 도구 (읽기 전용).

메인 프로그램(`python -m src.main`)과 별도 프로세스로 실행한다:

    python -m tools.data_monitor

시료/주문/생산 큐 JSON 데이터를 표 형태로 출력한다. 데이터를 생성/수정/삭제하지 않으며,
기존 Repository(`SampleRepository`/`OrderRepository`/`ProductionQueueRepository`)를 그대로
재사용해 조회만 수행한다. "r"을 입력하면 파일을 다시 읽어 최신 상태를 보여주고, "q"를 입력하면
종료한다.
"""
from src.repository.order_repository import OrderRepository
from src.repository.production_queue_repository import ProductionQueueRepository
from src.repository.sample_repository import SampleRepository
from src.view import colors


class DataMonitor:
    def __init__(self, sample_repository: SampleRepository = None,
                 order_repository: OrderRepository = None,
                 production_queue_repository: ProductionQueueRepository = None):
        self._sample_repository = sample_repository or SampleRepository()
        self._order_repository = order_repository or OrderRepository()
        self._production_queue_repository = production_queue_repository or ProductionQueueRepository()

    def render(self) -> None:
        self._render_samples()
        self._render_orders()
        self._render_production_queue()

    def _render_samples(self) -> None:
        samples = self._sample_repository.get_all()
        print(colors.header("\n==== 시료 목록 (samples.json) ===="))
        if not samples:
            print("등록된 시료가 없습니다.")
            return
        print(f"{'시료ID':<10}{'이름':<15}{'평균생산시간':<15}{'수율':<10}{'재고':<10}")
        for s in samples:
            print(f"{s.sample_id:<10}{s.name:<15}{s.avg_production_time:<15}"
                  f"{s.yield_rate:<10}{s.stock_quantity:<10}")

    def _render_orders(self) -> None:
        orders = self._order_repository.get_all()
        print(colors.header("\n==== 주문 목록 (orders.json) ===="))
        if not orders:
            print("등록된 주문이 없습니다.")
            return
        print(f"{'주문ID':<10}{'시료ID':<10}{'고객명':<15}{'수량':<10}{'상태':<12}")
        for o in orders:
            print(f"{o.order_id:<10}{o.sample_id:<10}{o.customer_name:<15}"
                  f"{o.quantity:<10}{colors.status_text(f'{o.status.value:<12}')}")

    def _render_production_queue(self) -> None:
        jobs = self._production_queue_repository.get_all()
        print(colors.header("\n==== 생산 큐 (production_queue.json) ===="))
        if not jobs:
            print("대기 중인 생산 작업이 없습니다.")
            return
        print(f"{'주문ID':<10}{'시료ID':<10}{'부족수량':<10}{'실생산량':<10}"
              f"{'총생산시간':<12}{'상태':<12}")
        for j in jobs:
            print(f"{j.order_id:<10}{j.sample_id:<10}{j.shortage_quantity:<10}"
                  f"{j.actual_quantity:<10}{j.total_production_time:<12}{j.status:<12}")


def main() -> None:
    monitor = DataMonitor()
    monitor.render()
    while True:
        command = input("\n[r: 새로고침 / q: 종료] > ").strip().lower()
        if command == "r":
            monitor.render()
        elif command == "q":
            print("데이터 모니터링 도구를 종료합니다.")
            return
        else:
            print("잘못된 입력입니다. r 또는 q를 입력해 주세요.")


if __name__ == "__main__":
    main()
