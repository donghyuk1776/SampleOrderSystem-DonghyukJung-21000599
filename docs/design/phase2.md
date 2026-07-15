# Phase 2 설계 - 시료 주문 + 주문 승인/거절

> 목표 정의: [PLAN.md](../../PLAN.md) Phase 2
> 기능 명세: [docs/FEATURES/sample-order.md](../FEATURES/sample-order.md),
> [docs/FEATURES/order-approval-rejection.md](../FEATURES/order-approval-rejection.md)
> 전제: [Phase 1](./phase1.md)에서 시료 등록/조회가 동작해야 주문을 넣을 시료가 존재한다.

## 1. 목표

- 시료를 대상으로 주문을 접수(`RESERVED`)할 수 있다.
- 접수된 주문을 승인/거절할 수 있으며, 승인 시 재고 상황에 따라 `CONFIRMED` 또는 `PRODUCING`으로
  자동 분기한다.
- 재고 부족으로 `PRODUCING`이 된 주문은 이후 [Phase 3](./phase3.md)에서 실제로 생산 처리된다.
  Phase 2에서는 "생산 큐에 등록되었다"는 표시까지만 확인한다.

## 2. 디렉터리 추가분

```
src/
  model/
    order.py                     # Order 데이터 모델 (+ OrderStatus enum)
  repository/
    order_repository.py          # Order CRUD (JSON 기반)
  controller/
    order_controller.py          # 주문 접수/승인/거절 유스케이스
  view/
    order_view.py                 # 시료주문, 주문승인/거절 화면
data/
  orders.json
tests/
  test_order_repository.py
  test_order_controller.py
```

## 3. 데이터 모델 (`model/order.py`)

```python
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
```

- `order_id`는 `OrderRepository.next_order_id()`가 `len(get_all())+1`을 `"O001"` 형식으로
  포맷하여 자동 생성한다 (별도 시퀀스 파일 없음). 주문 삭제 기능은 없다는 전제이며, 향후 삭제
  기능이 추가되면 ID 재사용/충돌 방지를 위해 별도 시퀀스 저장 방식으로 변경이 필요하다.

## 4. 컨트롤러 (`controller/order_controller.py`)

- `create_order(sample_id, customer_name, quantity)`:
  - 검증: `sample_id`가 `SampleRepository`에 존재하는지, `quantity >= 1` 정수인지(`bool`은
    정수로 취급하지 않고 거부), `customer_name` 공백 아님
  - `customer_name`은 앞뒤 공백을 제거(`strip()`)한 뒤 저장한다
  - 통과 시 `Order(status=RESERVED)` 생성 및 저장
- `list_reserved()`: `RESERVED` 상태 주문만 반환 (승인/거절 화면용)
- `approve(order_id)`:
  - 대상 주문이 `RESERVED`가 아니면 거부
  - `SampleRepository`에서 해당 시료의 `stock_quantity`와 `quantity` 비교
    - 재고 충분(`stock_quantity >= quantity`): 재고를 `quantity`만큼 차감, 상태 `CONFIRMED`로 변경
    - 재고 부족: 부족분(`quantity - stock_quantity`)을 계산해
      [`ProductionLineController`](./phase3.md)에 생산 요청 등록(생산 큐 append), 상태
      `PRODUCING`으로 변경
      - Phase 2 시점에는 `ProductionLineController`가 아직 없으므로, 이 연동 지점은
        인터페이스만 정의해두고(`production_queue.enqueue(order, shortage)` — 실생산량 계산식
        `ceil(부족분/수율)`에 부족분이 필요하므로 `shortage`를 함께 전달) Phase 3에서 실제
        구현을 연결한다. Phase 2 완료 시점에는 최소한 "부족분 계산 + PRODUCING 전환 + 큐에 데이터가
        쌓이는 것"까지 확인 가능해야 한다 (생산 완료 처리 자체는 Phase 3에서 확인).
  - 이미 `RESERVED`가 아닌 주문에 대한 재승인 시도는 에러 처리
- `reject(order_id)`: `RESERVED`가 아니면 거부, 맞으면 상태 `REJECTED`로 변경

## 5. 뷰 흐름

**시료주문 메뉴**: 시료ID/고객명/주문수량 입력 → 생성 결과(주문ID, 상태 `RESERVED`) 출력

**주문승인/거절 메뉴**:
```
==== 접수된 주문 (RESERVED) ====
[주문ID] 시료ID / 고객명 / 수량
...
1. 주문 승인
2. 주문 거절
0. 이전 메뉴로
>
```
- 승인/거절 후 처리 결과(전환된 상태)를 즉시 출력

## 6. 상태 전이 검증 포인트

```
RESERVED --(승인, 재고충분)--> CONFIRMED
RESERVED --(승인, 재고부족)--> PRODUCING
RESERVED --(거절)--> REJECTED
```

## 7. 테스트 계획

- `test_order_repository.py`: 저장/조회/재실행 후 유지 여부 (Phase 1 패턴과 동일)
- `test_order_controller.py`
  - 존재하지 않는 시료ID로 주문 생성 시 거부
  - 수량 0/음수/실수 입력 시 거부
  - 재고 충분 시 승인 → `CONFIRMED` + 재고 차감 검증
  - 재고 부족 시 승인 → `PRODUCING` + 부족분 계산 검증
  - 거절 → `REJECTED`
  - `RESERVED`가 아닌 주문 재처리 시도 → 거부

## 8. 실행 및 수동 테스트 방법 (고객님용)

1. Phase 1에서 등록한 시료 중 하나로 주문 생성 (수량은 재고보다 적게)
2. 주문승인/거절 메뉴에서 방금 만든 주문을 승인 → `CONFIRMED`로 바뀌고 재고가 줄어드는지 확인
3. 재고보다 많은 수량으로 새 주문을 생성 후 승인 → `PRODUCING`으로 바뀌는지 확인 (실제 생산은
   Phase 3에서 확인)
4. 새 주문을 하나 더 만들어 거절 → `REJECTED`로 바뀌는지 확인
5. 이미 처리된 주문을 다시 승인/거절 시도 → 에러 메시지로 거부되는지 확인

## 9. Phase 2 완료 기준 (Definition of Done)

- 7번 테스트 전부 통과
- 8번 수동 테스트 시나리오 사람이 직접 수행 시 기대대로 동작
- Verify Harness(4-Subagent) 통과
