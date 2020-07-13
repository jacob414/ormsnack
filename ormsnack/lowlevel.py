# yapf

import os
import sys
from pathlib import Path

import inspect
import ast
from typing import Any, Mapping, Tuple, Optional, Union, Generator

from os.path import dirname

import funcy as fy
from funcy import flow

import kingston
from kingston import match
from kingston.match import Match

import types

import astunparse

PY38 = sys.version_info[:2] >= (3, 8)


def select(typ, top) -> Generator[ast.AST, None, None]:
    ""
    wanted = fy.isa(typ)
    return (node for node in ast.walk(top) if wanted(node))


def module(top: ast.AST) -> ast.Module:
    "Does module"
    return ast.Module([top], []) if PY38 else ast.Module(body=[top])


@flow.collecting
def better_fix(native: ast.AST) -> ast.AST:
    for node in ast.walk(native):
        yield ast.fix_missing_locations(node)


Func = type(better_fix)

srcfile_by_type = match.Match({
    (Func, ): lambda fn: sys.modules[fn.__module__].__file__,
    (types.ModuleType, ): lambda mod: mod.__file__
})

base_excludes = {
    'runpy.py',
    dirname(os.__file__),
}


@fy.curry
def includer(excludes, frame) -> bool:
    return excludes - set(Path(frame.filename).parts) == excludes


def sourcefile(ob: Any, begins: int = 1) -> str:
    try:
        return inspect.getsourcefile(ob)
    except TypeError:
        try:
            return inspect.getsourcefile(type(ob))
        except TypeError:
            stack = inspect.stack()
            include = includer(base_excludes | {'match.py'})
            return next(
                fy.drop(begins,
                        (frame.filename
                         for frame in inspect.stack() if include(frame))))
