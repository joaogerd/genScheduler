#BOP
# !MODULE: resource_directives.py
# !DESCRIPTION:
# Render scheduler resource allocation from the explicit rank-based contract.
# !INTERFACE:
# render_resource_directives(request, scheduler, ...)
# !REMARKS:
# PBS means PBS Professional/OpenPBS select syntax, not legacy Torque.
# Explicit overrides are resolved config < machine < CLI and validated.
# This module does not render launchers or alter legacy script generation.
# !REVISION HISTORY:
# - 25th November 2026, J. G. de Mattos: Initial resource directive renderer.
#EOP
#BOC

from collections.abc import Mapping
from .resources import ResourceRequest, _positive_integer


def render_resource_directives(
    request: ResourceRequest,
    scheduler: str,
    *,
    config: Mapping | None = None,
    machine: Mapping | None = None,
    cli: Mapping | None = None,
) -> tuple[str, ...]:
    """Render one consistent allocation; reject conflicting rank/CPU overrides."""
    if scheduler not in ("SLURM", "PBS"):
        raise ValueError("unsupported scheduler resource dialect")
    values = {}
    for layer in (config, machine, cli):
        if layer is not None:
            for key in ("node_count", "tasks_per_node", "total_task_count", "cpus_per_task"):
                if key in layer and layer[key] is not None:
                    values[key] = layer[key]
    for key, value in values.items():
        _positive_integer(key, value)
    ranks = values.get("total_task_count", request.mpi_tasks)
    cpus = values.get("cpus_per_task", request.cpus_per_task)
    if ranks != request.mpi_tasks or cpus != request.cpus_per_task:
        raise ValueError("rank or CPU override conflicts with ResourceRequest")
    per_node = values.get("tasks_per_node", min(ranks, request.tasks_per_node))
    if per_node > request.tasks_per_node:
        raise ValueError("tasks_per_node exceeds node capacity")
    minimum = (ranks + per_node - 1) // per_node
    nodes = values.get("node_count", minimum)
    if nodes < minimum or nodes > ranks:
        raise ValueError("node_count cannot accommodate the requested ranks")
    if scheduler == "SLURM":
        return (
            f"#SBATCH --nodes={nodes}",
            f"#SBATCH --ntasks={ranks}",
            f"#SBATCH --ntasks-per-node={per_node}",
            f"#SBATCH --cpus-per-task={cpus}",
        )
    # Allocate exactly the requested ranks across the requested nonempty chunks.
    # Spread ranks evenly so every requested node has at least one rank.
    base, remainder = divmod(ranks, nodes)
    chunks = []
    for count, chunk_ranks in ((remainder, base + 1), (nodes - remainder, base)):
        if count:
            chunks.append(
                f"{count}:ncpus={chunk_ranks * cpus}:mpiprocs={chunk_ranks}"
                f":ompthreads={request.threads_per_mpi_task}"
            )
    return ("#PBS -l select=" + "+".join(chunks), "#PBS -l place=scatter")


#EOC
