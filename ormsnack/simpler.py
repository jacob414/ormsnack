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
from ormsnack import tree
from typing import Any, List, Iterable, Callable, Union, Optional
import funcy  # type: ignore
from micropy import lang  # type: ignore
import _ast
import ast
import operator as ops
from . import mappings
import re
import itertools
from abc import ABC, abstractmethod

body = ops.attrgetter('body')
hasbody = lambda o: hasattr(o, 'body')


class _Node(ABC):
    """The top-level abstraction for Node's. Beware that at the top of the
    module an empty class that is later overridden by one with the
    same name is declared. This is to make the typing hints more
    readable.

    """
    _value: List['_Node'] = []
    _simpler: List['_Node'] = []
    elements: List['_Node'] = []
    org: Optional[ast.AST] = None
    simpler: Optional['_Node'] = None
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
    def value(self, value: Any) -> None:
        raise NotImplementedError(".value property setter not overridden")
    
    @property
    @abstractmethod
    def children(self) -> Iterable:
        raise NotImplementedError(".value property not overridden")


class Branch(_Node, ABC):
    "Marker/common behaviour for branching nodes"

    def simplify(self, children):
        self.body = simpany(children)

    def __getitem__(self, idx: Any) -> Iterable[_Node]:
        "Should return child node(s) from this branch specified by `idx`."
        return self.children[idx]

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
    def children(self) -> List[_Node]:
        return self.body


isbranch = funcy.isa(Branch)


class Leaf(_Node, ABC):
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
        return []  # pragma: nocov   (just a safeguard)


isleaf = funcy.isa(Branch)

isnode = funcy.isa(_Node)


class Node(_Node):
    """
    Defined on Node:

    .spec = details about Node as str, e.g 'return'
    .ident = an identifier if applicable, otherwise same as .spec
    .primval = expressed as a Python primitive value

    .desc = ??? description?
    """
    def __init__(self, full, desc):
        self._value = desc.value
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

    def trial(self, **env):
        return tuple(tree.run_all(self.desc.full, **env).values())[0]


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
    def children(self):
        return self.elements

    @property
    def spec(self) -> str:
        return self.desc.spec

    @property
    def primval(self) -> Any:
        return [desc.value for desc in self.desc.children]

    def trial(self, **env):
        symname, node = self.trialsym, self.desc.getexpr()
        return tree.run_sym(node, symname=symname, **env)


class Block(Node, Branch):
    """
    ONE `Statement` with arbitrary hierarchy of child Nodes.
    """
    def __init__(self, full, desc):
        super().__init__(full, desc)

        self.simplify(desc.children)

        # Uughh bypass `simpany()` infinite recursion otherwise. XXX
        self.stmt = Statement(full, mappings.desc(desc.expr.full))

        self._value = desc.value

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
        return str(self._value)

    @property
    def primval(self) -> Any:
        return self._value


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
        self._value = self.name = desc.value
        # self.desc = desc.value

    def __str__(self) -> str:
        "Return string representation of this Node"
        return f'<Literal:{self.primval!r}:{self.spec.__name__}>'

    @property
    def primval(self) -> Any:
        return self._value

    @property
    def codeish(self) -> str:
        "Does codeish"
        return str(self._value)


# Maps native AST nodes to their simplified equivalent
simplifiers = {
    _ast.Return: Statement,
    _ast.BinOp: Expr,
    _ast.Name: Symbol,
    _ast.Str: Literal,
    _ast.Num: Literal,
    _ast.FunctionDef: Block,
    _ast.Expr: Expr,
    _ast.arguments: Expr,
    _ast.arg: Symbol,
    _ast.Add: Symbol,
    _ast.If: Block,
}

NodeOrIter = Union[ast.AST, Iterable, Node]


def simpany(node_or_many: NodeOrIter) -> Union[_Node, Iterable[_Node]]:
    "Converts objects or iterables to Ormsnack Node object(s)."
    if isinstance(node_or_many, ast.AST):
        return simplify(node_or_many)
    elif isinstance(node_or_many, Node):
        return node_or_many
    elif funcy.is_seqcoll(node_or_many):
        return [simplify(desc.full) for desc in node_or_many]
    raise TypeError(f'Unclassifiable node ({node_or_many!r})')


def simplify(node: Union[ast.AST, Iterable]) -> _Node:
    "Creates a simplified ormsnack Node object from any ast object"

    Kind = simplifiers[type(node)]
    desc = mappings.desc(node)
    return Kind(node, desc)
