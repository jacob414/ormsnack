# yapf
"""This modules handles the core idéa of ormsnack: simplification of
native AST nodes in as few categories we can get away with:

  - Statement nodes (= one statement, then an expression e.g. return,
    assert)
  - Expression nodes (all expressions)
  - Block nodes (= one statement with child nodes e.g. def,if,for,while,with)
  - Symbol nodes (variable references)
  - Literal nodes (hard-coded values)
"""
import ast
import itertools
import operator as ops
import re
from abc import ABC, abstractmethod
from typing import (Any, Callable, Iterable, List, Optional, Sized, Union,
                    cast)

import funcy as fy
import _ast
from . import mappings
from kingston import lang
from ormsnack import tree

body = ops.attrgetter('body')
hasbody = lambda o: hasattr(o, 'body')


class AbstractNode(ABC):
    ...


class Node(AbstractNode):
    ...


class AbstractNode(ABC):  # type: ignore
    """The top-level abstraction for Node's. Beware that at the top of the
    module an empty class that is later overridden by one with the
    same name is declared. This is to make the typing hints more
    readable.

    """
    _simpler: List[Node] = []
    elements: List[Node] = []
    body: List[Node] = []
    org: Optional[ast.AST] = None
    simpler: Optional[Node] = None
    ident: str = '?'

    @property
    @abstractmethod
    def codeish(self) -> str:
        "Should return the simplified form of the ast.AST tree"
        raise NotImplementedError(".codeish property not overridden")

    @property
    @abstractmethod
    def primval(self) -> Any:
        raise NotImplementedError(".primval property not overridden")

    @property
    @abstractmethod
    def value(self) -> Any:
        raise NotImplementedError(".value property getter not overridden")

    @property
    @abstractmethod
    def children(self) -> Iterable:
        raise NotImplementedError(".value property not overridden")

    @property
    def linear(self) -> Iterable[Node]:
        "Linear representation - the node itself followed by it's children"
        return [cast(Node, self), *self.children]


class Branch(AbstractNode, ABC):
    "Marker/common behaviour for branching nodes"

    def simplify(self, children):
        self.body = simpany(children)

    def __getitem__(self, idx: Any) -> Iterable[AbstractNode]:
        "Should return child node(s) from this branch specified by `idx`."
        return self.linear[idx]

    def __len__(self) -> int:
        return len(self.body)

    @property
    def value(self) -> Any:
        "Does value"
        return [child.value for child in self.body]

    @property
    def primval(self) -> Any:
        "Does primval"
        raise NotImplementedError("Branch nodes doesn't have primitive values")

    @property
    def children(self) -> List[Node]:
        return [simplify(desc.full) for desc in self.desc.children]


isbranch = fy.isa(Branch)


class Leaf(AbstractNode, ABC):
    "Marker for leaf nodes"

    @property
    def value(self) -> Any:
        """Value property - for leaf nodes that means the Python literal for
        literals, the name as a String for Symbols."""
        return self.desc.value

    @value.setter
    def value(self, value: Any) -> None:
        self.desc.value = value

    @property
    def primval(self) -> Any:
        """Primitive value property - for leaf nodes thats the Python literal
        of the AST node.

        """
        return self.value

    @property
    def children(self) -> Iterable:
        return [self]  # pragma: nocov   (just a safeguard)

    @property
    def linear(self):
        return []


isleaf = fy.isa(Branch)

isnode = fy.isa(AbstractNode)


class Node(AbstractNode):
    """
    Defined on Node:

    .spec = details about Node as str, e.g 'return'
    .ident = an identifier if applicable, otherwise same as .spec
    .primval = expressed as a Python primitive value

    .desc = ??? description?
    """
    def __init__(self, full, desc):
        self.full = full
        self.desc = desc
        self.ident = desc.ident
        self.trialc = itertools.count()

    def __str__(self) -> str:
        return f'<{self.spec}:{self.spec}/{self.ident}>'

    @property
    def trialsym(self) -> str:
        count = next(self.trialc)
        me = self.__class__.__name__
        return f'trial_{me}_{count}'

    @property
    def spec(self) -> str:
        return self.desc.spec

    def __eq__(self, value):
        return self.desc.value == value

    def __call__(self, **env):
        return tuple(tree.run_all(self.desc.full, **env).values())[0]

    def __hash__(self):
        return hash(self.desc)


