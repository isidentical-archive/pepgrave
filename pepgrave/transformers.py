import ast
import importlib
import inspect
import io
import token
import tokenize
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


class TokenTransformer:
    def _next_token_slot(self):
        index = max(token.tok_name.keys(), default=0)
        return index + 1

    def _register_token(self, token_string, token_name):
        token_index = self._next_token_slot()
        setattr(token, token_name, token_index)
        token.tok_name[token_index] = token_name
        token.EXACT_TOKEN_TYPES[token_string] = token_index

    def _register_tokens(self):
        for name, member in inspect.getmembers(self):
            if name.startswith("register_"):
                token_name = name.replace("register_", "", 1).upper()
                token_string = member()
                self._register_token(token_string, token_name)

        importlib.reload(tokenize)

    def transform(self, source):
        self._register_tokens()

        readline = io.StringIO(source).readline
        stream_tokens = tuple(tokenize.generate_tokens(readline))
        buffer = []

        for stream_token in stream_tokens:
            if stream_token.string in tokenize.EXACT_TOKEN_TYPES:
                type = tokenize.EXACT_TOKEN_TYPES[stream_token.string]
            else:
                type = stream_token.type

            name = tokenize.tok_name[type]
            visitor = getattr(self, f"visit_{name.lower()}", self.dummy)
            buffer.append(visitor(stream_token) or stream_token)

        return tokenize.untokenize(buffer)

    def dummy(self, token):
        # Implement dummy on subclasses for logging purposes or getting all tokens
        return None
