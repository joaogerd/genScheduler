#-----------------------------------------------------------------------------#
#                 genScheduler - HPC Submission Script Generator              #
#-----------------------------------------------------------------------------#
#BOP
#
# !MODULE: test_characterization.py
#
# !DESCRIPTION:
# Characterization tests that freeze the observable behavior of the original genScheduler implementation before and during refactoring.
#
# !INTERFACE:
# Executed by pytest as part of the genScheduler automated validation suite.
#
# !RETURN VALUE:
# No application value is returned. Tests pass silently or fail with assertions
# that identify compatibility or documentation regressions.
#
# !REVISION HISTORY:
# - 03rd October 2026, J. G. de Mattos: Added characterization tests for legacy scheduler behavior.
#
# !SEE ALSO:
# genScheduler/script_generator.py
# .github/workflows/tests.yml
#
#EOP
#-----------------------------------------------------------------------------#
#BOC

from types import SimpleNamespace

import pytest

from genScheduler.parallel_processing_info import ParallelProcessingInfo
from genScheduler.scheduler_directives import SchedulerDirectives
from genScheduler.script_generator import (
    create_ulimit_command,
    generate_submission_script,
    initialize_directives,
    merge_keys,
    read_yaml_config,
)


def _args(**overrides):
    values = {
        "machine": "EGEON",
        "scheduler": "SLURM",
        "max_cores_per_node": None,
        "mpi_tasks": 64,
        "threads_per_mpi_task": 2,
        "output": "job.sh",
        "queue": None,
        "node_count": None,
        "total_task_count": None,
        "tasks_per_node": None,
        "cpus_per_task": None,
        "wall_clock_limit": None,
        "output_file": None,
        "error_file": None,
        "combine_stdout_stderr": None,
        "copy_environment": None,
        "event_notification": None,
        "email_address": None,
        "job_name": None,
        "job_restart": None,
        "working_directory": None,
        "resource_sharing": None,
        "memory_size": None,
        "account_to_charge": None,
        "job_dependency": None,
        "job_host_preference": None,
        "quality_of_service": None,
        "job_arrays": None,
        "generic_resources": None,
        "licenses": None,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def _config():
    return {
        "scheduler": {
            "directives": {
                "job_name": "sample",
                "queue": "default",
                "account_to_charge": "PROJECT",
                "shell": "/bin/bash",
                "wall_clock_limit": "01:00:00",
            },
            "extraInfo": {
                "exec": "model.exe",
                "ulimit_c": "unlimited",
                "ulimit_s": "unlimited",
                "redirect_stdout": "stdout.log",
            },
        },
        "machine": {
            "EGEON": {
                "max_cores_per_node": 64,
                "queue": "batch",
                "export": [{"OMP_NUM_THREADS": 2}],
                "modules": ["mpi"],
                "commands": ["echo ready"],
            }
        },
    }


def test_parallel_processing_characterizes_current_calculation():
    info = ParallelProcessingInfo(40, 160, 2)

    assert info.tasks_per_node == 20
    assert info.pes == 80
    assert info.nodes == 8


def test_scheduler_directives_loaded_from_packaged_yaml():
    directives = initialize_directives()

    assert directives.get_directive("hash", "PBS") == "#PBS"
    assert directives.get_directive("hash", "SLURM") == "#SBATCH"
    assert directives.get_directive("queue", "PBS") == "-q"
    assert directives.get_directive("queue", "SLURM") == "-p"
    assert "job_name" in directives.get_directive_names()


def test_scheduler_directives_missing_values_return_none():
    directives = SchedulerDirectives()
    directives.add_directive("queue", PBS="-q")

    assert directives.get_directive("queue", "SLURM") is None
    assert directives.get_directive("missing", "PBS") is None


def test_ulimit_command_preserves_mapping_order():
    data = {
        "exec": "model.exe",
        "ulimit_c": "unlimited",
        "other": "ignored",
        "ulimit_s": 8192,
    }

    assert create_ulimit_command(data) == ["-c unlimited", "-s 8192"]


def test_merge_keys_characterizes_current_membership_semantics():
    merged = merge_keys(
        ["job_name", "queue", "wall_clock_limit"],
        {"job_name": "a", "ignored": 1},
        {"queue": "q", "ignored_too": 2},
    )

    # Current implementation intentionally offers no ordering guarantee because it
    # builds the result through a set. Characterization therefore protects the
    # membership semantics without inventing a new ordering contract.
    assert set(merged) == {"job_name", "queue"}


def test_read_yaml_config_missing_file_exits_with_current_message(tmp_path, capsys):
    missing = tmp_path / "missing.yml"

    with pytest.raises(SystemExit) as exc:
        read_yaml_config(missing)

    assert exc.value.code == 1
    assert f"Error: The file '{missing}' was not found." in capsys.readouterr().out


def test_generate_slurm_script_preserves_current_external_output():
    script, filename = generate_submission_script(_config(), _args())

    assert filename == "job.sh"

    lines = script.splitlines()
    assert lines[0] == "#!/bin/bash"

    directive_lines = {line for line in lines if line.startswith("#SBATCH")}
    assert directive_lines == {
        "#SBATCH --job-name= sample",
        "#SBATCH -p batch",
        "#SBATCH --account= PROJECT",
        "#SBATCH -t 01:00:00",
        "#SBATCH --tasks-per-node 32",
        "#SBATCH -N 2",
    }

    tail = script[script.index("\n# Additional HPC Configuration") :]
    assert tail == """\n# Additional HPC Configuration
ulimit -c unlimited
ulimit -s unlimited

# Define environment variables
export OMP_NUM_THREADS=2

# Load essential modules
module load mpi

# Execute necessary shell commands
echo ready

# Change to the working directory and execute the process.
cd $SLURM_SUBMIT_DIR
srun -n 32 -N 32 -c 2 ./model.exe > stdout.log
"""


def test_command_line_values_keep_highest_precedence():
    args = _args(queue="cli", job_name="cli-job")

    script, filename = generate_submission_script(_config(), args)

    assert "#SBATCH -p cli\n" in script
    assert "#SBATCH --job-name= cli-job\n" in script
    assert filename == "job.sh"


def test_missing_machine_with_cli_core_count_keeps_warning_and_generates(capsys):
    config = _config()
    args = _args(machine="UNKNOWN", max_cores_per_node=64)

    script, _ = generate_submission_script(config, args)

    out = capsys.readouterr().out
    assert "Machine configuration is empty. Please check your configuration." in out
    assert "Machine name: UNKNOWN" in out
    assert "cd $SLURM_SUBMIT_DIR" in script


def test_missing_executable_exits_as_current_behavior(capsys):
    config = _config()
    del config["scheduler"]["extraInfo"]["exec"]

    with pytest.raises(SystemExit) as exc:
        generate_submission_script(config, _args())

    assert exc.value.code == 1
    assert "Error: Executable not configured." in capsys.readouterr().out

#EOC
#-----------------------------------------------------------------------------#
