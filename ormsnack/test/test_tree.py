# yapf

import pytest
from kingston.testing import fixture  # type: ignore
from typing import Any

from ormsnack import tree

import ast

from ormsnack.test import examples

pytestmark = pytest.mark.skip

@fixture.params(
    "thing, expected",
    ('Foo', ['Module', 'Expr', 'Constant']),
    ({}, ['Module', 'Expr', 'Dict']),
    (examples.foo, [
        'FunctionDef', 'arguments', 'Expr', 'Return', 'arg', 'Constant',
        'BinOp', 'Name', 'Add', 'Constant', 'Load'
    ]),
    (lambda x: x, ['Module', 'Lambda', 'arguments', 'Name', 'arg', 'Load']),
    ((lambda x: 1, 2), ['Module', 'Lambda', 'arguments', 'Name', 'arg', 'Load']),
)
def test_get_run_ast_roundtrip(thing:Any, expected:Any) -> None:
    "Should "
    nodes = tree.getast(thing)
    tree.run_all(nodes)
