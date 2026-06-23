from __future__ import annotations

import json
from pathlib import Path

base = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
}

SCHEMA_DIR = Path(__file__).resolve().parent


def load_tool_schemas() -> dict[str, dict[str, object]]:
    return {
        path.stem: json.loads(path.read_text())
        for path in sorted(SCHEMA_DIR.glob("*.json"))
    }
