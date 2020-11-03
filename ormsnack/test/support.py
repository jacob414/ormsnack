import ast2json
from pprint import pformat
import ast

def pp_ast(top:ast.AST) -> None:
    print(pformat(ast2json.ast2json(top)))
