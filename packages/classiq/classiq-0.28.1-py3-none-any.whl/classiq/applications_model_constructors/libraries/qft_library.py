from typing import List

from classiq.interface.generator.expressions.expression import Expression
from classiq.interface.generator.functions.port_declaration import (
    PortDeclaration,
    PortDeclarationDirection,
)
from classiq.interface.model.handle_binding import HandleBinding, SlicedHandleBinding
from classiq.interface.model.native_function_definition import NativeFunctionDefinition
from classiq.interface.model.quantum_function_call import (
    QuantumFunctionCall,
    QuantumLambdaFunction,
)

from classiq import Integer

QFT_LIBRARY: List[NativeFunctionDefinition] = [
    NativeFunctionDefinition(
        name="qft_step",
        param_decls={"num_qbits": Integer()},
        port_declarations={
            "qbv": PortDeclaration(
                name="qbv",
                size=Expression(expr="num_qbits"),
                direction=PortDeclarationDirection.Inout,
            ),
        },
        body=[
            QuantumFunctionCall(
                function="H",
                inouts={
                    "target": SlicedHandleBinding(
                        name="qbv",
                        start=Expression(expr="0"),
                        end=Expression(expr="1"),
                    ),
                },
            ),
            QuantumFunctionCall(
                function="repeat",
                params={
                    "count": Expression(expr="num_qbits-1"),
                    "port_size": Expression(expr="num_qbits"),
                },
                inouts={"qbv": HandleBinding(name="qbv")},
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
                                        start=Expression(expr="index+1"),
                                        end=Expression(expr="index+2"),
                                    ),
                                    "target": SlicedHandleBinding(
                                        name="qbv",
                                        start=Expression(expr="0"),
                                        end=Expression(expr="1"),
                                    ),
                                },
                                operands={
                                    "operand": QuantumLambdaFunction(
                                        body=[
                                            QuantumFunctionCall(
                                                function="PHASE",
                                                params={
                                                    "theta": Expression(
                                                        expr="pi/2**(index+1)"
                                                    )
                                                },
                                                inouts={
                                                    "target": HandleBinding(
                                                        name="target"
                                                    )
                                                },
                                            )
                                        ],
                                    ),
                                },
                            )
                        ],
                    ),
                },
            ),
        ],
    ),
    NativeFunctionDefinition(
        name="qft",
        param_decls={"num_qbits": Integer()},
        port_declarations={
            "qbv": PortDeclaration(
                name="qbv",
                size=Expression(expr="num_qbits"),
                direction=PortDeclarationDirection.Inout,
            ),
        },
        body=[
            QuantumFunctionCall(
                function="repeat",
                params={
                    "count": Expression(expr="num_qbits//2"),
                    "port_size": Expression(expr="num_qbits"),
                },
                inouts={"qbv": HandleBinding(name="qbv")},
                operands={
                    "iteration": QuantumLambdaFunction(
                        body=[
                            QuantumFunctionCall(
                                function="SWAP",
                                inouts={
                                    "qbit0": SlicedHandleBinding(
                                        name="qbv",
                                        start=Expression(expr="index"),
                                        end=Expression(expr="index+1"),
                                    ),
                                    "qbit1": SlicedHandleBinding(
                                        name="qbv",
                                        start=Expression(expr="num_qbits-1-index"),
                                        end=Expression(expr="num_qbits-index"),
                                    ),
                                },
                            )
                        ],
                    ),
                },
            ),
            QuantumFunctionCall(
                function="repeat",
                params={
                    "count": Expression(expr="num_qbits"),
                    "port_size": Expression(expr="num_qbits"),
                },
                inouts={"qbv": HandleBinding(name="qbv")},
                operands={
                    "iteration": QuantumLambdaFunction(
                        body=[
                            QuantumFunctionCall(
                                function="qft_step",
                                params={
                                    "num_qbits": Expression(expr="num_qbits-index")
                                },
                                inouts={
                                    "qbv": SlicedHandleBinding(
                                        name="qbv",
                                        start=Expression(expr="index"),
                                        end=Expression(expr="num_qbits"),
                                    ),
                                },
                            )
                        ],
                    )
                },
            ),
        ],
    ),
]
