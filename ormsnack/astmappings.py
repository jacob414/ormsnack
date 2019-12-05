# yapf

from _ast import *
from micropy.lang import typemapx  # type: ignore

# Unpack values / condition
subnodes = typemapx({
    Str: lambda str_: ((str_.s, ), ()),
    Add: lambda add_: (('+', ), ()),
    Sub: lambda add_: (('-', ), ()),
    Return: lambda ret: ((ret.value, ), ()),
    FunctionDef: lambda fdef: (fdef.body, fdef.args.args),
    arguments: lambda args: (args.args, ()),
    Expr: lambda expr: ((expr.value, ), ()),
    BinOp: lambda bo: ((bo.left, bo.op, bo.right), ()),
    Num: lambda num: ((num.n, ), ()),
    Name: lambda name: ((name.id, ), ()),
    arg: lambda arg_: ((arg_.arg, ), ()),
})

# Express as code / for human
desc = typemapx({
    Str: ('str', lambda s: ("'{}'".format(s.s))),
    Add: ('+', lambda _: '+'),
    Sub: ('-', lambda _: '-'),
    Return: ('return', lambda kids: 'return {}'.format(' '.join(
        (kid.codeish for kid in kids)))),
    FunctionDef:
    ('def',
     lambda n: '{}({})'.format(n.name,
                               (n.name, ', '.join(el.desc
                                                  for el in n.children)))),
    arguments: ('()', lambda args: '({})'.format(', '.join(
        (arg.codeish for ar in args)))),
    Module: ('module', lambda mod: '?'),
})

# Express as code / for human
desc = typemapx({
    Str:
    lambda s: "'{}'".format(s.s),
    Add:
    lambda _: '+',
    Sub:
    lambda _: '-',
    Return:
    lambda kids: 'return {}'.format('XXX'),
    FunctionDef:
    lambda n: '{}({})'.format(n.name, 'XXX'),
    arguments:
    lambda args: '({})'.format(', '.join((arg.codeish for ar in args))),
    Module:
    lambda mod: '?',
})
