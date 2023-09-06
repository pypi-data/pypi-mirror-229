import itertools
from functools import cached_property
from typing import Any, Callable, Dict, List

from classiq.interface.generator.functions import mangle_keyword
from classiq.interface.model.local_handle import LocalHandle
from classiq.interface.model.quantum_function_call import QuantumFunctionCall
from classiq.interface.model.quantum_function_declaration import (
    QuantumFunctionDeclaration,
)

from classiq.pyqmod.qmod_parameter import QParam
from classiq.pyqmod.qmod_variable import QVar
from classiq.pyqmod.quantum_callable import QCallable


class QExpandable(QCallable):
    def __init__(self, decl: QuantumFunctionDeclaration, py_callable: Callable) -> None:
        super().__init__(decl)
        self._py_callable = py_callable
        self._local_handles: List[LocalHandle] = list()
        self._body: List[QuantumFunctionCall] = list()

    @property
    def local_handles(self) -> List[LocalHandle]:
        return self._local_handles

    @cached_property
    def body(self) -> List[QuantumFunctionCall]:
        self._expand()
        return self._body

    def __enter__(self) -> "QExpandable":
        QExpandable.QCALLABLE_STACK.append(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        qfunc_def = QExpandable.QCALLABLE_STACK.pop()
        assert qfunc_def is self

    def _expand(self) -> None:
        with self:
            self._py_callable(
                **self._get_qvars_from_port_decls(),
                **self._get_qparams_from_param_decls(),
                **self._get_qexpandables_from_operand_decls(),
            )

    def infer_rename_params(self) -> Dict[str, str]:
        return {
            decl_name: actual_name
            for decl_name, actual_name in list(
                zip(
                    self._decl.param_decls.keys(),
                    self._py_callable.__annotations__.keys(),
                )
            )
            if decl_name != actual_name
        }

    def _add_local_handle(self, qfunc_call: QuantumFunctionCall) -> None:
        for binding in itertools.chain(
            qfunc_call.inputs.values(),
            qfunc_call.inouts.values(),
            qfunc_call.outputs.values(),
        ):
            if binding.name not in self._decl.port_declarations and not any(
                lh.name == binding.name for lh in self._local_handles
            ):
                self._local_handles.append(LocalHandle(name=binding.name))

    def append_call_to_body(self, qfunc_call: QuantumFunctionCall) -> None:
        self._add_local_handle(qfunc_call)
        self._body.append(qfunc_call)

    def _get_qvars_from_port_decls(self) -> Dict[str, QVar]:
        return {
            mangle_keyword(name): QVar(name=name)
            for name in self._decl.port_declarations
        }

    def _get_qparams_from_param_decls(self) -> Dict[str, QParam]:
        result: Dict[str, QParam] = {}
        rename_dict = self.infer_rename_params()
        for name in self._decl.param_decls:
            actual_name = rename_dict[name] if name in rename_dict else name
            result[actual_name] = QParam(name=actual_name)
        return result

    def _get_qexpandables_from_operand_decls(self) -> Dict[str, QCallable]:
        return {
            name: QTerminalCallable(decl)
            for name, decl in self._decl.operand_declarations.items()
        }

    def prepare_operands(self, kwargs: Dict[str, Any]) -> None:
        _prepare_operands(self._decl, kwargs)


class QTerminalCallable(QCallable):
    def prepare_operands(self, kwargs: Dict[str, Any]) -> None:
        _prepare_operands(self._decl, kwargs)

    def append_call_to_body(self, qfunc_call: QuantumFunctionCall) -> None:
        raise NotImplementedError  # Terminal callables don't have an SDK body


def _prepare_operands(decl, kwargs: Dict[str, Any]) -> None:
    kwargs.update(
        {
            mangle_keyword(name): QExpandable(decl, kwargs[mangle_keyword(name)])
            for name, decl in decl.operand_declarations.items()
            if not isinstance(kwargs[mangle_keyword(name)], QExpandable)
        }
    )
