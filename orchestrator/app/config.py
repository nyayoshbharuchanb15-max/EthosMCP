from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    app_name: str = "AI Compliance Orchestrator"
    app_version: str = "1.0.0"
    host: str = "0.0.0.0"
    port: int = 8080

    # Database
    database_url: str = "postgresql+asyncpg://governance_admin:secure_password_change_me@postgres:5432/ai_compliance"
    neo4j_uri: str = "bolt://neo4j:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "secure_password_change_me"
    redis_url: str = "redis://redis:6379"

    # NATS
    nats_url: str = "nats://nats:4222"

    # Vault / KMS
    kms_type: str = "vault"
    vault_addr: str = "http://vault:8200"
    vault_token: Optional[str] = None
    vault_transit_key_id: str = "ai-compliance-signing-key"

    # TSA
    tsa_url: str = "http://timestamp.yourorg.internal"

    # DID
    did_method: str = "key"
    issuer_did: str = "did:key:z6MkhaXgBZDzqzthE2t5JLafwGSGPj3NjJqxYW1D6J9d6d"
    enable_live_regulatory_feeds: bool = False

    # OAuth
    oauth_jwks_uri: Optional[str] = None
    oauth_issuer: Optional[str] = None
    oauth_audience: str = "ai-compliance-mcp"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
