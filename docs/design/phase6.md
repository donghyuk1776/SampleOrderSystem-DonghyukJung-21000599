# Phase 6 설계 - 통합 도구 및 전체 마무리

> 목표 정의: [PLAN.md](../../PLAN.md) Phase 6
> 참고: [CLAUDE.md](../../CLAUDE.md) 참고 PoC 저장소 (DataMonitor, DummyDataGenerator)
> 전제: Phase 1~5의 모든 기능이 개별적으로 동작해야 한다.

## 1. 목표

- 참고 PoC 저장소를 활용해 **데이터 모니터링 도구**와 **Dummy 데이터 생성 도구**를 추가한다.
- 시료등록 → 주문 → 승인/거절 → 생산 → 출고 → 모니터링까지 전체 시나리오가 하나의 프로그램
  안에서 끊김 없이 동작하는지 통합 점검한다.
- 문서(`CLAUDE.md`/`PRD.md`/`docs/FEATURES`/`docs/design`)와 코드 품질(Clean Code, 테스트
  커버리지)을 최종 정리한다.

## 2. 디렉터리 추가분

```
tools/
  data_monitor.py        # DataMonitor PoC 참고: 저장된 JSON(samples/orders/production_queue)
                          # 데이터를 콘솔에서 실시간(요청 시 재조회)으로 조회
  dummy_data_generator.py  # DummyDataGenerator PoC 참고: 테스트용 시료/주문 더미 데이터를
                            # 생성해 data/*.json 에 추가
tests/
  test_end_to_end.py     # 전체 시나리오(등록->주문->승인->생산->출고->모니터링) 통합 테스트
```

## 3. 데이터 모니터링 도구 (`tools/data_monitor.py`)

- 참고: `DataMonitor-DonghyukJung-21000599`
- 실행 방법: `python -m tools.data_monitor` (메인 프로그램과 별도 실행 가능한 콘솔 도구)
- 기능: `data/samples.json`, `data/orders.json`, `data/production_queue.json`을 읽어 표
  형태로 출력. 새로고침(재조회) 명령을 제공해 메인 프로그램 실행 중에도 최신 상태를 확인할 수
  있게 한다.
- 메인 애플리케이션의 도메인 로직을 변경하지 않는 **읽기 전용** 도구로 구현한다.

## 4. Dummy 데이터 생성 도구 (`tools/dummy_data_generator.py`)

- 참고: `DummyDataGenerator-DonghyukJung-21000599`
- 실행 방법: `python -m tools.dummy_data_generator --samples 5 --orders 10` (인자 개수는
  자율 결정)
- 기존 `SampleRepository`/`OrderRepository`를 재사용해 더미 시료/주문을 생성한다 (직접 JSON을
  조작하지 않고 Phase 1~2에서 만든 Repository API를 통해 생성하여 검증 로직을 그대로 통과하도록
  한다).
- 생성되는 시료의 수율은 0 초과 1 이하로 랜덤 생성한다.

## 5. 통합 테스트 (`tests/test_end_to_end.py`)

- 임시 데이터 디렉터리를 사용해 아래 전체 시나리오를 하나의 테스트로 검증한다.
  1. 시료 등록
  2. 재고보다 적은 수량으로 주문 생성 후 승인 → `CONFIRMED`
  3. 재고보다 많은 수량으로 주문 생성 후 승인 → `PRODUCING` → 생산 완료 처리 → `CONFIRMED`
  4. 두 `CONFIRMED` 주문 모두 출고 처리 → `RELEASE`
  5. 모니터링 집계 결과가 위 시나리오와 일치하는지 확인

## 6. 문서/품질 정리

- `CLAUDE.md`/`PRD.md`/`docs/FEATURES/*.md`/`docs/design/*.md`가 최종 구현과 어긋나는 부분이
  없는지 점검하고 필요한 부분을 갱신한다 (Verify Harness의 SubAgent1 - 문서 정합성 검증 역할).
- Clean Code 관점에서 중복 로직/불필요한 추상화가 없는지 점검한다 (SubAgent4 - Compliance
  Verify). Phase 2~4 compliance 검증에서 넘어온 백로그 항목을 포함한다:
  - `sample_controller.py`/`order_controller.py`/`shipment_controller.py`에 각각 중복
    정의된 `ValidationError`를 공용 `controller/errors.py`로 추출할지 검토
  - `sample_view.py`(재입력 루프)와 `order_view.py`/`shipment_view.py`(파싱 실패 시 메뉴로
    복귀)의 숫자/입력 오류 처리 UX 패턴 통일 여부 검토
- 테스트 커버리지가 Phase 1~5의 각 설계 문서에 명시한 테스트 계획을 모두 포함하는지 확인한다.

## 7. 실행 및 수동 테스트 방법 (고객님용)

1. `python -m tools.dummy_data_generator`로 더미 데이터를 생성
2. 메인 프로그램(`python -m src.main`)을 실행해 등록 → 주문 → 승인/거절 → (필요 시) 생산 완료
   처리 → 출고 → 모니터링까지 전체 흐름을 한 번에 진행
3. 별도 터미널에서 `python -m tools.data_monitor`를 실행해, 메인 프로그램에서 처리한 내용이
   실시간으로 반영되는지 확인
4. 지금까지 Phase 1~5에서 드렸던 피드백/버그 리포트가 모두 반영되었는지 최종 확인

## 8. Phase 6 완료 기준 (Definition of Done)

- 5번 통합 테스트 통과
- 7번 수동 테스트 시나리오 사람이 직접 수행 시 기대대로 동작
- 문서/코드 정리 완료, Verify Harness(4-Subagent) 최종 통과
