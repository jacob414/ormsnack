# yapf

import pytest
from typing import Any
from ormsnack.tree import getast
from ormsnack import mappings as M
from micropy.testing import fixture
from micropy.dig import dig


def foo(x: Any) -> None:
    "Docstring"
    1
    2
    return x + 3


tree = getast(foo)


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


@pytest.mark.wbox
@fixture.params(
    "index, type_",
    (0, str),
    (1, int),
    (2, int),
    (3, list),
)
def test_typecheck_values(node_types, index, type_) -> None:
    "Should typecheck_values"
    assert node_types[index] == type_


@pytest.mark.wbox
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
