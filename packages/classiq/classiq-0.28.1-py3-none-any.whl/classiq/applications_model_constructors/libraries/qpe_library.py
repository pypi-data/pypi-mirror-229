from classiq.interface.generator.expressions.expression import Expression
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

from classiq import Integer
from classiq.applications_model_constructors.libraries.qft_library import QFT_LIBRARY

QPE_LIBRARY = [
    *QFT_LIBRARY,
    NativeFunctionDefinition(
        name="qpe",
        param_decls={"reg_size": Integer(), "qpe_reg_size": Integer()},
        local_handles=[LocalHandle(name="repeat")],
        port_declarations={
            "x": PortDeclaration(
                name="x",
                size=Expression(expr="reg_size"),
                direction=PortDeclarationDirection.Inout,
            ),
            "q": PortDeclaration(
                name="q",
                size=Expression(expr="qpe_reg_size"),
                direction=PortDeclarationDirection.Inout,
            ),
        },
        operand_declarations={
            "qfunc": QuantumOperandDeclaration(
                name="qfunc",
                port_declarations={
                    "target": PortDeclaration(
                        name="target",
                        direction=PortDeclarationDirection.Inout,
                        size=Expression(expr="reg_size"),
                    )
                },
            )
        },
        body=[
            QuantumFunctionCall(
                function="uniform_superposition",
                params={"num_qubits": Expression(expr="qpe_reg_size")},
                inouts={"q": HandleBinding(name="q")},
            ),
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
                    "count": Expression(expr="qpe_reg_size"),
                    "port_size": Expression(expr="reg_size + qpe_reg_size"),
                },
                inouts={"qbv": HandleBinding(name="repeat")},
                operands={
                    "iteration": QuantumLambdaFunction(
                        body=[
                            QuantumFunctionCall(
                                function="control",
                                params={
                                    "ctrl_size": Expression(expr="1"),
                                    "target_size": Expression(expr="reg_size"),
                                },
                                inouts={
                                    "ctrl": SlicedHandleBinding(
                                        name="qbv",
                                        start=Expression(expr="reg_size+index"),
                                        end=Expression(expr="reg_size+index+1"),
                                    ),
                                    "target": SlicedHandleBinding(
                                        name="qbv",
                                        start=Expression(expr="0"),
                                        end=Expression(expr="reg_size"),
                                    ),
                                },
                                operands={
                                    "operand": QuantumLambdaFunction(
                                        body=[
                                            QuantumFunctionCall(
                                                function="repeat",
                                                params={
                                                    "count": Expression(
                                                        expr="2**index"
                                                    ),
                                                    "port_size": Expression(
                                                        expr="reg_size"
                                                    ),
                                                },
                                                inouts={
                                                    "qbv": HandleBinding(name="target")
                                                },
                                                operands={
                                                    "iteration": QuantumLambdaFunction(
                                                        body=[
                                                            QuantumFunctionCall(
                                                                function="qfunc",
                                                                inouts={
                                                                    "target": HandleBinding(
                                                                        name="qbv"
                                                                    )
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
                        ]
                    ),
                },
            ),
            QuantumFunctionCall(
                function="split",
                params={
                    "out1_size": Expression(expr="reg_size"),
                    "out2_size": Expression(expr="qpe_reg_size"),
                },
                inputs={"in": HandleBinding(name="repeat")},
                outputs={
                    "out1": HandleBinding(name="x"),
                    "out2": HandleBinding(name="q"),
                },
            ),
            QuantumFunctionCall(
                function="invert",
                params={
                    "target_size": Expression(expr="qpe_reg_size"),
                },
                inouts={"target": HandleBinding(name="q")},
                operands={
                    "operand": QuantumLambdaFunction(
                        body=[
                            QuantumFunctionCall(
                                function="qft",
                                params={"num_qbits": Expression(expr="qpe_reg_size")},
                                inouts={"qbv": HandleBinding(name="target")},
                            )
                        ]
                    )
                },
            ),
        ],
    ),
]
