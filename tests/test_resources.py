#BOP
# !MODULE: test_resources.py
# !DESCRIPTION:
# Tests for the additive resource contract.
# !INTERFACE:
# pytest tests/test_resources.py
# !SEE ALSO:
# genScheduler/resources.py
# !REVISION HISTORY:
# - 25th November 2026, J. G. de Mattos:
#   - Introduced resource contract.
#   - Tested explicit rank-based adapter and legacy compatibility.
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

def test_rank_based_adapter_and_helper():
    from genScheduler.parallel_processing_info import ParallelProcessingInfo
    from genScheduler.script_generator import calculate_variables

    request = ResourceRequest(160, 128, 4)
    info = ParallelProcessingInfo.from_resource_request(request)
    assert (info.tasks_per_node, info.pes, info.nodes) == (32, 160, 5)
    assert (info.calculate_tasks_per_node(), info.calculate_pes(), info.calculate_nodes()) == (32, 160, 5)
    assert calculate_variables(128, 160, 4, rank_based=True) == (32, 160, 5)
    assert calculate_variables(128, 160, 4) == (32, 40, 2)
    legacy = ParallelProcessingInfo(128, 160, 4)
    assert (legacy.tasks_per_node, legacy.pes, legacy.nodes) == (32, 40, 5)


def test_adapter_uses_reserved_cpus_not_threads_for_capacity():
    from genScheduler.parallel_processing_info import ParallelProcessingInfo

    info = ParallelProcessingInfo.from_resource_request(ResourceRequest(9, 32, 2, 4))
    assert (info.tasks_per_node, info.pes, info.nodes) == (8, 9, 2)


def test_legacy_omitted_threads_defaults_to_one():
    from genScheduler.parallel_processing_info import ParallelProcessingInfo

    for info in (ParallelProcessingInfo(8, 9), ParallelProcessingInfo(8, 9, None)):
        assert (info.threads_per_mpi_task, info.tasks_per_node, info.pes, info.nodes) == (1, 8, 9, 2)
        assert info.calculate_threads_per_mpi_task() == 1


def test_legacy_nodes_use_exact_integer_arithmetic():
    from genScheduler.parallel_processing_info import ParallelProcessingInfo

    assert ParallelProcessingInfo(8, 2**60 + 1, 1).nodes == 2**57 + 1


#EOC
