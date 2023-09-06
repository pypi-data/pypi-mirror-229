import base64
import io
from datetime import datetime
from typing import Dict, List, Optional, Tuple, cast

import matplotlib.pyplot as plt
import numpy as np
import pydantic
from matplotlib.ticker import MaxNLocator
from PIL import Image
from pydantic import BaseModel
from tabulate import tabulate

from classiq.interface.generator.complex_type import Complex
from classiq.interface.generator.functions.classical_type import QmodPyObject
from classiq.interface.helpers.custom_pydantic_types import PydanticProbabilityFloat
from classiq.interface.helpers.versioned_model import VersionedModel

Solution = Tuple[int, ...]


class SolverResult(VersionedModel):
    energy: float
    # TODO: add time units (like seconds)
    time: Optional[float]
    solution: Optional[Solution]


class SolutionData(BaseModel):
    solution: Solution
    repetitions: pydantic.PositiveInt
    probability: PydanticProbabilityFloat
    cost: float


class VQEIntermediateData(BaseModel):
    utc_time: datetime = pydantic.Field(description="Time when the iteration finished")
    iteration_number: pydantic.PositiveInt = pydantic.Field(
        description="The iteration's number (evaluation count)"
    )
    parameters: List[float] = pydantic.Field(
        description="The optimizer parameters for the variational form"
    )
    mean_all_solutions: Optional[float] = pydantic.Field(
        default=None, description="The mean score of all solutions in this iteration"
    )
    solutions: List[SolutionData] = pydantic.Field(
        description="Solutions found in this iteration, their score and"
        "number of repetitions"
    )
    standard_deviation: float = pydantic.Field(
        description="The evaluated standard deviation"
    )


_MAX_BIN = 50


class VQESolverResult(SolverResult, QmodPyObject):
    eigenstate: Dict[str, Complex]
    intermediate_results: List[VQEIntermediateData]
    optimal_parameters: Dict[str, float]
    convergence_graph_str: str
    num_solutions: Optional[int] = None
    num_shots: int

    def show_convergence_graph(self) -> None:
        self.convergence_graph.show()

    @property
    def convergence_graph(self):
        return Image.open(io.BytesIO(base64.b64decode(self.convergence_graph_str)))

    @property
    def energy_std(self) -> float:
        return self.intermediate_results[-1].standard_deviation


class OptimizationResult(VQESolverResult):
    solution: Solution
    solution_distribution: List[SolutionData]

    @property
    def best_cost(self) -> float:
        return self.solution_distribution[0].cost

    @property
    def best_cost_probability(self) -> float:
        return sum(
            solution.probability
            for solution in self.solution_distribution
            if np.isclose(solution.cost, self.best_cost)
        )

    @property
    def energy_average(self) -> float:
        return cast(
            float,
            np.mean(
                [solution_data.cost for solution_data in self.solution_distribution]
            ),
        )

    @property
    def energy_std(self) -> float:
        return cast(
            float,
            np.std(
                [solution_data.cost for solution_data in self.solution_distribution]
            ),
        )

    def optimal_parameters_graph(self, num_lines: int = 2) -> None:
        optimal_parameters = list(self.optimal_parameters.values())
        layers = list(range(len(optimal_parameters) // num_lines))

        if num_lines == 2:
            legends = [r"$\gamma$", r"$\beta$"]
        else:
            legends = [f"line{i}" for i in range(num_lines)]

        for i in range(num_lines):
            plt.plot(
                layers,
                optimal_parameters[i::num_lines],
                marker="o",
                linestyle="--",
            )
        plt.xlabel("repetition")
        plt.ylabel("value")
        plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))
        plt.legend(legends)

    def __str__(self) -> str:
        return "\n".join(self.formatted())

    def formatted(self) -> List[str]:
        if self.num_solutions is None:
            self.num_solutions = len(self.solution_distribution)

        lines = []
        lines.append("=== OPTIMAL SOLUTION ===")
        lines.append(
            tabulate(
                [[tuple(self.solution), self.best_cost]], headers=["solution", "cost"]
            )
        )
        lines.append("\n=== STATISTICS === ")
        lines.append(f"mean: {self.energy_average}")
        lines.append(f"standard deviation: {self.energy_std}")

        lines.append("\n=== SOLUTION DISTRIBUTION ===")
        solution_distribution_table = [
            [solution_data.solution, solution_data.cost, solution_data.probability]
            for solution_data in self.solution_distribution[: self.num_solutions]
        ]
        lines.append(
            tabulate(
                solution_distribution_table, headers=["solution", "cost", "probability"]
            )
        )
        lines.append("\n=== OPTIMAL_PARAMETERS ===")
        lines.append(str(self.optimal_parameters))
        lines.append("\n=== TIME ===")
        lines.append(str(self.time))
        return lines

    def histogram(self) -> None:
        repetitions = [
            solution_data.repetitions for solution_data in self.solution_distribution
        ]
        costs = [solution_data.cost for solution_data in self.solution_distribution]

        bins = min(len(set(costs)), _MAX_BIN)
        eps = (max(costs) - min(costs)) / bins / 2
        hist_range = (min(costs) - eps, max(costs) + eps)
        plt.hist(
            x=costs, bins=bins, density=True, weights=repetitions, range=hist_range
        )

        plt.ylabel("Probability")
        plt.xlabel("value")
