# yapf

from _ast import *
import ast

from kingston import lang
from kingston import match

from typing import Any, Iterable, Callable, Optional, Union, Collection, cast
import types
from dataclasses import dataclass
import funcy  # type: ignore
from collections import namedtuple

# Note: the actual value is injected from the mappings module after it
# has been defined to avoid a circular dependency.
desc: Callable[[ast.AST], 'NodeDesc'] = ...  # type: ignore

from .defs import (AstAttrGetter, AstAttrSetter, ExprGetter, PrimOrDesc,
                   Native, Described, MaybeDesc, Value)


def descend(*nodes: ast.AST) -> Iterable['NodeDesc']:
    "Descends one level into a native AST branch"
    return [desc(node) for node in nodes]


def descender(nodes: Iterable[ast.AST]) -> Callable[[], Iterable['NodeDesc']]:
    # "Returns a generalised descend function"
    return lambda: [desc(node) for node in nodes]
