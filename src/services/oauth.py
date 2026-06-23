from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class OAuthMetadata:
    issuer: str
    authorization_endpoint: str
    token_endpoint: str
    jwks_uri: str


def oauth_metadata(base_url: str) -> OAuthMetadata:
    return OAuthMetadata(
        issuer=base_url,
        authorization_endpoint=f"{base_url}/oauth/authorize",
        token_endpoint=f"{base_url}/oauth/token",
        jwks_uri=f"{base_url}/.well-known/jwks.json",
    )
