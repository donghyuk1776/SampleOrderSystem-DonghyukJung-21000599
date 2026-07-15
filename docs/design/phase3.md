# Phase 3 설계 - 생산라인

> 목표 정의: [PLAN.md](../../PLAN.md) Phase 3
> 기능 명세: [docs/FEATURES/production-line.md](../FEATURES/production-line.md)
> 전제: [Phase 2](./phase2.md)에서 재고 부족 주문이 `PRODUCING`으로 전환되고 생산 큐 연동
> 지점이 마련되어 있어야 한다.

## 1. 목표

- Phase 2에서 `PRODUCING`으로 전환된 주문을 생산 큐(FIFO)에서 실제로 처리한다.
- 실생산량/총생산시간을 계산하고, 생산 현황과 대기열을 조회할 수 있다.
- 생산이 완료되면 주문 상태 `PRODUCING -> CONFIRMED`로 전환하고, 재고를 `+= 실생산량 - 주문수량`
  으로 갱신한다 (재고 충분 케이스의 승인 즉시 차감과 동일하게, CONFIRMED가 되는 시점에 주문
  수량만큼 재고에서 소진되어야 한다 — `docs/FEATURES/production-line.md` §2 참고).

## 2. 디렉터리 추가분

```
src/
  model/
    production_job.py            # 생산 작업(큐 아이템) 모델
  repository/
    production_queue_repository.py  # 생산 큐 영속화 (JSON 기반, 리스트 순서 = FIFO 순서)
  controller/
    production_line_controller.py   # 생산 큐 등록/처리 로직 (Phase 2의 연동 지점 구현)
  view/
    production_line_view.py          # 생산라인 현황/대기열 화면
data/
  production_queue.json
tests/
  test_production_line_controller.py
```

## 3. 데이터 모델 (`model/production_job.py`)

```python
@dataclass
class ProductionJob:
    order_id: str
    sample_id: str
    shortage_quantity: int        # 부족분
    actual_quantity: int          # 실생산량 = ceil(shortage_quantity / yield_rate)
    total_production_time: float  # = avg_production_time * actual_quantity
    status: str = "PENDING"       # 표기용 필드. process_next()가 "다음 생산 완료 처리"를
                                   # 즉시 완결시키는 설계이므로 큐에 있는 동안은 항상 PENDING
                                   # 이며 별도 IN_PROGRESS/DONE 전이는 없다. 큐의 맨 앞 항목은
                                   # (뷰 §5의 "현재 생산중" 표기 목적) 사람이 트리거하기 전까지
                                   # "다음에 처리될 작업"을 의미한다.
```

## 4. 컨트롤러 (`controller/production_line_controller.py`)

- `enqueue(order, shortage_quantity)`:
  - 대상 시료의 `yield_rate`, `avg_production_time` 조회
  - `actual_quantity = ceil(shortage_quantity / yield_rate)`
  - `total_production_time = avg_production_time * actual_quantity`
  - `ProductionJob` 생성 후 큐(리스트) 맨 뒤에 추가 (FIFO)
  - Phase 2의 `OrderController.approve()`에서 재고 부족 분기 시 이 메서드를 호출하도록 연결한다.
- `list_pending()`: 큐에 남아있는 작업을 등록 순서대로 반환 (대기주문확인 화면용)
- `process_next()` 또는 `process_job(order_id)` (콘솔 메뉴에서 "생산 진행/완료 처리" 트리거로
  호출; 자동 타이머는 사용하지 않고 사람이 메뉴에서 진행시키는 방식으로 구현):
  - 큐 맨 앞(FIFO) 작업을 꺼내 처리
  - 해당 `order_id`의 주문을 조회해 `PRODUCING` 상태인 경우: `SampleRepository`의 재고를
    `actual_quantity - order.quantity`만큼 증감시키고(즉, 생산량은 더하고 이 주문이 소진하는
    수량은 뺀다), 주문 상태를 `CONFIRMED`로 변경
    - (버그 수정 이력) 최초 구현에서는 `actual_quantity`만 더하고 `order.quantity`를 빼지
      않아, 생산을 거쳐 출고까지 완료된 주문의 수량이 재고에서 전혀 소진되지 않는
      재고 계산 오류가 있었다. 재고 충분 케이스(승인 즉시 `order.quantity` 차감)와 동일한
      시점(= CONFIRMED 전환 시점)에 소진되도록 수정했다.
    - 주문을 찾지 못했거나 이미 다른 사유로 `PRODUCING`이 아니게 된 경우(방어적 케이스)는
      `actual_quantity`만 재고에 더한다 (어떤 주문에도 소진되지 않았으므로 전량 재고로 남는다).
  - 큐에서 제거

> 참고: PRD/기능 명세에는 생산이 "자동으로 완료되는 시점"이 명시돼 있지 않으므로, Phase 3에서는
> 사람이 콘솔 메뉴에서 "다음 생산 완료 처리"를 실행하는 방식으로 구현한다. 이는
> `docs/FEATURES/production-line.md`의 "표기할 정보 수준은 자율적으로 결정" 조항에 따른 설계
> 판단이며, 실제 구현 시 CLAUDE.md/PRD.md에 확정 내용을 반영한다.

## 5. 뷰 흐름

**생산라인 메뉴**:
```
==== 생산라인 ====
[현재 생산중]
주문ID / 시료ID / 실생산량 / 총생산시간

[대기중 (FIFO)]
1) 주문ID ...
2) 주문ID ...

1. 다음 생산 완료 처리
0. 이전 메뉴로
>
```

## 6. 상태 전이 검증 포인트

```
PRODUCING --(생산완료 처리)--> CONFIRMED  (+ 재고 증가)
```

## 7. 테스트 계획

- `ceil(shortage/yield_rate)` 계산 검증 (나누어 떨어지지 않는 경우 포함, 예: 부족분 5, 수율
  0.9 → ceil(5/0.9)=6)
- `total_production_time` 계산 검증
- 여러 건을 순서대로 등록 후 `process_job` 반복 호출 시 FIFO 순서로 처리되는지 검증
- 생산 완료 후 주문 상태 `CONFIRMED` 전환 및 재고 증가량이 `actual_quantity`와 일치하는지 검증

## 8. 실행 및 수동 테스트 방법 (고객님용)

1. Phase 2에서 만들어 둔 재고 부족 `PRODUCING` 주문을 생산라인 메뉴에서 대기열로 확인
2. 여러 건을 추가로 만들어 등록 순서와 대기열 표시 순서가 같은지 확인
3. "다음 생산 완료 처리"를 실행 → 먼저 등록한 주문부터 처리되는지, 처리 후 대기열에서 빠지는지
   확인
4. 처리된 주문을 [시료주문/승인](./phase2.md) 메뉴나 [시료관리](./phase1.md) 조회에서 확인 →
   상태가 `CONFIRMED`로 바뀌고 재고가 늘어났는지 확인

## 9. Phase 3 완료 기준 (Definition of Done)

- 7번 테스트 전부 통과
- 8번 수동 테스트 시나리오 사람이 직접 수행 시 기대대로 동작
- Verify Harness(4-Subagent) 통과
