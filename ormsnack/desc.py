# yapf

from _ast import *
import ast
from micropy import lang
from typing import Any, Iterable, Callable, Optional, Union, Collection, cast
from dataclasses import dataclass
import funcy


class NodeDesc(object):
    ...


# Note: the actual value is injected from the mappings module after it
# has been defined to avoid a circular dependency.
desc: Callable[[ast.AST], NodeDesc] = ...

AstAttrGetter = Callable[[], Any]
AstAttrSetter = Callable[[Any], None]
ExprGetter = Optional[Callable[[], Optional[ast.AST]]]
PrimOrDesc = Union[NodeDesc, Any]
Native = Union[ast.AST, Collection[ast.AST]]
Described = Union[NodeDesc, Collection[NodeDesc]]
MaybeDesc = Callable[[ast.AST], NodeDesc]


@dataclass
class NodeDesc(object):  # type: ignore
    full: ast.AST
    spec: Any
    ident: str
    get: AstAttrGetter
    set: AstAttrSetter
    hide: bool = False
    getexpr: ExprGetter = lambda: None

    @property
    def children(self) -> Collection[NodeDesc]:
        "NodeDesc objects for all children descending from AST node."
        value_or_desc = self.value
        # if isinstance(value_or_desc, ast.AST):
        #     return desc(value_or_desc)
        if funcy.is_seqcoll(value_or_desc):
            # XXX: typing ???
            return value_or_desc
        else:
            return []

    @property
    def value(self) -> Union[Union[NodeDesc, Collection[NodeDesc], Any]]:
        # XXX how to handle self here?
        raw = self.get()
        if lang.isprimitive(raw):
            return raw  # -> Any
        else:
            return desc(raw)  # -> NodeDesc

    @value.setter
    def value(self, value) -> None:
        "Setter for the native AST node's value"
        # XXX how to handle self here?
        self.set(value)  # type: ignore

    @property
    def expr(self) -> Optional[ast.AST]:
        if callable(self.getexpr):
            return self.getexpr()
        else:
            raise AttributeError('No expression given for this NodeDesc.')

    def __len__(self) -> int:
        "Does __len__"
        children = self.children
        if funcy.is_seqcoll(children):
            return len(children)
        else:
            raise
        return len(self.children)

    def __getitem__(self, idx) -> Any:
        return self.children[idx]

    def __hash__(self):
        value = self.get()
        try:
            valuehash = hash(value)
        except:
            valuehash = sum(hash(node) for node in self.get())
        return hash(self.full) + hash(self.spec) + valuehash + sum(
            hash(child) for child in self.children)


N = NodeDesc


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


def descender(nodes: Iterable[ast.AST]) -> Iterable[NodeDesc]:
    # "Returns a generalised descend function"
    return lambda: [desc(node) for node in nodes]


class nodedisp(lang.callbytype):
    def __call__(self, native: Native) -> Described:
        describe = super().__call__
        if funcy.is_seqcoll(native):
            return [describe(node) for node in native]
        else:
            return describe(native)
