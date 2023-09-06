from classiq._internals.enum_utils import StrEnum


class QSolver(StrEnum):
    QAOAPenalty = "QAOAPenalty"
    QAOAMixer = "QAOAMixer"
    Custom = "Custom"
    GAS = "GAS"
