# yapf

import ast
import inspect
from pprint import pformat
from typing import Any, Mapping, Tuple, Optional, Union
import types
from functools import singledispatch
import astunparse


def code(node: ast.AST) -> str:  # pragma: nocov
    "Does pp"
    code = astunparse.unparse(node)
    return code


def getast(obj: Any, name: str = None) -> ast.AST:
    """Grab AST of `obj`. (Uses inspect.getsource() behind the scenes).

    Highly simplified version of what's can be found in other
    librearies (e.g. astor, patterns).

    """
    if name is None:
        name = getattr(obj, '__name__', '?')
    try:
        source = inspect.getsource(obj)
    except TypeError:
        # Try to handle an object that inspect.getsource() couldn't handle.
        # XXX first sketch, ind of weak, let's see how long it holds..
        source = pformat(obj)
        return ast.Module(body=ast.parse(source).body)

    full = ast.parse(source)
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


def compile_ast(tree_: ast.AST, filename: str = None,
                topsym: str = 'xyz') -> types.CodeType:
    "Compiles `tree_`, returning recompiled ast (if `compile()` succeeds"
    if filename is None:
        filename = '<ormsnack.tree.eval_ast:?>'
    target = ast.Interactive(body=[assign(**{topsym: tree_})])
    try:
        return compile(target, filename, 'single')
    except TypeError:
        target = ast.Module(body=[tree_])
        return compile(target, filename, 'exec')
    except SyntaxError:
        msg = "Syntax error when trying to compile:\n{astunparse.unparse(target)}"
        raise SyntaxError(msg)


ASTOrCode = Union[ast.AST, types.CodeType]


def maybe_compile(target: ASTOrCode, filename: str = None) -> types.CodeType:
    "Does maybe_compile"
    if isinstance(target, ast.AST):
        compiled = compile_ast(target, filename)
        return compiled
    else:
        return target


def run_all(target: ASTOrCode, **env: Tuple[str, Any]) -> Mapping[str, Any]:
    "Does exec"
    ns: Mapping[str, Any] = dict(env)
    exec(maybe_compile(target), globals(), ns)
    return ns


def run_sym(target: ASTOrCode, symname: str) -> Any:
    "Does run_sym"
    full = run_all(target)
    return full[symname]


def run_ast(topnode: ast.AST,
            name: Optional[str] = None,
            **env: Tuple[str, Any]) -> Union[Any, Mapping[str, Any]]:
    "Full roundtrip execute from an AST node as parameter"
    code = compile_ast(topnode)
    full = run_all(code, **env)
    return full[name] if name else full
