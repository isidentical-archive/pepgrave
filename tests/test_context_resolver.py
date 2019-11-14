import ast
from pathlib import Path

import pytest

from pepgrave.context_resolver import Contexts, ContextVisitor, get_context

CODE = """
class Foo:
    foobar

    def bar(x, y):
        baz

foobarbaz
"""


def test_context_resolver():
    tree = ast.parse(CODE)
    resolver = ContextVisitor()
    resolver.visit(tree)

    first_context = get_context(resolver, tree.body[0])
    assert first_context.name == "Foo"
    assert first_context.context is Contexts.CLASS

    second_context = get_context(resolver, tree.body[0].body[0])
    assert second_context.name == "Foo"
    assert second_context.context is Contexts.CLASS

    third_context = get_context(resolver, tree.body[0].body[1])
    assert third_context.name == "bar"
    assert third_context.context is Contexts.FUNCTION

    fourth_context = get_context(resolver, tree.body[0].body[1].body[0])
    assert third_context.name == "bar"
    assert third_context.context is Contexts.FUNCTION

    fifth_context = get_context(resolver, tree.body[1])
    assert fifth_context.name == "__main__"
    assert fifth_context.context is Contexts.GLOBAL
