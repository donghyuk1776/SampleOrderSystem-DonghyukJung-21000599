"""DataMonitor 스모크 테스트.

읽기 전용 도구이므로 렌더링이 예외 없이 동작하는지, 빈 데이터일 때 안내 문구를
출력하는지, 실제 데이터를 반영하는지 확인한다.
"""
import os

from tools.data_monitor import DataMonitor
from src.model.sample import Sample
from src.repository.order_repository import OrderRepository
from src.repository.production_queue_repository import ProductionQueueRepository
from src.repository.sample_repository import SampleRepository


def build_monitor(tmp_path):
    sample_repository = SampleRepository(os.path.join(tmp_path, "samples.json"))
    order_repository = OrderRepository(os.path.join(tmp_path, "orders.json"))
    queue_repository = ProductionQueueRepository(os.path.join(tmp_path, "production_queue.json"))
    monitor = DataMonitor(sample_repository, order_repository, queue_repository)
    return monitor, sample_repository


def test_render_empty_data_prints_guidance_without_crash(tmp_path, capsys):
    monitor, _ = build_monitor(tmp_path)

    monitor.render()

    output = capsys.readouterr().out
    assert "등록된 시료가 없습니다." in output
    assert "등록된 주문이 없습니다." in output
    assert "대기 중인 생산 작업이 없습니다." in output


def test_render_reflects_current_repository_data(tmp_path, capsys):
    monitor, sample_repository = build_monitor(tmp_path)
    sample_repository.add(Sample(
        sample_id="S001", name="WaferA", avg_production_time=2.5,
        yield_rate=0.9, stock_quantity=3,
    ))

    monitor.render()

    output = capsys.readouterr().out
    assert "S001" in output
    assert "WaferA" in output
