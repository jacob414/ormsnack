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


class NodeDesc(object):
    ...


NodeState = namedtuple("NodeState", ("full", "spec", "ident", "value", "expr"))

# Note: the actual value is injected from the mappings module after it
# has been defined to avoid a circular dependency.
desc: Callable[[ast.AST], NodeDesc] = ...  # type: ignore

AstAttrGetter = Callable[[], Any]
AstAttrSetter = Callable[[Any], None]
ExprGetter = Optional[Callable[[], Optional[ast.AST]]]
PrimOrDesc = Union[NodeDesc, Any]
Native = Union[ast.AST, Collection[ast.AST]]
Described = Union[NodeDesc, Collection[NodeDesc]]
MaybeDesc = Callable[[ast.AST], NodeDesc]
Value = Union[Union[NodeDesc, Collection[NodeDesc], Any]]


@dataclass
class NodeDesc(object):  # type: ignore
    ident: str
    get: AstAttrGetter
    set: AstAttrSetter
    state: Callable[[], NodeState]
    getexpr: ExprGetter = lambda: None

    @property
    def full(self) -> ast.AST:
        "Returns the native AST node for this NodeDesc object."
        return self.state().full  # type: ignore

    @property
    def children(self) -> Union[NodeDesc, Collection[NodeDesc]]:
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


def astattrsetter(node: ast.AST, attrname: str) -> AstAttrSetter:
    """Returns a function that will set an attribute in a native AST
    node. Specify name in the wrapping function.

    """
    def setter(value: Any) -> Any:
        setattr(node, attrname, value)

    return setter


def astattrgetter(node: ast.AST,
                  attrname: str) -> Union[AstAttrGetter, ExprGetter]:
    "Does astattrgetter"

    def get_ast_attr() -> Any:
        "Does get_ast_attr"
        return getattr(node, attrname)

    return get_ast_attr


def descend(*nodes: ast.AST) -> Iterable[NodeDesc]:
    "Descends one level into a native AST branch"
    return [desc(node) for node in nodes]


def descender(nodes: Iterable[ast.AST]) -> Callable[[], Iterable[NodeDesc]]:
    # "Returns a generalised descend function"
    return lambda: [desc(node) for node in nodes]


class nodedisp(match.Match):
    def __call__(self, native: Native) -> Described:
        describe = super().__call__
        if funcy.is_seqcoll(native):
            return native
        else:
            return describe(native)
