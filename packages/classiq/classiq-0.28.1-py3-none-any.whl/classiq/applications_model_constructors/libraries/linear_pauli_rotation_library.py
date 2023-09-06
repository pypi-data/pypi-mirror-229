from typing import List

from classiq.interface.generator.expressions.expression import Expression
from classiq.interface.generator.functions.classical_type import Pauli, Real
from classiq.interface.generator.functions.port_declaration import (
    PortDeclaration,
    PortDeclarationDirection,
)
from classiq.interface.model.handle_binding import HandleBinding, SlicedHandleBinding
from classiq.interface.model.local_handle import LocalHandle
from classiq.interface.model.native_function_definition import NativeFunctionDefinition
from classiq.interface.model.quantum_function_call import (
    QuantumFunctionCall,
    QuantumLambdaFunction,
)
from classiq.interface.model.quantum_function_declaration import (
    QuantumOperandDeclaration,
)

from classiq import ClassicalList, Integer

LPR_LIBRARY: List[NativeFunctionDefinition] = [
    NativeFunctionDefinition(
        name="single_pauli",
        param_decls={"reg_size": Integer(), "slope": Real(), "offset": Real()},
        port_declarations={
            "x": PortDeclaration(
                name="x",
                size=Expression(expr="reg_size"),
                direction=PortDeclarationDirection.Inout,
            ),
            "q": PortDeclaration(
                name="q",
                size=Expression(expr="1"),
                direction=PortDeclarationDirection.Inout,
            ),
        },
        local_handles=[LocalHandle(name="repeat")],
        operand_declarations={
            "q1_qfunc": QuantumOperandDeclaration(
                name="q1_qfunc",
                param_decls={"theta": Real()},
                port_declarations={
                    "target": PortDeclaration(
                        name="target",
                        direction=PortDeclarationDirection.Inout,
                        size=Expression(expr="1"),
                    )
                },
            )
        },
        body=[
            QuantumFunctionCall(
                function="join",
                inputs={
                    "in1": HandleBinding(name="x"),
                    "in2": HandleBinding(name="q"),
                },
                outputs={"out": HandleBinding(name="repeat")},
            ),
            QuantumFunctionCall(
                function="repeat",
                params={
                    "count": Expression(expr="reg_size"),
                    "port_size": Expression(expr="reg_size + 1"),
                },
                inouts={"qbv": HandleBinding(name="repeat")},
                operands={
                    "iteration": QuantumLambdaFunction(
                        body=[
                            QuantumFunctionCall(
                                function="control",
                                params={
                                    "ctrl_size": Expression(expr="1"),
                                    "target_size": Expression(expr="1"),
                                },
                                inouts={
                                    "ctrl": SlicedHandleBinding(
                                        name="qbv",
                                        start=Expression(expr="index"),
                                        end=Expression(expr="index+1"),
                                    ),
                                    "target": SlicedHandleBinding(
                                        name="qbv",
                                        start=Expression(expr="reg_size"),
                                        end=Expression(expr="reg_size+1"),
                                    ),
                                },
                                operands={
                                    "operand": QuantumLambdaFunction(
                                        body=[
                                            QuantumFunctionCall(
                                                function="q1_qfunc",
                                                params={
                                                    "theta": Expression(
                                                        expr="2**index*slope"
                                                    )
                                                },
                                                inouts={
                                                    "target": HandleBinding(
                                                        name="target"
                                                    )
                                                },
                                            ),
                                        ]
                                    ),
                                },
                            ),
                        ]
                    ),
                },
            ),
            QuantumFunctionCall(
                function="split",
                params={
                    "out1_size": Expression(expr="reg_size"),
                    "out2_size": Expression(expr="1"),
                },
                inputs={"in": HandleBinding(name="repeat")},
                outputs={
                    "out1": HandleBinding(name="x"),
                    "out2": HandleBinding(name="q"),
                },
            ),
            QuantumFunctionCall(
                function="q1_qfunc",
                params={"theta": Expression(expr="offset")},
                inouts={"target": HandleBinding(name="q")},
            ),
        ],
    ),
    NativeFunctionDefinition(
        name="linear_pauli_rotations",
        param_decls={
            "reg_size": Integer(),
            "num_state_qubits": Integer(),
            "bases": ClassicalList(element_type=Pauli()),
            "slopes": ClassicalList(element_type=Real()),
            "offsets": ClassicalList(element_type=Real()),
        },
        port_declarations={
            "x": PortDeclaration(
                name="x",
                size=Expression(expr="reg_size"),
                direction=PortDeclarationDirection.Inout,
            ),
            "q": PortDeclaration(
                name="q",
                size=Expression(expr="num_state_qubits"),
                direction=PortDeclarationDirection.Inout,
            ),
        },
        local_handles=[LocalHandle(name="repeat")],
        body=[
            QuantumFunctionCall(
                function="join",
                inputs={
                    "in1": HandleBinding(name="x"),
                    "in2": HandleBinding(name="q"),
                },
                outputs={"out": HandleBinding(name="repeat")},
            ),
            QuantumFunctionCall(
                function="repeat",
                params={
                    "count": Expression(expr="num_state_qubits"),
                    "port_size": Expression(expr="reg_size + num_state_qubits"),
                },
                inouts={"qbv": HandleBinding(name="repeat")},
                operands={
                    "iteration": QuantumLambdaFunction(
                        body=[
                            QuantumFunctionCall(
                                function="single_pauli",
                                params={
                                    "reg_size": Expression(expr="reg_size"),
                                    "slope": Expression(expr="slopes[index]"),
                                    "offset": Expression(expr="offsets[index]"),
                                },
                                inouts={
                                    "x": SlicedHandleBinding(
                                        name="qbv",
                                        start=Expression(expr="0"),
                                        end=Expression(expr="reg_size"),
                                    ),
                                    "q": SlicedHandleBinding(
                                        name="qbv",
                                        start=Expression(expr="reg_size+index"),
                                        end=Expression(expr="reg_size+index+1"),
                                    ),
                                },
                                operands={
                                    "q1_qfunc": QuantumLambdaFunction(
                                        body=[
                                            QuantumFunctionCall(
                                                function="switch",
                                                params={
                                                    "port_size": Expression(expr="1"),
                                                    "selector": Expression(
                                                        expr="bases[index]"
                                                    ),
                                                },
                                                inouts={
                                                    "qbv": HandleBinding(name="target")
                                                },
                                                operands={
                                                    "cases": [
                                                        QuantumLambdaFunction(
                                                            body=[
                                                                QuantumFunctionCall(
                                                                    function="IDENTITY",
                                                                    inouts={
                                                                        "target": HandleBinding(
                                                                            name="qbv"
                                                                        ),
                                                                    },
                                                                )
                                                            ]
                                                        ),
                                                        QuantumLambdaFunction(
                                                            body=[
                                                                QuantumFunctionCall(
                                                                    function="RX",
                                                                    params={
                                                                        "theta": Expression(
                                                                            expr="theta"
                                                                        ),
                                                                    },
                                                                    inouts={
                                                                        "target": HandleBinding(
                                                                            name="qbv"
                                                                        ),
                                                                    },
                                                                ),
                                                            ]
                                                        ),
                                                        QuantumLambdaFunction(
                                                            body=[
                                                                QuantumFunctionCall(
                                                                    function="RY",
                                                                    params={
                                                                        "theta": Expression(
                                                                            expr="theta"
                                                                        ),
                                                                    },
                                                                    inouts={
                                                                        "target": HandleBinding(
                                                                            name="qbv"
                                                                        ),
                                                                    },
                                                                ),
                                                            ]
                                                        ),
                                                        QuantumLambdaFunction(
                                                            body=[
                                                                QuantumFunctionCall(
                                                                    function="RZ",
                                                                    params={
                                                                        "theta": Expression(
                                                                            expr="theta"
                                                                        ),
                                                                    },
                                                                    inouts={
                                                                        "target": HandleBinding(
                                                                            name="qbv"
                                                                        ),
                                                                    },
                                                                ),
                                                            ]
                                                        ),
                                                    ]
                                                },
                                            )
                                        ]
                                    )
                                },
                            ),
                        ]
                    ),
                },
            ),
            QuantumFunctionCall(
                function="split",
                params={
                    "out1_size": Expression(expr="reg_size"),
                    "out2_size": Expression(expr="num_state_qubits"),
                },
                inputs={"in": HandleBinding(name="repeat")},
                outputs={
                    "out1": HandleBinding(name="x"),
                    "out2": HandleBinding(name="q"),
                },
            ),
        ],
    ),
]
