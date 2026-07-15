"""모니터링 화면 (읽기 전용)."""
from src.controller.monitoring_controller import MonitoringController
from src.view import colors


class MonitoringView:
    def __init__(self, controller: MonitoringController = None):
        self._controller = controller or MonitoringController()

    def run(self) -> None:
        while True:
            status_counts = self._controller.count_by_status()
            orders_by_status = self._controller.orders_by_status()
            stock_statuses = self._controller.stock_status()

            print(colors.header("\n==== 모니터링 ===="))
            print("[주문량]")
            for status, count in status_counts.items():
                order_ids = orders_by_status.get(status, [])
                ids_text = ", ".join(order_ids) if order_ids else "-"
                print(f"  {colors.status_text(status)}: {count}건 ({ids_text})")

            print("\n[재고량]")
            if not stock_statuses:
                print("등록된 시료가 없습니다.")
            else:
                print("시료ID / 이름 / 재고수량 / 상태")
                for s in stock_statuses:
                    print(f"{s.sample_id} / {s.name} / {s.stock_quantity} / "
                          f"{colors.stock_status_text(s.status_label)}")

            print("0. 이전 메뉴로")
            choice = input("> ").strip()

            if choice == "0":
                return
            else:
                print("잘못된 입력입니다. 다시 선택해 주세요.")
