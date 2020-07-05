import ast
from typing import Any, Collection, List, NamedTuple, Union


class NodeDesc(object):
    ...


class NodeState(NamedTuple):
    """Holds information about at native AST node. Provides access to a
    few standardised attributes:

      - `.full`: the native AST node this `NodeState` is based upon.
      - `.spec`: interpretation of a corresponding 'type' for this AST
                 node.

       - `.ident`: identifies the AST node type as a `str`. Often a
                   reflection of the node's value, or a semantic
                   representation.

      - `value`: the value of the AST node. It's either a Python
                 primitive (for e.g. `ast.Str`, `ast.Num` etc), or an
                 iterable containing values of child nodes.

     - `expr`: an expression that might me needed to complete the
               node, e.g the expression inside an `if` statement, the
               argument list to a function def etc.

    """
    full: ast.AST
    spec: Any
    ident: str
    value: Any
    expr: Any


Native = Union[ast.AST, List[ast.AST]]
Value = Union[Union[NodeDesc, Collection[NodeDesc], Any]]
NodeDescList = List[NodeDesc]
Described = Union[NodeDesc, List[NodeDesc]]
