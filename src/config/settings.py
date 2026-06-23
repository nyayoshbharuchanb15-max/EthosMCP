from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os


@dataclass(frozen=True)
class Settings:
    app_name: str
    version: str
    default_transport: str
    port: int
    data_dir: Path
    config_path: Path


settings = Settings(
    app_name="EthosMCP",
    version="1.1.0",
    default_transport=os.getenv("ETHOSMCP_TRANSPORT", "stdio"),
    port=int(os.getenv("PORT", "8000")),
    data_dir=Path(os.getenv("ETHOSMCP_DATA_DIR", "data")),
    config_path=Path(os.getenv("ETHOSMCP_CONFIG", "config.yaml")),
)
