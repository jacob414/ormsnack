# yapf

import ast
import inspect
import types
from functools import singledispatch
from pprint import pformat
import funcy as fy  # type: ignore[import]
from typing import Any, Mapping, Optional, Tuple, Union, List, Collection, cast
from types import LambdaType

import astunparse

from . import lowlevel as low

import pyclbr as ob


def code(node: ast.AST) -> str:  # pragma: nocov
    "Does pp"
    code = astunparse.unparse(node)
    return code


def get_short_lambda_source(lambda_: LambdaType) -> str:
    """
    Return source code of a live lambda object.

    :param lambda_: Lambda to get source from.

    :return: Python source of  ``lambda_``.
    :rtype: str
    """
    src, _ = inspect.getsourcelines(lambda_)
    if len(src) > 1:
        raise ValueError(f"Ambigous source lines from lambda {lambda_!r}")
    return src[0].strip()


def extract_lambda(line: str, lambda_: LambdaType) -> ast.Lambda:
    nodes = None
    while nodes is None:
        # Work backwards from the 'lambda' keyword, what can be
        # parsed with ast.parse() first is the AST of the lambda.
        try:
            attempt = f"({line})"
            codeob = compile(attempt, '?', 'eval')
            nodes = ast.parse(attempt)
            if len(codeob.co_code) == len(lambda_.__code__.co_code):
                break
        except SyntaxError:
            pass

        line = line[:-1]

    return cast(ast.Lambda, next(low.select(cast(ast.AST, ast.Lambda), nodes)))


def getast(obj: Any, name: str = None) -> ast.AST:
    """Grab AST of `obj`. (Uses inspect.getsource() behind the scenes).

    Highly simplified version of what's can be found in other
    librearies (e.g. astor, patterns).

    """
    if name is None:
        name = getattr(obj, '__name__', '?')

    if 'lambda' in repr(obj):
        # http://xion.io/post/code/python-get-lambda-code.html
        lambda_ = cast(LambdaType, obj)
        line = get_short_lambda_source(lambda_)
        return extract_lambda(line[line.index('lambda'):], lambda_)

    try:
        source = inspect.getsource(obj)
    except TypeError:
        # Try to handle an object that inspect.getsource() couldn't handle.
        # XXX first sketch, ind of weak, let's see how long it holds..
        src = pformat(obj)
        return module(ast.parse(src).body)

    full = ast.parse(src)

    full = ast.parse(source)
    cands = [node for node in full.body if getattr(node, 'name', 'X') == name]

    if len(cands) == 1:
        return ast.fix_missing_locations(cands[0])
    else:
        return full.body


def module(nodes: Collection,
           type_ignores: List = [],
           lineno: int = 0,
           col_offset: int = 0) -> ast.Module:
    "Does module"
    mod = ast.Module(body=list(nodes), type_ignores=type_ignores)
    mod.lineno = lineno
    mod.col_offset = col_offset
    return mod


def assign(**exprs) -> ast.AST:
    "Does assignp"
    for key, value in exprs.items():
        name = key
        exp = value

    node = ast.Assign(targets=[ast.Name(id=name, ctx=ast.Store())], value=exp)
    return ast.fix_missing_locations(node)


def compile_ast(tree_: ast.AST,
                filename: str = None,
                topsym: str = 'xyz') -> types.CodeType:
    "Compiles `tree_`, returning recompiled ast (if `compile()` succeeds"
    if filename is None:
        filename = '<ormsnack.tree.eval_ast:?>'

    assign_ = assign(**{topsym: tree_})

    target = ast.Interactive(body=[assign_])
    try:
        try:
            return compile(target, filename, 'single')
        except TypeError:
            target = low.module(tree_)
            return compile(target, filename, 'exec')
    except SyntaxError as exc:
        code_ = code(target)
        print(f"Syntax error when compiling AST:\n{code_}")
        raise


ASTOrCode = Union[ast.AST, types.CodeType]


def maybe_compile(target: ASTOrCode,
                  filename: str = None,
                  symname: str = None) -> types.CodeType:
    "Does maybe_compile"
    if isinstance(target, ast.AST):
        if symname is None:
            symname = 'xyz'
        compiled = compile_ast(target, filename, topsym=symname)
        return compiled
    else:
        return target


def run_all(target: ASTOrCode,
            symname: str = None,
            **env: Tuple[str, Any]) -> Mapping[str, Any]:
    "Does exec"
    ns: Mapping[str, Any] = dict(env)
    exec(maybe_compile(target, symname=symname), globals(), ns)
    return ns


def run_sym(target: ASTOrCode, symname: str, **env: Tuple[str, Any]) -> Any:
    "Does run_sym"
    full = run_all(target, symname=symname, **env)
    return full[symname]


def run_ast(topnode: ast.AST,
            name: Optional[str] = None,
            **env: Tuple[str, Any]) -> Union[Any, Mapping[str, Any]]:
    "Full roundtrip execute from an AST node as parameter"
    code = compile_ast(topnode)
    full = run_all(code, **env)
    return full[name] if name else full


def count_nodes(origin:ast.AST):
    return len(tuple(ast.walk(top)))
