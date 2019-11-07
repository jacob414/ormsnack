# yapf
from ormsnack import tree
from typing import Any, Tuple, Iterable, Mapping, Callable, Union
import funcy as fn
from micropy import lang
from micropy import dig
from micropy import microscope as ms
import _ast
from patterns import patterns, Mismatch


class Branch(object):
    "Marker for branching nodes"


class Leaf(object):
    "Marker for leaf nodes"


class Node(object):
    def __init__(self, full):
        self.value = f'VALUE? {full}'
        self.full = full
        self.desc = full.__class__.__name__
        try:
            self.ident = full.name
        except AttributeError:
            self.ident = full.__class__.__name__

    @property
    def spec(self):
        return f'{self.desc}:{self.ident}'

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
    def __init__(self, cond, full):
        super().__init__(full)
        self.cond_raw = cond
        self.cond = self.value = simpany(cond)

    def __str__(self):
        return f'<Block {self.spec}>'


class Sym(Node, Leaf):
    def __init__(self, name, full):
        super().__init__(full)
        self.name = self.value = name


class Expr(Node, Leaf):
    def __init__(self, elements, full):
        super().__init__(full)
        self.elements = self.value = simpany(elements)


class Const(Node, Leaf):
    def __init__(self, value, full):
        super().__init__(full)
        self.value = value


class Skip(Node):
    def __init__(self, value, full):
        pass


@patterns
def simplificator():
    if n is _ast.Return: lambda retrn: (Block, retrn.value)
    if n is _ast.BinOp: lambda binop: (Expr, (binop.left, binop.right))
    if n is _ast.Name: lambda name: (Sym, name.id)
    if n is _ast.Str: lambda str_: (Const, str_.s)
    if n is _ast.Num: lambda num: (Const, num.n)
    if n is _ast.Module: lambda mod: (Skip, 0)
    if n is _ast.FunctionDef: lambda fnd: (Block, fnd.body)
    if n is _ast.Expr: lambda exp: (Expr, exp.value)


def categ(node: _ast.AST) -> Tuple[Node, Tuple]:
    "Does unpack"
    try:
        return simplificator(node)(node)
    except Mismatch:
        print(f'No match: {node}')
        import ipdb
        ipdb.set_trace()
        pass
        raise


def simplify(node: _ast.AST) -> Iterable[Node]:
    "Does simplify"
    Kind, body = categ(node)
    return Kind(body, node)


childhand = {
    list: fn.identity,
    _ast.BinOp: lambda n: (n.value.left, n.value.right),
    _ast.Str: lambda n: n.value.s,
    _ast.Expr: lambda n: n.value,
    _ast.Return: lambda n: n.value
}


def unpack(node: _ast.AST) -> None:
    "Does unpack"
    return childhand[type(children(node))](node)


# Pattern match by exception concept....
# for n in (
#         n for n in dir(_ast)
#         if n != 'AST' and not n.startswith('PyCF') and not n.startswith('__')):
#     excname = f'{n}Exc'
#     print(excname)
#     Exc = lang.mkclass(excname, (Exception, ))
#     locals()[n] = Exc


def children(node: _ast.AST) -> Iterable:
    "Does child"
    print(f'children of {node}..')

    typ = type(node)
    if typ is list:
        return node

    try:
        handler = childhand[typ]
        ret = handler(node)
        print(f'child extractor {type(node)} says {ret}')
        return ret
    except KeyError as exc:
        print(f'Missmatch on {type(node)}')
        try:
            return node.body
        except AttributeError as exc:
            import ipdb
            ipdb.set_trace()
            raise


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
    start = fn.walk(children, children(node))
    full = fn.flatten(start, lambda n: not leaf(n))
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
