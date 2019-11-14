import ast
from functools import wraps

from pepgrave.context_resolver import Contexts, ContextVisitor, get_context


def require_tree(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if hasattr(self, "tree") and isinstance(self.tree, ast.Module):
            return func(self, *args, **kwargs)
        else:
            return None

    return wrapper


def re_resolve(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        self.resolver.visit(self.tree)
        return result

    return wrapper


class ASTTransformer(ast.NodeTransformer):
    def transform(self, tree):
        self.tree = tree
        self.resolver = ContextVisitor()
        self.resolver.visit(tree)
        self.visit(tree)

    @property
    @require_tree
    def globals(self):
        global_nodes = set()
        for node in ast.iter_child_nodes(self.tree):
            if get_context(self.resolver, node).context is Contexts.GLOBAL:
                global_nodes.add(node)
        return global_nodes

    @require_tree
    @re_resolve
    def insert_global(self, node):
        ast.fix_missing_locations(node)
        self.tree.body.insert(0, node)
