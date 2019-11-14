import ast

from pepgrave.pep import PEP


class Flint(ast.NodeTransformer):

    ALLOWED_NAMES = {"Magic", "pepgrave.magic.Magic", "magic.Magic"}

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
