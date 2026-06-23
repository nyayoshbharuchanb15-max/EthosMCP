from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.config import settings


def load_metadata_records(file_name: str) -> list[dict[str, Any]]:
    data_path = settings.data_dir / file_name
    try:
        with Path(data_path).open() as file_handle:
            return json.load(file_handle)
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"Metadata file not found: {data_path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON metadata in file: {data_path}") from exc
