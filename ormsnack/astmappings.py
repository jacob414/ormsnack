# yapf

from _ast import *
import ast
from micropy.lang import callbytype  # type: ignore
from typing import Any, Iterable
from dataclasses import dataclass
import funcy


@dataclass
class NodeDesc(object):
    full: ast.AST
    spec: Any
    ident: str
    value: Any
    cond: Any = None

    @property
    def children(self) -> Iterable:
        if funcy.is_seqcoll(self.value):
            return self.value
        else:
            return []

    def __hash__(self):
        return hash(self.full) + hash(self.value) + hash(self.spec) + hash(
            self.ident)


N = NodeDesc


def desc_many(nodes: Iterable[ast.AST]) -> Iterable[NodeDesc]:
    "Creates NodeDesc objects from an iterable of ast nodes."
    return [desc(node) for node in nodes]


desc = callbytype({
    # hm? starting out by just descending into it..
    BinOp:
    lambda bo: desc_many([bo.left, bo.op, bo.right]),
    Expr:
    lambda expr: desc(expr.value),
    If:
    lambda iff: N(full=iff,
                  spec='if',
                  ident='if',
                  value=desc_many(iff.body),
                  cond=desc(iff.test)),
    Call:
    lambda call: N(full=call,
                   spec=f'call/{call.func.id}',
                   ident=call.func.id,
                   value=desc(call.func)),
    FunctionDef:
    lambda fdef: N(full=fdef,
                   spec=f'def',
                   ident=fdef.name,
                   value=desc_many(fdef.body),
                   cond=desc(fdef.args)),
    arguments:
    lambda args:
    N(full=args, spec='args', ident='args', value=desc_many(args.args)),
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
                   value=desc_many([cmp_.left, *cmp_.comparators])),
    Str:
    lambda s: N(full=s, spec=str, ident=s.s, value=s.s),
    Num:
    lambda num: N(full=num, spec=type(num.n), ident=str(num.n), value=num.n),
    Add:
    lambda a: N(full=a, spec='op', ident='+', value='+'),
    Return:
    lambda ret:
    N(full=ret, spec='return', ident='return', value=desc(ret.value)),
    Name:
    lambda name: N(full=name, spec=name.id, ident=name.id, value=name.id)
})
