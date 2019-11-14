# Adapted from inspectortiger
# (inspectortiger.plugins.context, Batuhan Taskaya, 2019)
from __future__ import annotations

import ast
from dataclasses import dataclass
from enum import Enum, auto
from functools import wraps


class Contexts(Enum):
    ANON = auto()
    CLASS = auto()
    GLOBAL = auto()
    UNKNOWN = auto()
    FUNCTION = auto()


@dataclass
class Context:
    name: str
    context: Contexts
    positions: PositionPair


@dataclass(unsafe_hash=True)
class PositionPair:
    start: int
    end: int

    @classmethod
    def from_node(cls, node, type="lineno"):
        return cls(start=getattr(node, type), end=getattr(node, f"end_{type}"))

    def __sub__(self, other):
        start = self.start - other.start
        end = self.end - other.end
        return (start ** 2 + end ** 2) ** 1 / 2


CTX_TYPES = {
    ast.ClassDef: Contexts.CLASS,
    ast.FunctionDef: Contexts.FUNCTION,
}

GLOBAL_CTX = Context("__main__", Contexts.GLOBAL, PositionPair(0, 0))
UNKNOWN_CTX = Context(None, Contexts.UNKNOWN, PositionPair(-1, -1))


def _verify_module(func):
    @wraps(func)
    def wrapper(ctxmanager, *args, **kwargs):
        if isinstance(ctxmanager.previous_contexts, list):
            return func(ctxmanager, *args, **kwargs)
        return None

    return wrapper


@_verify_module
def get_context(ctxmanager, node):
    if isinstance(node, ast.Module):
        return ctxmanager.global_context

    if not hasattr(node, "lineno"):
        return UNKNOWN_CTX

    possible_contexts = []
    node_positions = PositionPair.from_node(node)

    for positions, context in ctxmanager.next_contexts.items():
        if (
            node_positions.start >= positions.start
            and node_positions.end <= positions.end
        ):
            possible_contexts.append((positions - node_positions, context))

    possible_contexts.sort(key=lambda ctx: ctx[0])
    try:
        return possible_contexts[0][1]
    except IndexError:
        return ctxmanager.global_context


class ContextVisitor(ast.NodeVisitor):
    def visit_Module(self, node):
        self.context = global_ctx = GLOBAL_CTX
        self.global_context = global_ctx
        self.previous_contexts = []
        self.next_contexts = {}
        for possible_context in ast.walk(node):
            if isinstance(possible_context, tuple(CTX_TYPES)):
                positions = PositionPair.from_node(possible_context)
                ctx = CTX_TYPES[type(possible_context)]
                ctx = Context(possible_context.name, ctx, positions)
                self.next_contexts[positions] = ctx
        self.generic_visit(node)

    def join_context(self, node):
        context = get_context(self, node)
        self.previous_contexts.append(self.context)
        self.context = context

    def leave_context(self, node):
        context = self.previous_contexts.pop()
        self.context = context

    def visit_FunctionDef(self, node):
        self.join_context(node)
        self.generic_visit(node)
        self.leave_context(node)

    def visit_ClassDef(self, node):
        self.join_context(node)
        self.generic_visit(node)
        self.leave_context(node)
