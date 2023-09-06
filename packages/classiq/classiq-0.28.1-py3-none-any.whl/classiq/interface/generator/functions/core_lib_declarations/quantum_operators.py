from classiq.interface.generator.expressions.expression import Expression
from classiq.interface.generator.functions.classical_type import Bool, Integer
from classiq.interface.generator.functions.port_declaration import (
    PortDeclaration,
    PortDeclarationDirection,
)
from classiq.interface.helpers.pydantic_model_helpers import nameables_to_dict
from classiq.interface.model.quantum_function_declaration import (
    QuantumFunctionDeclaration,
    QuantumOperandDeclaration,
)

REPEAT_OPERATOR = QuantumFunctionDeclaration(
    name="repeat",
    param_decls={"count": Integer(), "port_size": Integer()},
    port_declarations={
        "qbv": PortDeclaration(
            name="qbv",
            direction=PortDeclarationDirection.Inout,
            size=Expression(expr="port_size"),
        )
    },
    operand_declarations={
        "iteration": QuantumOperandDeclaration(
            name="iteration",
            param_decls={"index": Integer()},
            port_declarations={
                "qbv": PortDeclaration(
                    name="qbv",
                    direction=PortDeclarationDirection.Inout,
                    size=Expression(expr="port_size"),
                )
            },
        )
    },
)


INVERT_OPERATOR = QuantumFunctionDeclaration(
    name="invert",
    param_decls={"target_size": Integer()},
    port_declarations={
        "target": PortDeclaration(
            name="target",
            direction=PortDeclarationDirection.Inout,
            size=Expression(expr="target_size"),
        ),
    },
    operand_declarations={
        "operand": QuantumOperandDeclaration(
            name="operand",
            port_declarations={
                "target": PortDeclaration(
                    name="target",
                    direction=PortDeclarationDirection.Inout,
                    size=Expression(expr="target_size"),
                )
            },
        ),
    },
)


CONTROL_OPERATOR = QuantumFunctionDeclaration(
    name="control",
    param_decls={"ctrl_size": Integer(), "target_size": Integer()},
    port_declarations={
        "ctrl": PortDeclaration(
            name="ctrl",
            direction=PortDeclarationDirection.Inout,
            size=Expression(expr="ctrl_size"),
        ),
        "target": PortDeclaration(
            name="target",
            direction=PortDeclarationDirection.Inout,
            size=Expression(expr="target_size"),
        ),
    },
    operand_declarations={
        "operand": QuantumOperandDeclaration(
            name="operand",
            port_declarations={
                "target": PortDeclaration(
                    name="target",
                    direction=PortDeclarationDirection.Inout,
                    size=Expression(expr="target_size"),
                )
            },
        )
    },
)

IF_OPERATOR = QuantumFunctionDeclaration(
    name="if",
    param_decls={"condition": Bool(), "port_size": Integer()},
    port_declarations={
        "qbv": PortDeclaration(
            name="qbv",
            direction=PortDeclarationDirection.Inout,
            size=Expression(expr="port_size"),
        )
    },
    operand_declarations={
        "then": QuantumOperandDeclaration(
            name="then",
            port_declarations={
                "qbv": PortDeclaration(
                    name="qbv",
                    direction=PortDeclarationDirection.Inout,
                    size=Expression(expr="port_size"),
                )
            },
        ),
        "else": QuantumOperandDeclaration(
            name="else",
            port_declarations={
                "qbv": PortDeclaration(
                    name="qbv",
                    direction=PortDeclarationDirection.Inout,
                    size=Expression(expr="port_size"),
                )
            },
        ),
    },
)

SWITCH_OPERATOR = QuantumFunctionDeclaration(
    name="switch",
    param_decls={"selector": Integer(), "port_size": Integer()},
    port_declarations={
        "qbv": PortDeclaration(
            name="qbv",
            direction=PortDeclarationDirection.Inout,
            size=Expression(expr="port_size"),
        )
    },
    operand_declarations={
        "cases": QuantumOperandDeclaration(
            name="cases",
            port_declarations={
                "qbv": PortDeclaration(
                    name="qbv",
                    direction=PortDeclarationDirection.Inout,
                    size=Expression(expr="port_size"),
                )
            },
            is_list=True,
        )
    },
)


JOIN_OPERATOR = QuantumFunctionDeclaration(
    name="join",
    port_declarations={
        "in1": PortDeclaration(name="in1", direction="input"),
        "in2": PortDeclaration(name="in2", direction="input"),
        "out": PortDeclaration(
            name="out",
            direction="output",
            size=Expression(expr="len(in1)+len(in2)"),
        ),
    },
)


SPLIT_OPERATOR = QuantumFunctionDeclaration(
    name="split",
    param_decls={"out1_size": Integer(), "out2_size": Integer()},
    port_declarations={
        "in": PortDeclaration(
            name="in",
            direction="input",
            size=Expression(expr="out1_size+out2_size"),
        ),
        "out1": PortDeclaration(
            name="out1", direction="output", size=Expression(expr="out1_size")
        ),
        "out2": PortDeclaration(
            name="out2", direction="output", size=Expression(expr="out2_size")
        ),
    },
)


PERMUTE_OPERATOR = QuantumFunctionDeclaration(
    name="permute",
    param_decls={"port_size": Integer()},
    port_declarations={
        "qbv": PortDeclaration(
            name="qbv",
            direction=PortDeclarationDirection.Inout,
            size=Expression(expr="port_size"),
        )
    },
    operand_declarations={
        "functions": QuantumOperandDeclaration(
            name="functions",
            port_declarations={
                "qbv": PortDeclaration(
                    name="qbv",
                    direction=PortDeclarationDirection.Inout,
                    size=Expression(expr="port_size"),
                )
            },
            is_list=True,
        )
    },
)


POWER_OPERATOR = QuantumFunctionDeclaration(
    name="power",
    param_decls={"power": Integer(), "port_size": Integer()},
    port_declarations={
        "qbv": PortDeclaration(
            name="qbv",
            direction=PortDeclarationDirection.Inout,
            size=Expression(expr="port_size"),
        )
    },
    operand_declarations={
        "operand": QuantumOperandDeclaration(
            name="operand",
            port_declarations={
                "qbv": PortDeclaration(
                    name="qbv",
                    direction=PortDeclarationDirection.Inout,
                    size=Expression(expr="port_size"),
                )
            },
        )
    },
)


_BUILTIN_QUANTUM_OPERATOR_LIST = [
    REPEAT_OPERATOR,
    INVERT_OPERATOR,
    CONTROL_OPERATOR,
    IF_OPERATOR,
    SWITCH_OPERATOR,
    JOIN_OPERATOR,
    SPLIT_OPERATOR,
    PERMUTE_OPERATOR,
    POWER_OPERATOR,
]


QuantumFunctionDeclaration.BUILTIN_FUNCTION_DECLARATIONS.update(
    nameables_to_dict(_BUILTIN_QUANTUM_OPERATOR_LIST)
)
