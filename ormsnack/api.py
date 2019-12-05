# yapf
from ormsnack import tree
from typing import Any, Tuple, List, Iterable, Mapping, Callable, Union
import funcy  # type: ignore
from micropy import lang  # type: ignore
from micropy import dig  # type: ignore
from micropy import microscope as ms  # type: ignore
import _ast
from patterns import patterns, Mismatch  # type: ignore
import operator as ops
from . import astmappings

from clipboard import copy as k

body = ops.attrgetter('body')
hasbody = lambda o: hasattr(o, 'body')
body_or_empty = funcy.iffy(hasbody, body, [])
body_lvl_0 = lambda node: funcy.walk(body_or_empty, node.body)


class Node(object):
    def __init__(self, full, body, cond):
        self._value = f'VALUE? {full}'
        self.full = full
        try:
            self.desc = astmappings.desc(full)
        except KeyError:
            self.desc = full.__class__.__name__
        try:
            self.ident = full.name
        except AttributeError:
            self.ident = full.__class__.__name__
        self.cond_hook(cond)

    def cond_hook(self, cond):
        pass

    @property
    def spec(self):
        return f'{self.desc}'

    @property
    def children(self) -> Union[List['Node'], List]:
        "Does children"
        return []

    @property
    def primval(self):
        raise NotImplemented('Unsubclassed Node')

    @property
    def codeish(self) -> str:
        "Does express"
        return ' '.join(
            (str(self.desc), *(el.codeish for el in self.children)))

    def __str__(self):
        return f'<{self.__class__.__name__}:{self.spec}>'

    def __rep__(self):
        return str(self)

    def rebuild(self) -> _ast.AST:
        "Recreates tree."
        raise NotImplemented()

    def eval(self, globals_: Mapping, ns: Mapping, **env: Any) -> None:
        "Does eval"
        # exec(compile(self.rebuild(), '?', 'single'), globals_, ns)
        # return ns
        raise NotImplemented()


class Branch(object):
    "Marker for branching nodes"

    def cond_hook(self, cond) -> None:
        "Does role_hook"
        self.cond = simpany(cond)

    @property
    def value(self) -> Any:
        "Does value"
        return self._value

    @property
    def primval(self) -> None:
        "Does primval"
        raise NotImplemented('Branch node have no primval')

    @property
    def children(self) -> Union[List[Node], List]:
        return [node for node in self._value.elements]


isbranch = funcy.isa(Branch)


class Leaf(object):
    "Marker for leaf nodes"

    @property
    def value(self) -> Any:
        "Does value"
        return self._value[0]

    @property
    def primval(self) -> Any:
        "Does primval"
        return self._value[0]


isleaf = funcy.isa(Branch)


class Statement(Node, Branch):
    """A statement node. A statement is considered to have a name and
    exactly ONE `Exper` in it.

    """
    def __init__(self, full, body, cond) -> None:
        super().__init__(full, body, cond)
        self._value = self
        self._value.elements = body
        self.desc = astmappings.codename(full)
        self.cnt = simpany(body)

    @property
    def children(self):
        return self.cnt


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

    @property
    def codeish(self) -> str:
        "Does codeish"
        return self.desc.format()


class Sym(Node, Leaf):
    def __init__(self, full, body, cond):
        super().__init__(full, body, cond)
        self.desc = self.name = self._value = body

    @property
    def codeish(self) -> str:
        return str(self._value)


class Expr(Node, Leaf):
    def __init__(self, full, body, cond):
        super().__init__(full, body, cond)
        self.elements = self._value = simpany(body)

    @property
    def values(self):
        return [el._value for el in self.elements]

    @property
    def codeish(self) -> str:
        "Does codeish"
        return ', '.join((el.codeish for el in self._value.elements))


class Literal(Node, Leaf):
    def __init__(self, full, body, cond):
        super().__init__(full, body, cond)
        self._value = self.name = body
        self.desc = body

    @property
    def codeish(self) -> str:
        "Does codeish"
        return str(self._value)


# Unpack values
simplifiers = lang.typemapx({
    _ast.Return:
    lambda retrn: (Statement, retrn.value, None),
    _ast.BinOp:
    lambda binop: (Expr, (binop.left, binop.op, binop.right), None),
    _ast.Name:
    lambda name: (Sym, name.id, None),
    _ast.Str:
    lambda str_: (Literal, str_.s, None),  # ok
    _ast.Num:
    lambda num: (Literal, num.n, None),
    _ast.Module:
    lambda mod: (Skip, 0, 0),
    _ast.FunctionDef:
    lambda fnd: (Block, fnd.body, fnd.args),
    _ast.Expr:
    lambda exp: (Expr, exp.value, None),
    _ast.arguments:
    lambda args: (Expr, args.args, None),
    _ast.arg:
    lambda arg: (Sym, arg.arg, None),
    _ast.Add:
    lambda add: (Sym, '+', None),
})

NodeOrIter = Union[_ast.AST, Iterable, Node]


def simpany(node_or_many: NodeOrIter) -> Union[Node, Iterable[Node]]:
    "Converts objects or iterables to Ormsnack Node object(s)."
    if isinstance(node_or_many, _ast.AST):
        return simplify(node_or_many)
    elif isinstance(node_or_many, Node):
        return node_or_many
    elif funcy.is_seqcoll(node_or_many):
        return [simplify(node) for node in node_or_many]
    raise TypeError(f'Unclassifiable node ({node_or_many!r})')


def simplify(node: Union[_ast.AST, Iterable]) -> Union[Node, Iterable[Node]]:
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


class ASTQuery(lang.ComposePiping):
    pass


class Snack(object):
    def __init__(self, tr):
        self.org = tr
        self.simpler = None

    @property
    def rep(self):
        "Simplify tree"
        if self.simpler is None:
            self.simpler = simplify(self.org.body[0])
        return self.simpler

    def q(self, query: ASTQuery):
        "Perform a query on AST tree."
        rep = self.rep
        import ipdb; ipdb.set_trace(); pass
        res = self.res = tuple(filter(query, self.rep.values))
        return self


def snacka(ob: Any) -> None:
    "Does snacka"
    return Snack(tree.getast(ob))
