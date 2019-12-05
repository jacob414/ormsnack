# yapf

import ast
import inspect
from typing import Any, Mapping
import types


def getast(obj: Any, name: str = None) -> Any:
    """Grab AST of `obj`. (Uses inspect.getsource() behind the scenes).

    Highly simplified version of what's can be found in other
    librearies (e.g. astor, patterns).

    """
    if name is None:
        name = obj.__name__
    body = ast.parse(inspect.getsource(obj)).body
    return ast.Module(body=[next(node for node in body if node.name == name)])


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
