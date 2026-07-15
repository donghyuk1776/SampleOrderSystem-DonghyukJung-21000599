"""시료주문, 주문승인/거절 화면."""
from src.controller.order_controller import OrderController, ValidationError
from src.view import colors


class OrderView:
    def __init__(self, controller: OrderController = None):
        self._controller = controller or OrderController()

    def run_create_order(self) -> None:
        print(colors.header("\n==== 시료 주문 ===="))
        sample_id = input("시료ID: ").strip()
        customer_name = input("고객명: ").strip()
        quantity_raw = input("주문수량: ").strip()

        try:
            quantity = int(quantity_raw)
        except ValueError:
            print(colors.error("주문 실패: 주문수량은 1 이상의 정수여야 합니다."))
            return

        try:
            order = self._controller.create_order(sample_id, customer_name, quantity)
            print(f"주문이 접수되었습니다. (주문ID: {order.order_id}, 상태: {colors.status_text(order.status.value)})")
        except ValidationError as e:
            print(colors.error(f"주문 실패: {e}"))

    def run_approval(self) -> None:
        while True:
            reserved_orders = self._controller.list_reserved()
            print(colors.header("\n==== 접수된 주문 (RESERVED) ===="))
            if not reserved_orders:
                print("접수된 주문이 없습니다.")
            else:
                for o in reserved_orders:
                    print(f"[{colors.warning(o.order_id)}] {o.sample_id} / {o.customer_name} / {o.quantity}")

            print("1. 주문 승인")
            print("2. 주문 거절")
            print("0. 이전 메뉴로")
            choice = input("> ").strip()

            if choice == "1":
                self._approve()
            elif choice == "2":
                self._reject()
            elif choice == "0":
                return
            else:
                print("잘못된 입력입니다. 다시 선택해 주세요.")

    def _approve(self) -> None:
        order_id = input(f"승인할 주문ID{self._reserved_ids_hint()}: ").strip()
        try:
            order = self._controller.approve(order_id)
            print(f"주문 '{order_id}'가 승인되었습니다. (전환된 상태: {colors.status_text(order.status.value)})")
        except ValidationError as e:
            print(colors.error(f"승인 실패: {e}"))

    def _reject(self) -> None:
        order_id = input(f"거절할 주문ID{self._reserved_ids_hint()}: ").strip()
        try:
            order = self._controller.reject(order_id)
            print(f"주문 '{order_id}'가 거절되었습니다. (전환된 상태: {colors.status_text(order.status.value)})")
        except ValidationError as e:
            print(colors.error(f"거절 실패: {e}"))

    def _reserved_ids_hint(self) -> str:
        """입력 프롬프트에 지금 승인/거절 가능한 주문ID 목록을 덧붙여 보여준다."""
        reserved_ids = [o.order_id for o in self._controller.list_reserved()]
        if not reserved_ids:
            return ""
        return f" (승인/거절 가능: {', '.join(reserved_ids)})"
