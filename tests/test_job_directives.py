#BOP
# !MODULE: test_job_directives.py
# !DESCRIPTION:
# Check portable job directive syntax, precedence and unsupported options.
# !REVISION HISTORY:
# - 25th November 2026, J. G. de Mattos: Initial tests.
#EOP
#BOC

import pytest
from genScheduler.job_directives import render_job_directives


def test_slurm_corrected_options():
    assert render_job_directives("SLURM", config={
        "job_dependency": "afterok:123", "working_directory": "/tmp/run",
        "job_restart": False, "copy_environment": True,
    }) == ("#SBATCH --export=ALL", "#SBATCH --dependency=afterok:123",
           "#SBATCH --no-requeue", "#SBATCH --chdir=/tmp/run")


@pytest.mark.parametrize("scheduler,array", [("PBS", "-J"), ("TORQUE", "-t")])
def test_pbs_options(scheduler, array):
    assert render_job_directives(scheduler, config={
        "job_arrays": "1-5", "job_dependency": "afterok:123",
        "combine_stdout_stderr": True, "copy_environment": True,
        "job_restart": False,
    }) == ("#PBS -j oe", "#PBS -V", f"#PBS {array} 1-5",
           "#PBS -W depend=afterok:123", "#PBS -r n")


def test_precedence_and_resource_separation():
    assert render_job_directives("SLURM", config={"queue": "a"},
        machine={"queue": "b"}, cli={"queue": "c", "node_count": 2}
    ) == ("#SBATCH --partition=c",)


@pytest.mark.parametrize("scheduler,options", [
    ("PBS", {"working_directory": "/tmp"}),
    ("PBS", {"resource_sharing": "exclusive"}),
    ("SLURM", {"combine_stdout_stderr": True}),
    ("SLURM", {"job_restart": "false"}),
    ("SLURM", {"job_name": "test\n#SBATCH --exclusive"}),
    ("SLURM", {"job_name": "-bad"}),
    ("TORQUE", {"licenses": "foo"}),
])
def test_unsupported_or_unsafe(scheduler, options):
    with pytest.raises(ValueError):
        render_job_directives(scheduler, config=options)


#EOC
