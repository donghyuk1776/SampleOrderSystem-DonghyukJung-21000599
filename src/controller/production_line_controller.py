"""생산 큐 등록/처리 유스케이스 (Phase 2 OrderController.approve()의 연동 지점 구현)."""
import math

from src.model.order import OrderStatus
from src.model.production_job import ProductionJob
from src.repository.order_repository import OrderRepository
from src.repository.production_queue_repository import ProductionQueueRepository
from src.repository.sample_repository import SampleRepository


class ProductionLineError(Exception):
    """생산라인 처리 중 발생한, 사용자에게 보여줄 메시지를 담은 예외."""


class ProductionLineController:
    def __init__(self, sample_repository: SampleRepository = None,
                 order_repository: OrderRepository = None,
                 production_queue_repository: ProductionQueueRepository = None):
        self._sample_repository = sample_repository or SampleRepository()
        self._order_repository = order_repository or OrderRepository()
        self._production_queue_repository = production_queue_repository or ProductionQueueRepository()

    def enqueue(self, order, shortage_quantity: int) -> ProductionJob:
        """OrderController가 재고 부족 시 호출하는 인터페이스."""
        sample = self._sample_repository.find_by_id(order.sample_id)
        if sample is None:
            raise ProductionLineError(f"존재하지 않는 시료ID입니다: {order.sample_id}")
        actual_quantity = math.ceil(shortage_quantity / sample.yield_rate)
        total_production_time = sample.avg_production_time * actual_quantity

        job = ProductionJob(
            order_id=order.order_id,
            sample_id=order.sample_id,
            shortage_quantity=shortage_quantity,
            actual_quantity=actual_quantity,
            total_production_time=total_production_time,
        )
        self._production_queue_repository.add(job)
        return job

    def list_pending(self) -> list:
        """큐에 남아있는 작업을 등록 순서대로 반환한다."""
        return self._production_queue_repository.get_all()

    def process_next(self):
        """큐 맨 앞(FIFO) 작업을 꺼내 처리한다.

        재고 증가, 주문 상태 PRODUCING -> CONFIRMED 전환, 큐에서 제거를 수행한다.
        큐가 비어있으면 None을 반환한다.
        """
        job = self._production_queue_repository.pop_first()
        if job is None:
            return None

        sample = self._sample_repository.find_by_id(job.sample_id)
        if sample is None:
            raise ProductionLineError(f"존재하지 않는 시료ID입니다: {job.sample_id}")

        order = self._order_repository.find_by_id(job.order_id)
        if order is not None and order.status == OrderStatus.PRODUCING:
            # 생산된 만큼 재고를 늘리되, 이 주문에 예약된 수량(order.quantity)은 그만큼
            # 다시 차감해 최종 재고에 반영한다 - 재고 충분 케이스(OrderController.approve())가
            # 승인 시점에 즉시 주문수량을 차감하는 것과 동일하게, 이 주문은 "충족되었다"는
            # 상태(CONFIRMED)가 되는 시점에 재고에서 소진되어야 한다. 남는 차이
            # (actual_quantity - order.quantity)는 수율 손실을 감안해 더 생산한 여유분으로,
            # 다른 주문에 쓸 수 있는 재고로 남는다.
            sample.stock_quantity += job.actual_quantity - order.quantity
            order.status = OrderStatus.CONFIRMED
            self._order_repository.update(order)
        else:
            sample.stock_quantity += job.actual_quantity
        self._sample_repository.update(sample)

        return job
