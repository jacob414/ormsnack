# yapf

import ast
import types
from collections import namedtuple
from dataclasses import dataclass
from typing import (Any, Callable, Generic, Iterable, List, Optional, TypeVar,
                    Union, cast)

import funcy as fy  # type: ignore
from .defs import Described, Native, NodeState, Value
from kingston import lang, match

# Note: the actual value is injected from the mappings module after it
# has been defined to avoid a circular dependency.
desc: Callable[[ast.AST], 'NodeDesc'] = ...  # type: ignore

AstAttrGetter = Callable[[], Any]
AstAttrSetter = Callable[[Any], None]
ExprGetter = Optional[Callable[[], Optional[ast.AST]]]
PrimOrDesc = Union['NodeDesc', Any]
MaybeDesc = Callable[[ast.AST], 'NodeDesc']
NodeStateFn = Callable[[], NodeState]


@dataclass(order=True)
class NodeDesc(object):  # type: ignore
    state: NodeStateFn
    attrname: str

    # XXX, must revisit, this one is difficult
    def set(self, value) -> None:
        full = self.state().full  # type: ignore
        setattr(full, self.attrname, value)

    @property
    def full(self) -> ast.AST:
        "Returns the native AST node for this NodeDesc object."
        return self.state().full  # type: ignore

    @property
    def ident(self) -> str:
        return self.state().ident  # type: ignore

    @property
    def children(self) -> List['NodeDesc']:
        "NodeDesc objects for all children descending from AST node."
        value_or_desc = self.value
        if fy.is_seqcoll(value_or_desc):
            # XXX: typing ???
            return cast(List[NodeDesc], value_or_desc)
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
        if fy.is_seqcoll(children):
            return len(cast(List[NodeDesc], children))
        else:
            raise
        return len(self.children)

    def __getitem__(self, idx) -> Any:
        return self.children[idx]  # type: ignore

    def __hash__(self):
        value = self.state().value
        try:
            valuehash = hash(value)
        except:
            valuehash = sum(hash(node) for node in value)
        return hash(self.full) + hash(self.spec) + valuehash + sum(
            hash(child) for child in self.children)


def descend(*nodes: ast.AST) -> Iterable[NodeDesc]:
    "Descends one level into a native AST branch"
    from .mappings import desc
    return [desc(node) for node in nodes]


def descender(nodes: Iterable[ast.AST]) -> Callable[[], Iterable[NodeDesc]]:
    # "Returns a generalised descend function"
    from .mappings import desc
    return lambda: [desc(node) for node in nodes]


class nodedisp(match.TypeMatcher):  # type: ignore[name-defined]
    def __call__(self, native: Native) -> Described:
        describe = super().__call__
        if fy.is_seqcoll(native):
            return desc(native)  # type: ignore
        else:
            return describe(native)
