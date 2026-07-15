# CLAUDE.md

이 문서는 Claude Code가 이 저장소에서 작업할 때 따라야 할 규칙과 컨텍스트를 정리한다.
제품 요구사항은 [PRD.md](./PRD.md)를 참고한다.

## 문서 체계

이 프로젝트의 문서는 아래 흐름으로 연결된다.

`docs/FEATURES/*.md` (무엇을 만들 것인가, [AGENTS.md](./AGENTS.md)에 목록 관리)
→ [PLAN.md](./PLAN.md) (Phase별로 어떤 범위까지 만들 것인가, 소요시간 없이 목표/고객 확인
포인트만 정의)
→ `docs/design/phaseN.md` (Phase별로 어떻게 만들 것인가 - 디렉터리 구조, 모델/컨트롤러/뷰
설계, 테스트 계획, 수동 테스트 시나리오)

- [AGENTS.md](./AGENTS.md): `docs/FEATURES/` 문서 목록과, 이 문서들이 Phase별 목표 수립의
  근거임을 명시
- [PLAN.md](./PLAN.md): Phase 1~6 목표. 각 Phase 종료 시 실제로 동작하는 SW가 나와야 하며,
  사람이 직접 실행/테스트하고 피드백을 줄 수 있어야 한다 (일정/소요시간 없음)
- `docs/design/phase1.md` ~ `phase6.md`: Phase별 상세 설계
  1. [phase1.md](./docs/design/phase1.md) - 프로젝트 골격 + 시료 관리
  2. [phase2.md](./docs/design/phase2.md) - 시료 주문 + 주문 승인/거절
  3. [phase3.md](./docs/design/phase3.md) - 생산라인
  4. [phase4.md](./docs/design/phase4.md) - 출고처리
  5. [phase5.md](./docs/design/phase5.md) - 모니터링
  6. [phase6.md](./docs/design/phase6.md) - 통합 도구(데이터 모니터링/Dummy 데이터 생성) 및
     전체 마무리

## 프로젝트 개요

콘솔 기반 **반도체 시료 생산 주문 관리 시스템** (가상 회사 "S-Semi"). 상세 기능/도메인 모델은
[PRD.md](./PRD.md) 참조.

- 언어: **Python**
- 아키텍처: **MVC** (Model / Controller / View 패키지로 역할 분리)
- 데이터 저장: **JSON 파일 기반 영속성**, CRUD 지원
- 부가 도구: 콘솔 기반 **데이터 모니터링 도구**, **Dummy 데이터 생성 도구**

## 참고 PoC 저장소

아래 4개 저장소의 구조/코드를 참고하여 활용하고, 필요 시 각 저장소를 프로젝트 내부 Skill로
등록한다.

1. **MVC 스켈레톤**: Model/Controller/View 패키지 구조와 역할 분리
   `https://github.com/donghyuk1776/ConsoleMVC-DonghyukJung-21000599.git`
2. **데이터 영속성**: JSON 저장/로드 구조, CRUD 포함
   `https://github.com/donghyuk1776/DataPersistence-DonghyukJung-21000599.git`
3. **데이터 모니터링 Tool**: 저장된 데이터 상태를 콘솔에서 실시간 조회
   `https://github.com/donghyuk1776/DataMonitor-DonghyukJung-21000599.git`
4. **Dummy 데이터 생성 Tool**: 테스트용 더미 데이터를 생성해 DB(JSON)에 추가
   `https://github.com/donghyuk1776/DummyDataGenerator-DonghyukJung-21000599.git`

## Verify Harness Subagent 등록 (`.claude/agents/`)

개발 시 핵심 원칙 2번의 4-Subagent Verify Harness는 아래 4개 파일로 등록되어 있다. 코드
작성 흐름은 `code-implementer` → `test-verifier` → `doc-consistency-verifier` →
`compliance-verifier` 순으로 호출하는 것을 기본으로 하되, 상황에 따라 병렬로 호출해도 된다.

