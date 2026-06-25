import json
from pathlib import Path
from typing import Any, cast

import yaml


DATA_DIR = Path(__file__).parent.parent / "data"


def load_yaml(relative_path: str) -> dict[str, Any]:
    filepath = DATA_DIR / relative_path
    if not filepath.exists():
        raise FileNotFoundError(f"Data file not found: {filepath}")
    with open(filepath) as f:
        return cast(dict[str, Any], yaml.safe_load(f))


def load_json(relative_path: str) -> dict[str, Any]:
    filepath = DATA_DIR / relative_path
    if not filepath.exists():
        raise FileNotFoundError(f"Data file not found: {filepath}")
    with open(filepath) as f:
        return cast(dict[str, Any], json.load(f))
