# yapf

import ast
import inspect
import types
from functools import singledispatch
from pprint import pformat
from typing import Any, Mapping, Optional, Tuple, Union

from . import lowlevel as low
import astor


def code(node: ast.AST) -> str:  # pragma: nocov
    "Return Python code for an AST node (exact code generator lib may vary)"
    code = astor.to_source(node)
    return code


def getast(obj: Any, name: str = None) -> ast.AST:
    """Grab AST of `obj`. (Uses inspect.getsource() behind the scenes).

    Highly simplified version of what's can be found in other
    librearies (e.g. astor, patterns).

    """
    if name is None:
        name = getattr(obj, '__name__', '?')
    try:
        src = inspect.getsource(obj)
    except TypeError:
        # Try to handle an object that inspect.getsource() couldn't handle.
        # XXX first sketch, ind of weak, let's see how long it holds..
        src = pformat(obj)
        return ast.Module(body=ast.parse(src).body)

    if 'lambda' in src:
        wlam = '(' + src[src.index('lambda'):]
        full = None
        while full is None:
            # Work backwards from the 'lambda' keyword, what can be
            # parsed with ast.parse() first is the AST of the lambda.
            try:
                full = ast.parse(wlam)
            except SyntaxError:
                wlam = wlam[:-1]

            lnode = next(node for node in ast.walk(full)
                         if node.__class__ == ast.Lambda)
            return ast.Module(body=[lnode], types_ignore=[])
    else:
        full = ast.parse(src)

    cands = [node for node in full.body if getattr(node, 'name', 'X') == name]

    if len(cands) == 1:
        return cands[0]
    else:
        return full.body


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

    target = ast.Interactive(body=[assign(**{topsym: tree_})])
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
