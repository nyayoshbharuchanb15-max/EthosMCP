from __future__ import annotations

import json
from pathlib import Path
from typing import Any

SCHEMA_DIR = Path(__file__).resolve().parent


def load_tool_schemas() -> dict[str, dict[str, Any]]:
    return {path.stem: json.loads(path.read_text()) for path in sorted(SCHEMA_DIR.glob("*.json"))}
