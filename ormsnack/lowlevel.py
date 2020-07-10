# yapf

import ast
import sys
from typing import Any, Mapping, Tuple, Optional, Union, Generator

import funcy as fy
from funcy import flow

import types

import astunparse

PY38 = sys.version_info[:2] >= (3, 8)

def select(typ, top) -> Generator[ast.AST, None, None]:
    ""
    wanted = fy.isa(typ)
    return (node for node in ast.walk(top) if wanted(node))

def module(top:ast.AST) -> ast.Module:
    "Does module"
    return ast.Module([top], []) if PY38 else ast.Module(body=[top])



@flow.collecting
def better_fix(native:ast.AST) -> ast.AST:
    for node in ast.walk(native):
        yield ast.fix_missing_locations(node)

