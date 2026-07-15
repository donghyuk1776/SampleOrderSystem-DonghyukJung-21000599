"""Sample CRUD (JSON 기반)."""
from src.model.sample import Sample
from src.repository import json_storage


class SampleRepository:
    def __init__(self, path: str = "data/samples.json"):
        self._path = path

    def add(self, sample: Sample) -> None:
        if self.find_by_id(sample.sample_id) is not None:
            raise ValueError(f"이미 존재하는 시료ID입니다: {sample.sample_id}")
        samples = self.get_all()
        samples.append(sample)
        self._persist(samples)

    def get_all(self) -> list:
        raw = json_storage.load(self._path)
        return [Sample.from_dict(item) for item in raw]

    def find_by_id(self, sample_id: str):
        for sample in self.get_all():
            if sample.sample_id == sample_id:
                return sample
        return None

    def search_by_name(self, keyword: str) -> list:
        keyword_lower = keyword.lower()
        return [s for s in self.get_all() if keyword_lower in s.name.lower()]

    def update(self, sample: Sample) -> None:
        samples = self.get_all()
        for i, existing in enumerate(samples):
            if existing.sample_id == sample.sample_id:
                samples[i] = sample
                self._persist(samples)
                return
        raise ValueError(f"존재하지 않는 시료ID입니다: {sample.sample_id}")

    def _persist(self, samples: list) -> None:
        json_storage.save(self._path, [s.to_dict() for s in samples])
