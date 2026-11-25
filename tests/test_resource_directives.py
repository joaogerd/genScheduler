#BOP
# !MODULE: test_resource_directives.py
# !DESCRIPTION:
# Verify scheduler resource rendering and override precedence.
# !REVISION HISTORY:
# - 25th November 2026, J. G. de Mattos: Initial tests.
#EOP
#BOC

import pytest

from genScheduler.resources import ResourceRequest
from genScheduler.resource_directives import render_resource_directives


def test_slurm_hybrid():
    assert render_resource_directives(ResourceRequest(160, 128, 4), "SLURM") == (
        "#SBATCH --nodes=5", "#SBATCH --ntasks=160",
        "#SBATCH --ntasks-per-node=32", "#SBATCH --cpus-per-task=4",
    )


def test_pbs_partial_node():
    assert render_resource_directives(ResourceRequest(9, 32, 2, 4), "PBS") == (
        "#PBS -l select=1:ncpus=20:mpiprocs=5:ompthreads=2+1:ncpus=16:mpiprocs=4:ompthreads=2",
        "#PBS -l place=scatter",
    )


@pytest.mark.parametrize("scheduler", ["PBS", "SLURM"])
def test_precedence(scheduler):
    request = ResourceRequest(12, 16, 2)
    result = render_resource_directives(request, scheduler,
        config={"tasks_per_node": 8}, machine={"tasks_per_node": 6},
        cli={"tasks_per_node": 4, "node_count": 3})
    if scheduler == "SLURM":
        assert result[0] == "#SBATCH --nodes=3"
        assert result[2] == "#SBATCH --ntasks-per-node=4"
    else:
        assert result[0] == "#PBS -l select=3:ncpus=8:mpiprocs=4:ompthreads=2"


@pytest.mark.parametrize("override", [
    {"node_count": 1}, {"node_count": 13}, {"tasks_per_node": 9},
    {"total_task_count": 11}, {"cpus_per_task": 1}, {"node_count": True},
])
def test_conflicts(override):
    with pytest.raises(ValueError):
        render_resource_directives(ResourceRequest(12, 16, 2), "SLURM", cli=override)


def test_serial():
    assert render_resource_directives(ResourceRequest(1, 64), "PBS")[0] == (
        "#PBS -l select=1:ncpus=1:mpiprocs=1:ompthreads=1"
    )


def test_unsupported_dialect():
    with pytest.raises(ValueError, match="dialect"):
        render_resource_directives(ResourceRequest(1, 64), "TORQUE")


#EOC
