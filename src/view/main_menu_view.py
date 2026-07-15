"""메인 메뉴 콘솔 루프."""
from src.controller.sample_controller import SampleController
from src.view.sample_view import SampleView


class MainMenuView:
    def __init__(self, sample_controller: SampleController = None):
        self._sample_controller = sample_controller or SampleController()
        self._sample_view = SampleView(self._sample_controller)

    def run(self) -> None:
        while True:
            samples = self._sample_controller.list_all()
            total_count = len(samples)
            total_stock = sum(s.stock_quantity for s in samples)

            print("\n==== 반도체 시료 생산 주문 관리 시스템 ====")
            print(f"전체 등록 시료 수: {total_count}개 / 전체 재고 합계: {total_stock}개")
            print("1. 시료관리")
            print("2. 시료주문        (Phase 2 예정)")
            print("3. 주문승인/거절    (Phase 2 예정)")
            print("4. 모니터링        (Phase 5 예정)")
            print("5. 출고처리        (Phase 4 예정)")
            print("6. 생산라인        (Phase 3 예정)")
            print("0. 종료")
            choice = input("> ").strip()

            if choice == "1":
                self._sample_view.run()
            elif choice in ("2", "3", "4", "5", "6"):
                print("아직 준비 중입니다.")
            elif choice == "0":
                print("프로그램을 종료합니다.")
                return
            else:
                print("잘못된 입력입니다. 다시 선택해 주세요.")
