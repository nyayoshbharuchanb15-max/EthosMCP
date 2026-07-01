import hashlib
import pytest


class MerkleTree:
    def __init__(self, leaves: list[bytes]):
        if not leaves:
            raise ValueError("At least one leaf required")
        self.leaves = leaves
        self.tree = self._build(leaves)

    @staticmethod
    def _hash(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def _build(leaves: list[bytes]) -> list[list[str]]:
        tree = [[MerkleTree._hash(leaf) for leaf in leaves]]
        while len(tree[-1]) > 1:
            level = tree[-1]
            next_level = []
            for i in range(0, len(level), 2):
                if i + 1 < len(level):
                    combined = level[i] + level[i + 1]
                else:
                    combined = level[i] + level[i]
                next_level.append(MerkleTree._hash(combined.encode()))
            tree.append(next_level)
        return tree

    def root(self) -> str:
        return self.tree[-1][0]

    def proof(self, index: int) -> list[tuple[str, str]]:
        proof_path = []
        for level in self.tree[:-1]:
            if index % 2 == 0:
                sibling_idx = index + 1
                sibling = level[sibling_idx] if sibling_idx < len(level) else level[index]
                proof_path.append((level[index], sibling))
            else:
                sibling = level[index - 1]
                proof_path.append((sibling, level[index]))
            index //= 2
        return proof_path

    @staticmethod
    def verify(root: str, leaf: bytes, proof: list[tuple[str, str]]) -> bool:
        h = MerkleTree._hash(leaf)
        for left, right in proof:
            if h == left:
                h = MerkleTree._hash((left + right).encode())
            elif h == right:
                h = MerkleTree._hash((left + right).encode())
            else:
                return False
        return h == root


class TestMerkleTree:

    def test_single_leaf_root_equals_leaf_hash(self):
        leaf = b"single_artifact_hash"
        tree = MerkleTree([leaf])
        expected = hashlib.sha256(leaf).hexdigest()
        assert tree.root() == expected

    def test_two_leaves_root_is_deterministic(self):
        leaf_a = b"artifact_phase_1"
        leaf_b = b"artifact_phase_2"
        tree1 = MerkleTree([leaf_a, leaf_b])
        tree2 = MerkleTree([leaf_a, leaf_b])
        assert tree1.root() == tree2.root()
        assert len(tree1.root()) == 64

    def test_proof_verification_passes_for_valid_leaf(self):
        leaves = [b"ph1", b"ph2", b"ph3", b"ph4"]
        tree = MerkleTree(leaves)
        for i in range(len(leaves)):
            p = tree.proof(i)
            assert MerkleTree.verify(tree.root(), leaves[i], p)

    def test_proof_verification_fails_for_tampered_leaf(self):
        leaves = [b"ph1", b"ph2", b"ph3", b"ph4"]
        tree = MerkleTree(leaves)
        tampered = b"TAMPERED_PH1"
        p = tree.proof(0)
        assert not MerkleTree.verify(tree.root(), tampered, p)

    def test_any_leaf_change_changes_root(self):
        leaves_a = [b"a", b"b", b"c", b"d"]
        leaves_b = [b"a", b"b", b"CHANGED", b"d"]
        tree_a = MerkleTree(leaves_a)
        tree_b = MerkleTree(leaves_b)
        assert tree_a.root() != tree_b.root()
