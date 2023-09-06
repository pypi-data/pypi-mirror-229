from typing import Any, Generic, TypeVar

import sympy
from sympy import Symbol

if sympy.__version__ == "1.9":
    from sympy.core.compatibility import NotIterable
else:
    from sympy.utilities.iterables import NotIterable

_T = TypeVar("_T")


class QParam(Symbol, NotIterable, Generic[_T]):
    def __getitem__(self, key: Any) -> "QParam":
        return QParam(name=f"{str(self)}[{str(key)}]")
