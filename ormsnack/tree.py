# yapf

import ast
import inspect
from pprint import pformat
from typing import Any, Mapping, Optional, Union
import types
from functools import singledispatch


def getast(obj: Any, name: str = None) -> ast.Module:
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

    return ast.Module(body=[
        next(node for node in ast.parse(source).body
             if getattr(node, 'name', '') == name)
    ])


def assign(name, exp) -> ast.AST:
    "Does assignp"
    node = ast.Assign(targets=[ast.Name(id=name, ctx=ast.Store())], value=exp)
    return ast.fix_missing_locations(node)


def compile_ast(tree_: ast.AST, filename: str = None) -> types.CodeType:
    "Compiles `tree_`, returning recompiled ast (if `compile()` succeeds"
    if filename is None:
        filename = '<ormsnack.tree.eval_ast:?>'
    return compile(tree_, filename, 'exec')


def run_all(recompiled: types.CodeType) -> Mapping[str, Any]:
    "Does exec"
    ns: Mapping[str, Any] = {}
    exec(recompiled, globals(), ns)
    return ns


def run_sym(recompiled: types.CodeType, symname: str) -> Any:
    "Does run_sym"
    full = run_all(recompiled)
    return full[symname]


def run_ast(topnode: ast.AST,
            name: Optional[str] = None) -> Union[Any, Mapping[str, Any]]:
    "Full roundtrip execute from an AST node as parameter"
    code = compile_ast(topnode)
    full = run_all(code)
    return full[name] if name else full
