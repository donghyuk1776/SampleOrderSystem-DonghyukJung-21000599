# 반도체 시료 생산 주문 관리 시스템 (S-Semi)

가상의 반도체 회사 "S-Semi"를 위한 콘솔 기반 시료 생산 주문 관리 시스템. 배경/요구사항은
[PRD.md](./PRD.md), 개발 원칙/아키텍처는 [CLAUDE.md](./CLAUDE.md), Phase별 목표는
[PLAN.md](./PLAN.md)를 참고한다.

## 기술 스택

- Python (MVC 아키텍처: `src/model` / `src/controller` / `src/view` / `src/repository`)
- JSON 파일 기반 데이터 영속성 (`data/*.json`, 실행 시 자동 생성)
- 테스트: `pytest`

## 실행 방법

```bash
# 메인 애플리케이션 (콘솔 메뉴)
python -m src.main

# 더미 데이터 생성 (선택, 시연/테스트용)
python -m tools.dummy_data_generator --samples 5 --orders 5

# 데이터 모니터링 도구 (메인 앱과 별도 터미널에서 실행 가능, 읽기 전용)
python -m tools.data_monitor

# 전체 테스트 실행
pytest
```

## 문서 구조

| 문서 | 내용 |
|---|---|
| [PRD.md](./PRD.md) | 배경, 도메인 모델, 상태 흐름, 기능 명세, 계산식 |
| [CLAUDE.md](./CLAUDE.md) | 개발 원칙, 아키텍처, Verify Harness/Skills 등록 현황 |
| [AGENTS.md](./AGENTS.md) | `docs/FEATURES/*.md` 목록 (Phase별 목표의 근거 문서) |
| [PLAN.md](./PLAN.md) | Phase 1~6 목표 및 Phase별 고객 확인 포인트 |
| `docs/FEATURES/*.md` | 기능별 상세 요구사항 (메인메뉴/시료관리/시료주문/주문승인거절/모니터링/생산라인/출고처리) |
| `docs/design/phase1~6.md` | Phase별 상세 설계 (디렉터리, 클래스/메서드, 테스트 계획, 수동 테스트 시나리오) |
| `.claude/agents/*.md` | Verify Harness 4-Subagent (문서정합성/코드작성/테스트검증/컴플라이언스검증) |
| `.claude/skills/*` | 참고 PoC 저장소 4종에 대한 Skill (MVC 스켈레톤/데이터 영속성/데이터 모니터링/더미데이터 생성) |

## Phase별 개발 현황

각 Phase는 [PLAN.md](./PLAN.md)의 목표에 따라 구현되었으며, 완료 시마다 아래 4단계
Verify Harness(`.claude/agents/`)를 거쳐 커밋되었다:
**code-implementer(구현) → test-verifier(테스트) → doc-consistency-verifier(문서 정합성) →
compliance-verifier(Clean Code/컴플라이언스)**.

"Verify Harness" 열은 위 4단계 검증이 모두 통과되어 커밋된 상태를 의미하며, "고객 승인" 열은
[PLAN.md](./PLAN.md)에 안내된 "고객님이 확인할 부분"을 사람이 직접 실행해보고 승인한 상태를
의미한다 (아직 미확인인 항목은 실행 후 체크 표시로 갱신한다).

| Phase | 기능 | 설계 문서 | Verify Harness | 커밋 | 고객 승인 |
|---|---|---|---|---|---|
| 1 | 프로젝트 골격 + 시료 관리 | [phase1.md](./docs/design/phase1.md) | ✅ 통과 | `8c5ad7f` | [o] 승인 (2026-07-15) |
| 2 | 시료 주문 + 주문 승인/거절 | [phase2.md](./docs/design/phase2.md) | ✅ 통과 | `5f6c975` | [o] 승인 (2026-07-15) |
| 3 | 생산라인 | [phase3.md](./docs/design/phase3.md) | ✅ 통과 | `bbf3dfc` | [o] 승인 (2026-07-15) |
| 4 | 출고처리 | [phase4.md](./docs/design/phase4.md) | ✅ 통과 | `72bd0d0` | [o] 승인 (2026-07-15) |
| 5 | 모니터링 | [phase5.md](./docs/design/phase5.md) | ✅ 통과 | `2ec632e` | [o] 승인 (2026-07-15) |
| 6 | 통합 도구(데이터 모니터링/Dummy 데이터 생성) 및 마무리 | [phase6.md](./docs/design/phase6.md) | ✅ 통과 | `a4ab105` | [o] 승인 (2026-07-15) |

> 고객 승인: 각 Phase의 설계 문서(`docs/design/phaseN.md`) "실행 및 수동 테스트 방법
> (고객님용)" 절과 [PLAN.md](./PLAN.md)의 "고객님이 확인할 부분"에 따라 담당자가 직접
> `python -m src.main`을 실행해 Phase 1~6 전체 기능을 확인하고 승인함.

## 테스트 현황

- 전체 테스트: 121건 통과 (`pytest`)
- 구성: 시료관리(Phase 1), 시료주문/주문승인거절(Phase 2), 생산라인(Phase 3), 출고처리
  (Phase 4), 모니터링(Phase 5), 전체 시나리오 통합 테스트 및 도구 스모크 테스트(Phase 6)

## 요구사항 외 추가 사용성 개선

Phase별 요구사항에는 명시되어 있지 않지만, 실제 사용해보며 발견된 문제를 반영해 아래 개선을
추가로 적용했다.

- 콘솔 출력에 상태/성공/실패별 색상 적용 (가독성 개선)
- 모니터링 화면에서 상태별 주문 개수뿐 아니라 해당 주문ID 목록도 함께 표시
- 주문 승인/거절 시 "입력할 주문ID" 프롬프트에 지금 처리 가능한 주문ID를 바로 보여주도록 개선
- 주문ID 입력 시 대문자 `O`와 숫자 `0`을 헷갈리는 실수를 자동 보정
- 생산라인을 거쳐 출고된 주문의 재고가 정확히 차감되지 않던 재고 계산 오류 수정
