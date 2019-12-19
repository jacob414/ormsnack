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
body_or_empty = funcy.iffy(hasbody, body, [])


class _Node(object):
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
    def children(self) -> List['_Node']:
        "Does children"
        return self._simpler

    @property
    @abstractmethod
    def simplified(self) -> Optional['_Node']:
        "Should return the simplified form of the ast.AST tree"
        pass

    @property
    @abstractmethod
    def codeish(self) -> str:
        "Should return the simplified form of the ast.AST tree"
        pass

    @property
    @abstractmethod
    def primval(self) -> Any:
        pass


class Branch(_Node, ABC):
    "Marker for branching nodes"

    def cond_hook(self, cond) -> None:
        "Does role_hook"
        self.cond = simpany(cond)

    @property
    def value(self) -> Any:
        "Does value"
        return self._value

    @property
    def primval(self) -> Any:
        "Does primval"
        raise NotImplementedError("Branch nodes doesn't have primitive values")

    @property
    def children(self) -> List[_Node]:
        return self.elements

    @property
    def simplified(self) -> Optional[_Node]:
        "Does simplified"
        if self.simpler is not None:
            self.simpler = simplify(self.org.body[0])  # type: ignore
        return self.simpler


isbranch = funcy.isa(Branch)


class Leaf(_Node, ABC):
    "Marker for leaf nodes"

    @property
    def value(self) -> Any:
        """Value property - for leaf nodes that means the Python literal for
        literals, the name as a String for Symbols."""
        return self._value[0]

    @property
    def primval(self) -> Any:
        "Does primval"
        return self.value

    @property
    def simplified(self) -> Optional[_Node]:
        "Does simplify"
        self.simpler = simplify(self.org.body[0])  # type: ignore

        return self.simpler

    @property
    def simplified(self) -> Optional[_Node]:
        "Does simplify"
        self.simpler = simplify(self.org.body[0])  # type: ignore

        return self.simpler


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
    def __init__(self, full, body, cond):
        self._value = f'VALUE? {full}'
        self.full = full
        try:
            self.ident = full.name
        except AttributeError:
            self.ident = full.__class__.__name__
        self.cond_hook(cond)

    def cond_hook(self, cond):
        pass

    @property
    def children(self) -> Union[List[_Node], List]:
        "Does children"
        return []

    @property
    def spec(self) -> str:
        "Does spec"
        try:
            return astmappings.desc(self.full.value)
        except KeyError:
            # XXX Breaks Zen
            return self.full.__class__.__name__.lower()

    @property
    def codeish(self) -> str:
        "Does express"
        return ' '.join(
            (str(self.desc), *(el.codeish for el in self.children)))

    def __str__(self):
        return f'<{self.__class__.__name__}:{self.codeish}>'

    def __repr__(self):
        return str(self)

    def rebuild(self) -> ast.AST:
        "Recreates tree."
        raise NotImplementedError('Node.rebuild(): TBD')

    def eval(self, globals_: Mapping, ns: Mapping, **env: Any) -> None:
        "Does eval"
        # exec(compile(self.rebuild(), '?', 'single'), globals_, ns)
        # return ns
        raise NotImplementedError('Node.eval(): TBD')


class Statement(Node, Branch):
    """A statement node. A statement is considered to have a name and
    exactly ONE `Exper` in it.

    """
    def __init__(self, full, body, cond) -> None:
        super().__init__(full, body, cond)
        # if type(full) == ast.Return:
        # import ipdb; ipdb.set_trace(); pass

        self._value = [self]
        self.elements = body
        desc, codeme = astmappings.desc(full)
        self.name = getattr(full, 'name', desc)
        self.desc = desc
        self.codeme = codeme
        self.cnt = simpany(body)
        self.cond = simpany(cond)
        # self.cond = [astmappings.desc(part) for part in cond]

    @property
    def codeish(self):
        # return astmappings.desc(self.full).format(', '.join(
        # el.value for el in self.cond)) + ':'
        return self.codeme

    @property
    def children(self):
        return self.cnt

    @property
    def spec(self) -> str:
        return self.name

    @property
    def primval(self) -> Any:
        return [child.value for child in self.children]


