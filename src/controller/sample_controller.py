"""시료 등록/조회/검색 유스케이스 + 검증."""
from src.model.sample import Sample
from src.repository.sample_repository import SampleRepository


class ValidationError(Exception):
    """사용자에게 보여줄 메시지를 담은 검증 실패 예외."""


class SampleController:
    def __init__(self, repository: SampleRepository = None):
        self._repository = repository or SampleRepository()

    def register(self, sample_id: str, name: str, avg_production_time: float,
                 yield_rate: float) -> Sample:
        if not sample_id or not name:
            raise ValidationError("시료ID와 이름은 비어 있을 수 없습니다.")
        if self._repository.find_by_id(sample_id) is not None:
            raise ValidationError(f"이미 존재하는 시료ID입니다: {sample_id}")
        if not (0 < yield_rate <= 1):
            raise ValidationError("수율은 0보다 크고 1 이하이어야 합니다.")
        if not (avg_production_time > 0):
            raise ValidationError("평균 생산시간은 0보다 커야 합니다.")

        sample = Sample(
            sample_id=sample_id,
            name=name,
            avg_production_time=avg_production_time,
            yield_rate=yield_rate,
            stock_quantity=0,
        )
        self._repository.add(sample)
        return sample

    def list_all(self) -> list:
        return self._repository.get_all()

    def search(self, keyword: str) -> list:
        return self._repository.search_by_name(keyword)
