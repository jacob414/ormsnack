# yapf

from _ast import *
import ast
from micropy.lang import callbytype  # type: ignore
from typing import Any

def fundef_desc(node: ast.FunctionDef) -> str:
    "Does fundef_desc"
    return '{}({})'.format(node.name, ', '.join(arg.arg for arg in node.args.args))

def autoflat(nose: ast.AST) -> Any:
    "Does autoflat"
    pass


# Express as code / for human
desc = callbytype({
    Str:
    lambda s: (str, "'{}'".format(s.s)),
    Add:
    lambda _: ("+", '+'),
    Sub:
    lambda _: ('-', '-'),
    Return:
    lambda kids: ('return', 'return {}'),
    FunctionDef:
    lambda fdef: ('def', fundef_desc(fdef)),
    arguments:
    lambda args: ('()', '({})'.format(', '.join(
        (arg.arg for ar in args.args)))),
    arg: lambda arg: ('arg', arg.arg),
    Module:
    lambda mod: ('module', '?'),
    BinOp: lambda bo: ('BO', (desc(bo.left), desc(bo.op), desc(bo.right))),  # typing: ifnore
    Num: lambda num: (type(num.n), num.n),
    Name: lambda name: ('symbol', name.id),
    Expr: lambda exp: ('ex', desc(exp.value)[1]),  # RECUR!
})

def fundef_desc(node: ast.AST) -> str:
    "Does fundef_desc"
    return '{}({})'.format(node.name, ', '.join(arg.arg for arg in node.args.args))

# Express as code / for human
desc = callbytype({
    Str:
    lambda s: (str, "'{}'".format(s.s)),
    Add:
    lambda _: ("+", '+'),
    Sub:
    lambda _: ('-', '-'),
    Return:
    lambda kids: ('return', 'return {}'),
    FunctionDef:
    lambda fdef: ('def', fundef_desc(fdef)),
    arguments:
    lambda args: ('()', '({})'.format(', '.join(
        (arg.arg for ar in args.args)))),
    arg: lambda arg: ('arg', arg.arg),
    Module:
    lambda mod: ('module', '?'),
    BinOp: lambda bo: ('BO', (desc(bo.left), desc(bo.op), desc(bo.right))),
    Num: lambda num: (type(num.n), num.n),
    Name: lambda name: ('symbol', name.id),
    Expr: lambda exp: ('ex', desc(exp.value)[1]),  # RECUR!
})

# Unpack values / condition
subnodes = callbytype({
    Str: lambda str_: ((str_.s, ), ()),
    Add: lambda add_: (('+', ), ()),
    Sub: lambda add_: (('-', ), ()),
    Return: lambda ret: subnodes(ret.value),
    FunctionDef: lambda fdef: (fdef.body, fdef.args.args),
    arguments: lambda args: (args.args, ()),
    Expr: lambda expr: ((expr.value, ), ()),
    BinOp: lambda bo: ((bo.left, bo.op, bo.right), ()),
    Num: lambda num: ((num.n, ), ()),
    Name: lambda name: ((name.id, ), ()),
    arg: lambda arg_: ((arg_.arg, ), ()),
})
