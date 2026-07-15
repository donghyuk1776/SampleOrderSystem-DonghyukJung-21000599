"""생산 큐 CRUD (JSON 기반, 리스트 순서 = FIFO 순서)."""
from src.model.production_job import ProductionJob
from src.repository import json_storage


class ProductionQueueRepository:
    def __init__(self, path: str = "data/production_queue.json"):
        self._path = path

    def add(self, job: ProductionJob) -> None:
        """큐 맨 뒤에 추가한다 (FIFO)."""
        jobs = self.get_all()
        jobs.append(job)
        self._persist(jobs)

    def get_all(self) -> list:
        """등록 순서 그대로 반환한다."""
        raw = json_storage.load(self._path)
        return [ProductionJob.from_dict(item) for item in raw]

    def pop_first(self):
        """큐 맨 앞 작업을 제거 후 반환한다. 비어있으면 None을 반환한다."""
        jobs = self.get_all()
        if not jobs:
            return None
        first = jobs.pop(0)
        self._persist(jobs)
        return first

    def remove(self, order_id: str) -> None:
        jobs = self.get_all()
        remaining = [j for j in jobs if j.order_id != order_id]
        self._persist(remaining)

    def _persist(self, jobs: list) -> None:
        json_storage.save(self._path, [j.to_dict() for j in jobs])
