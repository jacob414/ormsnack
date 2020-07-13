# yapf

import ast

from typing import Any, Iterable, Callable, Optional, Union, Collection, cast
import types
from dataclasses import dataclass
import funcy  # type: ignore
from collections import namedtuple

from .defs import (AstAttrGetter, AstAttrSetter, ExprGetter, PrimOrDesc,
                   Native, Described, MaybeDesc, Value, NodeDisp)

@dataclass
class NodeState(object):
    """Represents one single normalized snapshot of the contents of a
    native AST node.

    """
    full: ast.AST
    spec: Any
    ident: str
    value: Any
    expr: Any

@dataclass
class NodeDesc(object):  # type: ignore
    ident: str
    get: AstAttrGetter
    set: AstAttrSetter
    state: Callable[[], 'NodeState']
    getexpr: ExprGetter = lambda: None

    @property
    def full(self) -> ast.AST:
        "Returns the native AST node for this NodeDesc object."
        return self.state().full  # type: ignore

    @property
    def children(self) -> Union['NodeDesc', Collection['NodeDesc']]:
        "NodeDesc objects for all children descending from AST node."
        value_or_desc = self.value
        if funcy.is_seqcoll(value_or_desc):
            # XXX: typing ???
            return value_or_desc
        else:
            return []

    @property
    def value(self) -> Value:
        # XXX how to handle self here?
        raw = self.state().value  # type: ignore
        return raw

    @value.setter
    def value(self, value) -> None:
        "Setter for the native AST node's value"
        # XXX how to handle self here?
        self.set(value)  # type: ignore

    @property
    def spec(self) -> str:
        return self.state().spec  # type: ignore

    @property
    def expr(self) -> Optional[ast.AST]:
        state = self.state()  # type: ignore
        if state.expr:
            return state.expr
        else:
            raise AttributeError('No expression given for this NodeDesc.')

    def __len__(self) -> int:
        "Does __len__"
        children = self.children
        if funcy.is_seqcoll(children):
            return len(cast(Collection, children))
        else:
            raise
        return len(self.children)

    def __getitem__(self, idx) -> Any:
        return self.children[idx]  # type: ignore

    def __hash__(self):
        value = self.get()
        try:
            valuehash = hash(value)
        except:
            valuehash = sum(hash(node) for node in self.get())
        return hash(self.full) + hash(self.spec) + valuehash + sum(
            hash(child) for child in self.children)
