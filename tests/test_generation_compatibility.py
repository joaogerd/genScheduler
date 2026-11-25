#-----------------------------------------------------------------------------#
#                 genScheduler - HPC Submission Script Generator              #
#-----------------------------------------------------------------------------#
#BOP
#
# !MODULE: test_generation_compatibility.py
#
# !DESCRIPTION:
# Compatibility tests for PBS generation, explicit resource directives, csh environment rendering, date masks and automatic output filenames.
#
# !INTERFACE:
# Executed by pytest as part of the genScheduler automated validation suite.
#
# !RETURN VALUE:
# No application value is returned. Tests pass silently or fail with assertions
# that identify compatibility or documentation regressions.
#
# !REVISION HISTORY:
# - 03rd October 2026, J. G. de Mattos:
#   - Expanded compatibility coverage for PBS, shell environments and dated
#     outputs.
#   - Added characterization for malformed YAML and missing maximum-core
#     configuration errors.
#   - Added end-to-end generation coverage using the repository's maintained
#     tests/config.yml example.
#
# !SEE ALSO:
# genScheduler/script_generator.py
# .github/workflows/tests.yml
#
#EOP
#-----------------------------------------------------------------------------#
#BOC

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from genScheduler.script_generator import generate_submission_script, read_yaml_config


