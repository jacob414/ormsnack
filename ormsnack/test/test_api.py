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


def test_snacka(Fob) -> None:
    "Should be able to roundtrip the example code."
    assert \
        type(compile(codegen.to_source(Fob.org), '', 'single')) == \
        type(foo.__code__)  # yapf: ignore

@fixture.params(
    "index, spec, value, primval",
    (0, str, "Docstring", "Docstring"),
    (1, int, 1, 1),
    (-1, 'return', ['x', '+', 1], ['x', '+', 1]),
)
def test_node_base_props(Fob, index, spec, value, primval) -> None:
    "Should snacka_codeish"
    node = Fob[index]
    assert (node.spec, node.value, node.primval) == (spec, value, primval)

def test_bug(Fob) -> None:
    "Should bug"
    node = None
    found = [node for node in Fob << 'foo']
    assert [node.ident for node in found] == ['foo']
