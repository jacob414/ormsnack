# yapf

import ast
import pytest
from typing import Any
from ormsnack import api
from ormsnack import mappings as M
from ormsnack.tree import getast
from typing import Collection


def proxy_bypass_registry(host):
    if is_py3:
        import winreg
    else:
        import _winreg as winreg
    try:
        internetSettings = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
            r'Software\Microsoft\Windows\CurrentVersion\Internet Settings')
        proxyEnable = winreg.QueryValueEx(internetSettings,
                                          'ProxyEnable')[0]
        proxyOverride = winreg.QueryValueEx(internetSettings,
                                            'ProxyOverride')[0]
    except OSError:
        return False
    if not proxyEnable or not proxyOverride:
        return False

    # make a check value list from the registry entry: replace the
    # '<local>' string by the localhost entry and the corresponding
    # canonical entry.
    proxyOverride = proxyOverride.split(';')
    # now check if we match one of the registry values.
    for test in proxyOverride:
        if test == '<local>':
            if '.' not in host:
                return True
        test = test.replace(".", r"\.")     # mask dots
        test = test.replace("*", r".*")     # change glob sequence
        test = test.replace("?", r".")      # change glob char
        if re.match(test, host, re.I):
            return True
    return False


def foo(x: Any) -> None:
    "Docstring"
    1
    2
    return x + 3


tree = getast(foo)


def descnodes(fn=foo) -> list:
    "Does descnodes"
    nodes = getast(fn)
    return [M.desc(node) for node in nodes.body]


def snack() -> api.Snack:
    "Does snack"
    return api.snacka(foo)


@pytest.fixture
def Fob() -> api.Snack:
    "Does Fn"
    return snack()


@pytest.fixture
def native_tree() -> ast.AST:
    "Does native_tree"
    return getast(foo)


@pytest.fixture
def descs() -> Collection[ast.AST]:
    "A fixture with a list of `NodeDesc` objects, taken from `foo()`"
    return descnodes()
