---
name: dummy-data-generator
description: 테스트용 더미 시료/주문 데이터를 생성하는 도구를 만들거나 수정할 때 사용. Phase 6 "Dummy 데이터 생성 도구" 작업, "테스트 데이터 채우기", "더미 데이터 생성" 관련 작업 시 트리거.
---

# Dummy 데이터 생성 Tool Skill

참고 PoC: `DummyDataGenerator-DonghyukJung-21000599`
(`https://github.com/donghyuk1776/DummyDataGenerator-DonghyukJung-21000599.git`, [CLAUDE.md](../../../CLAUDE.md) 참조)

## 언제 사용하는가

- [Phase 6](../../../docs/design/phase6.md)의 `tools/dummy_data_generator.py` 구현/수정 시
- 수동 테스트나 통합 테스트를 위해 빠르게 시료/주문 데이터를 채워야 할 때

## 이 프로젝트의 요구사항

- 반드시 `src/repository/*.py`의 CRUD API(`SampleRepository.add`, `OrderRepository.create` 등)를
  통해 데이터를 생성한다 — JSON 파일을 직접 조작하지 않는다. 그래야 Controller/Repository의
  검증 로직(중복 ID 금지, 수율 범위 등)을 그대로 통과한 유효한 데이터만 생성된다
- 생성 개수는 CLI 인자로 조절 가능해야 한다 (예: `--samples`, `--orders`)
- 생성되는 값은 `PRD.md`/`docs/FEATURES/sample-management.md`의 제약을 반드시 지킨다
  (수율은 0 초과 1 이하, 평균 생산시간은 양수, 주문 수량은 1 이상 정수)
- 난수 생성 시 시드를 고정할지 여부는 구현 시 결정하되, 테스트에서 사용할 경우 재현 가능하도록
  시드를 고정하는 것을 권장한다

## 작업 절차

1. DummyDataGenerator PoC의 생성 패턴(랜덤 값 생성 → Repository API 호출)을 참고한다.
2. [Phase 6 설계](../../../docs/design/phase6.md)의 통합 테스트/수동 테스트 시나리오에서
   "더미 데이터로 전체 흐름을 시연"할 수 있도록, 최소 1개 이상은 재고가 충분한 시료, 1개
   이상은 재고가 부족해 `PRODUCING` 분기를 유도할 수 있는 시료를 만들도록 구성하는 것을
   권장한다.
3. 생성 후 `.claude/skills/data-monitor-tool`로 만든 도구나 시료조회/모니터링 메뉴로 데이터가
   정상 반영되었는지 확인한다.
