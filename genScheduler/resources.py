#BOP
# !MODULE: resources.py
# !DESCRIPTION:
# Scheduler-independent, immutable compute resource request.
# !INTERFACE:
# from genScheduler.resources import ResourceRequest
# !ARGUMENTS:
# mpi_tasks: total MPI ranks (positive integer).
# threads_per_mpi_task: OpenMP threads per rank (default 1).
# cpus_per_task: allocated CPUs per rank; defaults to thread count.
# max_cores_per_node: usable scheduler CPUs per node, not necessarily
# physical cores; required, with consistent units across the request.
# !REMARKS:
# No oversubscription; homogeneous nodes. Explicit scheduler overrides,
# placement and legacy conversions are outside this contract.
# !REVISION HISTORY:
# - 25th November 2026, J. G. de Mattos: Introduced resource contract.
#EOP
#BOC

from dataclasses import dataclass


def _positive_integer(name: str, value: int) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(f"{name} must be a positive integer")


@dataclass(frozen=True)
class ResourceRequest:
    """Compute demand, independent of CLI, scheduler and machine name."""

    mpi_tasks: int
    max_cores_per_node: int
    threads_per_mpi_task: int = 1
    cpus_per_task: int | None = None

    def __post_init__(self) -> None:
        for name in ("mpi_tasks", "max_cores_per_node", "threads_per_mpi_task"):
            _positive_integer(name, getattr(self, name))
        cpus = self.cpus_per_task
        if cpus is None:
            cpus = self.threads_per_mpi_task
        _positive_integer("cpus_per_task", cpus)
        if cpus < self.threads_per_mpi_task:
            raise ValueError("cpus_per_task must cover threads_per_mpi_task")
        if cpus > self.max_cores_per_node:
            raise ValueError("cpus_per_task exceeds max_cores_per_node")
        object.__setattr__(self, "cpus_per_task", cpus)

    @property
    def total_cpus(self) -> int:
        """Total CPU demand, not whole-node allocation."""
        return self.mpi_tasks * self.cpus_per_task

    @property
    def tasks_per_node(self) -> int:
        """Maximum ranks that fit on one node (not actual placement)."""
        return self.max_cores_per_node // self.cpus_per_task

    @property
    def nodes(self) -> int:
        """Minimum nodes with packed ranks, using exact integer arithmetic."""
        capacity = self.tasks_per_node
        return (self.mpi_tasks + capacity - 1) // capacity

#EOC
