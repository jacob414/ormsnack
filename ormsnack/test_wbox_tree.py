import pytest
from micropy.testing import fixture
from ormsnack import tree
import ast
from altered import E


def foo(x):
    return x


# XXX extra param: fix in micropy later..
@fixture.params(
    "thing, x",
    ('Foo', ''),
    ({
        1: 2
    }, ''),
    (foo, ''),
)
def test_getast_sources(thing, x) -> None:
    "Python objects tree.getast() should be able to return an AST for."
    # XXX not supported:
    #  - [ ] Lambdas
    assert type(tree.getast(thing)) is ast.Module
