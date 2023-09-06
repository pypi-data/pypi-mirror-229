from typing import List, Literal

from classiq.pyqmod.qmod_parameter import QParam
from classiq.pyqmod.qmod_variable import InputQVar, OutputQVar, QVar
from classiq.pyqmod.quantum_callable import QCallable
from classiq.pyqmod.quantum_function import ExternalQFunc


@ExternalQFunc
def H(
    target: QVar[Literal[1]],
):
    pass


@ExternalQFunc
def X(
    target: QVar[Literal[1]],
):
    pass


@ExternalQFunc
def Y(
    target: QVar[Literal[1]],
):
    pass


@ExternalQFunc
def Z(
    target: QVar[Literal[1]],
):
    pass


@ExternalQFunc
def I(
    target: QVar[Literal[1]],
):
    pass


@ExternalQFunc
def S(
    target: QVar[Literal[1]],
):
    pass


@ExternalQFunc
def T(
    target: QVar[Literal[1]],
):
    pass


@ExternalQFunc
def SDG(
    target: QVar[Literal[1]],
):
    pass


@ExternalQFunc
def TDG(
    target: QVar[Literal[1]],
):
    pass


@ExternalQFunc
def PHASE(
    theta: QParam[float],
    target: QVar[Literal[1]],
):
    pass


@ExternalQFunc
def RX(
    theta: QParam[float],
    target: QVar[Literal[1]],
):
    pass


@ExternalQFunc
def RY(
    theta: QParam[float],
    target: QVar[Literal[1]],
):
    pass


@ExternalQFunc
def RZ(
    theta: QParam[float],
    target: QVar[Literal[1]],
):
    pass


@ExternalQFunc
def RXX(
    theta: QParam[float],
    target: QVar[Literal[2]],
):
    pass


@ExternalQFunc
def RYY(
    theta: QParam[float],
    target: QVar[Literal[2]],
):
    pass


@ExternalQFunc
def RZZ(
    theta: QParam[float],
    target: QVar[Literal[2]],
):
    pass


@ExternalQFunc
def CH(
    target: QVar[Literal[1]],
    control: QVar[Literal[1]],
):
    pass


@ExternalQFunc
def CX(
    target: QVar[Literal[1]],
    control: QVar[Literal[1]],
):
    pass


@ExternalQFunc
def CY(
    target: QVar[Literal[1]],
    control: QVar[Literal[1]],
):
    pass


@ExternalQFunc
def CZ(
    target: QVar[Literal[1]],
    control: QVar[Literal[1]],
):
    pass


@ExternalQFunc
def CRX(
    theta: QParam[float],
    target: QVar[Literal[1]],
    control: QVar[Literal[1]],
):
    pass


@ExternalQFunc
def CRY(
    theta: QParam[float],
    target: QVar[Literal[1]],
    control: QVar[Literal[1]],
):
    pass


@ExternalQFunc
def CRZ(
    theta: QParam[float],
    target: QVar[Literal[1]],
    control: QVar[Literal[1]],
):
    pass


@ExternalQFunc
def CPHASE(
    theta: QParam[float],
    target: QVar[Literal[1]],
    control: QVar[Literal[1]],
):
    pass


@ExternalQFunc
def SWAP(
    qbit0: QVar[Literal[1]],
    qbit1: QVar[Literal[1]],
):
    pass


@ExternalQFunc
def IDENTITY(
    target: QVar,
):
    pass


@ExternalQFunc
def prepare_state(
    probabilities: QParam[List[float]],
    bound: QParam[float],
    out: OutputQVar[Literal["log(len(probabilities), 2)"]],
):
    pass


@ExternalQFunc
def add(
    left: InputQVar,
    right: InputQVar,
    result: OutputQVar[Literal["Max(len(left), len(right)) + 1"]],
):
    pass


@ExternalQFunc
def U(
    theta: QParam[float],
    phi: QParam[float],
    lam: QParam[float],
    gam: QParam[float],
    target: QVar[Literal[1]],
):
    pass


@ExternalQFunc
def allocate(
    num_qubits: QParam[int],
    out: OutputQVar[Literal["num_qubits"]],
):
    pass


@ExternalQFunc
def repeat(
    count: QParam[int],
    port_size: QParam[int],
    iteration: QCallable[QParam[int], QVar[Literal["port_size"]]],
    qbv: QVar[Literal["port_size"]],
):
    pass


@ExternalQFunc
def invert(
    target_size: QParam[int],
    operand: QCallable[QVar[Literal["target_size"]]],
    target: QVar[Literal["target_size"]],
):
    pass


@ExternalQFunc
def control(
    ctrl_size: QParam[int],
    target_size: QParam[int],
    operand: QCallable[QVar[Literal["target_size"]]],
    ctrl: QVar[Literal["ctrl_size"]],
    target: QVar[Literal["target_size"]],
):
    pass


@ExternalQFunc
def if_(
    condition: QParam[bool],
    port_size: QParam[int],
    then: QCallable[QVar[Literal["port_size"]]],
    else_: QCallable[QVar[Literal["port_size"]]],
    qbv: QVar[Literal["port_size"]],
):
    pass


@ExternalQFunc
def switch(
    selector: QParam[int],
    port_size: QParam[int],
    cases: QCallable[QVar[Literal["port_size"]]],
    qbv: QVar[Literal["port_size"]],
):
    pass


@ExternalQFunc
def join(
    in1: InputQVar,
    in2: InputQVar,
    out: OutputQVar[Literal["len(in1)+len(in2)"]],
):
    pass


@ExternalQFunc
def split(
    out1_size: QParam[int],
    out2_size: QParam[int],
    in_: InputQVar[Literal["out1_size+out2_size"]],
    out1: OutputQVar[Literal["out1_size"]],
    out2: OutputQVar[Literal["out2_size"]],
):
    pass


@ExternalQFunc
def permute(
    port_size: QParam[int],
    functions: QCallable[QVar[Literal["port_size"]]],
    qbv: QVar[Literal["port_size"]],
):
    pass


@ExternalQFunc
def power(
    power: QParam[int],
    port_size: QParam[int],
    operand: QCallable[QVar[Literal["port_size"]]],
    qbv: QVar[Literal["port_size"]],
):
    pass


@ExternalQFunc
def bloch_sphere_feature_map(
    feature_dimension: QParam[int],
    qbv: QVar[Literal["ceiling(feature_dimension/2)"]],
):
    pass


__all__ = [
    "H",
    "X",
    "Y",
    "Z",
    "I",
    "S",
    "T",
    "SDG",
    "TDG",
    "PHASE",
    "RX",
    "RY",
    "RZ",
    "RXX",
    "RYY",
    "RZZ",
    "CH",
    "CX",
    "CY",
    "CZ",
    "CRX",
    "CRY",
    "CRZ",
    "CPHASE",
    "SWAP",
    "IDENTITY",
    "prepare_state",
    "add",
    "U",
    "allocate",
    "repeat",
    "invert",
    "control",
    "if_",
    "switch",
    "join",
    "split",
    "permute",
    "power",
    "bloch_sphere_feature_map",
]
