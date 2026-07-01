import time
import hashlib
from typing import Optional

from .tree import AuditMerkleTree


class AnchorRecord:
    def __init__(
        self,
        artifact_hash: str,
        root_hash: str,
        proof_path: list[dict],
        leaf_index: int,
        timestamp: float,
    ):
        self.artifact_hash = artifact_hash
        self.root_hash = root_hash
        self.proof_path = proof_path
        self.leaf_index = leaf_index
        self.timestamp = timestamp

    def to_dict(self) -> dict:
        return {
            "artifact_hash": self.artifact_hash,
            "root_hash": self.root_hash,
            "proof_path": self.proof_path,
            "leaf_index": self.leaf_index,
            "timestamp": self.timestamp,
        }

    @staticmethod
    def from_dict(data: dict) -> "AnchorRecord":
        return AnchorRecord(
            artifact_hash=data["artifact_hash"],
            root_hash=data["root_hash"],
            proof_path=data["proof_path"],
            leaf_index=data["leaf_index"],
            timestamp=data["timestamp"],
        )


class MerkleAnchor:
    def __init__(self):
        self._anchors: dict[str, AnchorRecord] = {}

    @staticmethod
    def hash_artifact(artifact_data: bytes) -> str:
        return hashlib.sha256(artifact_data).hexdigest()

    def anchor_artifact(
        self,
        artifact_hash: str,
        merkle_tree: AuditMerkleTree,
        leaf_index: Optional[int] = None,
    ) -> dict:
        if leaf_index is None:
            for i in range(merkle_tree.leaf_count):
                if merkle_tree.get_leaf_hash(i) == artifact_hash:
                    leaf_index = i
                    break
            if leaf_index is None:
                leaf_index = 0
        proof = merkle_tree.get_proof(leaf_index)
        root_hash = merkle_tree.root
        record = AnchorRecord(
            artifact_hash=artifact_hash,
            root_hash=root_hash,
            proof_path=proof,
            leaf_index=leaf_index,
            timestamp=time.time(),
        )
        self._anchors[artifact_hash] = record
        return record.to_dict()

    def verify_anchored_artifact(
        self, artifact_hash: str, proof: list[dict], root_hash: str
    ) -> bool:
        return AuditMerkleTree.verify_proof(artifact_hash, proof, root_hash)

    def verify_stored_anchor(self, artifact_hash: str) -> Optional[bool]:
        record = self._anchors.get(artifact_hash)
        if record is None:
            return None
        return AuditMerkleTree.verify_proof(
            record.artifact_hash, record.proof_path, record.root_hash
        )

    def get_anchor(self, artifact_hash: str) -> Optional[AnchorRecord]:
        return self._anchors.get(artifact_hash)

    def list_anchors(self) -> list[AnchorRecord]:
        return list(self._anchors.values())
