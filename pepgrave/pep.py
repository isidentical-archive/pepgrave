import ast
import importlib
from dataclasses import dataclass
from typing import FrozenSet


@dataclass(unsafe_hash=True)
class PEP:
    idx: int
    resolver: ast.NodeTransformer
    suppresses: FrozenSet[Exception]

    @classmethod
    def from_id_seq(cls, pep_idxs, strict=False):
        peps = set()
        for pep_idx in pep_idxs:
            try:
                module = importlib.import_module(f"pepgrave.peps.pep{pep_idx}")
            except ImportError:
                if strict:
                    raise
                else:
                    continue
            else:
                resolver = getattr(module, f"PEP{pep_idx}Resolver")()
                suppresses = getattr(resolver, "suppresses", set())
                peps.add(cls(pep_idx, resolver, frozenset(suppresses)))
        return peps
