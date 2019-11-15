import ast

from pepgrave.transformers import ASTTransformer


class PEP276Resolver(ASTTransformer):
    # for i in 7

    def visit_For(self, node):
        if isinstance(node.iter, ast.Constant) and isinstance(
            node.iter.value, int
        ):
            node.iter = ast.copy_location(
                ast.Call(ast.Name("range", ast.Load()), [node.iter], []),
                node.iter,
            )
        return node
