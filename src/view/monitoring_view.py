"""모니터링 화면 (읽기 전용)."""
from src.controller.monitoring_controller import MonitoringController


class MonitoringView:
    def __init__(self, controller: MonitoringController = None):
        self._controller = controller or MonitoringController()

    def run(self) -> None:
        while True:
            status_counts = self._controller.count_by_status()
            stock_statuses = self._controller.stock_status()

            print("\n==== 모니터링 ====")
            counts_line = " / ".join(f"{status}: {count}" for status, count in status_counts.items())
            print(f"[주문량] {counts_line}")

            print("\n[재고량]")
            if not stock_statuses:
                print("등록된 시료가 없습니다.")
            else:
                print("시료ID / 이름 / 재고수량 / 상태")
                for s in stock_statuses:
                    print(f"{s.sample_id} / {s.name} / {s.stock_quantity} / {s.status_label}")

            print("0. 이전 메뉴로")
            choice = input("> ").strip()

            if choice == "0":
                return
            else:
                print("잘못된 입력입니다. 다시 선택해 주세요.")
