"""Order CRUD (JSON 기반)."""
from src.model.order import Order, OrderStatus
from src.repository import json_storage


class OrderRepository:
    def __init__(self, path: str = "data/orders.json"):
        self._path = path

    def add(self, order: Order) -> None:
        orders = self.get_all()
        orders.append(order)
        self._persist(orders)

    def get_all(self) -> list:
        raw = json_storage.load(self._path)
        return [Order.from_dict(item) for item in raw]

    def find_by_id(self, order_id: str):
        for order in self.get_all():
            if order.order_id == order_id:
                return order
        return None

    def list_by_status(self, status: OrderStatus) -> list:
        return [o for o in self.get_all() if o.status == status]

    def update(self, order: Order) -> None:
        orders = self.get_all()
        for i, existing in enumerate(orders):
            if existing.order_id == order.order_id:
                orders[i] = order
                self._persist(orders)
                return
        raise ValueError(f"존재하지 않는 주문ID입니다: {order.order_id}")

    def next_order_id(self) -> str:
        orders = self.get_all()
        return f"O{len(orders) + 1:03d}"

    def _persist(self, orders: list) -> None:
        json_storage.save(self._path, [o.to_dict() for o in orders])
