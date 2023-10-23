from typing import Any


def error_wrapper(message: str) -> dict[str, Any]:
    return {"error": message}
