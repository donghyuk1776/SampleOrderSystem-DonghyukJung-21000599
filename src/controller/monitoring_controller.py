"""모니터링(읽기 전용 집계) 유스케이스."""
from collections import namedtuple

from src.model.order import OrderStatus
from src.repository.order_repository import OrderRepository
from src.repository.sample_repository import SampleRepository

StockStatus = namedtuple("StockStatus", ["sample_id", "name", "stock_quantity", "status_label"])

_COUNTED_STATUSES = [
    OrderStatus.RESERVED,
    OrderStatus.CONFIRMED,
    OrderStatus.PRODUCING,
    OrderStatus.RELEASE,
]

_UNSHIPPED_STATUSES = (OrderStatus.RESERVED, OrderStatus.PRODUCING, OrderStatus.CONFIRMED)


class MonitoringController:
    def __init__(self, order_repository: OrderRepository = None,
                 sample_repository: SampleRepository = None):
        self._order_repository = order_repository or OrderRepository()
        self._sample_repository = sample_repository or SampleRepository()

    def count_by_status(self) -> dict:
        orders = self._order_repository.get_all()
        return {
            status.value: len([o for o in orders if o.status == status])
            for status in _COUNTED_STATUSES
        }

    def stock_status(self) -> list:
        orders = self._order_repository.get_all()
        samples = self._sample_repository.get_all()

        result = []
        for sample in samples:
            unshipped_demand = sum(
                o.quantity for o in orders
                if o.sample_id == sample.sample_id and o.status in _UNSHIPPED_STATUSES
            )
            result.append(StockStatus(
                sample_id=sample.sample_id,
                name=sample.name,
                stock_quantity=sample.stock_quantity,
                status_label=self._status_label(sample.stock_quantity, unshipped_demand),
            ))
        return result

    @staticmethod
    def _status_label(stock_quantity: int, unshipped_demand: int) -> str:
        if stock_quantity == 0:
            return "고갈"
        if stock_quantity < unshipped_demand:
            return "부족"
        return "여유"
