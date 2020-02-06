# yapf
"""
White-box tests for ormsnack.simpler.
"""

import pytest
from typing import Any
from ormsnack import simpler as S
from ormsnack.tree import getast
from ormsnack import mappings as M
from micropy.testing import fixture
from micropy.dig import dig

pytestmark = pytest.mark.wbox


def foo(x: Any) -> None:
    "Docstring"
    1
    2
    return x + 3


tree = getast(foo)
allnodes = [tree, *tree.body]


@pytest.fixture
def simplified() -> S.Node:
    "Does simplified"
    return S.simplify(tree)


@pytest.mark.parametrize("node", allnodes)
def test_simpany_can_simplify(node) -> None:
    "Guards against unsimplifiable AST nodes"
    assert isinstance(S.simpany(node), S.Node)


@fixture.params("idx, expected",
   (0, 'def'),
   (1, str),
   (2, int),
   (3, int),
   (4, 'return')
)  # yapf: disable
def test_simplify_correct(simplified, idx, expected) -> None:
    "Should simplify_correct"
    node = simplified[idx]
    assert node.spec == expected


@fixture.params("idx, expected",
   (1, "Docstring"),
   (2, 1),
   (3, 2),
)  # yapf: disable
def test_nodes_comparable(simplified, idx, expected) -> None:
    "Should simplify_correct"
    node = simplified[idx]
    assert node == expected


def test_trial_if_called(simplified) -> None:
    "Should be able to trial execute child nodes by calling them."
    assert simplified[-1](x=1) == 4  # trial
