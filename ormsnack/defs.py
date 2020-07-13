# yapf
"""
Defines types used by Ormsnack.
"""
import ast
from dataclasses import dataclass

import funcy as fy
from typing import Any, Callable, Union, Optional, Collection

from kingston.match import Match

from .categories import STATEMENTS

AstAttrGetter = Callable[[], Any]
AstAttrSetter = Callable[[Any], None]
ExprGetter = Optional[Callable[[], Optional[ast.AST]]]
PrimOrDesc = Union['NodeDesc', Any]
Native = Union[ast.AST, Collection[ast.AST]]
Described = Union['NodeDesc', Collection['NodeDesc']]
MaybeDesc = Callable[[ast.AST], 'NodeDesc']
Value = Union[Union['NodeDesc', Collection['NodeDesc'], Any]]

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


class NodeDisp(Match):
    def __call__(self, native: Native) -> Described:
        describe = super().__call__
        if fy.is_seqcoll(native):
            return native
        else:
            return describe(native)
