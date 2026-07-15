---
name: mvc-console-skeleton
description: 콘솔 기반 Python MVC(Model/Controller/View) 골격을 새로 만들거나 확장할 때 사용. "MVC 구조", "Model/Controller/View 나누기", "콘솔 메뉴 골격 만들기", Phase 1의 프로젝트 골격 작업 시 트리거.
---

# MVC 콘솔 스켈레톤 Skill

참고 PoC: `ConsoleMVC-DonghyukJung-21000599`
(`https://github.com/donghyuk1776/ConsoleMVC-DonghyukJung-21000599.git`, [CLAUDE.md](../../../CLAUDE.md) 참조)

## 언제 사용하는가

- Phase 1 ([docs/design/phase1.md](../../../docs/design/phase1.md)) 처럼 프로젝트의 MVC
  골격을 처음 세울 때
- 새로운 화면/메뉴(Controller+View 쌍)를 기존 MVC 구조에 추가할 때

## 이 프로젝트의 MVC 규칙

- `src/model/` — 도메인 데이터 클래스만 둔다 (`dataclass`), 비즈니스 로직/검증 없음
- `src/controller/` — 유스케이스 + 검증 로직. Repository를 통해서만 데이터에 접근하고,
  콘솔 입출력을 직접 하지 않는다
- `src/view/` — 콘솔 입출력, 메뉴 렌더링만 담당. 비즈니스 로직을 갖지 않고 Controller를 호출만
  한다
- `src/repository/` — 실제 저장(JSON) 담당. Model 객체 단위로 CRUD 제공 (자세한 내용은
  [json-data-persistence](../json-data-persistence/SKILL.md) Skill 참고)
- `src/main.py` — 메인 메뉴 루프, 하위 View들을 라우팅

## 작업 절차

1. ConsoleMVC PoC의 계층 분리 패턴(입력 파싱 → Controller 호출 → 결과 출력)을 참고하되, 이
   프로젝트의 실제 도메인(Sample/Order/ProductionJob)에 맞게 적용한다.
2. 새 메뉴를 추가할 때는 항상 `model → repository → controller → view → main.py 라우팅` 순서로
   만든다.
3. 메뉴 진입/에러 처리 패턴은 [docs/design/phase1.md](../../../docs/design/phase1.md)의
   "메인 메뉴"/"시료관리 메뉴" 콘솔 흐름 예시를 기준 스타일로 따른다 (잘못된 입력 시 프로그램이
   종료되지 않고 재입력을 요청).
4. 각 계층 책임이 섞이지 않았는지는 `.claude/agents/compliance-verifier.md` 서브에이전트로
   검증한다.
