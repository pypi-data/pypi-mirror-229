from typing import List

from classiq.interface.generator.classical_function_call import ClassicalFunctionCall
from classiq.interface.generator.expressions.expression import Expression
from classiq.interface.generator.functions.assignment_statement import (
    AssignmentStatement,
)
from classiq.interface.generator.functions.classical_function_definition import (
    ClassicalFunctionDefinition,
)
from classiq.interface.generator.functions.classical_type import Histogram, Real
from classiq.interface.generator.functions.port_declaration import (
    PortDeclaration,
    PortDeclarationDirection,
)
from classiq.interface.generator.functions.return_statement import ReturnStatement
from classiq.interface.generator.functions.save_statement import SaveStatement
from classiq.interface.generator.functions.variable_declaration_statement import (
    VariableDeclaration,
)
from classiq.interface.generator.quantum_invoker_call import QuantumInvokerCall
from classiq.interface.model.handle_binding import HandleBinding
from classiq.interface.model.native_function_definition import NativeFunctionDefinition
from classiq.interface.model.quantum_function_call import (
    QuantumFunctionCall,
    QuantumLambdaFunction,
)
from classiq.interface.model.quantum_function_declaration import (
    QuantumOperandDeclaration,
)

from classiq import Integer
from classiq.applications_model_constructors.libraries.grover_library import (
    GROVER_LIBRARY,
)
from classiq.applications_model_constructors.libraries.qpe_library import QPE_LIBRARY

AE_LIBRARY: List[NativeFunctionDefinition] = [
    *GROVER_LIBRARY,
    *QPE_LIBRARY,
    NativeFunctionDefinition(
        name="amplitude_estimation",
        param_decls={
            "num_phase_qubits": Integer(),
            "num_unitary_qubits": Integer(),
        },
        port_declarations={
            "phase_port": PortDeclaration(
                name="phase_port",
                size=Expression(expr="num_phase_qubits"),
                direction=PortDeclarationDirection.Output,
            ),
            "unitary_port": PortDeclaration(
                name="unitary_port",
                size=Expression(expr="num_unitary_qubits"),
                direction=PortDeclarationDirection.Output,
            ),
        },
        operand_declarations={
            "sp_op": QuantumOperandDeclaration(
                name="sp_op",
                param_decls={"num_unitary_qubits": Integer()},
                port_declarations={
                    "spq": PortDeclaration(
                        name="spq",
                        direction="inout",
                        size=Expression(expr="num_unitary_qubits"),
                    )
                },
            ),
            "oracle_op": QuantumOperandDeclaration(
                name="oracle_op",
                param_decls={"num_unitary_qubits": Integer()},
                port_declarations={
                    "oq": PortDeclaration(
                        name="oq",
                        direction="inout",
                        size=Expression(expr="num_unitary_qubits"),
                    )
                },
            ),
        },
        body=[
            QuantumFunctionCall(
                function="sp_op",
                params={"num_unitary_qubits": Expression(expr="num_unitary_qubits")},
                outputs={"spq": HandleBinding(name="unitary_port")},
            ),
            QuantumFunctionCall(
                function="qpe",
                params={
                    "reg_size": Expression(expr="num_unitary_qubits"),
                    "qpe_reg_size": Expression(expr="num_phase_qubits"),
                },
                operands={
                    "qfunc": QuantumLambdaFunction(
                        body=[
                            QuantumFunctionCall(
                                function="grover_operator",
                                params={
                                    "num_qubits": Expression(expr="num_unitary_qubits")
                                },
                                operands={
                                    "oracle_op": QuantumLambdaFunction(
                                        body=[
                                            QuantumFunctionCall(
                                                function="oracle_op",
                                                params={
                                                    "num_unitary_qubits": Expression(
                                                        expr="num_unitary_qubits",
                                                    )
                                                },
                                                inouts={"oq": HandleBinding(name="oq")},
                                            )
                                        ]
                                    ),
                                    "sp_op": QuantumLambdaFunction(
                                        body=[
                                            QuantumFunctionCall(
                                                function="sp_op",
                                                params={
                                                    "num_unitary_qubits": Expression(
                                                        expr="num_unitary_qubits",
                                                    )
                                                },
                                                inouts={
                                                    "spq": HandleBinding(name="spq")
                                                },
                                            )
                                        ]
                                    ),
                                },
                                inouts={"p": HandleBinding(name="target")},
                            ),
                        ],
                    )
                },
                inouts={"x": HandleBinding(name="unitary_port")},
                outputs={
                    "q": HandleBinding(name="phase_port"),
                },
            ),
        ],
    ),
]

AE_CLASSICAL_LIBRARY = [
    ClassicalFunctionDefinition(
        name="execute_amplitude_estimation",
        param_decls={
            "phase_port_size": Integer(),
        },
        return_type=Real(),
        body=[
            VariableDeclaration(name="result", var_type=Histogram()),
            AssignmentStatement(
                assigned_variable="result",
                invoked_expression=QuantumInvokerCall(
                    function="sample",
                    target_function="main",
                ),
            ),
            SaveStatement(saved_variable="result"),
            VariableDeclaration(name="estimation", var_type=Real()),
            AssignmentStatement(
                assigned_variable="estimation",
                invoked_expression=ClassicalFunctionCall(
                    function="qae_with_qpe_result_post_processing",
                    params={
                        "estimation_register_size": Expression(expr="phase_port_size"),
                        "estimation_method": Expression(expr="1"),
                        "result": Expression(expr="result"),
                    },
                ),
            ),
            ReturnStatement(returned_variable="estimation"),
        ],
    ),
]
