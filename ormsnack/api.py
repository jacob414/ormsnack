# yapf
from ormsnack import tree
from typing import Any, List, Iterable, Callable, Union, Optional
import functools
import funcy  # type: ignore
from kingston import lang  # type: ignore
import ast
import operator as ops
from . import mappings
import re
import itertools
from abc import ABC, abstractmethod
from .simpler import Node, Statement, Expr, Symbol, Literal, simplify, nodes

expand = ops.attrgetter('linear')

MatchStr = Callable[[str], bool]
MatchNode = Callable[[Node], bool]


def scanner(value: Any, matches: MatchStr) -> MatchNode:
    "Does named"

    textual = str(value)

    @functools.wraps(matches)
    def seek(node: Node) -> bool:
        "Does match"
        return matches(node.ident)

    return seek


class ASTQuery(lang.ComposePiping, lang.LogicPiping):
    def __init__(self, snack=None):
        super().__init__(kind='pipe', format=bool)
        self.snack = snack

    def __call__(self, *params, **opts):
        return super(lang.LogicPiping, self).__call__(*params, **opts)

    def __eq__(self, exact) -> 'ASTQuery':
        "Bitwise OR as simple function composition"
        top = self.rep
        self.logically((lambda node: node.ident == exact), True)
        self.run_q(top)
        return self

    def __lshift__(self, value: Any) -> 'ASTQuery':
        "Filter nodes by parameter `name`, exact matching"

        textual = str(value)

        def exact(value: Any) -> bool:
            # print(f'{value} == {textual} {value == textual}?')
            return str(value) == textual

        self.logically(scanner(value, exact), True)
        return self

    def __matmul__(self, pattern: str) -> 'ASTQuery':
        "Filter nodes by RegExp pattern `pattern`"
        rx = re.compile(pattern)

        def rx_node_fn(node: Node) -> bool:
            "Does rx_node_fn"
            return bool(rx.match(node.ident))

        self.logically(rx_node_fn, True)
        return self

    @property
    def linear(self):
        return self.rep.linear

    def run_q(self, top: Node) -> List:
        "Perform a query on AST tree."
        # self.zero()
        pfunc = super(lang.LogicPiping, self).__call__
        all_ = tuple(funcy.flatten((sub.linear for sub in top.linear)))
        res = [node for node in all_ if pfunc(node)]
        return res

    def zero(self):
        ops_ = self.ops
        self.reset()
        self.ops = ops_
        self.res = ()


class Snack(ASTQuery):
    def __init__(self, tr):
        super().__init__(snack=self)
        self.org = tr
        self.simpler = None
        self.res = ()

    @property
    def rep(self):
        "Simplify tree"
        if self.simpler is None:
            org = self.org
            simpler = simplify(org)
            self.simpler = simpler
        return self.simpler

    def __call__(self, *params, **opts):
        root = self.rep
        x = self.run_q(root)
        return funcy.compact(self.truthy)

    def _run_cur(self) -> ASTQuery:
        "Runs current Query."
        root = self.rep
        if len(self.ops) > 0:
            self.run_q(root)  # nb: next, to initiate generator
            return funcy.compact(self.truthy)
        else:
            raise ValueError("INTERNAL: Snack._run_cur() called without query "
                             "terms specified")

    @property
    def cur(self) -> Iterable[Node]:
        "Does run"
        if len(self.ops) > 0:
            self.res = self._run_cur()
            return self.res
        else:
            return self.rep

    def __getattribute__(self, name: str) -> Any:
        try:
            return super(ASTQuery, self).__getattribute__(name)
        except AttributeError:
            root = self.rep
            rq = self.run_q
            self << name
            res = rq(root)
            return nodes(res)

    def __getitem__(self, idx: Any) -> Iterable[Node]:
        "Indexed access"
        if not self.res and self.ops:
            from_ = self._run_cur()
        else:
            from_ = self.rep.children
        return from_[idx]

    def __len__(self) -> int:
        "Length of tree or last query result."
        if not self.res:
            self.res = self.cur
        return len(self.res)

    @property
    def q(self) -> 'Snack':
        "Does q"
        self.query = ASTQuery(self)
        return self


def snacka(ob: Any) -> Snack:
    "Does snacka"
    return Snack(tree.getast(ob))
