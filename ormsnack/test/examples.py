# yapf

import ast
import pytest
from typing import Any
from ormsnack import api
from ormsnack import mappings as M
from ormsnack.tree import getast


def foo(x: Any) -> None:
    "Docstring"
    1
    2
    return x + 3


tree = getast(foo)


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
