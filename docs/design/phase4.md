# Phase 4 설계 - 출고처리

> 목표 정의: [PLAN.md](../../PLAN.md) Phase 4
> 기능 명세: [docs/FEATURES/shipment.md](../FEATURES/shipment.md)
> 전제: [Phase 2](./phase2.md)/[Phase 3](./phase3.md)를 통해 `CONFIRMED` 상태 주문이 존재해야
> 한다.

## 1. 목표

- `CONFIRMED` 상태 주문을 선택해 출고 처리를 실행하면 `RELEASE`로 전환한다.
- 이 시점부터 시료등록 → 주문 → 승인/(생산) → 출고까지 전체 흐름을 처음부터 끝까지 사람이
  직접 실행해볼 수 있다.

## 2. 디렉터리 추가분

```
src/
  controller/
    shipment_controller.py      # 출고 처리 유스케이스 (OrderRepository 재사용)
  view/
    shipment_view.py             # 출고처리 화면
tests/
  test_shipment_controller.py
```

- 별도의 Model/Repository 없이 Phase 2의 `Order`/`OrderRepository`를 재사용한다.
- 예외 클래스도 별도로 만들지 않고 Phase 2의 `order_controller.ValidationError`를 그대로
  import하여 재사용한다 (컨트롤러 간 예외 계약을 통일하기 위함. 컨트롤러가 늘어나면 Phase 6
  품질 정리 단계에서 공용 `errors.py`로 추출을 검토한다).

## 3. 컨트롤러 (`controller/shipment_controller.py`)

- `list_confirmed()`: `CONFIRMED` 상태 주문 목록 반환
- `ship(order_id)`:
  - 대상 주문이 `CONFIRMED`가 아니면 에러 처리 (거부 사유를 명시: 존재하지 않는 주문 / 상태
    불일치)
  - 통과 시 상태를 `RELEASE`로 변경 후 저장

## 4. 뷰 흐름

```
==== 출고처리 ====
[CONFIRMED 상태 주문]
[주문ID] 시료ID / 고객명 / 수량
...
1. 출고 실행
0. 이전 메뉴로
>
```
- 출고 실행 후 결과(주문ID, 전환된 상태) 출력

## 5. 상태 전이 검증 포인트

```
CONFIRMED --(출고처리)--> RELEASE
```

## 6. 테스트 계획

- `CONFIRMED` 주문 출고 → `RELEASE` 전환 검증
- `CONFIRMED`가 아닌 상태(`RESERVED`, `PRODUCING`, `REJECTED`, 이미 `RELEASE`)에 대한 출고
  시도 → 거부 검증
- 존재하지 않는 `order_id`로 출고 시도 → 거부 검증

## 7. 실행 및 수동 테스트 방법 (고객님용)

1. Phase 1~3을 통해 `CONFIRMED` 상태가 된 주문을 출고처리 메뉴에서 확인
2. 출고 실행 → 상태가 `RELEASE`로 바뀌는지 확인
3. 이미 `RELEASE`된 주문이나 `RESERVED`/`PRODUCING` 상태 주문에 대해 출고를 시도해 거부되는지
   확인
4. **전체 흐름 시연**: 새 시료 등록 → 주문 생성 → 승인(재고 충분/부족 각각 한 번씩) → (부족한
   경우) 생산 완료 처리 → 출고까지 처음부터 끝까지 진행해보고 막히는 부분이 없는지 확인

## 8. Phase 4 완료 기준 (Definition of Done)

- 6번 테스트 전부 통과
- 7번 수동 테스트(특히 전체 흐름 시연) 사람이 직접 수행 시 기대대로 동작
- Verify Harness(4-Subagent) 통과
