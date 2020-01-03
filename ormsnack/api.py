# yapf
from ormsnack import tree
from typing import Any, List, Iterable, Mapping, Callable, Union, Optional
import funcy  # type: ignore
from micropy import lang  # type: ignore
import _ast
import ast
import operator as ops
from . import astmappings
import re
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
        raise NotImplementedError(".value property not overridden")

    @property
    @abstractmethod
    def children(self) -> Iterable:
        raise NotImplementedError(".value property not overridden")


class Branch(_Node, ABC):
    "Marker for branching nodes"

    def simplify(self, children):
        self.body = simpany(children)

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

    def __str__(self) -> str:
        return f'<{self.spec}:{self.spec}/{self.ident}>'

    @property
    def spec(self) -> str:
        return self.desc.spec


class Statement(Node, Branch):
    """A statement node. A statement is considered to have a name and
    exactly ONE `Exper` in it.

    """
    def __init__(self, full, desc) -> None:
        super().__init__(full, desc)
        self.simplify(desc.children)
        nodes = [node.full for node in desc.value]
        # self.elements = [astmappings.desc(node.full) for node in desc.value]
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


class Block(Node, Branch):
    """
    ONE `Statement` with arbitrary hierarchy of child Nodes.
    """
    def __init__(self, full, desc):
        super().__init__(full, desc)

        self.simplify(desc.children)

        # Uughh bypass `simpany()` infinite recursion otherwise. XXX
        self.stmt = Statement(full, desc.cond)

        self._value = desc.value

    def __str__(self) -> str:
        return f'<Block:{self.ident}{self.stmt.desc.ident}>'

    def __getitem__(self, idx: Any) -> Iterable[Node]:
        "Does __getitem__"
        return self.children[idx]

    def __len__(self) -> int:
        return len(self.body)

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

    @property
    def primval(self) -> Any:
        return self._value

    @property
    def codeish(self) -> str:
        "Does codeish"
        return str(self._value)


# Unpack values
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
    desc = astmappings.desc(node)
    return Kind(node, desc)


MatchFn = Callable[[_Node], bool]


def named(needle: str, matches: Callable) -> MatchFn:
    "Does named"

    def match(node: _Node) -> bool:
        "Does match"
        return matches(node.ident)

    return match


class ASTQuery(lang.ComposePiping, lang.LogicPiping):
    def __init__(self, snack=None):
        super().__init__(kind='pipe', format=bool)
        self.snack = snack

    def __rshift__(self,
                   stepf: Callable[[Any, None, None], Any]) -> 'ASTQuery':
        "Bitwise OR as simple function composition"
        self.logically(stepf, True)
        return self

    def __lshift__(self, name: str) -> 'ASTQuery':
        "Filter nodes by parameter `name`, exact matching"

        def exact(desc: str) -> bool:
            return desc == name

        self.logically(named(name, exact), True)
        return self

    def __matmul__(self, pattern: str) -> 'ASTQuery':
        "Filter nodes by RegExp pattern `pattern`"
        rx = re.compile(pattern)
        self.logically(named(pattern, rx.match), True)
        return self

    def run_q(self, top: Node) -> Iterable:
        "Perform a query on AST tree."
        all_ = [top, *top.children]
        self.res = [node for node in all_ if self(node)]
        return self


class Snack(ASTQuery):
    def __init__(self, tr):
        super().__init__(snack=self)
        self.org = tr
        self.simpler = None

    @property
    def rep(self):
        "Simplify tree"
        if self.simpler is None:
            self.simpler = simplify(self.org.body[0])
        return self.simpler

    @property
    def cur(self) -> None:
        "Does run"
        if len(self.ops) > 0:
            top = self.rep
            self.run_q(top)
            return self.res
        else:
            if self.simpler is None:
                self.simpler = simplify(self.org.body[0])
            return self.simpler

    def __getitem__(self, idx: Any) -> Iterable[Node]:
        "Indexed access"
        now = self.cur
        return now[idx]

    def __len__(self) -> int:
        "Length of tree or last query result."
        return len(self.cur)

    @property
    def q(self) -> 'Snack':
        "Does q"
        self.query = ASTQuery(self)
        return self


def snacka(ob: Any) -> Snack:
    "Does snacka"
    return Snack(tree.getast(ob))
