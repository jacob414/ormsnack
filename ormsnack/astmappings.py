# yapf

from _ast import *
import ast
from micropy.lang import callbytype  # type: ignore
from typing import Any, Iterable, Callable
from dataclasses import dataclass
import funcy


def attrsetter(attrname: str) -> None:
    "Does attrsetter"

    def set_and_return_self(node: ast.AST, value: Any) -> Any:
        setattr(node.full, attrname, value)

    return set_and_return_self


def attrgetter(attrname: str) -> Callable[[ast.AST], Any]:
    "Does attrsetter"

    def get_node_value(node: ast.AST) -> Any:
        return getattr(node, attrname)

    return get_node_value


@dataclass
class NodeDesc(object):
    full: ast.AST
    spec: Any
    ident: str
    get: Callable[[], 'NodeDesc']
    set: Callable[[Any], None]
    cond: Any = None

    @property
    def children(self) -> Iterable:
        value = self.value
        if funcy.is_seqcoll(value):
            return value
        else:
            return []

    @property
    def value(self) -> Any:
        return self.get(self.full)

    @value.setter
    def value(self, value) -> 'NodeDesc':
        "Does _"
        self.set(self, value)

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


N = NodeDesc


def decender(nodes: Iterable[ast.AST]) -> Callable[[], Iterable[NodeDesc]]:
    "Creates NodeDesc objects from an iterable of ast nodes."

    def decend(_: ast.AST) -> Iterable[NodeDesc]:
        print(nodes)
        return [desc(node) for node in nodes]

    return decend


def fwd_get(attrname: str) -> N:
    "Returns a composition of `desc()` through `gettattr`"

    def desc_and_get(node: ast.AST) -> N:
        "Does desc_and_get"
        res = desc(getattr(node, attrname))
        return res

    return desc_and_get


desc = callbytype({  # hm? starting out by just descending into it..
    BinOp:
    lambda bo: decender([bo.left, bo.op, bo.right]),
    Expr:
    lambda expr: desc(expr.value),
    If:
    lambda iff: N(full=iff,
                  spec='if',
                  ident='if',
                  get=attrgetter('body'),
                  set=attrsetter('body'),
                  cond=desc(iff.test)),
    Call:
    lambda call: N(full=call,
                   spec=f'call/{call.func.id}',
                   ident=call.func.id,
                   get=attrgetter('func'),
                   set=attrsetter('func')),
    FunctionDef:
    lambda fdef: N(full=fdef,
                   spec=f'def',
                   ident=fdef.name,
                   get=decender(fdef.body),
                   set=attrsetter('body'),
                   cond=desc(fdef.args)),
    arguments:
    lambda args: N(full=args,
                   spec='args',
                   ident='({})'.format(','.join(arg.arg for arg in args.args)),
                   get=decender(args.args),
                   set=lambda v: setattr(args, 'args', v)),
    arg:
    lambda arg: N(
        full=arg,
        spec='arg',
        ident=arg.arg,
        value=arg.arg,
    ),
    Compare:
    lambda cmp_: N(full=cmp_,
                   spec='cmp',
                   ident='cmp',
                   get=decender([cmp_.left, *cmp_.comparators]),
                   set=attrsetter('comparators')),
    Str:
    lambda s:
    N(full=s, spec=str, ident=s.s, get=attrgetter('s'), set=attrsetter('s')),
    Num:
    lambda num: N(full=num,
                  spec=type(num.n),
                  ident=str(num.n),
                  get=attrgetter('n'),
                  set=attrsetter('n')),
    Add:
    lambda a: N(full=a,
                spec='op',
                ident='+',
                get=lambda: '+',
                set=lambda v: setattr(a, 'op', v)),
    Return:
    lambda ret: N(full=ret,
                  spec='return',
                  ident='return',
                  get=lambda _: desc(ret.value)(ret.value),
                  set=lambda v: setattr(ret, 'value', v)),
    Name:
    lambda name: N(full=name,
                   spec=name.id,
                   ident=name.id,
                   get=lambda: name.id,
                   set=lambda v: setattr(name, 'id', v))
})
