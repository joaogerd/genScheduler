"""Parallel resource calculations used by generated scheduler launch commands."""

import math
from typing import Optional


class ParallelProcessingInfo:
    """Calculate the legacy parallel-processing values used by genScheduler.

    The formulas are intentionally unchanged because they directly affect the
    generated PBS/SLURM command lines.
    """

    def __init__(
        self,
        max_cores_per_node: int,
        mpi_tasks: int,
        threads_per_mpi_task: Optional[int] = None,
    ) -> None:
        self.max_cores_per_node = max_cores_per_node
        self.mpi_tasks = mpi_tasks
        self.threads_per_mpi_task = (
            threads_per_mpi_task
            if threads_per_mpi_task is not None
            else self.calculate_threads_per_mpi_task()
        )

        self.tasks_per_node = self.calculate_tasks_per_node()
        self.pes = self.calculate_pes()
        self.nodes = self.calculate_nodes()

    def calculate_tasks_per_node(self) -> int:
        """Return tasks per node using the historical integer division."""
        return self.max_cores_per_node // self.threads_per_mpi_task

    def calculate_pes(self) -> int:
        """Return the historical process-count calculation."""
        return self.mpi_tasks // self.threads_per_mpi_task

    def calculate_nodes(self) -> int:
        """Return the historical node-count calculation."""
        return math.ceil(self.mpi_tasks / self.tasks_per_node)

    def calculate_threads_per_mpi_task(self) -> int:
        """Return the historical implicit thread calculation.

        This method intentionally preserves the original implementation. The
        normal CLI always supplies threads_per_mpi_task explicitly.
        """
        return self.max_cores_per_node // self.tasks_per_node
