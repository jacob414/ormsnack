# yapf

import pytest
from ormsnack import api
from typing import Any
import _ast
import codegen
from micropy import microscope as ms
from micropy import dig
from micropy.testing import fixture

from .examples import *


def test_snacka(Fob) -> None:
    "Should be able to roundtrip the example code."
    assert \
        type(compile(codegen.to_source(Fob.org), '', 'single')) == \
        type(foo.__code__)  # yapf: ignore


@fixture.params(
    "index, spec, value, primval",
    (0, str, "Docstring", "Docstring"),
    (1, int, 1, 1),
    (-1, 'return', ['x', '+', 3], ['x', '+', 3]),
)  # yapf: disable
def test_node_base_props(Fob, index, spec, value, primval) -> None:
    "Should snacka_codeish"
    node = Fob[index]
    assert (node.spec, node.value, node.primval) == (spec, value, primval)


@fixture.params(
    "query, idents",
    ((snack() << 'foo'), ['foo']),
    ((snack() @ 'fo.$'), ['foo']),
    ((snack() << 1), ['1'])
)  # yapf: disable
def test_queries(query, idents) -> None:
    "Should find known nodes "
    root = query.rep
    found = [node for node in query]
    assert [node.ident for node in found] == idents


@fixture.params("idx, env, expected",
  (0, {}, 'Docstring'),
  (1, {}, 1),
  (2, {}, 2),
  (3, {'x':1}, 4)

)  # yapf: disable
@pytest.mark.wbox
def test_node_trial_steps(Fob, idx, env, expected) -> None:
    "Should node_trial_steps"
    step_ = Fob[idx]
    res = step_(**env)
    assert res == expected


@fixture.params("idx, env, change, expected_result",
  (0, {}, "Foo", "Foo"),
  (1, {}, 10, 10),
  (2, {}, 8, 8),
  # (3, {'x':3}, ('x', '+', 'x'), 6),

)  # yapf: disable
@pytest.mark.wbox
def test_node_change_re_trial(Fob, idx, env, change, expected_result) -> None:
    "Should node_change_re_trial"
    node = Fob[idx]
    node.value = change
    assert node(**env) == expected_result


@fixture.params("idx, expected", (1, "Docstring"), (2, 1), (int, [1, 2, 3]))
@pytest.mark.wbox
def test_attr_index_variants(Fob, idx, expected) -> None:
    "Should attr_indexed"
    foonode = Fob.foo
    node = foonode[idx]
    assert node.value == expected
