"""Sample(시료) 데이터 모델."""
from dataclasses import dataclass


@dataclass
class Sample:
    sample_id: str
    name: str
    avg_production_time: float
    yield_rate: float  # 0 < yield_rate <= 1
    stock_quantity: int = 0

    def to_dict(self) -> dict:
        return {
            "sample_id": self.sample_id,
            "name": self.name,
            "avg_production_time": self.avg_production_time,
            "yield_rate": self.yield_rate,
            "stock_quantity": self.stock_quantity,
        }

    @staticmethod
    def from_dict(data: dict) -> "Sample":
        return Sample(
            sample_id=data["sample_id"],
            name=data["name"],
            avg_production_time=data["avg_production_time"],
            yield_rate=data["yield_rate"],
            stock_quantity=data.get("stock_quantity", 0),
        )
