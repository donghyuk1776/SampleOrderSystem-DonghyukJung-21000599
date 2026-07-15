"""출고처리 화면."""
from src.controller.order_controller import ValidationError
from src.controller.shipment_controller import ShipmentController


class ShipmentView:
    def __init__(self, controller: ShipmentController = None):
        self._controller = controller or ShipmentController()

    def run(self) -> None:
        while True:
            confirmed_orders = self._controller.list_confirmed()
            print("\n==== 출고처리 ====")
            if not confirmed_orders:
                print("출고 대상(CONFIRMED) 주문이 없습니다.")
            else:
                for o in confirmed_orders:
                    print(f"[{o.order_id}] {o.sample_id} / {o.customer_name} / {o.quantity}")

            print("1. 출고 실행")
            print("0. 이전 메뉴로")
            choice = input("> ").strip()

            if choice == "1":
                self._ship()
            elif choice == "0":
                return
            else:
                print("잘못된 입력입니다. 다시 선택해 주세요.")

    def _ship(self) -> None:
        order_id = input("출고할 주문ID: ").strip()
        try:
            order = self._controller.ship(order_id)
            print(f"주문 '{order_id}'가 출고되었습니다. (전환된 상태: {order.status.value})")
        except ValidationError as e:
            print(f"출고 실패: {e}")