def _args(**overrides):
    values = {
        "machine": "TEST",
        "scheduler": "PBS",
        "max_cores_per_node": None,
        "mpi_tasks": 40,
        "threads_per_mpi_task": 2,
        "output": "job.sh",
        "config": "config.yml",
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


def test_generate_pbs_launcher_and_working_directory():
    config = {
        "scheduler": {
            "directives": {
                "job_name": "pbs-job",
                "shell": "/bin/bash",
            },
            "extraInfo": {"exec": "model.exe"},
        },
        "machine": {
            "TEST": {
                "max_cores_per_node": 40,
            }
        },
    }

    script, filename = generate_submission_script(config, _args())

    assert filename == "job.sh"
    assert "#PBS -N pbs-job\n" in script
    assert "#PBS -l mppnppn 20\n" in script
    assert "#PBS -l nodes= 2\n" in script
    assert script.endswith(
        "# Change to the working directory and execute the process.\n"
        "cd $PBS_O_WORKDIR\n"
        "aprun -n 20 -N 20 -d 2 ./model.exe\n"
    )


def test_explicit_tasks_per_node_and_node_count_are_not_derived_again():
    config = {
        "scheduler": {
            "directives": {
                "job_name": "explicit",
                "shell": "/bin/bash",
                "tasks_per_node": "8",
                "node_count": 5,
            },
            "extraInfo": {"exec": "model.exe"},
        },
        "machine": {"TEST": {"max_cores_per_node": 40}},
    }

    script, _ = generate_submission_script(config, _args())

    assert script.count("#PBS -l mppnppn") == 1
    assert "#PBS -l mppnppn 8\n" in script
    assert script.count("#PBS -l nodes=") == 1
    assert "#PBS -l nodes= 5\n" in script


def test_csh_uses_setenv_with_legacy_rendering():
    config = {
        "scheduler": {
            "directives": {
                "job_name": "csh-job",
                "shell": "/bin/csh",
            },
            "extraInfo": {"exec": "model.exe"},
        },
        "machine": {
            "TEST": {
                "max_cores_per_node": 40,
                "export": [
                    {"OMP_NUM_THREADS": 2},
                    {"CASE": "control"},
                ],
            }
        },
    }

    script, _ = generate_submission_script(config, _args())

    assert "setenv OMP_NUM_THREADS 2\n" in script
    assert "setenv CASE control\n" in script
    assert "export OMP_NUM_THREADS" not in script


@patch("genScheduler.script_generator.datetime")
def test_redirect_datetime_mask_preserves_current_combined_mask_behavior(mock_datetime):
    mock_datetime.now.return_value.strftime.return_value = "2026100318"

    config = {
        "scheduler": {
            "directives": {"job_name": "dated", "shell": "/bin/bash"},
            "extraInfo": {
                "exec": "model.exe",
                "redirect_stdout": "stdout_%Y%m%d%H.log",
            },
        },
        "machine": {"TEST": {"max_cores_per_node": 40}},
    }

    script, _ = generate_submission_script(config, _args())

    mock_datetime.now.return_value.strftime.assert_called_once_with("%Y%m%d%H")
    assert "./model.exe > stdout_2026100318.log\n" in script


@patch("genScheduler.script_generator.datetime")
def test_automatic_filename_uses_job_name_and_current_timestamp(mock_datetime):
    mock_datetime.now.return_value.strftime.return_value = "2026-10-03_18-30-00"

    config = {
        "scheduler": {
            "directives": {"job_name": "forecast", "shell": "/bin/bash"},
            "extraInfo": {"exec": "model.exe"},
        },
        "machine": {"TEST": {"max_cores_per_node": 40}},
    }

    _, filename = generate_submission_script(config, _args(output=None))

    assert filename == "forecast_2026-10-03_18-30-00_submission_script.sh"
    mock_datetime.now.return_value.strftime.assert_called_once_with("%Y-%m-%d_%H-%M-%S")

def test_missing_max_cores_preserves_current_error_contract(capsys):
    config = {
        "scheduler": {
            "directives": {"job_name": "missing-cores", "shell": "/bin/bash"},
            "extraInfo": {"exec": "model.exe"},
        },
        "machine": {"TEST": {}},
    }

    with pytest.raises(SystemExit) as exc:
        generate_submission_script(config, _args(max_cores_per_node=None))

    assert exc.value.code == 1
    output = capsys.readouterr().out
    assert "Machine configuration is empty. Please check your configuration." in output
    assert "Machine name: TEST" in output
    assert "Error: Maximum cores per node must be defined." in output


def test_malformed_yaml_preserves_current_exit_behavior(tmp_path, capsys):
    config_file = tmp_path / "invalid.yml"
    config_file.write_text("scheduler: [invalid", encoding="utf-8")

    with pytest.raises(SystemExit) as exc:
        read_yaml_config(config_file)

    assert exc.value.code == 1
    assert "Error while reading the YAML file:" in capsys.readouterr().out


@patch("genScheduler.script_generator.datetime")
def test_repository_example_config_generates_expected_slurm_script(mock_datetime):
    mock_datetime.now.return_value.strftime.return_value = "2026100318"

    config_file = Path(__file__).with_name("config.yml")
    config = read_yaml_config(config_file)

    script, filename = generate_submission_script(
        config,
        _args(
            machine="EGEON",
            scheduler="SLURM",
            mpi_tasks=64,
            threads_per_mpi_task=1,
            output="gsi.sh",
        ),
    )

    assert filename == "gsi.sh"
    assert script.startswith("#!/bin/bash\n")
    assert "#SBATCH --job-name= gsiAnl\n" in script
    assert "#SBATCH -p batch\n" in script
    assert "#SBATCH --account= CPTEC\n" in script
    assert "#SBATCH -t 01:00:00\n" in script
    assert "#SBATCH --tasks-per-node 64\n" in script
    assert "#SBATCH -N 1\n" in script
    assert "export OMP_NUM_THREADS=1\n" in script
    assert "module load openmpi4/4.1.1\n" in script
    assert "cd diretorio_A\n" in script
    assert "rm arquivo_B\n" in script
    assert script.endswith(
        "# Change to the working directory and execute the process.\n"
        "cd $SLURM_SUBMIT_DIR\n"
        "srun -n 64 -N 64 -c 1 ./gsi.exe > gsiStdout_2026100318.log\n"
    )


#EOC
#-----------------------------------------------------------------------------#
