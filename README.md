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
| 1 | 프로젝트 골격 + 시료 관리 | [phase1.md](./docs/design/phase1.md) | ✅ 통과 | `8c5ad7f` | [ ] 미확인 |
| 2 | 시료 주문 + 주문 승인/거절 | [phase2.md](./docs/design/phase2.md) | ✅ 통과 | `5f6c975` | [ ] 미확인 |
| 3 | 생산라인 | [phase3.md](./docs/design/phase3.md) | ✅ 통과 | `bbf3dfc` | [ ] 미확인 |
| 4 | 출고처리 | [phase4.md](./docs/design/phase4.md) | ✅ 통과 | `72bd0d0` | [ ] 미확인 |
| 5 | 모니터링 | [phase5.md](./docs/design/phase5.md) | ✅ 통과 | `2ec632e` | [ ] 미확인 |
| 6 | 통합 도구(데이터 모니터링/Dummy 데이터 생성) 및 마무리 | [phase6.md](./docs/design/phase6.md) | ✅ 통과 | `a4ab105` | [ ] 미확인 |

> 고객 승인 방법: 각 Phase의 설계 문서(`docs/design/phaseN.md`) 마지막 "실행 및 수동 테스트
> 방법(고객님용)" 절 또는 [PLAN.md](./PLAN.md)의 "고객님이 확인할 부분"에 따라 직접
> `python -m src.main`을 실행해 해당 Phase 기능을 확인한 뒤, 이 표의 "[ ] 미확인"을
> "[x] 승인 (YYYY-MM-DD)"로 갱신하면 된다.

## 테스트 현황

- 전체 테스트: 99건 통과 (`pytest`)
- 구성: 시료관리(Phase 1), 시료주문/주문승인거절(Phase 2), 생산라인(Phase 3), 출고처리
  (Phase 4), 모니터링(Phase 5), 전체 시나리오 통합 테스트 및 도구 스모크 테스트(Phase 6)
