"""src.view.colors 단위 테스트."""
from src.view import colors


def test_colorize_wraps_text_with_reset():
    result = colors.colorize("hello", colors.RED)
    assert result == f"{colors.RED}hello{colors.RESET}"
    assert "hello" in result


def test_semantic_helpers_preserve_original_text():
    assert "제목" in colors.header("제목")
    assert "성공" in colors.success("성공")
    assert "실패" in colors.error("실패")
    assert "주의" in colors.warning("주의")


def test_status_text_known_values_are_colored():
    assert colors.status_text("RESERVED") == colors.colorize("RESERVED", colors.YELLOW)
    assert colors.status_text("CONFIRMED") == colors.colorize("CONFIRMED", colors.GREEN)
    assert colors.status_text("PRODUCING") == colors.colorize("PRODUCING", colors.CYAN)
    assert colors.status_text("RELEASE") == colors.colorize("RELEASE", f"{colors.GREEN}{colors.BOLD}")
    assert colors.status_text("REJECTED") == colors.colorize("REJECTED", colors.RED)


def test_status_text_unknown_value_is_unchanged():
    assert colors.status_text("UNKNOWN") == "UNKNOWN"


def test_status_text_preserves_padding_while_coloring():
    padded = colors.status_text("RESERVED   ")
    assert padded == colors.colorize("RESERVED   ", colors.YELLOW)
    assert "RESERVED   " in padded


def test_stock_status_text_known_labels_are_colored():
    assert colors.stock_status_text("여유") == colors.colorize("여유", colors.GREEN)
    assert colors.stock_status_text("부족") == colors.colorize("부족", colors.YELLOW)
    assert colors.stock_status_text("고갈") == colors.colorize("고갈", colors.RED)


def test_stock_status_text_unknown_label_is_unchanged():
    assert colors.stock_status_text("알수없음") == "알수없음"
