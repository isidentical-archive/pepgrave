import ast
import codecs
import tokenize
from dataclasses import dataclass

from pepgrave import CODEC_REGISTER
from pepgrave.context_resolver import PositionPair
from pepgrave.pep import PEP
from pepgrave.transformers import ASTTransformer, TokenTransformer, pattern

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
            if len(node.items[0].context_expr.args) < 1:
                raise SyntaxError(
                    "pepgrave.Magic should be called with 1 pep id"
                )

            peps = PEP.from_id_seq(
                pep.value for pep in node.items[0].context_expr.args
            )
            for pep in peps:
                if isinstance(pep.resolver, ASTTransformer):
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


class FlintToken(TokenTransformer):
    # match;
    # with Magic(<peps>)
    # with magic.Magic(<peps>)
    # with pepgrave.magic.Magic(<peps>)

    PARENS = "lpar", "*( number( comma number)*)", "rpar"

    def transform(self, source):
        self.source = source
        super().transform(source)
        return self.source

    @pattern("name", "name", *PARENS)
    @pattern("name", "name", "dot", "name", *PARENS)
    @pattern("name", "name", "dot", "name", "dot", "name", *PARENS)
    def context_finder(self, *tokens):
        tokens = iter(tokens)
        statement = next(tokens)
        names = []
        while current := next(tokens):
            if self._get_type(current) == tokenize.LPAR:
                break
            else:
                names.append(current)
        *pep_numbers, _ = tokens
        name = "".join(name.string for name in names)
        if statement.string == "with" and name in ALLOWED_NAMES:
            peps = PEP.from_id_seq(
                pep_number.string for pep_number in pep_numbers
            )
            for pep in peps:
                if isinstance(pep.resolver, TokenTransformer):
                    self.source = pep.resolver.transform(
                        self.source
                    )  # TO-DO: transform only with's body


class FlintAST(ASTTransformer, _PatternFinder):
    def fix(self, pep, node):
        fixed = pep.resolver.transform(node)
        return fixed


def flint(source):
    token_transformer = FlintToken()
    ast_transformer = FlintAST()
    source = token_transformer.transform(source)
    tree = ast_transformer.transform(ast.parse(source))
    ast.fix_missing_locations(tree)
    return tree


def decode(input, encoding, errors="strict"):
    if not isinstance(input, str):
        input, _ = encoding.decode(input, errors=errors)

    token_transformer = FlintToken()
    result = token_transformer.transform(input)
    return result, len(result)


def search(name):
    if "pepgrave" in name:
        encoding = (
            name.replace("pepgrave", "", 1).replace("-", "", 1) or "utf8"
        )
        encoding = codecs.lookup(encoding)

        return codecs.CodecInfo(encode=encoding.encoding, decode=flint_decoder)


if CODEC_REGISTER:
    codecs.register(search)
