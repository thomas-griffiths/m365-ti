"""Utility helpers for configuration and logging."""

import json
from pathlib import Path
from typing import Any


def load_config(path: str) -> dict[str, Any]:
    """Load configuration from a JSON file."""
    with Path(path).open() as f:
        return json.load(f)
