import ast
import tokenize

import pytest

from pepgrave.transformers import (
    ASTTransformer,
    TokenTransformer,
    pattern,
    require_tree,
)


@pytest.fixture
def ast_transformer():
    return ASTTransformer()


def test_require_tree():
    class Baz:
        @require_tree
        def bar(self, node):
            assert isinstance(self.tree, ast.Module)
            assert isinstance(node, ast.Constant)
            return ast.Constant(2)

    baz = Baz()
    constant = ast.Constant(2)
    assert baz.bar(constant) is None
    baz.tree = None
    assert baz.bar(constant) is None
    baz.tree = ast.Module()
    assert baz.bar(constant).value == constant.value


def test_globals(ast_transformer):
    module = ast.parse("a = 2\nb = 4\ndef foo():\n\tc = 6\nd = 8")
    result = ast_transformer.transform(module)
    assert len(ast_transformer.globals) == 3
    assert {
        assignment.targets[0].id for assignment in ast_transformer.globals
    } == set("abd")


def test_insert_global(ast_transformer):
    module = ast.parse("some_other\nsome_statement = 3")
    result = ast_transformer.transform(module)

    my_constant = ast.Constant(2)
    ast_transformer.insert_global(my_constant)

    assert my_constant in ast_transformer.globals


REAL_CODE = """
class X:
    if foo $ 1:
        def baz():
            pass
"""

EXPECTED_CODE = """
class X:
    if foo == 3:
        def baz():
            pass
"""


def test_token_transformer_new_syntax():
    class FooTokenTransformer(TokenTransformer):
        def visit_number(self, token):
            return token._replace(string="3")

        def visit_dolar(self, token):
            return token._replace(string="==", type=tokenize.OP)

        def register_dolar(self):
            return "$"

    foo = FooTokenTransformer()
    new = foo.transform(REAL_CODE)
    assert new == EXPECTED_CODE


def test_token_transformer_patternization():
    class Foo(TokenTransformer):
        @pattern("lsqb", "number", "colon", "number", "rsqb")
        def replace_to_threee(self, *tokens):
            _, n1, __, n2, ___ = tokens
            return _, n1._replace(string="3"), __, n2, ___

    foo = Foo()
    assert foo.transform("[1:10]") == "[3:10]"


def test_token_transformer_wildcarded_pattern():
    class Foo(TokenTransformer):
        @pattern("name", "*name", "newline")
        def replace_all_names_with_foo_bar(self, *tokens):
            name, *names, newline = tokens
            names = [name._replace(string="foobar") for name in names]
            return [name, *names, newline]

    foo = Foo()
    assert foo.transform("name1 name2 name3") == "name1 foobar foobar"
    assert (
        foo.transform("name1 name2 name3 name4 name5")
        == "name1 foobar foobar foobar foobar"
    )


def test_token_transformer_regex_pattern():
    class Foo(TokenTransformer):
        @pattern("name", "{2}name", "newline")
        def replace_all_names_with_foo_bar(self, *tokens):
            from pprint import pprint

            name, *names, newline = tokens
            names = [name._replace(string="foobar") for name in names]
            return [name, *names, newline]

    foo = Foo()
    assert (
        foo.transform("name1 name2 name3 name4") == "name1 name2 foobar foobar"
    )
