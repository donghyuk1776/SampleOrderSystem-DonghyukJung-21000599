---
name: json-data-persistence
description: JSON 파일 기반 데이터 저장/로드 및 CRUD Repository를 만들거나 수정할 때 사용. "JSON 저장", "데이터 영속성", "Repository 만들기", "재실행해도 데이터 유지" 관련 작업 시 트리거.
---

# JSON 데이터 영속성 Skill

참고 PoC: `DataPersistence-DonghyukJung-21000599`
(`https://github.com/donghyuk1776/DataPersistence-DonghyukJung-21000599.git`, [CLAUDE.md](../../../CLAUDE.md) 참조)

## 언제 사용하는가

- `src/repository/`에 새로운 Repository(`SampleRepository`, `OrderRepository`,
  `ProductionQueueRepository` 등)를 추가할 때
- 기존 JSON 저장 로직에 CRUD 메서드를 추가/수정할 때

## 이 프로젝트의 영속성 규칙

- 공용 유틸 `src/repository/json_storage.py` (`load(path)` / `save(path, data)`)를 모든
  Repository가 재사용한다 (중복 파일 입출력 코드를 만들지 않는다) — 자세한 내용은
  [docs/design/phase1.md](../../../docs/design/phase1.md) §4 참고
- 파일이 없으면 빈 리스트로 초기화하고, 있으면 파싱해서 반환한다
- 각 Repository는 Model 객체(dataclass)의 `to_dict()`/`from_dict()`를 이용해 직렬화한다
- 데이터 파일은 `data/<entity>.json` 형태로 저장한다 (`data/samples.json`, `data/orders.json`,
  `data/production_queue.json`)
- 최소 CRUD: `add`, `get_all`, `find_by_id`, `update` (검색이 필요하면 `search_by_*` 추가)
- 중복 키(예: `sample_id`) 추가 시 `ValueError`를 발생시켜 Controller가 사용자에게 안내하도록
  한다

## 작업 절차

1. DataPersistence PoC의 저장/로드 구조(파일 존재 확인 → 파싱 → 객체 매핑)를 참고해 이 형식에
   맞춘다.
2. Repository 추가/변경 후에는 반드시 "저장 → 재실행(새 Repository 인스턴스 생성) → 조회 시
   데이터 유지" 테스트를 작성한다 (모든 Phase 설계 문서의 "재실행해도 유지되는지 확인" 요구사항).
3. Repository는 콘솔 출력을 하지 않는다 (View/Controller 책임과 분리).
