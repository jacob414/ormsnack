# yapf
from ormsnack import tree
from typing import Any, Tuple, Iterable, Mapping, Callable, Union
import funcy
from micropy import lang
from micropy import dig
from micropy import microscope as ms
import _ast
from patterns import patterns, Mismatch
import operator as ops

body = ops.attrgetter('body')
hasbody = lambda o: hasattr(o, 'body')
body_or_empty = funcy.iffy(hasbody, body, [])
body_lvl_0 = lambda node: funcy.walk(body_or_empty, node.body)


class Branch(object):
    "Marker for branching nodes"

    @property
    def children(self):
        return [node for node in self.value]


class Leaf(object):
    "Marker for leaf nodes"


class Node(object):
    def __init__(self, full, head, body):
        self.value = f'VALUE? {full}'
        self.head = None
        self.full = full
        self.desc = full.__class__.__name__
        try:
            self.ident = full.name
        except AttributeError:
            self.ident = full.__class__.__name__

    @property
    def spec(self):
        return f'{self.desc}:{self.ident}'

    @property
    def deepval(self):
        res = False

    def __str__(self):
        return f'<{self.__class__.__name__} {self.spec}>'

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


class Statement(Node, Branch):
    pass


# noderecur = f.isa(list, tuple, set)

NodeOrIter = Union[_ast.AST, Iterable]


def simpany(node_or_many: NodeOrIter) -> NodeOrIter:
    "Does _simp"
    if isinstance(node_or_many, _ast.AST):
        value = simplify(node_or_many)
    else:
        value = [simplify(node) for node in node_or_many]
    return value


class Block(Node, Branch):
    def __init__(self, full, head, body):
        super().__init__(full, head, body)
        self.cond_raw = head

        if head is not None:
            self.head = simplify(head)

        self.cnt = self.value = simpany(body)


class Sym(Node, Leaf):
    def __init__(self, full, head, body):
        super().__init__(full, head, body)
        self.desc = self.name = self.value = body


class Expr(Node, Leaf):
    def __init__(self, full, head, body):
        super().__init__(full, head, body)
        self.elements = self.value = simpany(body)


class Const(Node, Leaf):
    def __init__(self, full, head, body):
        super().__init__(full, head, body)
        self.value = body


class Skip(Node):
    pass


@patterns
def simplificator():
    if n is _ast.Return: lambda retrn: (Block, None, retrn.value)
    if n is _ast.BinOp: lambda binop: (Expr, None, (binop.left, binop.right))
    if n is _ast.Name: lambda name: (Sym, None, name.id)
    if n is _ast.Str: lambda str_: (Const, None, str_.s)
    if n is _ast.Num: lambda num: (Const, None, num.n)
    if n is _ast.Module: lambda mod: (Skip, 0, 0)
    if n is _ast.FunctionDef: lambda fnd: (Block, fnd.args, fnd.body)
    if n is _ast.Expr: lambda exp: (Expr, None, exp.value)
    if n is _ast.arguments: lambda args: (Expr, None, args.args)
    if n is _ast.arg: lambda arg: (Sym, None, arg.arg)


def categ(node: _ast.AST) -> Tuple[Node, Tuple]:
    "Does unpack"
    return simplificator(node)(node)


def simplify(node: _ast.AST) -> Node:
    "Does simplify"
    Kind, head, body = simplificator(node)(node)
    return Kind(node, head, body)


childhand = {
    list: funcy.identity,
    _ast.BinOp: lambda n: (n.value.left, n.value.right),
    _ast.Str: lambda n: n.value.s,
    _ast.Expr: lambda n: n.value,
    _ast.Return: lambda n: n.value
}


def unpack(node: _ast.AST) -> None:
    "Does unpack"
    return childhand[type(children(node))](node)


def children(node: _ast.AST) -> Iterable:
    "Does child"
    typ = type(node)
    if typ is list:
        return node

    handler = childhand[typ]
    ret = handler(node)
    return ret


def leaf(node: _ast.AST) -> bool:
    "Does leaf"
    return not hasattr(node, 'body')


def leaf_or_children(node: _ast.AST) -> None:
    "Does leaf_or_children"
    if leaf(node):
        return node
    else:
        return children(node)


def every(node) -> None:
    "Does every"
    start = funcy.walk(children, children(node))
    full = funcy.flatten(start, lambda n: not leaf(n))
    return [unpack(node) for node in [unpack(node) for node in full]]


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

    def q(self, query):
        "Perform a query on AST tree."
        org = self.org
        self.lq = Kind = getattr(_ast, query)
        full = every(org)
        return self

    def vals(self) -> Iterable:
        "Does vals"
        org = self.org
        res = self.qres
        pass


def snacka(ob: Any) -> None:
    "Does snacka"
    return Snack(tree.getast(ob))
