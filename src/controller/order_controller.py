"""주문 접수/승인/거절 유스케이스."""
from src.model.order import Order, OrderStatus
from src.repository.order_repository import OrderRepository
from src.repository.sample_repository import SampleRepository


class ValidationError(Exception):
    """사용자에게 보여줄 메시지를 담은 검증 실패 예외."""


class OrderController:
    def __init__(self, order_repository: OrderRepository = None,
                 sample_repository: SampleRepository = None,
                 production_queue=None):
        self._order_repository = order_repository or OrderRepository()
        self._sample_repository = sample_repository or SampleRepository()
        # 재고 부족 시 생산 등록을 위한 연동 지점. enqueue(order, shortage) 메서드를 가진
        # 객체(Phase 3의 ProductionLineController)가 주입되면 호출하고, 없으면 아무 것도 하지
        # 않는다.
        self._production_queue = production_queue

    def create_order(self, sample_id: str, customer_name: str, quantity) -> Order:
        if self._sample_repository.find_by_id(sample_id) is None:
            raise ValidationError(f"존재하지 않는 시료ID입니다: {sample_id}")
        if not customer_name or not customer_name.strip():
            raise ValidationError("고객명은 비어 있을 수 없습니다.")
        if not isinstance(quantity, int) or isinstance(quantity, bool) or quantity < 1:
            raise ValidationError("주문수량은 1 이상의 정수여야 합니다.")

        order = Order(
            order_id=self._order_repository.next_order_id(),
            sample_id=sample_id,
            customer_name=customer_name.strip(),
            quantity=quantity,
            status=OrderStatus.RESERVED,
        )
        self._order_repository.add(order)
        return order

    def list_reserved(self) -> list:
        return self._order_repository.list_by_status(OrderStatus.RESERVED)

    def approve(self, order_id: str) -> Order:
        order = self._get_reserved_order(order_id)

        sample = self._sample_repository.find_by_id(order.sample_id)
        if sample is None:
            raise ValidationError(f"존재하지 않는 시료ID입니다: {order.sample_id}")
        if sample.stock_quantity >= order.quantity:
            sample.stock_quantity -= order.quantity
            self._sample_repository.update(sample)
            order.status = OrderStatus.CONFIRMED
        else:
            shortage = order.quantity - sample.stock_quantity
            if self._production_queue is not None:
                self._production_queue.enqueue(order, shortage)
            order.status = OrderStatus.PRODUCING

        self._order_repository.update(order)
        return order

    def reject(self, order_id: str) -> Order:
        order = self._get_reserved_order(order_id)
        order.status = OrderStatus.REJECTED
        self._order_repository.update(order)
        return order

    def _get_reserved_order(self, order_id: str) -> Order:
        order = self._order_repository.find_by_id(order_id)
        if order is None:
            raise ValidationError(f"존재하지 않는 주문ID입니다: {order_id}")
        if order.status != OrderStatus.RESERVED:
            raise ValidationError(f"RESERVED 상태의 주문만 처리할 수 있습니다. (현재 상태: {order.status.value})")
        return order
