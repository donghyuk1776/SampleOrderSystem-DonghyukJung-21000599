"""범용 JSON 파일 read/write 유틸."""
import json
import os


def load(path: str) -> list:
    """파일이 없으면 빈 리스트를 반환하고, 있으면 읽어서 파싱한다."""
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        content = f.read().strip()
        if not content:
            return []
        return json.loads(content)


def save(path: str, data: list) -> None:
    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