| SubAgent | 파일 | 역할 |
|---|---|---|
| SubAgent1 | [.claude/agents/doc-consistency-verifier.md](./.claude/agents/doc-consistency-verifier.md) | 문서 정합성 검증 |
| SubAgent2 | [.claude/agents/code-implementer.md](./.claude/agents/code-implementer.md) | AI Action (코드 작성) |
| SubAgent3 | [.claude/agents/test-verifier.md](./.claude/agents/test-verifier.md) | Test Verify |
| SubAgent4 | [.claude/agents/compliance-verifier.md](./.claude/agents/compliance-verifier.md) | Compliance Verify |

## Skills 등록 (`.claude/skills/`)

"참고 PoC 저장소" 4개는 아래 Skill로 등록되어 있으며, 각 Skill 문서에 이 프로젝트에 맞춘 구현
규칙과 참고 PoC 저장소 링크가 정리되어 있다.

| PoC 저장소 | Skill |
|---|---|
| ConsoleMVC-DonghyukJung-21000599 | [.claude/skills/mvc-console-skeleton/SKILL.md](./.claude/skills/mvc-console-skeleton/SKILL.md) |
| DataPersistence-DonghyukJung-21000599 | [.claude/skills/json-data-persistence/SKILL.md](./.claude/skills/json-data-persistence/SKILL.md) |
| DataMonitor-DonghyukJung-21000599 | [.claude/skills/data-monitor-tool/SKILL.md](./.claude/skills/data-monitor-tool/SKILL.md) |
| DummyDataGenerator-DonghyukJung-21000599 | [.claude/skills/dummy-data-generator/SKILL.md](./.claude/skills/dummy-data-generator/SKILL.md) |

## 개발 시 핵심 원칙

1. **문서 관리**: 기능/도메인 변경 시 `CLAUDE.md`, `PRD.md`를 최신 상태로 함께 갱신한다.
2. **Verify Harness 도입 (Subagent 기반)**: 코드 작성 후 아래 4개 서브에이전트로 검증한다.
   - SubAgent1 - **문서 정합성 검증**: 구현이 `PRD.md`/`CLAUDE.md`와 일치하는지 확인
   - SubAgent2 - **AI Action (코드 작성)**: 실제 기능 구현 수행
   - SubAgent3 - **Test Verify**: 테스트 작성/실행 및 통과 여부 검증
   - SubAgent4 - **Compliance Verify**: Clean Code, 컨벤션, 보안 등 준수 여부 검증
3. **Test 코드 작성**: 기능 구현과 함께 테스트 코드를 작성한다 (신규 기능은 테스트 없이 완료로
   간주하지 않는다).
4. **Clean Code 작성**: 가독성, 단일 책임, 불필요한 추상화 지양 등 Clean Code 원칙을 따른다.
5. **Phase 별 Commit 관리**: 기능/작업 단위(Phase)로 커밋을 분리하여 이력을 관리한다. 하나의
   거대한 커밋으로 몰아서 작업하지 않는다.

## 디렉터리 구조 (예정)

```
src/model/       # 도메인 모델 (Sample, Order, ProductionJob 등)
src/controller/  # 비즈니스 로직 / 상태 전이 처리
src/view/        # 콘솔 입출력, 메뉴 렌더링
src/repository/  # JSON 기반 데이터 저장/로드, CRUD
tools/           # 데이터 모니터링, Dummy 데이터 생성 도구 (Phase 6)
tests/           # 테스트 코드
```

상세 파일 구조는 `docs/design/phaseN.md` 참조.

## 테스트

- 기능 단위 테스트를 `tests/` 에 작성한다.
- 주문 상태 전이(RESERVED → CONFIRMED/PRODUCING → RELEASE, REJECTED)와 수율/실생산량/
  총생산시간 계산식은 반드시 테스트로 검증한다.

## 커밋 규칙

- [PLAN.md](./PLAN.md)에 정의된 Phase 단위(1~6)로 커밋을 분리한다 (예: `Phase 1: 프로젝트
  골격 + 시료 관리`, `Phase 2: 시료 주문 + 주문 승인/거절`, `Phase 3: 생산라인`,
  `Phase 4: 출고처리`, `Phase 5: 모니터링`, `Phase 6: 통합 도구 및 마무리`).
- 커밋 메시지는 무엇을 왜 변경했는지 간결히 기술한다.
