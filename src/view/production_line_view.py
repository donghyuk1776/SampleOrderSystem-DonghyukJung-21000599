"""생산라인 현황/대기열 화면."""
from src.controller.production_line_controller import ProductionLineController, ProductionLineError


class ProductionLineView:
    def __init__(self, controller: ProductionLineController = None):
        self._controller = controller or ProductionLineController()

    def run(self) -> None:
        while True:
            pending_jobs = self._controller.list_pending()
            print("\n==== 생산라인 ====")
            print("[현재 생산중]")
            if not pending_jobs:
                print("생산 중인 시료가 없습니다.")
            else:
                self._print_job(pending_jobs[0])

            print("\n[대기중 (FIFO)]")
            waiting_jobs = pending_jobs[1:]
            if not waiting_jobs:
                print("대기 중인 생산 작업이 없습니다.")
            else:
                for i, job in enumerate(waiting_jobs, start=1):
                    print(f"{i}) ", end="")
                    self._print_job(job)

            print("1. 다음 생산 완료 처리")
            print("0. 이전 메뉴로")
            choice = input("> ").strip()

            if choice == "1":
                self._process_next()
            elif choice == "0":
                return
            else:
                print("잘못된 입력입니다. 다시 선택해 주세요.")

    def _process_next(self) -> None:
        try:
            job = self._controller.process_next()
        except ProductionLineError as e:
            print(f"생산 완료 처리 실패: {e}")
            return
        if job is None:
            print("대기 중인 생산 작업이 없습니다.")
            return
        print(f"주문 '{job.order_id}' 생산이 완료되었습니다. "
              f"(시료ID: {job.sample_id}, 실생산량: {job.actual_quantity})")

    def _print_job(self, job) -> None:
        print(f"주문ID:{job.order_id} / 시료ID:{job.sample_id} / "
              f"실생산량:{job.actual_quantity} / 총생산시간:{job.total_production_time}")
