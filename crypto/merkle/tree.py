import hashlib
from typing import Optional


class AuditMerkleTree:
    def __init__(self, leaf_hashes: list[str]):
        if not leaf_hashes:
            raise ValueError("leaf_hashes must not be empty")
        self._leaves = leaf_hashes[:]
        self._levels = self._build_tree(leaf_hashes)

    @staticmethod
    def _hash_pair(left: str, right: str) -> str:
        combined = bytes.fromhex(left) + bytes.fromhex(right)
        return hashlib.sha256(combined).hexdigest()

    def _build_tree(self, nodes: list[str]) -> list[list[str]]:
        levels: list[list[str]] = [nodes[:]]
        current = nodes[:]
        while len(current) > 1:
            next_level: list[str] = []
            for i in range(0, len(current), 2):
                left = current[i]
                if i + 1 < len(current):
                    right = current[i + 1]
                else:
                    right = current[-1]
                next_level.append(self._hash_pair(left, right))
            levels.append(next_level)
            current = next_level
        return levels

    @property
    def root(self) -> str:
        return self._levels[-1][0] if self._levels else ""

    @property
    def depth(self) -> int:
        return len(self._levels)

    @property
    def leaf_count(self) -> int:
        return len(self._leaves)

    def get_proof(self, leaf_index: int) -> list[dict]:
        if leaf_index < 0 or leaf_index >= len(self._leaves):
            raise IndexError(f"leaf_index {leaf_index} out of range [0, {len(self._leaves) - 1}]")
        proof: list[dict] = []
        idx = leaf_index
        for level_idx in range(len(self._levels) - 1):
            level = self._levels[level_idx]
            if idx % 2 == 0:
                if idx + 1 < len(level):
                    sibling = level[idx + 1]
                    direction = "right"
                else:
                    sibling = level[idx]
                    direction = "right"
            else:
                sibling = level[idx - 1]
                direction = "left"
            proof.append({"hash": sibling, "direction": direction})
            idx //= 2
        return proof

    def get_leaf_hash(self, leaf_index: int) -> str:
        return self._leaves[leaf_index]

    @staticmethod
    def verify_proof(leaf_hash: str, proof: list[dict], root: str) -> bool:
        current = leaf_hash
        for step in proof:
            sibling = step["hash"]
            if step["direction"] == "left":
                combined = bytes.fromhex(sibling) + bytes.fromhex(current)
            else:
                combined = bytes.fromhex(current) + bytes.fromhex(sibling)
            current = hashlib.sha256(combined).hexdigest()
        return current == root
