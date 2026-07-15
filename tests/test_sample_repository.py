"""SampleRepository 테스트.

docs/design/phase1.md §8, docs/FEATURES/sample-management.md "테스트 관점" 기준:
- 신규 시료 추가 후 get_all()에 반영되는지
- 중복 sample_id 추가 시 ValueError 발생
- search_by_name이 부분 일치(대소문자 무시)로 동작하는지
- 저장 후 새 Repository 인스턴스로 다시 읽었을 때 데이터가 유지되는지 (JSON 영속성)
"""
import os

import pytest

from src.model.sample import Sample
from src.repository.sample_repository import SampleRepository


@pytest.fixture
def repo_path(tmp_path):
    return os.path.join(tmp_path, "samples.json")


def make_sample(sample_id="S001", name="WaferA", avg_production_time=2.5,
                 yield_rate=0.9, stock_quantity=0):
    return Sample(
        sample_id=sample_id,
        name=name,
        avg_production_time=avg_production_time,
        yield_rate=yield_rate,
        stock_quantity=stock_quantity,
    )


def test_add_reflected_in_get_all(repo_path):
    repo = SampleRepository(repo_path)
    assert repo.get_all() == []

    sample = make_sample()
    repo.add(sample)

    all_samples = repo.get_all()
    assert len(all_samples) == 1
    assert all_samples[0].sample_id == "S001"
    assert all_samples[0].name == "WaferA"
    assert all_samples[0].stock_quantity == 0


def test_add_duplicate_sample_id_raises_value_error(repo_path):
    repo = SampleRepository(repo_path)
    repo.add(make_sample(sample_id="S001", name="WaferA"))

    with pytest.raises(ValueError):
        repo.add(make_sample(sample_id="S001", name="WaferB"))

    # 중복 등록 시도 실패 후에도 기존 데이터는 그대로 1건이어야 한다.
    assert len(repo.get_all()) == 1


def test_search_by_name_partial_match_case_insensitive(repo_path):
    repo = SampleRepository(repo_path)
    repo.add(make_sample(sample_id="S001", name="WaferAlpha"))
    repo.add(make_sample(sample_id="S002", name="WaferBeta"))
    repo.add(make_sample(sample_id="S003", name="Substrate"))

    # 부분 일치
    result = repo.search_by_name("wafer")
    assert {s.sample_id for s in result} == {"S001", "S002"}

    # 대소문자 무시 (대문자로 검색)
    result_upper = repo.search_by_name("WAFER")
    assert {s.sample_id for s in result_upper} == {"S001", "S002"}

    # 완전히 다른 부분 문자열 일치
    result_mid = repo.search_by_name("bstr")
    assert {s.sample_id for s in result_mid} == {"S003"}

    # 존재하지 않는 키워드 -> 빈 리스트
    assert repo.search_by_name("nonexistent") == []


def test_persistence_across_new_repository_instance(repo_path):
    repo1 = SampleRepository(repo_path)
    repo1.add(make_sample(sample_id="S001", name="WaferA", avg_production_time=3.0,
                           yield_rate=0.85, stock_quantity=0))

    assert os.path.exists(repo_path)

    # 새 인스턴스로 다시 읽었을 때 데이터가 유지되어야 한다.
    repo2 = SampleRepository(repo_path)
    all_samples = repo2.get_all()
    assert len(all_samples) == 1
    restored = all_samples[0]
    assert restored.sample_id == "S001"
    assert restored.name == "WaferA"
    assert restored.avg_production_time == 3.0
    assert restored.yield_rate == 0.85
    assert restored.stock_quantity == 0


def test_find_by_id(repo_path):
    repo = SampleRepository(repo_path)
    repo.add(make_sample(sample_id="S001", name="WaferA"))

    found = repo.find_by_id("S001")
    assert found is not None
    assert found.name == "WaferA"

    assert repo.find_by_id("NOPE") is None


def test_update_persists_changes(repo_path):
    repo = SampleRepository(repo_path)
    repo.add(make_sample(sample_id="S001", name="WaferA", stock_quantity=0))

    sample = repo.find_by_id("S001")
    sample.stock_quantity = 10
    repo.update(sample)

    repo2 = SampleRepository(repo_path)
    assert repo2.find_by_id("S001").stock_quantity == 10


def test_update_nonexistent_raises_value_error(repo_path):
    repo = SampleRepository(repo_path)
    with pytest.raises(ValueError):
        repo.update(make_sample(sample_id="NOPE"))
