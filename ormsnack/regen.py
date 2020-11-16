# yapf

import ast
from kingston.match import Matcher, TypeMatcher  # type: ignore[attr-defined]
from kingston.decl import box
from typing import Any, Collection, List, Dict
from types import CodeType, FunctionType, ModuleType
import traceback
from functools import singledispatch

from ormsnack import make, mappings

compiler: Matcher[ast.AST, CodeType] = TypeMatcher()

fix = ast.fix_missing_locations


def autoname(node: ast.AST, idx: int) -> str:
    return f"{node.__class__.__name__}_{idx}"


@compiler.case
def compile_module(module: ast.Module) -> CodeType:
    back, *_ = traceback.extract_stack()
    if any(mappings.countnames(node) == 0 for node in module.body):
        for idx, node in enumerate(module.body):
            if mappings.countnames(node) == 0:
                name = autoname(node, idx)
                assigned = make.make(name, node)
                module.body[idx] = fix(assigned)

    return compile(module, back.filename, 'exec')


@compiler.case
def compile_lambda(lambda_: ast.Lambda) -> CodeType:
    back, *_ = traceback.extract_stack()
    return compile(ast.Expression(body=lambda_), back.filename, 'eval')


@compiler.case
def compile_assign(assign: ast.Assign) -> CodeType:
    back, *_ = traceback.extract_stack()
    return compiler(make.module([fix(assign)]))


@compiler.case
def compile_interactive(inter: ast.Interactive) -> CodeType:
    back, *_ = traceback.extract_stack()
    return compile(inter, back.filename, 'single')


@singledispatch
def run(what: Any) -> dict:
    raise NotImplementedError(f"regen.run() not implemented for {type(what)}")


@run.register(CodeType)
def run_code(code: CodeType) -> Dict[str, Any]:
    ns: Dict[str, Any] = {}
    exec(code, globals(), ns)
    return ns


@run.register(ast.AST)
def run_ast(nodes: ast.AST) -> dict:
    if mappings.countnames(nodes):
        return run(compiler(nodes))
    else:
        code = compiler(make.module([*box(nodes)]))
        return run(compiler(make.module([*box(nodes)])))
