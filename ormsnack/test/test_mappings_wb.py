# yapf

import pytest
from typing import Any
from ormsnack.tree import getast
from ormsnack import mappings as M
from kingston.testing import fixture
from kingston.dig import dig

from .examples import *

pytestmark = pytest.mark.wbox


def descnodes() -> list:
    "Does descnodes"
    return [M.desc(node) for node in tree.body]


@pytest.fixture
def node_types() -> list:
    "Does nodes"
    return [type(n.value) for n in descnodes()]


@pytest.fixture
def nodes() -> list:
    "Does nodes"
    return descnodes()


def test_mapping_top() -> None:
    "Should map top node correctly (guards against recursion risk)"
    assert M.desc(tree).ident == 'foo'


@fixture.params(
    "index, expected",
    (0, []),
    (1, []),
    (2, []),
    (3, ['x', '+', 3]),
)
def test_children(nodes, index, expected) -> None:
    "Should return correct children"
    node = nodes[index]
    kids = node.children
    assert [node.value for node in kids] == expected


@fixture.params(
    "index, dpath, change",
    (0, "full.s", "Other string"),
    (1, "full.n", 1),
    (2, "full.n", 2),
    # XXX: not ready to update ast.Return.value yet.
)
def test_change_node_value(nodes, index, dpath, change) -> None:
    "Should change_node_value"
    node = nodes[index]
    node.value = change
    assert node.value == change
    assert dig(node, dpath) == change


def run_expr(node: ast.expr):
    code = compile(ast.Interactive(body=[node]), 'test', 'single')
    ns = {}
    exec(code, globals(), ns)
    return ns


@fixture.params("rep, expected_ns",
                (('a', 1), {'a':1}),
                (({'a': 1},), {'a':1}),
                ({'a': 1}, {'a': 1}),
) # yapf: disable
def test_make(rep, expected_ns) -> None:
    "Should make"
    if isinstance(rep, dict):
        node = M.make(**rep)
    else:
        node = M.make(*rep)
    ns = run_expr(node)
    assert ns == expected_ns


def test_special_assign_kwargs() -> None:
    "Should special_assign_kwargs"
    node = M.make(a=1)
    ns = run_expr(node)
    assert ns == {'a': 1}
