# src/utils/crypto.py

import hmac
import hashlib
from src.config import settings

def generate_hmac_signature(data: str) -> str:
    """Generates an HMAC-SHA256 signature for the given data."""
    key = settings.crypto_key.encode("utf-8")
    message = data.encode("utf-8")
    signature = hmac.new(key, message, hashlib.sha256).hexdigest()
    return signature

def generate_sha256_hash(data: str) -> str:
    """Generates a SHA256 hash for the given data."""
    return hashlib.sha256(data.encode("utf-8")).hexdigest()
