"""Order(주문) 데이터 모델 + 상태 enum."""
from dataclasses import dataclass
from enum import Enum


class OrderStatus(str, Enum):
    RESERVED = "RESERVED"
    REJECTED = "REJECTED"
    PRODUCING = "PRODUCING"
    CONFIRMED = "CONFIRMED"
    RELEASE = "RELEASE"


@dataclass
class Order:
    order_id: str
    sample_id: str
    customer_name: str
    quantity: int
    status: OrderStatus = OrderStatus.RESERVED

    def to_dict(self) -> dict:
        return {
            "order_id": self.order_id,
            "sample_id": self.sample_id,
            "customer_name": self.customer_name,
            "quantity": self.quantity,
            "status": self.status.value,
        }

    @staticmethod
    def from_dict(data: dict) -> "Order":
        return Order(
            order_id=data["order_id"],
            sample_id=data["sample_id"],
            customer_name=data["customer_name"],
            quantity=data["quantity"],
            status=OrderStatus(data.get("status", OrderStatus.RESERVED.value)),
        )
