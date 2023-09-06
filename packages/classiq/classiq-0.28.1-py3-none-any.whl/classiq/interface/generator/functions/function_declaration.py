import abc
import keyword
from typing import Dict

import pydantic
from pydantic.main import BaseModel

from classiq.interface.generator.functions.classical_type import ConcreteClassicalType


class FunctionDeclaration(BaseModel, abc.ABC):
    """
    Facilitates the creation of a common function interface object.
    """

    name: str = pydantic.Field(description="The name of the function")

    param_decls: Dict[str, ConcreteClassicalType] = pydantic.Field(
        description="The expected interface of the functions parameters",
        default_factory=dict,
    )

    class Config:
        extra = pydantic.Extra.forbid


class OperandDeclaration(FunctionDeclaration):
    is_list: bool = pydantic.Field(
        description="Indicate whether the operand expects an unnamed list of lambdas",
        default=False,
    )


FunctionDeclaration.update_forward_refs()


def mangle_keyword(name: str) -> str:
    if keyword.iskeyword(name):
        name = f"{name}_"
    return name


def unmangle_keyword(name: str) -> str:
    assert name
    if name[-1] == "_" and keyword.iskeyword(name[:-1]):
        name = name[:-1]
    return name
