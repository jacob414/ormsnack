import pytest  # type: ignore
from micropy.testing import fixture  # type: ignore
from ormsnack import tree
import ast
import types


def foo(x):
    return x


@pytest.fixture
def fooast() -> ast.AST:
    "Does fooast"
    return tree.getast(foo)


# XXX extra param: fix in micropy later..
@fixture.params(
    "thing, x",
    ('Foo', ''),
    ({
        1: 2
    }, ''),
    (foo, ''),
)
@pytest.mark.wbox
def test_getast_sources(thing, x) -> None:
    "Python objects tree.getast() should be able to return an AST for."
    # XXX not supported:
    #  - [ ] Lambdas
    assert type(tree.getast(thing)) is ast.Module


@pytest.mark.wbox
def test_lowlevel_roundtrip(fooast: ast.AST) -> None:
    "Should simplest_roundtrip"

    # It must succeed if passed a freshly passed AST top-node.
    recompiled = tree.compile_ast(fooast)
    # The resulting code must have type `types.CodeType`
    assert type(recompiled) is types.CodeType

    roundtriped_foo = tree.run_sym(recompiled, 'foo')
    # An unchanged tree should give the same result as the original function.
    assert roundtriped_foo(2) == foo(2)


@pytest.mark.wbox
@fixture.params(
    "roundtrip, org",
    ((lambda x: tree.run_ast(tree.getast(foo))['foo'](x)), foo),
    ((lambda x: tree.run_ast(tree.getast(foo), 'foo')(x)), foo),
)
def test_ast_eval_run_unchanged_combo(fooast, roundtrip, org) -> None:
    "Should be able to "
    assert roundtrip(1) == org(1)


def test_gen_assign() -> None:
    "Should be able to generate assignments"
    compile(tree.assign('x', ast.Num(n=10)), '', 'single')
