# yapf

import ast
from kingston.match import Matcher, TypeMatcher  # type: ignore[attr-defined]
from funcy import flow

from typing import Any, Collection, List, Dict

from . import tree

from mock import MagicMock as Mock


def copy(fromnode: ast.AST, after: ast.AST, grandparent: ast.AST) -> ast.AST:
    """
    Copy a node and place it after another node.
    """


def adopt(fromnode: ast.AST, path: str, fromline: int) -> ast.AST:
    """Change an AST fragment to be placed in another file, starting at a
    specified line number.

    """


def new_module_from(module: Any):
    pass


class Blueprint(Mock):
    """Documentation for Blueprint

    """
    def __init__(self, *args, **kwargs):
        super(Blueprint, self).__init__(*args, **kwargs)
        self.__inherits__ = []

    def inherit(self, What):
        self.__inherits__.append(What)

    @flow.collecting
    def create_methods(self):
        for call in self.method_calls:
            callsrc = str(call)
            parts = re.split(r'(\w*)', callsrc)
            yield re.match(r'call\.(\w*?)\(', callsrc).groups()[0]


class ClassicTemplate(object):
    """Documentation for {Classname}

    """
    def __init__(self, *args, **kwargs):
        super(ClassicTemplate, self).__init__(*args, **kwargs)
        self.args = args


def classic(live: Any) -> ast.AST:
    """
    Interpolate a 'classic class' from a live object.
    """
    # 1. Get all attrs from ``live``.
    # 2. Get the ast from a 'classic' class template.


def template(thing: Any, reps: dict) -> ast.AST:
    return tree.getast(thing)
