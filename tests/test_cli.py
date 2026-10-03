from genScheduler.script_generator import parser
from genSchedulerScr import main


def test_parser_keeps_legacy_default_config_filename():
    args = parser(
        [
            "--machine",
            "EGEON",
            "--scheduler",
            "SLURM",
            "--mpi-tasks",
            "64",
            "--threads-per-mpi-task",
            "2",
        ]
    )
    assert args.config == "config.yml"


def test_cli_accepts_config_outside_current_directory(tmp_path):
    config_file = tmp_path / "custom.yml"
    output_file = tmp_path / "generated.sh"
    config_file.write_text(
        """scheduler:
  directives:
    job_name: portable
    shell: /bin/bash
  extraInfo:
    exec: model.exe
machine:
  GENERIC:
    max_cores_per_node: 64
""",
        encoding="utf-8",
    )

    main(
        [
            "--config",
            str(config_file),
            "--machine",
            "GENERIC",
            "--scheduler",
            "SLURM",
            "--mpi-tasks",
            "64",
            "--threads-per-mpi-task",
            "2",
            "--output",
            str(output_file),
        ]
    )

    generated = output_file.read_text(encoding="utf-8")
    assert generated.startswith("#!/bin/bash\n")
    assert "#SBATCH --job-name= portable\n" in generated
    assert "#SBATCH --tasks-per-node 32\n" in generated
    assert "#SBATCH -N 2\n" in generated
    assert generated.endswith(
        "# Change to the working directory and execute the process.\n"
        "cd $SLURM_SUBMIT_DIR\n"
        "srun -n 32 -N 32 -c 2 ./model.exe\n"
    )
