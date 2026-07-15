"""시료관리 화면 (등록/조회/검색)."""
from src.controller.sample_controller import SampleController, ValidationError
from src.view import colors


class SampleView:
    def __init__(self, controller: SampleController = None):
        self._controller = controller or SampleController()

    def run(self) -> None:
        while True:
            print(colors.header("\n==== 시료 관리 ===="))
            print("1. 시료 등록")
            print("2. 시료 조회")
            print("3. 시료 검색")
            print("0. 이전 메뉴로")
            choice = input("> ").strip()

            if choice == "1":
                self._register()
            elif choice == "2":
                self._list_all()
            elif choice == "3":
                self._search()
            elif choice == "0":
                return
            else:
                print("잘못된 입력입니다. 다시 선택해 주세요.")

    def _register(self) -> None:
        sample_id = input("시료ID: ").strip()
        name = input("이름: ").strip()
        avg_production_time = self._read_float("평균 생산시간: ")
        yield_rate = self._read_float("수율 (0~1): ")

        try:
            self._controller.register(sample_id, name, avg_production_time, yield_rate)
            print(colors.success(f"시료 '{sample_id}'가 등록되었습니다."))
        except ValidationError as e:
            print(colors.error(f"등록 실패: {e}"))

    def _read_float(self, prompt: str) -> float:
        while True:
            raw = input(prompt).strip()
            try:
                return float(raw)
            except ValueError:
                print(colors.warning("숫자를 입력해 주세요."))

    def _list_all(self) -> None:
        samples = self._controller.list_all()
        if not samples:
            print("등록된 시료가 없습니다.")
            return
        self._print_samples(samples)

    def _search(self) -> None:
        keyword = input("검색어(이름): ").strip()
        results = self._controller.search(keyword)
        if not results:
            print("검색 결과가 없습니다.")
            return
        self._print_samples(results)

    def _print_samples(self, samples: list) -> None:
        print(f"{'시료ID':<10}{'이름':<15}{'평균생산시간':<15}{'수율':<10}{'재고':<10}")
        for s in samples:
            print(f"{s.sample_id:<10}{s.name:<15}{s.avg_production_time:<15}"
                  f"{s.yield_rate:<10}{s.stock_quantity:<10}")
