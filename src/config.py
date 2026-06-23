from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class Settings:
    app_name: str = "EthosMCP"
    version: str = "1.1.0"
    default_transport: str = "stdio"

settings = Settings()
