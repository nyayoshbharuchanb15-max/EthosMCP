from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.config import settings


def load_metadata_records(file_name: str) -> list[dict[str, Any]]:
    data_path = settings.data_dir / file_name
    return json.loads(Path(data_path).read_text())
