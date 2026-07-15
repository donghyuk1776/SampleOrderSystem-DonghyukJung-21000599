"""ProductionJob(생산 작업/큐 아이템) 데이터 모델."""
from dataclasses import dataclass


@dataclass
class ProductionJob:
    order_id: str
    sample_id: str
    shortage_quantity: int
    actual_quantity: int
    total_production_time: float
    status: str = "PENDING"

    def to_dict(self) -> dict:
        return {
            "order_id": self.order_id,
            "sample_id": self.sample_id,
            "shortage_quantity": self.shortage_quantity,
            "actual_quantity": self.actual_quantity,
            "total_production_time": self.total_production_time,
            "status": self.status,
        }

    @staticmethod
    def from_dict(data: dict) -> "ProductionJob":
        return ProductionJob(
            order_id=data["order_id"],
            sample_id=data["sample_id"],
            shortage_quantity=data["shortage_quantity"],
            actual_quantity=data["actual_quantity"],
            total_production_time=data["total_production_time"],
            status=data.get("status", "PENDING"),
        )
