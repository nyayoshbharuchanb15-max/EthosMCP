import os
import json
import base64
from pathlib import Path
from typing import Optional

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PrivateFormat,
    PublicFormat,
    NoEncryption,
    load_der_private_key,
    load_pem_private_key,
)
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes


class LocalKMS:
    ALGORITHMS = {"ED25519"}

    def __init__(self, key_path: str = ""):
        self._key_path = Path(key_path) if key_path else Path.home() / ".ethosmcp" / "keys"
        self._key_path.mkdir(parents=True, exist_ok=True)
        self._master_key = self._load_or_create_master_key()
        self._keys: dict[str, Ed25519PrivateKey] = {}

    def _master_key_file(self) -> Path:
        return self._key_path / ".master_key"

    def _load_or_create_master_key(self) -> bytes:
        mkf = self._master_key_file()
        if mkf.exists():
            return mkf.read_bytes()
        key = AESGCM.generate_key(bit_length=256)
        mkf.write_bytes(key)
        mkf.chmod(0o600)
        return key

    def _encrypt_key(self, private_bytes: bytes) -> str:
        aesgcm = AESGCM(self._master_key)
        nonce = os.urandom(12)
        ct = aesgcm.encrypt(nonce, private_bytes, None)
        return base64.b64encode(nonce + ct).decode()

    def _decrypt_key(self, encrypted: str) -> bytes:
        raw = base64.b64decode(encrypted)
        nonce, ct = raw[:12], raw[12:]
        aesgcm = AESGCM(self._master_key)
        return aesgcm.decrypt(nonce, ct, None)

    def _key_file(self, key_id: str) -> Path:
        return self._key_path / f"{key_id}.enc"

    def _load_key(self, key_id: str) -> Ed25519PrivateKey:
        kf = self._key_file(key_id)
        if not kf.exists():
            raise ValueError(f"Key '{key_id}' not found at {kf}")
        encrypted = kf.read_text().strip()
        private_bytes = self._decrypt_key(encrypted)
        return load_der_private_key(private_bytes, password=None)  # type: ignore

    def create_key(self, key_id: str) -> Ed25519PublicKey:
        private_key = Ed25519PrivateKey.generate()
        private_bytes = private_key.private_bytes(
            Encoding.DER, PrivateFormat.PKCS8, NoEncryption()
        )
        encrypted = self._encrypt_key(private_bytes)
        kf = self._key_file(key_id)
        kf.write_text(encrypted)
        kf.chmod(0o600)
        self._keys[key_id] = private_key
        return private_key.public_key()

    async def sign(self, key_id: str, data: bytes, algorithm: str = "ED25519") -> bytes:
        if algorithm not in self.ALGORITHMS:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
        if algorithm == "ED25519":
            private_key = self._keys.get(key_id)
            if private_key is None:
                private_key = self._load_key(key_id)
                self._keys[key_id] = private_key
            return private_key.sign(data)
        raise ValueError(f"Unsupported algorithm: {algorithm}")

    async def get_public_key(self, key_id: str) -> Ed25519PublicKey:
        private_key = self._keys.get(key_id)
        if private_key is None:
            private_key = self._load_key(key_id)
            self._keys[key_id] = private_key
        return private_key.public_key()

    def list_keys(self) -> list[str]:
        return [f.stem for f in self._key_path.glob("*.enc")]
