"""콘솔 출력용 ANSI 색상 유틸.

텍스트 앞뒤에 ANSI escape code를 덧씌우는 순수 스타일링 헬퍼만 제공한다. 원본 문구/내용을
바꾸지 않는다.
"""
from src.model.order import OrderStatus

RESET = "\x1b[0m"
BOLD = "\x1b[1m"

RED = "\x1b[31m"
GREEN = "\x1b[32m"
YELLOW = "\x1b[33m"
BLUE = "\x1b[34m"
MAGENTA = "\x1b[35m"
CYAN = "\x1b[36m"


def colorize(text: str, color: str) -> str:
    return f"{color}{text}{RESET}"


def header(text: str) -> str:
    return colorize(text, f"{CYAN}{BOLD}")


def success(text: str) -> str:
    return colorize(text, GREEN)


def error(text: str) -> str:
    return colorize(text, RED)


def warning(text: str) -> str:
    return colorize(text, YELLOW)


_STATUS_COLORS = {
    OrderStatus.RESERVED.value: YELLOW,
    OrderStatus.CONFIRMED.value: GREEN,
    OrderStatus.PRODUCING.value: CYAN,
    OrderStatus.RELEASE.value: f"{GREEN}{BOLD}",
    OrderStatus.REJECTED.value: RED,
}

_STOCK_STATUS_COLORS = {
    "여유": GREEN,
    "부족": YELLOW,
    "고갈": RED,
}


def status_text(status_value: str) -> str:
    color = _STATUS_COLORS.get(status_value.strip())
    if color is None:
        return status_value
    return colorize(status_value, color)


def stock_status_text(label: str) -> str:
    color = _STOCK_STATUS_COLORS.get(label.strip())
    if color is None:
        return label
    return colorize(label, color)
