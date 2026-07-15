---
name: data-monitor-tool
description: 저장된 JSON 데이터를 콘솔에서 실시간으로 조회하는 별도의 데이터 모니터링 도구를 만들거나 수정할 때 사용. Phase 6 "데이터 모니터링 도구" 작업, "저장된 데이터 실시간 조회 도구" 관련 작업 시 트리거.
---

# 데이터 모니터링 Tool Skill

참고 PoC: `DataMonitor-DonghyukJung-21000599`
(`https://github.com/donghyuk1776/DataMonitor-DonghyukJung-21000599.git`, [CLAUDE.md](../../../CLAUDE.md) 참조)

## 언제 사용하는가

- [Phase 6](../../../docs/design/phase6.md)의 `tools/data_monitor.py` 구현/수정 시
- 메인 애플리케이션과 별도로 실행되는, 읽기 전용 데이터 조회 도구가 필요할 때

## 이 프로젝트의 요구사항

- `tools/data_monitor.py`는 메인 앱(`src/main.py`)과 **별도 프로세스로 실행 가능**해야 한다
  (`python -m tools.data_monitor`)
- 기존 Repository (`src/repository/*.py`)를 재사용해 `data/samples.json`,
  `data/orders.json`, `data/production_queue.json`을 읽는다 — JSON 파일을 직접 다시
  파싱하는 코드를 중복 작성하지 않는다
- **읽기 전용**이어야 한다: 이 도구를 통해 데이터를 생성/수정/삭제하지 않는다
- "실시간 조회"는 자동 폴링이 아니라, 사용자가 새로고침 명령을 입력할 때마다 파일을 다시 읽어
  최신 상태를 보여주는 방식으로 구현한다 (메인 앱이 실행 중일 때 파일이 갱신된 것을 확인하는
  용도)

## 작업 절차

1. DataMonitor PoC의 조회/출력 패턴(표 형태 렌더링)을 참고한다.
2. 표시 항목: 시료 목록(재고 포함), 주문 목록(상태 포함), 생산 큐 대기 목록을 최소한 포함한다.
3. [Phase 6 설계](../../../docs/design/phase6.md)의 "고객님이 확인할 부분" — 메인 프로그램에서
   처리한 내용이 이 도구에도 실시간(재조회 시) 반영되는지 — 를 수동 테스트 시나리오에 포함한다.
