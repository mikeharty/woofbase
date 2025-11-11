import os
from typing import Any, Any, Optional, overload
from dotenv import load_dotenv

load_dotenv()


@overload
def get_env(key: str, default: Any) -> Any: ...


@overload
def get_env(key: str, default: None = None) -> Optional[str]: ...


def get_env(key: str, default: Optional[Any] = None) -> Optional[Any]:
    value = os.getenv(key, default=default)
    if isinstance(value, str):
        if isinstance(default, str):
            return value
        elif isinstance(default, int) and value.isdigit():
            return int(value)
        elif isinstance(default, float) and "." in value:
            try:
                return float(value)
            except (TypeError, ValueError):
                return default
    return value
