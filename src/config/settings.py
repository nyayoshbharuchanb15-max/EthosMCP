from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    app_name: str
    version: str
    default_transport: str
    port: int
    data_dir: Path
    config_path: Path
    base_url: str
    crypto_key: str


_port = int(os.getenv("PORT", "8000"))

settings = Settings(
    app_name="EthosMCP",
    version="1.1.0",
    default_transport=os.getenv("ETHOSMCP_TRANSPORT", "stdio"),
    port=_port,
    data_dir=Path(os.getenv("ETHOSMCP_DATA_DIR", "data")),
    config_path=Path(os.getenv("ETHOSMCP_CONFIG", "config.yaml")),
    base_url=os.getenv("ETHOSMCP_BASE_URL", f"http://localhost:{_port}"),
    crypto_key=os.getenv("CRYPTO_KEY", "ethosmcp-default-audit-key"),
)
