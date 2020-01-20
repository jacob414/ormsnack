# yapf
from ormsnack import tree
from typing import Any, List, Iterable, Callable, Union, Optional
import funcy  # type: ignore
from micropy import lang  # type: ignore
import _ast
import ast
import operator as ops
from . import mappings
import re
import itertools
from abc import ABC, abstractmethod

from .simpler import _Node, Node, Statement, Expr, Symbol, Literal, simplify

MatchFn = Callable[[_Node], bool]
def named(needle: str, matches: Callable) -> MatchFn:
    "Does named"

    def match(node: _Node) -> bool:
        "Does match"
        return matches(node.ident)

    return match


class ASTQuery(lang.ComposePiping, lang.LogicPiping):
    def __init__(self, snack=None):
        super().__init__(kind='pipe', format=bool)
        self.snack = snack

    def __rshift__(self,
                   stepf: Callable[[Any, None, None], Any]) -> 'ASTQuery':
        "Bitwise OR as simple function composition"
        self.logically(stepf, True)
        return self

    def __lshift__(self, name: str) -> 'ASTQuery':
        "Filter nodes by parameter `name`, exact matching"

        def exact(desc: str) -> bool:
            return desc == name

        self.logically(named(name, exact), True)
        return self

    def __matmul__(self, pattern: str) -> 'ASTQuery':
        "Filter nodes by RegExp pattern `pattern`"
        rx = re.compile(pattern)
        self.logically(named(pattern, rx.match), True)
        return self

    def run_q(self, top: Node) -> Iterable:
        "Perform a query on AST tree."
        all_ = [top, *top.children]
        self.res = [node for node in all_ if self(node)]
        return self


class Snack(ASTQuery):
    def __init__(self, tr):
        super().__init__(snack=self)
        self.org = tr
        self.simpler = None

    @property
    def rep(self):
        "Simplify tree"
        if self.simpler is None:
            self.simpler = simplify(self.org)
        return self.simpler

    @property
    def cur(self) -> None:
        "Does run"
        if len(self.ops) > 0:
            top = self.rep
            self.run_q(top)
            return self.res
        else:
            return self.rep

    def __getitem__(self, idx: Any) -> Iterable[Node]:
        "Indexed access"
        now = self.cur
        return now[idx]

    def __len__(self) -> int:
        "Length of tree or last query result."
        return len(self.cur)

    @property
    def q(self) -> 'Snack':
        "Does q"
        self.query = ASTQuery(self)
        return self


def snacka(ob: Any) -> Snack:
    "Does snacka"
    return Snack(tree.getast(ob))
