# yapf

import ast
import inspect
from pprint import pformat
from typing import Any, Mapping, Tuple, Optional, Union
import types
from functools import singledispatch
from . import lowlevel as low
from .mappings import make
from astor import code_gen


def code(node: ast.AST) -> str:  # pragma: nocov
    "Does pp"
    code = code_gen.to_source(node)
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


def compile_ast(tree_: ast.AST,
                filename: str = None,
                topsym: str = 'xyz') -> types.CodeType:
    "Compiles `tree_`, returning recompiled ast (if `compile()` succeeds"
    if filename is None:
        filename = '<ormsnack.tree.eval_ast:?>'

    target = ast.Interactive(body=[make(topsym, tree_)])
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
