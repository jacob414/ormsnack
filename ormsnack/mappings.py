# yapf

import ast
from dataclasses import dataclass
from typing import Any, Callable, Collection, Iterable, Optional, Union, cast

from .desc import (AstAttrGetter, AstAttrSetter, ExprGetter, NodeDesc,
                   NodeState, PrimOrDesc, descender, nodedisp)
from kingston import lang, match

StateFn = Callable[[ast.AST], NodeState]

# XXX note type: ignore comments below. They relate to this:
#  https://github.com/python/mypy/issues/2852 ,
#  https://github.com/python/mypy/issues/7250 ,
#  https://gitter.im/python/mypy?at=5a5479ffba39a53f1af2f4c0,
#  https://github.com/samuelcolvin/pydantic/issues/781,
#  https://github.com/python/mypy/issues/4290
#
# As far as I've been able to read, this isn't what happens and have
# been fixed, but in my setup I have never been able to get it to work
# properly. If anyone can run the below code under mypy without the
# type ignores, I'd be very happy to try their solution.
desc: nodedisp = nodedisp({
    # XXX irregularity:
    ast.BinOp:
    lambda bo: [desc(bo.left), desc(bo.op),
                desc(bo.right)],  # XXX idea: define special type?
    # XXX irregularity:
    ast.Expr:
    lambda expr: desc(expr.value),
    ast.If:
    lambda iff: NodeDesc(lambda cur=iff: NodeState(full=cur,
                                                   spec='if',
                                                   ident='if',
                                                   value=
                                                   [desc(n) for n in cur.body],
                                                   expr=cur.test),
                         'body'),  # type: ignore
    ast.Call:
    lambda call: NodeDesc(lambda cur=call: NodeState(full=cur,
                                                     spec=
                                                     f'call/{cur.func.id}',
                                                     ident=cur.func.id,
                                                     value=cur.func,
                                                     expr=()),
                          'func'),  # type: ignore
    ast.FunctionDef:
    lambda fdef: NodeDesc(lambda cur=fdef: NodeState(
        full=cur,
        spec='def',
        ident=cur.name,
        value=[desc(child) for child in cur.body],
        expr=cur.args),
                          'body'),  # type: ignore
    ast.arguments:
    lambda args: NodeDesc(lambda cur=args: NodeState(
        full=cur,
        spec='args',
        ident='({})'.format(','.join(arg.arg for arg in args.args)),
        value=cur.args,
        expr=()),
                          'args'),  # type: ignore
    ast.arg:
    lambda arg: NodeDesc(lambda cur=arg: NodeState(
        full=cur, spec='arg', ident=cur.arg, value=cur.arg, expr=()),
                         'arg'),  # type: ignore
    ast.Compare:
    lambda cmp_: NodeDesc(lambda cur=cmp_: NodeState(
        full=cur,
        spec='cmp',
        ident='cmp',
        value=descender([cur.left, *cur.comparators]),
        expr=()),
                          'comparators'),  # type: ignore
    ast.Str:
    lambda s: NodeDesc(lambda cur=s: NodeState(
        full=cur, spec=str, ident=s.s, value=s.s, expr=()),
                       's'),  # type: ignore
    ast.Num:
    lambda num: NodeDesc(lambda cur=num: NodeState(
        full=cur, spec=type(cur.n), ident=str(cur.n), value=cur.n, expr=()),
                         'n'),  # type: ignore
    ast.Add:
    lambda a: NodeDesc(lambda cur=a: NodeState(
        full=cur, spec='op/+', ident='+', value='+', expr=()),
                       'op'),  # type: ignore
    ast.Return:
    lambda ret: NodeDesc(lambda cur=ret: NodeState(full=cur,
                                                   spec='return',
                                                   ident='return',
                                                   value=desc(cur.value),
                                                   expr=cur.value),
                         'value'),  # type: ignore
    ast.Constant:
    lambda con: NodeDesc(lambda cur=con: NodeState(full=cur,
                                                   spec=type(cur.value),
                                                   ident=str(cur.value),
                                                   value=cur.value,
                                                   expr=()),
                         'value'),  # type: ignore
    ast.Name:
    lambda name: NodeDesc(lambda cur=name: NodeState(
        full=cur, spec=cur.id, ident=cur.id, value=cur.id, expr=()),
                          'id'),  # type: ignore
})

p2a: match.Matcher[Any, ast.AST] = match.TypeMatcher({
    str:
    lambda v: ast.Name(id=v),
})
