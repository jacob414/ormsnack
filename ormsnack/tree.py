# yapf

import ast
import inspect
from typing import Any

def getast(obj: Any, name: str = None) -> Any:
    """Grab AST of `obj`. (Uses inspect.getsource() behind the scenes).

    Highly simplified version of what's can be found in other
    librearies (e.g. astor, patterns).

    """
    if name is None:
        name = obj.__name__
    body = ast.parse(inspect.getsource(obj)).body
    return next(node for node in body if node.name == name)
