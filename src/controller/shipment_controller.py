"""출고 처리 유스케이스."""
from src.controller.order_controller import ValidationError
from src.model.order import OrderStatus
from src.repository.order_repository import OrderRepository


class ShipmentController:
    def __init__(self, order_repository: OrderRepository = None):
        self._order_repository = order_repository or OrderRepository()

    def list_confirmed(self) -> list:
        return self._order_repository.list_by_status(OrderStatus.CONFIRMED)

    def ship(self, order_id: str):
        order = self._order_repository.find_by_id(order_id)
        if order is None:
            raise ValidationError(f"존재하지 않는 주문ID입니다: {order_id}")
        if order.status != OrderStatus.CONFIRMED:
            raise ValidationError(f"CONFIRMED 상태의 주문만 출고할 수 있습니다. (현재 상태: {order.status.value})")

        order.status = OrderStatus.RELEASE
        self._order_repository.update(order)
        return order
