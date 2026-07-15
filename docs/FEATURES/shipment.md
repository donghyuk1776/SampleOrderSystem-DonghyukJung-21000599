# Feature: 출고처리 (Shipment)

> 상위 문서: [CLAUDE.md](../../CLAUDE.md), [PRD.md](../../PRD.md) §5.7

## 개요

재고가 충분해진 `CONFIRMED` 상태 주문에 대하여 출고를 처리하는 기능.

## 요구사항

1. 출고 대상은 `CONFIRMED` 상태의 주문이다.
2. 특정 주문을 선택하여 출고를 실행한다.
3. 출고 실행 시 주문 상태를 `RELEASE`로 전환한다.
4. `CONFIRMED` 상태가 아닌 주문(예: `RESERVED`, `PRODUCING`, `REJECTED`, 이미 `RELEASE`된
   주문)에 대한 출고 시도는 거부한다.

## 상태 전이

```
CONFIRMED --(출고처리)--> RELEASE
```

## 예외 처리

- 존재하지 않는 주문ID로 출고 시도 → 에러 메시지
- `CONFIRMED` 상태가 아닌 주문에 대한 출고 시도 → 거부 및 에러 메시지

## 테스트 관점

- `CONFIRMED` 주문 출고 시 `RELEASE`로 정상 전환되는지 검증
- `CONFIRMED`가 아닌 상태의 주문에 대해 출고가 거부되는지 검증
- 이미 `RELEASE`된 주문에 대한 재출고 시도가 거부되는지 검증
