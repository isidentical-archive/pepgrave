import ast
import tokenize
from dataclasses import dataclass

from pepgrave.context_resolver import PositionPair
from pepgrave.pep import PEP
from pepgrave.transformers import ASTTransformer, TokenTransformer

ALLOWED_NAMES = {"Magic", "pepgrave.magic.Magic", "magic.Magic"}


@dataclass
class _FlintPosition:
    lineno: PositionPair
    col_offset: PositionPair

    @classmethod
    def from_node(self, node):
        return cls(
            PositionPair.from_node(node),
            PositionPair.from_node(node, type="col_offset"),
        )


class _PatternFinder(ast.NodeVisitor):
    def visit_With(self, node):
        if (
            len(node.items) > 0
            and isinstance(node.items[0], ast.withitem)
            and isinstance(node.items[0].context_expr, ast.Call)
            and self.unparse(node.items[0].context_expr.func)
        ):
            inital_node = node
            if len(node.items[0].context_expr.args) != 1:
                raise SyntaxError(
                    "pepgrave.Magic should be called with 1 pep id"
                )

            peps = PEP.from_id_seq(
                pep.value for pep in node.items[0].context_expr.args
            )
            for pep in peps:
                if isinstance(pep.resolver, self.__class__.__bases__[0]):
                    node = self.fix(pep, node)
                    ast.copy_location(node, inital_node)

        return node

    @staticmethod
    def unparse(expr):
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

        return result in ALLOWED_NAMES


class FlintToken(ASTTransformer):
    def transform(self, source):
        self.source = source
        return super().transform(ast.parse(source))

    def fix(self, pep, node):
        fixed = pep.resolver.transform(
            ast.get_source_segment(node, self.source)
        )
        return ast.parse(fixed)


class FlintAST(ASTTransformer, _PatternFinder):
    def fix(self, pep, node):
        fixed = pep.resolver.transform(node)
        return fixed


def flint(source):
    token_transformer = FlintToken()
    ast_transformer = FlintAST()

    source = token_transformer.transform(source)
    tree = ast_transformer.transform(ast.parse(source))
    return tree
