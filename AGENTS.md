# AGENTS.md

이 문서는 `docs/FEATURES/` 하위의 기능 명세 문서 목록을 관리한다.

## docs/FEATURES/ 문서 목록

| 문서 | 기능 |
|---|---|
| [docs/FEATURES/main-menu.md](./docs/FEATURES/main-menu.md) | 메인 메뉴 |
| [docs/FEATURES/sample-management.md](./docs/FEATURES/sample-management.md) | 시료 관리 |
| [docs/FEATURES/sample-order.md](./docs/FEATURES/sample-order.md) | 시료 주문 |
| [docs/FEATURES/order-approval-rejection.md](./docs/FEATURES/order-approval-rejection.md) | 주문 승인/거절 |
| [docs/FEATURES/monitoring.md](./docs/FEATURES/monitoring.md) | 모니터링 |
| [docs/FEATURES/production-line.md](./docs/FEATURES/production-line.md) | 생산라인 |
| [docs/FEATURES/shipment.md](./docs/FEATURES/shipment.md) | 출고처리 |

> **중요**: `docs/FEATURES/` 의 각 문서는 단순 기능 명세가 아니라, **Phase 별 개발 목표를
> 세우기 위한 근거 문서**이다. 즉, 이 문서들에 정의된 기능 단위를 바탕으로
> [PLAN.md](./PLAN.md)의 Phase 목표가 도출되었으며, 각 Phase의 상세 설계는
> `docs/design/phaseN.md`에 정리된다.
>
> 문서 간 관계:
> `docs/FEATURES/*.md` (무엇을 만들 것인가) → `PLAN.md` (Phase별로 언제/어떤 범위로 만들 것인가)
> → `docs/design/phaseN.md` (Phase별로 어떻게 만들 것인가)
