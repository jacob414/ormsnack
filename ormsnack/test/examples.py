# yapf

import ast
import pytest
from typing import Any
from ormsnack import api
from ormsnack import mappings as M
from ormsnack.tree import getast
from typing import Collection


def foo(x: Any) -> None:
    "Docstring"
    1
    2
    return x + 3


tree = getast(foo)


def descnodes(fn=foo) -> list:
    "Does descnodes"
    nodes = getast(fn)
    return [M.desc(node) for node in nodes.body]


def snack() -> api.Snack:
    "Does snack"
    return api.snacka(foo)


@pytest.fixture
def Fob() -> api.Snack:
    "Does Fn"
    return snack()


@pytest.fixture
def native_tree() -> ast.AST:
    "Does native_tree"
    return getast(foo)


@pytest.fixture
def descs() -> Collection[ast.AST]:
    "A fixture with a list of `NodeDesc` objects, taken from `foo()`"
    return descnodes()
