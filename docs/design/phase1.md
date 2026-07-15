# Phase 1 설계 - 프로젝트 골격 + 시료 관리

> 목표 정의: [PLAN.md](../../PLAN.md) Phase 1
> 기능 명세: [docs/FEATURES/sample-management.md](../FEATURES/sample-management.md)
> 개발 원칙: [CLAUDE.md](../../CLAUDE.md)

## 1. 목표

- MVC + JSON 영속성이라는 프로젝트의 기본 골격을 세운다.
- 콘솔 실행 → 메인 메뉴 → 시료관리 메뉴로 진입하여 **시료 등록 / 조회 / 검색**이 실제로
  동작하고, 종료 후 재실행해도 데이터가 유지되도록 한다.

## 2. 디렉터리 구조

```
src/
  main.py                        # 엔트리 포인트, 메인 메뉴 루프
  model/
    __init__.py
    sample.py                    # Sample 데이터 모델
  repository/
    __init__.py
    json_storage.py               # 범용 JSON 파일 read/write 유틸
    sample_repository.py          # Sample CRUD (JSON 기반)
  controller/
    __init__.py
    sample_controller.py          # 시료 등록/조회/검색 유스케이스 + 검증
  view/
    __init__.py
    main_menu_view.py              # 메인 메뉴 렌더링/입력
    sample_view.py                 # 시료관리 화면 렌더링/입력
data/
  samples.json                    # 실행 시 생성되는 영속 데이터 파일
tests/
  test_sample_repository.py
  test_sample_controller.py
```

## 3. 데이터 모델 (`model/sample.py`)

```python
@dataclass
class Sample:
    sample_id: str
    name: str
    avg_production_time: float
    yield_rate: float          # 0 < yield_rate <= 1
    stock_quantity: int = 0
```

- `to_dict()` / `from_dict()` 메서드를 제공해 JSON 직렬화/역직렬화에 사용한다.

## 4. 영속성 (`repository/`)

- `json_storage.py`: 파일이 없으면 빈 리스트/딕셔너리로 초기화, 있으면 읽어서 파싱하는 공용
  `load(path)` / `save(path, data)` 함수 제공. (Phase 6에서 다른 Repository도 재사용)
- `sample_repository.py` (`SampleRepository`):
  - `add(sample: Sample) -> None`: `sample_id` 중복 시 `ValueError` 발생
  - `get_all() -> list[Sample]`
  - `find_by_id(sample_id: str) -> Sample | None`
  - `search_by_name(keyword: str) -> list[Sample]`: 부분 일치(대소문자 무시) 검색
  - `update(sample: Sample) -> None`: 이후 Phase에서 재고 차감/증가 시 재사용

- 데이터 파일: `data/samples.json`, 구조 예시:

```json
[
  {"sample_id": "S001", "name": "WaferA", "avg_production_time": 2.5,
   "yield_rate": 0.9, "stock_quantity": 0}
]
```

## 5. 컨트롤러 (`controller/sample_controller.py`)

- `register(sample_id, name, avg_production_time, yield_rate)`:
  - 검증: `sample_id` 미존재 여부, `0 < yield_rate <= 1`, `avg_production_time > 0`
  - 검증 실패 시 사용자에게 보여줄 메시지를 담은 예외(`ValidationError`)를 발생시킨다.
  - 통과 시 `Sample(stock_quantity=0)` 생성 후 Repository에 저장
- `list_all()`: Repository의 전체 목록 반환 (View에서 재고 포함 출력)
- `search(keyword)`: Repository의 이름 검색 위임, 결과 없으면 빈 리스트 반환 (View에서 "결과
  없음" 메시지 처리)

## 6. 뷰 / 콘솔 흐름 (`view/`)

**메인 메뉴** (`main_menu_view.py`):

```
==== 반도체 시료 생산 주문 관리 시스템 ====
전체 등록 시료 수: N개 / 전체 재고 합계: M개
1. 시료관리
2. 시료주문        (Phase 2 예정)
3. 주문승인/거절    (Phase 2 예정)
4. 모니터링        (Phase 5 예정)
5. 출고처리        (Phase 4 예정)
6. 생산라인        (Phase 3 예정)
0. 종료
> 
```

- Phase 1에서는 "1. 시료관리"만 실제로 동작하고, 나머지는 "아직 준비 중입니다" 메시지를 출력
  (메뉴 자체는 노출하여 전체 구조를 보여줌).

**시료관리 메뉴** (`sample_view.py`):

```
==== 시료 관리 ====
1. 시료 등록
2. 시료 조회
3. 시료 검색
0. 이전 메뉴로
>
```

- 시료 등록: 시료ID/이름/평균생산시간/수율을 순서대로 입력받아 컨트롤러 호출, 성공/실패 메시지
  출력
- 시료 조회: 표 형태로 시료ID/이름/평균생산시간/수율/재고 출력
- 시료 검색: 검색어 입력받아 결과 출력 (없으면 "검색 결과가 없습니다")

## 7. 예외/입력 검증 처리

- 숫자 입력이 필요한 곳에 문자열 등 잘못된 값이 들어오면 `ValueError`를 잡아 "숫자를 입력해
  주세요" 안내 후 재입력을 받는다 (프로그램이 죽지 않는다).
- 모든 사용자 입력 검증 실패는 콘솔에 이유를 명확히 출력한다 (예: "이미 존재하는 시료ID입니다",
  "수율은 0보다 크고 1 이하이어야 합니다").

## 8. 테스트 계획 (`tests/`)

- `test_sample_repository.py`
  - 신규 시료 추가 후 `get_all()`에 반영되는지
  - 중복 `sample_id` 추가 시 `ValueError` 발생
  - `search_by_name`이 부분 일치로 동작하는지
  - 저장 후 재생성한 Repository 인스턴스로 다시 읽었을 때 데이터가 유지되는지 (JSON 파일 기반
    영속성 검증)
- `test_sample_controller.py`
  - 정상 등록 시나리오
  - 잘못된 수율(0, 1.5, 음수)로 등록 시 검증 실패
  - 존재하지 않는 이름으로 검색 시 빈 리스트 반환

## 9. 실행 및 수동 테스트 방법 (고객님용)

```bash
python -m src.main
```

1. 메인 메뉴에서 `1`(시료관리) 입력
2. `1`(시료 등록) 선택 후 시료ID/이름/평균생산시간/수율 입력 → 등록 성공 메시지 확인
3. `2`(시료 조회) 선택 → 방금 등록한 시료가 재고 0으로 표시되는지 확인
4. `3`(시료 검색) 선택 → 등록한 시료 이름 일부만 입력해 검색되는지 확인
5. 동일한 시료ID로 다시 등록 시도 → 거부 메시지 확인
6. 프로그램 종료(`0` 반복 입력) 후 다시 `python -m src.main` 실행 → 조회 시 데이터가 그대로
   남아있는지 확인 (`data/samples.json` 파일 확인 가능)

## 10. Phase 1 완료 기준 (Definition of Done)

- 위 8번 테스트 계획의 모든 테스트가 통과
- 위 9번 수동 테스트 시나리오를 사람이 직접 수행했을 때 기대한 대로 동작
- `CLAUDE.md`의 Verify Harness(4-Subagent) 통과: 문서 정합성 / 코드 작성 / 테스트 검증 /
  Compliance 검증
