"""메인 메뉴 콘솔 루프."""
from src.controller.monitoring_controller import MonitoringController
from src.controller.order_controller import OrderController
from src.controller.production_line_controller import ProductionLineController
from src.controller.sample_controller import SampleController
from src.controller.shipment_controller import ShipmentController
from src.view.monitoring_view import MonitoringView
from src.view.order_view import OrderView
from src.view.production_line_view import ProductionLineView
from src.view.sample_view import SampleView
from src.view.shipment_view import ShipmentView
from src.view import colors


class MainMenuView:
    def __init__(self, sample_controller: SampleController = None,
                 order_controller: OrderController = None,
                 production_line_controller: ProductionLineController = None,
                 shipment_controller: ShipmentController = None,
                 monitoring_controller: MonitoringController = None):
        self._sample_controller = sample_controller or SampleController()
        self._sample_view = SampleView(self._sample_controller)
        self._production_line_controller = production_line_controller or ProductionLineController()
        if order_controller is not None:
            self._order_controller = order_controller
        else:
            self._order_controller = OrderController(production_queue=self._production_line_controller)
        self._order_view = OrderView(self._order_controller)
        self._production_line_view = ProductionLineView(self._production_line_controller)
        self._shipment_controller = shipment_controller or ShipmentController()
        self._shipment_view = ShipmentView(self._shipment_controller)
        self._monitoring_controller = monitoring_controller or MonitoringController()
        self._monitoring_view = MonitoringView(self._monitoring_controller)

    def run(self) -> None:
        while True:
            samples = self._sample_controller.list_all()
            total_count = len(samples)
            total_stock = sum(s.stock_quantity for s in samples)

            print(colors.header("\n==== 반도체 시료 생산 주문 관리 시스템 ===="))
            print(f"전체 등록 시료 수: {total_count}개 / 전체 재고 합계: {total_stock}개")
            print("1. 시료관리")
            print("2. 시료주문")
            print("3. 주문승인/거절")
            print("4. 모니터링")
            print("5. 출고처리")
            print("6. 생산라인")
            print(colors.warning("0. 종료"))
            choice = input("> ").strip()

            if choice == "1":
                self._sample_view.run()
            elif choice == "2":
                self._order_view.run_create_order()
            elif choice == "3":
                self._order_view.run_approval()
            elif choice == "4":
                self._monitoring_view.run()
            elif choice == "5":
                self._shipment_view.run()
            elif choice == "6":
                self._production_line_view.run()
            elif choice == "0":
                print("프로그램을 종료합니다.")
                return
            else:
                print("잘못된 입력입니다. 다시 선택해 주세요.")
