#BOP
# !MODULE: test_resources.py
# !DESCRIPTION:
# Tests for the additive resource contract.
# !INTERFACE:
# pytest tests/test_resources.py
# !SEE ALSO:
# genScheduler/resources.py
# !REVISION HISTORY:
# - 25th November 2026, J. G. de Mattos: Introduced resource contract.
#EOP
#BOC

from dataclasses import FrozenInstanceError

import pytest

from genScheduler.resources import ResourceRequest


@pytest.mark.parametrize("ranks,capacity,threads,cpus,total,per_node,nodes", [
    (1, 64, 1, None, 1, 64, 1),
    (160, 40, 2, None, 320, 20, 8),
    (21, 40, 2, None, 42, 20, 2),
    (4, 10, 3, None, 12, 3, 2),
    (9, 32, 2, 4, 36, 8, 2),
    (2**60 + 1, 8, 1, None, 2**60 + 1, 8, 2**57 + 1),
])
def test_resource_quantities(ranks, capacity, threads, cpus, total, per_node, nodes):
    request = ResourceRequest(ranks, capacity, threads, cpus)
    assert request.mpi_tasks == ranks
    assert request.cpus_per_task == (threads if cpus is None else cpus)
    assert (request.total_cpus, request.tasks_per_node, request.nodes) == (total, per_node, nodes)


@pytest.mark.parametrize("field", ["mpi_tasks", "max_cores_per_node", "threads_per_mpi_task", "cpus_per_task"])
@pytest.mark.parametrize("value", [0, -1, True, 1.5, "2"])
def test_invalid_values(field, value):
    kwargs = dict(mpi_tasks=4, max_cores_per_node=16, threads_per_mpi_task=2, cpus_per_task=2)
    kwargs[field] = value
    with pytest.raises(ValueError, match=field):
        ResourceRequest(**kwargs)


@pytest.mark.parametrize("threads,cpus", [(4, 2), (2, 17), (17, None)])
def test_invalid_cpu_relationships(threads, cpus):
    with pytest.raises(ValueError, match="cpus_per_task"):
        ResourceRequest(4, 16, threads, cpus)


def test_immutable_request():
    request = ResourceRequest(1, 8)
    with pytest.raises(FrozenInstanceError):
        request.mpi_tasks = 2

#EOC
