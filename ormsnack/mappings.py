# yapf

from _ast import *
import ast
from micropy import lang
from typing import Any, Iterable, Callable, Optional, Union, Collection, cast
from dataclasses import dataclass
import funcy

from . import desc as desc_module

from .desc import (NodeDesc, nodedisp, AstAttrGetter, AstAttrSetter,
                   ExprGetter, PrimOrDesc, astattrgetter, astattrsetter,
                   descender)

N = NodeDesc

desc: nodedisp = nodedisp({  # hm? starting out by just descending into it..
    # XXX irregularity:
    BinOp:
    lambda bo: [desc(bo.left), desc(bo.op),
                desc(bo.right)],
    Expr:
    lambda expr: desc(expr.value),
    If:
    lambda iff: N(full=iff,
                  spec='if',
                  ident='if',
                  get=lambda: [desc(n) for n in iff.body],
                  set=astattrsetter(iff, 'body'),
                  getexpr=astattrgetter(iff, 'test')),
    Call:
    lambda call: N(full=call,
                   spec=f'call/{call.func.id}',
                   ident=call.func.id,
                   get=astattrgetter(call, 'func'),
                   set=astattrsetter(call, 'func')),
    FunctionDef:
    lambda fdef: N(full=fdef,
                   spec=f'def',
                   ident=fdef.name,
                   get=astattrgetter(fdef, 'body'),
                   set=astattrsetter(fdef, 'body'),
                   getexpr=astattrgetter(fdef, 'args')),
    arguments:
    lambda args: N(full=args,
                   spec='args',
                   ident='({})'.format(','.join(arg.arg for arg in args.args)),
                   get=astattrgetter(args, 'args'),
                   set=astattrsetter(args, 'args')),
    arg:
    lambda arg: N(
        full=arg,
        spec='arg',
        ident=arg.arg,
        get=astattrgetter(arg, 'arg'),
        set=astattrsetter(arg, 'arg'),
    ),
    Compare:
    lambda cmp_: N(full=cmp_,
                   spec='cmp',
                   ident='cmp',
                   get=descender([cmp_.left, *cmp_.comparators]),
                   set=astattrsetter(cmp_, 'comparators')),
    Str:
    lambda s: N(full=s,
                spec=str,
                ident=s.s,
                get=astattrgetter(s, 's'),
                set=astattrsetter(s, 's')),
    Num:
    lambda num: N(full=num,
                  spec=type(num.n),
                  ident=str(num.n),
                  get=astattrgetter(num, 'n'),
                  set=astattrsetter(num, 'n')),
    Add:
    lambda a: N(full=a,
                spec='op',
                ident='+',
                get=lambda: '+',
                set=astattrsetter(a, 'op')),
    Return:
    lambda ret: N(full=ret,
                  spec='return',
                  ident='return',
                  getexpr=astattrgetter(ret, 'value'),
                  get=astattrgetter(ret, 'value'),
                  set=astattrsetter(ret, 'value')),
    Name:
    lambda name: N(full=name,
                   spec=name.id,
                   ident=name.id,
                   get=astattrgetter(name, 'id'),
                   set=astattrsetter(name, 'id'))
})

desc_module.desc = desc
