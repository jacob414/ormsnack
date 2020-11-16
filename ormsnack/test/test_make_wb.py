import pytest  # type: ignore[import]
from kingston.testing import fixture  # type: ignore[import]
from ormsnack import make, regen, mappings
import ast
import types
from ast2json import ast2json as view  # type: ignore[import]

pytestmark = pytest.mark.wbox

@fixture.params("prim, expected",
                (1, {'Constant_0': 1}),
                ('1', {'Constant_0': '1'}),
                ({'a':1, 'b':2}, {'a':1, 'b':2}),
                (('a', 1), {'a':1}),
)
def test_roundtrip(prim, expected) -> None:
    "Should make"
    result = regen.run(make.make(prim))
    assert result == expected
