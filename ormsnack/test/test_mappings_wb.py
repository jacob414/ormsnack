# yapf

import pytest
from typing import Any
from ormsnack.tree import getast
from ormsnack import mappings as M
from micropy.testing import fixture
from micropy.dig import dig

from .examples import *


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
def test_mapping_top() -> None:
    "Should map top node correctly (guards against recursion risk)"
    assert M.desc(tree).ident == 'foo'


@pytest.mark.wbox
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
