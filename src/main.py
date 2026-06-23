from __future__ import annotations

import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.config import settings
from src.server import run_server


if __name__ == "__main__":
    run_server(
        transport=settings.default_transport,
        port=settings.port,
        config_path=settings.config_path,
    )
