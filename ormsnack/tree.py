# yapf

import ast
import inspect
from pprint import pformat
from typing import Any, Mapping
import types


def getast(obj: Any, name: str = None) -> Any:
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
        next(node for node in ast.parse(source).body if node.name == name)
    ])


def compile_ast(tree_: ast.AST, filename: str = None) -> types.CodeType:
    "Compiles `tree_`, returning recompiled ast (if `compile()` succeeds"
    if filename is None:
        filename = '<ormsnack.tree.eval_ast:?>'
    return compile(tree_, filename, 'exec')


def exec_all(recompiled: types.CodeType) -> Mapping[str, Any]:
    "Does exec"
    ns: Mapping[str, Any] = {}
    exec(recompiled, globals(), ns)
    return ns


def exec_sym(recompiled: types.CodeType, symname: str) -> Any:
    "Does exec_sym"
    full = exec_all(recompiled)
    return full[symname]
