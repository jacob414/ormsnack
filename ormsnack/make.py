# yapf

import ast
from kingston.match import Matcher, TypeMatcher, ValueMatcher, Miss
from typing import Any, Collection, List, Mapping, Callable
from types import CodeType, FunctionType, ModuleType
import traceback

fix = ast.fix_missing_locations


def _node_factory(Cls, parent=None, **kwargs):
    lno, cno = 0, 0
    if parent:
        lno = getattr(parent, 'lineno', 0)
        cno = getattr(parent, 'coll_offset', 0)
    node = Cls(**kwargs)
    node.lineno = lno
    node.coll_offset = cno
    return node


N = _node_factory


def module(nodes: Collection,
           type_ignores: List = [],
           lineno: int = 0,
           col_offset: int = 0) -> ast.Module:
    "Does module"
    mod = N(ast.Module, body=list(nodes), type_ignores=type_ignores)
    mod.lineno = lineno
    mod.col_offset = col_offset
    return mod


assign: Matcher[Any, ast.Assign] = TypeMatcher()


def arith(Op: ast.AST) -> Callable:
    "Returns a function that generates a basic arithmetic operation"

    def assemble(left: Any, _: Any, right: Any) -> ast.BinOp:
        return ast.BinOp(left=ast.Name(id=left), op=Op(), right=make(right))

    return assemble


def rescue(mystery: Any) -> ast.AST:
    if isinstance(mystery, ast.AST):
        return mystery
    else:
        raise TypeError(f"Value {mystery!r} can't be converted to AST node")


makeb: Matcher[Any, ast.AST] = ValueMatcher({
    (Any, '+', Any): arith(ast.Add),
    (Any, '-', Any): arith(ast.Sub),
    (Any, '*', Any): arith(ast.Mult),
    (Any, '/', Any): arith(ast.Div),
    (Any, '=', Any): assign
})

make: Matcher[Any, ast.AST] = TypeMatcher({
    int: lambda v: N(ast.Num, n=v),
    str: lambda s: N(ast.Str, s=s),
    tuple: makeb,
    dict: assign,
    (str, Any): assign,
    Miss: rescue
})

opmake: Matcher[Any, ast.AST] = ValueMatcher({
    ('+', ):
    lambda: N(ast.Add),
    ('-', ):
    lambda: N(ast.Sub),
    ('*', ):
    lambda: N(ast.Mult),
    ('=', ): (lambda name, exp: assign(name, exp))
})


@assign.case
def name_value(name: str, value: Any) -> ast.Assign:
    return fix(
        N(ast.Assign,
          targets=[N(ast.Name, id=name, ctx=N(ast.Store))],
          value=make(value)))


@assign.case
def mapping(**kwargs: Mapping[str, Any]) -> ast.Assign:
    return N(ast.Interactive,
             body=[assign(name, val) for (name, val) in kwargs.items()])


@assign.case
def _dict(env: dict) -> ast.Assign:
    return assign(**env)
