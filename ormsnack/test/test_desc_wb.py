# yapf

import pytest
from typing import Any, Collection
from ormsnack.tree import getast
from ormsnack import mappings as M
from ormsnack import desc
from ormsnack.state import NodeDesc
from kingston.testing import fixture
from kingston.dig import dig
from funcy import is_seqcoll as many

import funcy
import _ast

from .examples import *

pytestmark = pytest.mark.wbox


@fixture.params("idx, expected",
  (0, 'Docstring'),
  (1, '1'),
  (2, '2'),
  (3, 'return')
)  # yapf: disable
def test_ident(descs: Collection[NodeDesc], idx: int, expected: str) -> None:
    "Checks that every Node descriptor's `ident` property is correct"
    assert descs[idx].ident == expected


@pytest.mark.parametrize("idx", range(0, 3))
def test_full(descs: Collection[NodeDesc], idx: int) -> None:
    "Node descriptor's `full` must be native AST nodes"
    assert isinstance(descs[idx].full, ast.AST)


@fixture.params("idx, expected",
  (0, 'Docstring'),
  (1, 1),
  (2, 2),
  (3, ['x', '+', 3])
)  # yapf: disable
def test_value(descs: Collection[NodeDesc], idx: int, expected: Any) -> None:
    "Node descriptor `.value` properties must equal known value."
    if many(expected):
        # NB: It will be the simplified node's job to expand Branch
        # values.
        assert [sub.value for sub in descs[idx].value] == expected
    else:
        assert descs[idx].value == expected


@fixture.params("idx, expected_length",
  (0, 0),
  (1, 0),
  (2, 0),
  (3, 3),
)  # yapf: disable
def test_children(
    descs: Collection[NodeDesc],
    idx: int,
    expected_length: int,
) -> None:
    """The `children` property of leaf node descriptors should be empty,
    branch node descriptors should be collections of child node
    descriptors.

    """
    assert len(descs[idx].children) == expected_length
