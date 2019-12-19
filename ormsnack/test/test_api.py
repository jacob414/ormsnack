# yapf

import pytest
from ormsnack import api
from typing import Any
import _ast
import codegen
from micropy import microscope as ms
from micropy import dig
from micropy.testing import fixture


def foo(x: Any) -> None:
    "Docstring"
    1
    2
    return x + 1


@pytest.fixture
def Fob() -> api.Snack:
    "Does Fn"
    return api.snacka(foo)


def fnbody(fob_) -> None:
    "Does fnboxy"
    return fob_.org.body[0].body[-1]


def test_snacka(Fob) -> None:
    "Should be able to roundtrip the example code."
    assert \
        type(compile(codegen.to_source(Fob.org), '', 'single')) == \
        type(foo.__code__)  # yapf: ignore


def test_simplify_return(Fob) -> None:
    "Should simplify_return"
    r_ = fnbody(Fob)
    ret = api.simplify(r_)
    assert [el.value for el in ret.children] == ['x', '+', 1]


def test_snacka_simplified(Fob) -> None:
    "Should snacka_simplified"
    assert [el.value for el in Fob.rep.values[1:4]] == ['Docstring', 1, 2]


@fixture.params(
    "index, spec, primval",
    (0, str, "Docstring"),
    (1, int, 1),
    (3, 'return', ['x', '+', 1]),
)
def test_node_base_props(Fob, index, spec, primval) -> None:
    "Should snacka_codeish"
    node = Fob[index]
    assert (node.spec, node.primval) == (spec, primval)
