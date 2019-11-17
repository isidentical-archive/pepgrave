import io
import textwrap
import tokenize

import pytest

from pepgrave.untokenizer import untokenize


@pytest.mark.parametrize("expr", ("2", "2 + 2", "func('call')"))
def test_untokenize_basic(expr):
    tokens = tokenize.generate_tokens(io.StringIO(expr).readline)
    assert untokenize(tokens) == expr


@pytest.mark.parametrize(
    "statement",
    (
        """
    import pytest
    import tokenize
    import io
    from pepgrave.untokenizer import untokenize
    if x: pass
    def func(a): return a
    """.splitlines()
    ),
)
def test_untokenize_basic_statement(statement):
    statement = textwrap.dedent(statement)
    tokens = tokenize.generate_tokens(io.StringIO(statement).readline)
    assert untokenize(tokens) == statement


STATEMENTS = (
    """
def func(x, y):
    z = compute(x, y)
    return z
""",
    """
def func(x, y):
  z = compute(x, y)
  return z
""",
    """
def func(x, y):
    z = compute(x, y)
    if multiple_indent_level > z:
        try:
            something_new()
        except:
            lol()
    return z
""",
    """
with SomeContextToManage():
    zzzz > expr
""",
)


@pytest.mark.parametrize("statement", (STATEMENTS))
def test_untokenize_complex_statement(statement):
    statement = textwrap.dedent(statement)
    tokens = tokenize.generate_tokens(io.StringIO(statement).readline)
    assert untokenize(tokens) == statement
