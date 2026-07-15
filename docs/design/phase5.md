# Phase 5 설계 - 모니터링

> 목표 정의: [PLAN.md](../../PLAN.md) Phase 5
> 기능 명세: [docs/FEATURES/monitoring.md](../FEATURES/monitoring.md)
> 전제: Phase 1~4에서 생성된 시료/주문 데이터를 읽기 전용으로 집계한다 (새 데이터를 만들지
> 않는다).

## 1. 목표

- 상태별(`RESERVED`/`CONFIRMED`/`PRODUCING`/`RELEASE`) 주문 현황을 확인할 수 있다
  (`REJECTED`는 집계에서 제외).
- 시료별 재고 수량과 "여유/부족/고갈" 상태를 확인할 수 있다.

## 2. 디렉터리 추가분

```
src/
  controller/
    monitoring_controller.py    # OrderRepository/SampleRepository를 읽어 집계만 수행
  view/
    monitoring_view.py
tests/
  test_monitoring_controller.py
```

- 별도 Model/Repository 없이 기존 `OrderRepository`, `SampleRepository`를 조회(read-only)한다.

## 3. 컨트롤러 (`controller/monitoring_controller.py`)

- `count_by_status()`: `REJECTED`를 제외한 각 상태별 주문 수를 dict로 반환
  (`{"RESERVED": n, "CONFIRMED": n, "PRODUCING": n, "RELEASE": n}`)
- `stock_status()`: 시료별로 아래 기준에 따라 상태 라벨을 계산해 반환
  - **재고 대비 기준 정의** (설계 확정 사항): 해당 시료의 미출고 수요 = 상태가 `RESERVED` +
    `PRODUCING` + `CONFIRMED`인 주문의 수량 합계
  - `stock_quantity == 0` → **고갈**
  - `stock_quantity > 0` and `stock_quantity < 미출고 수요` → **부족**
  - `stock_quantity > 0` and `stock_quantity >= 미출고 수요` (수요가 0인 경우 포함) → **여유**

## 4. 뷰 흐름

```
==== 모니터링 ====
[주문량] RESERVED: n / CONFIRMED: n / PRODUCING: n / RELEASE: n

[재고량]
시료ID / 이름 / 재고수량 / 상태(여유/부족/고갈)
...
0. 이전 메뉴로
>
```

## 5. 테스트 계획

- 상태별 개수 집계가 실제 저장 데이터와 일치하는지 (특히 `REJECTED` 제외 여부)
- 재고 상태 분류 경계값 검증: 재고 0(고갈), 재고 == 미출고 수요(여유), 재고 < 미출고 수요(부족)
- 시료/주문 데이터가 없을 때 빈 결과(0건/빈 목록)로 정상 출력되는지

## 6. 실행 및 수동 테스트 방법 (고객님용)

1. Phase 1~4에서 만들어 둔 데이터를 기준으로 모니터링 메뉴 진입
2. 화면의 상태별 주문 수가 실제로 지금까지 만든 주문 상태 분포와 맞는지 직접 세어서 비교
3. 일부러 주문 하나를 거절(`REJECTED`) 처리한 뒤 모니터링에서 집계가 줄어드는지(제외되는지)
   확인
4. 특정 시료의 재고를 0으로 만들어 "고갈"로 표시되는지, 재고를 충분히 늘려 "여유"로 바뀌는지
   확인

## 7. Phase 5 완료 기준 (Definition of Done)

- 5번 테스트 전부 통과
- 6번 수동 테스트 시나리오 사람이 직접 수행 시 기대대로 동작
- Verify Harness(4-Subagent) 통과
