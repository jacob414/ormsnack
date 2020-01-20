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


def snack() -> api.Snack:
    "Does snack"
    return api.snacka(foo)


@pytest.fixture
def Fob() -> api.Snack:
    "Does Fn"
    return snack()


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


@fixture.params(
    "query, idents",
    ((snack() << 'foo'), ['foo']),
    ((snack() @ 'fo.$'), ['foo']),
)
def test_queries(query, idents) -> None:
    "Should find known nodes "
    found = [node for node in query]
    assert [node.ident for node in found] == idents


@fixture.params("idx, env, expected",
  (0, {}, 'Docstring'),
  (1, {}, 1),
  (2, {}, 2),
  (3, {'x':1}, 2)

)  # yapf: disable
@pytest.mark.wbox
def test_node_trial_steps(Fob, idx, env, expected) -> None:
    "Should node_trial_steps"
    step_ = Fob[idx]
    res = step_.trial(**env)
    assert res == expected

@fixture.params("idx, env, change",
  (0, {}, "Foo"),
  (1, {}, 10),
  (2, {}, 8),

)  # yapf: disable
@pytest.mark.wbox
def test_node_change_re_trial(Fob, idx, env, change) -> None:
    "Should node_change_re_trial"
    node = Fob[idx]
    node.value = change
    assert node.trial(**env) == change
