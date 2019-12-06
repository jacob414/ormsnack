# yapf

from _ast import *
from micropy.lang import callbytype  # type: ignore

# Unpack values / condition
subnodes = callbytype({
    Str: lambda str_: ((str_.s, ), ()),
    Add: lambda add_: (('+', ), ()),
    Sub: lambda add_: (('-', ), ()),
    Return: lambda ret: ((ret.value, ), (ret.value, )),
    FunctionDef: lambda fdef: (fdef.body, fdef.args.args),
    arguments: lambda args: (args.args, ()),
    Expr: lambda expr: ((expr.value, ), ()),
    BinOp: lambda bo: ((bo.left, bo.op, bo.right), ()),
    Num: lambda num: ((num.n, ), ()),
    Name: lambda name: ((name.id, ), ()),
    arg: lambda arg_: ((arg_.arg, ), ()),
})

# Codelike names
codename = callbytype({
    Str: lambda str_: 'str',
    Add: lambda add_: '+',
    Sub: lambda add_: '-',
    Return: lambda ret: 'return',
    FunctionDef: lambda fdef: 'def',
    arguments: lambda args: '()',
    Expr: lambda expr: 'XXX expr?',
    BinOp: lambda bo: 'XXX binop?',
    Num: lambda num: repr(num.n),
    Name: lambda name: name.id,
    arg: lambda arg_: repr(arg_.arg),
})

# Express as code / for human
codename = callbytype({
    Str: lambda s: "'{}'".format(s.s),
    Add: lambda _: '+',
    Sub: lambda _: '-',
    Return: lambda kids: 'return',
    FunctionDef: lambda fdef: f'def {fdef.name}',
    arguments: lambda args: '(XXX)',
    Module: lambda mod: 'XXX (module)',
})

# Express as code / for human
desc = callbytype({
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
desc = callbytype({
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
