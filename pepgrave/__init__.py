import ast
import importlib
from contextlib import ExitStack, suppress
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


@dataclass(unsafe_hash=True)
class Magic(ExitStack):
    peps: FrozenSet[PEP]

    def __init__(self, *peps):
        self.peps = PEP.from_id_seq(peps)
        super().__init__()

    def __enter__(self):
        super().__enter__()
        for pep in self.peps:
            for exception in pep.suppresses:
                self.enter_context(suppress(exception))


class Flint(ast.NodeTransformer):

    ALLOWED_NAMES = {"Magic", "pepgrave.Magic"}

    def visit_With(self, node):
        if (
            len(node.items) > 0
            and isinstance(node.items[0], ast.withitem)
            and isinstance(node.items[0].context_expr, ast.Call)
            and self.unparse(node.items[0].context_expr.func)
        ):
            inital_node = node
            if len(node.items[0].context_expr.args) < 1:
                raise SyntaxError(
                    "pepgrave.Magic should be called with at least 1 pep index"
                )

            peps = PEP.from_id_seq(
                pep.value for pep in node.items[0].context_expr.args
            )
            for pep in peps:
                node = pep.resolver.visit(node)
                ast.copy_location(node, inital_node)

        return node

    def unparse(self, expr):
        # unparses pepgrave.Magic and Magic calls
        result = None
        if isinstance(expr, ast.Name):
            result = expr.id

        elif isinstance(expr, ast.Attribute):
            buffer = []
            current = expr

            while isinstance(current, ast.Attribute):
                buffer.append(current.attr)
                current = current.value

            if isinstance(current, ast.Name):
                buffer.append(current.id)
                result = ".".join(reversed(buffer))

        return result in self.ALLOWED_NAMES


def __internal_magic():
    main = __import__("__main__")
    flint = Flint()
    with open(main.__file__) as f:
        main_tree = ast.parse(f.read())
    main_tree = flint.visit(main_tree)
    ast.fix_missing_locations(main_tree)
    exec(compile(main_tree, main.__file__, "exec"), main.__dict__)
    exit()


__internal_magic()
