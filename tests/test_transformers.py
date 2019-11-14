import ast

import pytest

from pepgrave.transformers import ASTTransformer, require_tree


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
