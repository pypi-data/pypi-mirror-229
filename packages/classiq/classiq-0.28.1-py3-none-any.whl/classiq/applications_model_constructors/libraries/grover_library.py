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

GROVER_LIBRARY = [
    NativeFunctionDefinition(
        name="grover_diffuser",
        param_decls={"num_qubits": Integer()},
        local_handles=[
            LocalHandle(name="msbs"),
            LocalHandle(name="lsb"),
        ],
        port_declarations={
            "p": PortDeclaration(
                name="p",
                size=Expression(expr="num_qubits"),
                direction=PortDeclarationDirection.Inout,
            ),
        },
        body=[
            QuantumFunctionCall(
                function="apply_to_all",
                params={"num_qubits": Expression(expr="num_qubits")},
                inouts={"q": HandleBinding(name="p")},
                operands={
                    "gate_operand": QuantumLambdaFunction(
                        body=[
                            QuantumFunctionCall(
                                function="X",
                                inouts={"target": HandleBinding(name="target")},
                            )
                        ]
                    )
                },
            ),
            QuantumFunctionCall(
                function="split",
                params={
                    "out1_size": Expression(expr="num_qubits-1"),
                    "out2_size": Expression(expr="1"),
                },
                inputs={"in": HandleBinding(name="p")},
                outputs={
                    "out1": HandleBinding(name="msbs"),
                    "out2": HandleBinding(name="lsb"),
                },
            ),
            QuantumFunctionCall(
                function="control",
                params={
                    "ctrl_size": Expression(expr="num_qubits-1"),
                    "target_size": Expression(expr="1"),
                },
                inouts={
                    "ctrl": HandleBinding(name="msbs"),
                    "target": HandleBinding(name="lsb"),
                },
                operands={
                    "operand": QuantumLambdaFunction(
                        body=[
                            QuantumFunctionCall(
                                function="Z",
                                inouts={"target": HandleBinding(name="target")},
                            ),
                        ]
                    ),
                },
            ),
            QuantumFunctionCall(
                function="join",
                inputs={
                    "in1": HandleBinding(name="msbs"),
                    "in2": HandleBinding(name="lsb"),
                },
                outputs={"out": HandleBinding(name="p")},
            ),
            QuantumFunctionCall(
                function="apply_to_all",
                params={"num_qubits": {"expr": "num_qubits"}},
                inouts={"q": HandleBinding(name="p")},
                operands={
                    "gate_operand": QuantumLambdaFunction(
                        body=[
                            QuantumFunctionCall(
                                function="X",
                                inouts={"target": HandleBinding(name="target")},
                            )
                        ]
                    )
                },
            ),
        ],
    ),
    NativeFunctionDefinition(
        name="grover_operator",
        param_decls={"num_qubits": Integer()},
        port_declarations={
            "p": PortDeclaration(
                name="p",
                size=Expression(expr="num_qubits"),
                direction=PortDeclarationDirection.Inout,
            ),
        },
        operand_declarations={
            "sp_op": QuantumOperandDeclaration(
                name="sp_op",
                param_decls={"num_qubits": Integer()},
                port_declarations={
                    "spq": PortDeclaration(
                        name="spq",
                        direction="inout",
                        size=Expression(expr="num_qubits"),
                    )
                },
            ),
            "oracle_op": QuantumOperandDeclaration(
                name="oracle_op",
                param_decls={"num_qubits": Integer()},
                port_declarations={
                    "oq": PortDeclaration(
                        name="oq",
                        direction="inout",
                        size=Expression(expr="num_qubits"),
                    )
                },
            ),
        },
        body=[
            QuantumFunctionCall(
                function="oracle_op",
                params={"num_qubits": Expression(expr="num_qubits")},
                inouts={"oq": HandleBinding(name="p")},
            ),
            QuantumFunctionCall(
                function="invert",
                params={
                    "target_size": Expression(expr="num_qubits"),
                },
                inouts={"target": HandleBinding(name="p")},
                should_control=False,
                operands={
                    "operand": QuantumLambdaFunction(
                        body=[
                            QuantumFunctionCall(
                                function="sp_op",
                                params={"num_qubits": Expression(expr="num_qubits")},
                                inouts={"spq": HandleBinding(name="target")},
                            )
                        ]
                    )
                },
            ),
            QuantumFunctionCall(
                function="grover_diffuser",
                params={"num_qubits": Expression(expr="num_qubits")},
                inouts={"p": HandleBinding(name="p")},
            ),
            QuantumFunctionCall(
                function="sp_op",
                params={"num_qubits": Expression(expr="num_qubits")},
                inouts={"spq": HandleBinding(name="p")},
                should_control=False,
            ),
            # add a (-1) phase to the operator so that AE will work
            QuantumFunctionCall(
                function="U",
                params={
                    "theta": Expression(expr="0"),
                    "phi": Expression(expr="0"),
                    "lam": Expression(expr="0"),
                    "gam": Expression(expr="pi"),
                },
                inouts={
                    "target": SlicedHandleBinding(
                        name="p", start=Expression(expr="0"), end=Expression(expr="1")
                    )
                },
            ),
        ],
    ),
    NativeFunctionDefinition(
        name="uniform_superposition",
        param_decls={"num_qubits": Integer()},
        port_declarations={
            "q": PortDeclaration(
                name="q",
                size=Expression(expr="num_qubits"),
                direction=PortDeclarationDirection.Inout,
            ),
        },
        body=[
            QuantumFunctionCall(
                function="apply_to_all",
                operands={
                    "gate_operand": QuantumLambdaFunction(
                        body=[
                            QuantumFunctionCall(
                                function="H",
                                inouts={"target": HandleBinding(name="target")},
                            )
                        ]
                    )
                },
                params={"num_qubits": Expression(expr="num_qubits")},
                inouts={"q": HandleBinding(name="q")},
            )
        ],
    ),
    NativeFunctionDefinition(
        name="apply_to_all",
        param_decls={"num_qubits": Integer()},
        port_declarations={
            "q": PortDeclaration(
                name="q",
                size=Expression(expr="num_qubits"),
                direction=PortDeclarationDirection.Inout,
            ),
        },
        operand_declarations={
            "gate_operand": QuantumOperandDeclaration(
                name="gate_operand",
                port_declarations={
                    "target": PortDeclaration(
                        name="target",
                        direction="inout",
                        size=Expression(expr="1"),
                    )
                },
            )
        },
        body=[
            QuantumFunctionCall(
                function="repeat",
                params={
                    "count": Expression(expr="num_qubits"),
                    "port_size": Expression(expr="num_qubits"),
                },
                inouts={"qbv": HandleBinding(name="q")},
                operands={
                    "iteration": QuantumLambdaFunction(
                        body=[
                            QuantumFunctionCall(
                                function="gate_operand",
                                inouts={
                                    "target": SlicedHandleBinding(
                                        name="qbv",
                                        start=Expression(expr="index"),
                                        end=Expression(expr="index+1"),
                                    ),
                                },
                            ),
                        ]
                    ),
                },
            ),
        ],
    ),
    NativeFunctionDefinition(
        name="grover_search",
        param_decls={"num_qubits": Integer(), "reps": Integer()},
        port_declarations={
            "gsq": PortDeclaration(
                name="gsq",
                size=Expression(expr="num_qubits"),
                direction=PortDeclarationDirection.Inout,
            ),
        },
        operand_declarations={
            "oracle_op": QuantumOperandDeclaration(
                name="oracle_op",
                param_decls={"num_qubits": Integer()},
                port_declarations={
                    "oq": PortDeclaration(
                        name="oq",
                        direction="inout",
                        size=Expression(expr="num_qubits"),
                    )
                },
            )
        },
        body=[
            QuantumFunctionCall(
                function="uniform_superposition",
                params={"num_qubits": Expression(expr="num_qubits")},
                inouts={"q": HandleBinding(name="gsq")},
            ),
            QuantumFunctionCall(
                function="repeat",
                params={
                    "count": Expression(expr="reps"),
                    "port_size": Expression(expr="num_qubits"),
                },
                inouts={"qbv": HandleBinding(name="gsq")},
                operands={
                    "iteration": QuantumLambdaFunction(
                        body=[
                            QuantumFunctionCall(
                                function="grover_operator",
                                inouts={"p": HandleBinding(name="qbv")},
                                params={"num_qubits": Expression(expr="num_qubits")},
                                operands={
                                    "oracle_op": QuantumLambdaFunction(
                                        body=[
                                            QuantumFunctionCall(
                                                function="oracle_op",
                                                params={
                                                    "num_qubits": Expression(
                                                        expr="num_qubits"
                                                    )
                                                },
                                                inouts={"oq": HandleBinding(name="oq")},
                                            )
                                        ]
                                    ),
                                    "sp_op": QuantumLambdaFunction(
                                        body=[
                                            QuantumFunctionCall(
                                                function="uniform_superposition",
                                                params={
                                                    "num_qubits": Expression(
                                                        expr="num_qubits"
                                                    )
                                                },
                                                inouts={"q": HandleBinding(name="spq")},
                                            )
                                        ]
                                    ),
                                },
                            )
                        ]
                    )
                },
            ),
        ],
    ),
]
