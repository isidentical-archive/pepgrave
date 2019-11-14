import ast
import importlib
import inspect
import io
import token
import tokenize
from functools import wraps

from pepgrave.context_resolver import Contexts, ContextVisitor, get_context

token.EXACT_TOKEN_NAMES = dict(
    zip(token.EXACT_TOKEN_TYPES.values(), token.EXACT_TOKEN_TYPES.keys())
)


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
        return self.visit(tree)

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

    def _pattern_search(self):
        patterns = {}
        for name, member in inspect.getmembers(self):
            if name.startswith("pattern_"):
                token_names = (
                    name.replace("pattern_", "", 1).upper().split("_")
                )
                token_types = tuple(
                    self._get_type_from_name(token_name)
                    for token_name in token_names
                )
                if any(token_type is None for token_type in token_types):
                    raise ValueError(f"Unknown token for pattern '{name}'")
                patterns[token_types] = member
        return patterns

    def _get_type_from_name(self, name):
        if name in token.EXACT_TOKEN_NAMES:
            return token.EXACT_TOKEN_NAMES[name]
        elif hasattr(token, name):
            return getattr(token, name)
        else:
            return None

    def _get_type(self, stream_token):
        if stream_token.string in token.EXACT_TOKEN_TYPES:
            type = token.EXACT_TOKEN_TYPES[stream_token.string]
        else:
            type = stream_token.type
        return type

    def transform(self, source):
        self._register_tokens()
        patterns = self._pattern_search()

        readline = io.StringIO(source).readline
        stream_tokens = tuple(tokenize.generate_tokens(readline))
        stream_tokens_buffer = []

        for stream_token in stream_tokens:
            name = tokenize.tok_name[self._get_type(stream_token)]
            visitor = getattr(self, f"visit_{name.lower()}", self.dummy)
            stream_tokens_buffer.append(visitor(stream_token) or stream_token)

        stream_tokens = stream_tokens_buffer.copy()
        stream_tokens_buffer.clear()

        for pattern, visitor in patterns.items():
            start_indexes, end_indexes = [], []
            pattern_state = 0

            for token_index, stream_token in enumerate(stream_tokens):
                if pattern_state == len(pattern):
                    pattern_state = 0
                    end_indexes.append(token_index)
                if self._get_type(stream_token) == pattern[pattern_state]:
                    if pattern_state == 0:
                        start_indexes.append(token_index)
                    pattern_state += 1
                elif pattern_state != 0:
                    pattern_state = 0
                    start_indexes.pop()
            else:
                if pattern_state != 0:
                    start_indexes.pop()

            patterns = [
                slice(start, end)
                for start, end in zip(start_indexes, end_indexes)
            ]
            for pattern in patterns:
                matching_tokens = stream_tokens[pattern]
                tokens = visitor(*matching_tokens) or matching_tokens
                stream_tokens[pattern] = tokens

        return tokenize.untokenize(stream_tokens)

    def dummy(self, token):
        # Implement dummy on subclasses for logging purposes or getting all tokens
        return None
