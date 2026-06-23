from __future__ import annotations

import json
from pathlib import Path

TOOL_DIR = Path(__file__).resolve().parent

def load_tool_schemas() -> dict[str, object]:
    return json.loads((TOOL_DIR / "mcp_tools" / "get_ropa_records.json").read_text())
