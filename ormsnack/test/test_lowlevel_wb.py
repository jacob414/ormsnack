# yapf
import pytest
import os
from ormsnack import lowlevel as low
from kingston.testing import fixture
from altered import base, E

pytestmark = pytest.mark.wbox


def func():
    pass


class Cls:
    pass


@fixture.params(
    "obj, expected",
    ('foo', __file__),
    (func, __file__),
    (1, __file__),
    (low, low.__file__),
    (low.select, low.__file__),
    (os.path, os.path.__file__),
    (Cls, __file__),
    (Cls(), __file__),
    (E(a=1), base.__file__),
)
def test_sourcefile_known_paths(obj, expected) -> None:
    "Should sourcefile"
    assert low.sourcefile(obj) == expected