class Block(Node, Branch):
    """
    ONE `Statement` with arbitrary hierarchy of child Nodes.
    """
    def __init__(self, full, body, cond):
        super().__init__(full, body, cond)

        self.body = simpany(body)
        self.cond = simpany(cond)

        # Uughh bypass `simpany()` infinite recursion otherwise. XXX
        self.stmt = Statement(full, body, cond)

        self.cnt = self._value = self.body

    @property
    def values(self):
        return (self.stmt, ) + tuple(
            funcy.flatten(value._value for value in self.body))

    def __getitem__(self, idx: Any) -> Iterable[Node]:
        "Does __getitem__"
        return self.body[idx]

    def __len__(self) -> int:
        return len(self.body)

    @property
    @property
    def spec(self) -> str:
        "Does spec"
        return self.codeish

    def codeish(self) -> str:
        "Does codeish"
        return self.desc.format(', '.join((el.value for el in self.cond)))


class Symbol(Node, Leaf):
    def __init__(self, full, body, cond):
        super().__init__(full, body, cond)
        self.desc = self.name = self._value = body

    @property
    def codeish(self) -> str:
        return str(self._value)

    @property
    def primval(self) -> Any:
        return self._value


class Expr(Node, Leaf):
    def __init__(self, full, body, cond):
        super().__init__(full, body, cond)
        self.elements = self._value = simpany(body)
        desc, codeme = astmappings.desc(full)
        self.desc, self.codeme = desc, codeme

    @property
    def values(self):
        return [el._value for el in self.elements]

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
        return astmappings.desc(self.full.value)[0]


class Literal(Node, Leaf):
    def __init__(self, full, body, cond):
        super().__init__(full, body, cond)
        self._value = self.name = body
        self.desc = body

    @property
    def primval(self) -> Any:
        return self._value

    @property
    def codeish(self) -> str:
        "Does codeish"
        return str(self._value)


# Unpack values
simplifiers = lang.callbytype({
    _ast.Return:
    lambda retrn: (Statement, retrn.value, None),
    _ast.BinOp:
    lambda binop: (Expr, (binop.left, binop.op, binop.right), None),
    _ast.Name:
    lambda name: (Symbol, name.id, None),
    _ast.Str:
    lambda str_: (Literal, str_.s, None),  # ok
    _ast.Num:
    lambda num: (Literal, num.n, None),
    _ast.FunctionDef:
    lambda fnd: (Block, fnd.body, fnd.args),
    _ast.Expr:
    lambda exp: (Expr, exp.value, None),
    _ast.arguments:
    lambda args: (Expr, args.args, None),
    _ast.arg:
    lambda arg: (Symbol, arg.arg, None),
    _ast.Add:
    lambda add: (Symbol, '+', None),
})

NodeOrIter = Union[ast.AST, Iterable, Node]


def simpany(node_or_many: NodeOrIter) -> Union[_Node, Iterable[_Node]]:
    "Converts objects or iterables to Ormsnack Node object(s)."
    if isinstance(node_or_many, ast.AST):
        return simplify(node_or_many)
    elif isinstance(node_or_many, Node):
        return node_or_many
    elif funcy.is_seqcoll(node_or_many):
        return [simplify(node) for node in node_or_many]
    raise TypeError(f'Unclassifiable node ({node_or_many!r})')


def simplify(node: Union[ast.AST, Iterable]) -> _Node:
    "Creates a simplified ormsnack Node object from any ast object"

    Kind, _, _ = simplifiers(node)
    subnodes = astmappings.subnodes(node)

    return Kind(node, *subnodes)


childhand = {
    list: funcy.identity,
    _ast.BinOp: lambda n: (n.value.left, n.value.right),
    _ast.Str: lambda n: n.value.s,
    _ast.Expr: lambda n: n.value,
    _ast.Return: lambda n: n.value
}

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

    def run_q(self):
        "Perform a query on AST tree."
        self.res = tuple(node for node in self.rep.values if self(node))
        return self


class Snack(ASTQuery):
    def __init__(self, tr):
        lang.LogicPiping.__init__(self, kind='pipe')
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
            self.run_q()
            return self.res
        else:
            if self.simpler is None:
                self.simpler = simplify(self.org.body[0])
            return self.simpler

    def __getitem__(self, idx: Any) -> Iterable[Node]:
        "Indexed access"
        return self.cur[idx]

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