class NodeCollection(object):
    def __getitem__(self, idx) -> Any:
        "Finds individual node in itself or searches.."
        try:
            return super().__getitem__(idx)
        except TypeError:
            return self.__class__([node for node in self if node.spec == idx])

    @property
    def value(self) -> Any:
        return [node.value for node in self]


def nodes(src: Iterable) -> NodeCollection:
    "Does nodes"

    class NodeCollected(NodeCollection, src.__class__):
        pass

    return NodeCollected(src)


class Statement(Node, Branch):
    """A statement node. A statement is considered to have a name and
    exactly ONE `Exper` in it.

    """
    def __init__(self, full, desc) -> None:
        super().__init__(full, desc)
        self.simplify(desc.children)
        self.name = desc.ident

    def __str__(self) -> str:
        return f'<Statement:{self.spec}/{self.ident}>'

    @property
    def codeish(self):
        return f'<Statement:{self.desc.spec}>'

    @property
    def spec(self) -> str:
        return self.desc.spec

    @property
    def primval(self) -> Any:
        return [desc.value for desc in self.desc.children]

    def __call__(self, **env):
        symname = self.trialsym
        node = self.desc.expr
        symname, node = self.trialsym, self.desc.expr
        return tree.run_sym(node, symname=symname, **env)


class Block(Node, Branch):
    """
    ONE `Statement` with arbitrary hierarchy of child Nodes.
    """
    def __init__(self, full, desc):
        super().__init__(full, desc)

        self.simplify(desc.children)

        # Uughh bypass `simpany()` infinite recursion otherwise. XXX
        self.stmt = Statement(full, mappings.desc(desc.expr))

    def __str__(self) -> str:
        return f'<Block:{self.ident}{self.stmt.desc.ident}>'

    @property
    def spec(self) -> str:
        "Does spec"
        return self.desc.spec

    def codeish(self) -> str:
        "Does codeish"
        return self.desc.format(', '.join((el.value for el in self.cond)))


class Symbol(Node, Leaf):
    def __init__(self, full, desc):
        super().__init__(full, desc)

    @property
    def codeish(self) -> str:
        return str(self.value)

    @property
    def primval(self) -> Any:
        return self.value


class Expr(Node, Branch):
    def __init__(self, full, desc):
        super().__init__(full, desc)
        self.simplify(desc.children)

    @property
    def primval(self) -> Any:
        "Does primval"
        els = len(self.elements)
        if els == 1:
            return self.elements[0].value
        else:
            return [el.primval for el in self.elements]

    @property
    def codeish(self) -> str:
        "Does codeish"
        return ', '.join((el.codeish for el in self.elements))

    @property
    def spec(self) -> str:
        "Does spec"
        return self.desc.spec


class Literal(Node, Leaf):
    def __init__(self, full, desc):
        super().__init__(full, desc)

    def __str__(self) -> str:
        "Return string representation of this Node"
        return f'<Literal:{self.primval!r}:{self.spec.__name__}>'

    @property
    def primval(self) -> Any:
        return self.value

    @property
    def codeish(self) -> str:
        "Does codeish"
        return str(self.value)


# Maps native AST nodes to their simplified equivalent
simplifiers = {
    ast.Return: Statement,
    ast.BinOp: Expr,
    ast.Name: Symbol,
    ast.Str: Literal,
    ast.Num: Literal,
    ast.FunctionDef: Block,
    ast.Expr: Expr,
    ast.arguments: Expr,
    ast.arg: Symbol,
    ast.Add: Symbol,
    ast.If: Block,
    ast.Constant: Literal,
}

NodeOrIter = Union[ast.AST, Iterable, Node]


def simpany(node_or_many: NodeOrIter) -> Union[ast.AST, Iterable[Node]]:
    "Converts objects or iterables to Ormsnack Node object(s)"

    if isinstance(node_or_many, ast.AST):
        return simplify(node_or_many)
    elif isinstance(node_or_many, Node):
        return node_or_many
    elif fy.is_seqcoll(node_or_many):
        return node_or_many
    raise TypeError(f'Unclassifiable node ({node_or_many!r})')


def simplify(node: Union[ast.AST, Iterable]) -> Node:
    "Creates a simplified ormsnack Node object from any ast object"

    Kind, desc = simplifiers[type(node)], mappings.desc(node)
    return Kind(node, desc)
