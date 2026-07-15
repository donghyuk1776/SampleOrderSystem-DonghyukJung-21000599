"""엔트리 포인트: `python -m src.main`으로 실행한다."""
from src.view.main_menu_view import MainMenuView


def main() -> None:
    MainMenuView().run()


if __name__ == "__main__":
    main()
