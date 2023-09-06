from enum import IntEnum
from typing import List, Optional, Union

import pydantic
from pydantic import BaseModel

from classiq.interface.generator.generated_circuit_data import GeneratedFunction


class IDEDataQubit(BaseModel):
    id: int
    numChildren: Optional[int]


class IDEQubitDef(BaseModel):
    qId: int


class RegisterType(IntEnum):
    QUBIT = 0
    CLASSICAL = 1


class IDEClassicalBitDef(BaseModel):
    type: RegisterType
    qId: int
    cId: int


class DataAttributes(BaseModel):
    tooltip: Optional[GeneratedFunction] = None
    controlStates: str = ""


class ConditionalRender(IntEnum):
    ALWAYS = 0
    ON_ZERO = 1
    ON_ONE = 2
    AS_GROUP = 3


class IDEDataOperation(BaseModel):
    gate: str
    displayName: str
    children: List["IDEDataOperation"]

    displayArgs: str = ""
    targets: Union[List[IDEQubitDef], List[IDEClassicalBitDef]] = pydantic.Field(
        default_factory=list
    )
    controls: List[IDEQubitDef] = list()
    dataAttributes: DataAttributes = pydantic.Field(default_factory=DataAttributes)
    isControlled: bool = False
    isMeasurement: bool = False
    isConditional: bool = False
    conditional_render: Optional[ConditionalRender] = None


class IDEDataProperties(BaseModel):
    color: Optional[str]
    rightLabel: Optional[str]
    leftLabel: Optional[str]


class RegisterData(BaseModel):
    segmentIds: List[str]
    properties: IDEDataProperties
    registerId: str


class InterfaceSegmentData(BaseModel):
    segmentId: str
    properties: IDEDataProperties


class IDEData(BaseModel):
    qubits: List[IDEDataQubit]
    operations: List[IDEDataOperation]
    register_data: List[RegisterData]
    segment_data: List[InterfaceSegmentData]
