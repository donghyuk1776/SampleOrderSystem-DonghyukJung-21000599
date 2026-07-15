"""SampleController 테스트.

docs/design/phase1.md §8, docs/FEATURES/sample-management.md "테스트 관점" 기준:
- 정상 등록 시나리오
- 잘못된 수율(0, 1.5, 음수)로 등록 시 검증 실패 (ValidationError)
- 존재하지 않는 이름으로 검색 시 빈 리스트 반환
"""
import os

import pytest

from src.controller.sample_controller import SampleController, ValidationError
from src.repository.sample_repository import SampleRepository


@pytest.fixture
def controller(tmp_path):
    repo_path = os.path.join(tmp_path, "samples.json")
    repository = SampleRepository(repo_path)
    return SampleController(repository)


def test_register_happy_path(controller):
    sample = controller.register("S001", "WaferA", 2.5, 0.9)

    assert sample.sample_id == "S001"
    assert sample.stock_quantity == 0

    all_samples = controller.list_all()
    assert len(all_samples) == 1
    assert all_samples[0].sample_id == "S001"


def test_register_duplicate_sample_id_raises_validation_error(controller):
    controller.register("S001", "WaferA", 2.5, 0.9)

    with pytest.raises(ValidationError):
        controller.register("S001", "WaferB", 1.0, 0.5)


@pytest.mark.parametrize("invalid_yield_rate", [0, -0.1, 1.5])
def test_register_invalid_yield_rate_raises_validation_error(controller, invalid_yield_rate):
    with pytest.raises(ValidationError):
        controller.register("S001", "WaferA", 2.5, invalid_yield_rate)

    # 검증 실패 시 등록되지 않아야 한다.
    assert controller.list_all() == []


@pytest.mark.parametrize("invalid_time", [0, -1])
def test_register_invalid_avg_production_time_raises_validation_error(controller, invalid_time):
    with pytest.raises(ValidationError):
        controller.register("S001", "WaferA", invalid_time, 0.9)

    assert controller.list_all() == []


@pytest.mark.parametrize("sample_id,name", [("", "WaferA"), ("S001", "")])
def test_register_empty_id_or_name_raises_validation_error(controller, sample_id, name):
    with pytest.raises(ValidationError):
        controller.register(sample_id, name, 2.5, 0.9)

    assert controller.list_all() == []


def test_search_nonexistent_name_returns_empty_list(controller):
    controller.register("S001", "WaferA", 2.5, 0.9)

    result = controller.search("존재하지않는이름")
    assert result == []


def test_search_partial_match(controller):
    controller.register("S001", "WaferAlpha", 2.5, 0.9)
    controller.register("S002", "Substrate", 1.0, 0.8)

    result = controller.search("wafer")
    assert len(result) == 1
    assert result[0].sample_id == "S001"
