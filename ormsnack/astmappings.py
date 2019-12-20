# yapf

from _ast import *
import ast
from micropy.lang import callbytype  # type: ignore
from typing import Any, Iterable
from dataclasses import dataclass


@dataclass
class NodeDesc(object):
    spec: Any
    ident: str
    value: Any
    full: ast.AST

    @property
    def children(self) -> Iterable:
        return []


N = NodeDesc

odesc = callbytype({
    BinOp:
    lambda bo: N(full=bo,
                 spec='bo',
                 ident='bo',
                 value=[odesc(bo.left),
                        odesc(bo.op),
                        odesc(bo.right)]),
    Expr:
    lambda expr: N(full=expr, spec='ex', ident='ex', value=odesc(expr.value)),
    Str:
    lambda s: N(full=s, spec=str, ident='str', value=s.s),
    Num:
    lambda num: N(full=num, spec=type(num.n), ident=str(num.n), value=num.n),
    Add:
    lambda a: N(full=a, spec='op', ident='+', value='+'),
    Return:
    lambda ret: N(
        full=ret, spec='return', ident='return', value=odesc(ret.value)),
    Name:
    lambda name: N(full=name, spec=name.id, ident=name.id, value=name.id)
})


def fundef_desc(node: ast.FunctionDef) -> str:
    "Textual description of an `ast.FunctionDef` node. "
    return '{}({})'.format(node.name,
                           ', '.join(arg.arg for arg in node.args.args))


# Express as code / for human
desc = callbytype({
    Str:
    lambda s: (str, "'{}'".format(s.s), ((s.s, ), ())),
    Add:
    lambda _: ("+", '+', (('+', ), ())),
    Sub:
    lambda _: ('-', '-', (('-'), ())),
    Return:
    lambda kids: ('return', 'return {}', (desc(kids.value)[2], ())),
    FunctionDef:
    lambda fdef: ('def', fundef_desc(fdef), (fdef.body, fdef.args.args)),
    arguments:
    lambda args: ('()', '({})'.format(', '.join(
        (arg.arg for ar in args.args),
        (args.args, ()),
    ))),
    arg:
    lambda arg: ('arg', arg.arg, ((arg.arg, ), ())),
    Module:
    lambda mod: ('module', '?', (module.body, ())),
    BinOp:
    lambda bo: ('BO', (desc(bo.left), desc(bo.op), desc(bo.right)),
                (bo.left, bo.op, bo.right), ()),  # type: ignore
    Num:
    lambda num: (type(num.n), num.n, ((num.n, ), ())),
    Name:
    lambda name: ('symbol', name.id, ((name.id, ), ())),
    Expr:
    lambda exp: ('ex', desc(exp.value)[1], ((exp.value, ),
                                            ())),  # type: ignore
})

# Unpack values / condition
subnodes = callbytype({
    Str: lambda str_: ((str_.s, ), ()),
    Add: lambda add_: (('+', ), ()),
    Sub: lambda add_: (('-', ), ()),
    Return: lambda ret: subnodes(ret.value),  # type: ignore
    FunctionDef: lambda fdef: (fdef.body, fdef.args),
    arguments: lambda args: (args.args, ()),
    Expr: lambda expr: ((expr.value, ), ()),
    BinOp: lambda bo: ((bo.left, bo.yop, bo.right), ()),
    Num: lambda num: ((num.n, ), ()),
    Name: lambda name: ((name.id, ), ()),
    arg: lambda arg_: ((arg_.arg, ), ()),
})
