from typing import Any, ClassVar, Dict, Mapping, Set

import pydantic

from classiq.interface.generator.function_params import (
    ArithmeticIODict,
    IOName,
    PortDirection,
)
from classiq.interface.generator.functions.function_declaration import (
    FunctionDeclaration,
    OperandDeclaration,
)
from classiq.interface.generator.functions.port_declaration import PortDeclaration
from classiq.interface.generator.functions.quantum_function_declaration import (
    _ports_to_registers,
)
from classiq.interface.helpers.validation_helpers import (
    validate_nameables_mapping,
    validate_nameables_no_overlap,
)

from classiq.exceptions import ClassiqValueError


class QuantumFunctionDeclaration(FunctionDeclaration):
    """
    Facilitates the creation of a common quantum function interface object.
    """

    port_declarations: Dict[IOName, PortDeclaration] = pydantic.Field(
        description="The input and output ports of the function.",
        default_factory=dict,
    )

    operand_declarations: Mapping[str, "QuantumOperandDeclaration"] = pydantic.Field(
        description="The expected interface of the quantum function operands",
        default_factory=dict,
    )

    BUILTIN_FUNCTION_DECLARATIONS: ClassVar[
        Dict[str, "QuantumFunctionDeclaration"]
    ] = {}

    @property
    def input_set(self) -> Set[IOName]:
        return set(self.inputs.keys())

    @property
    def output_set(self) -> Set[IOName]:
        return set(self.outputs.keys())

    @property
    def inputs(self) -> ArithmeticIODict:
        return _ports_to_registers(self.port_declarations, PortDirection.Input)

    @property
    def outputs(self) -> ArithmeticIODict:
        return _ports_to_registers(self.port_declarations, PortDirection.Output)

    def update_logic_flow(
        self, function_dict: Mapping[str, "QuantumFunctionDeclaration"]
    ) -> None:
        pass

    def ports_by_direction(
        self, direction: PortDirection
    ) -> Mapping[str, PortDeclaration]:
        return {
            name: port
            for name, port in self.port_declarations.items()
            if port.direction.includes_port_direction(direction)
        }

    @pydantic.validator("operand_declarations")
    def _validate_operand_declarations_names(
        cls, operand_declarations: Dict[str, "OperandDeclaration"]
    ) -> Dict[str, "OperandDeclaration"]:
        validate_nameables_mapping(operand_declarations, "Operand")
        return operand_declarations

    @pydantic.validator("port_declarations")
    def _validate_port_declarations_names(
        cls, port_declarations: Dict[IOName, PortDeclaration]
    ) -> Dict[IOName, PortDeclaration]:
        validate_nameables_mapping(port_declarations, "Port")
        return port_declarations

    @pydantic.root_validator()
    def _validate_params_and_operands_uniqueness(
        cls, values: Dict[str, Any]
    ) -> Dict[str, Any]:
        operand_declarations = values.get("operand_declarations")
        parameter_declarations = values.get("param_decls")
        port_declarations = values.get("port_declarations")
        operand_parameter = validate_nameables_no_overlap(
            operand_declarations, parameter_declarations, "operand", "parameter"
        )
        operand_port = validate_nameables_no_overlap(
            operand_declarations, port_declarations, "operand", "port"
        )
        parameter_port = validate_nameables_no_overlap(
            parameter_declarations, port_declarations, "parameter", "port"
        )
        error_message = ",".join(
            msg
            for msg in [operand_parameter, operand_port, parameter_port]
            if msg is not None
        )

        if error_message:
            raise ClassiqValueError(error_message)

        return values


class QuantumOperandDeclaration(OperandDeclaration, QuantumFunctionDeclaration):
    pass


QuantumFunctionDeclaration.update_forward_refs()
