"""Generate PBS and SLURM submission scripts.

This module keeps the legacy genScheduler rendering contract while separating
configuration loading, CLI construction, and script rendering into small helpers.
The generated text intentionally preserves the historical formatting.
"""

from __future__ import annotations

import argparse
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import yaml

from .parallel_processing_info import ParallelProcessingInfo
from .scheduler_directives import SchedulerDirectives


_PACKAGE_DIR = Path(__file__).resolve().parent
_DEFAULT_DIRECTIVES_FILE = _PACKAGE_DIR / "data" / "directives.yaml"


def _read_directive_definitions(
    directives_file: str | os.PathLike[str] | None = None,
) -> list[dict[str, Any]]:
    """Load CLI/directive metadata from the package YAML file.

    A custom path is accepted primarily for testing and embedding. Omitting it
    preserves the historical behavior of loading data/directives.yaml from the
    installed package.
    """
    path = Path(directives_file) if directives_file is not None else _DEFAULT_DIRECTIVES_FILE
    with path.open("r") as yaml_file:
        data = yaml.safe_load(yaml_file)
    return data["directives"]


def build_argument_parser(
    directives_file: str | os.PathLike[str] | None = None,
) -> argparse.ArgumentParser:
    """Build the command-line parser without consuming process arguments."""
    directive_definitions = _read_directive_definitions(directives_file)

    type_mapping = {
        "str": str,
        "int": int,
        "float": float,
        "bool": bool,
    }

    argument_parser = argparse.ArgumentParser(
        description="Generate customized submission scripts for PBS and SLURM schedulers."
    )
    argument_parser.add_argument(
        "--machine", type=str, required=True, help="Machine name (e.g., XC50, EGEON)"
    )
    argument_parser.add_argument(
        "--scheduler", type=str, required=True, help="Script type (PBS or SLURM)"
    )
    argument_parser.add_argument(
        "--max-cores-per-node",
        type=int,
        required=False,
        help="Maximum number of cores per node",
    )
    argument_parser.add_argument(
        "--mpi-tasks", type=int, required=True, help="Number of MPI Tasks"
    )
    argument_parser.add_argument(
        "--threads-per-mpi-task",
        type=int,
        required=True,
        help="Number of cores per MPI task",
    )
    argument_parser.add_argument(
        "--output",
        type=str,
        help="Specify the output filename for the generated content.",
    )
    argument_parser.add_argument(
        "--config",
        default="config.yml",
        help="Path to the YAML configuration file (default: config.yml).",
    )

    for entry in directive_definitions:
        name = entry["name"]
        argument_parser.add_argument(
            f"--{name}",
            type=type_mapping.get(entry["type"], str),
            required=entry["required"],
            help=entry["description"],
        )

    return argument_parser


def parser(
    argv: Sequence[str] | None = None,
    directives_file: str | os.PathLike[str] | None = None,
) -> argparse.Namespace:
    """Parse command-line arguments.

    Calling parser() with no arguments remains backward compatible. argv and
    directives_file are optional seams that make the CLI deterministic and
    independently testable.
    """
    return build_argument_parser(directives_file).parse_args(argv)


def initialize_directives(
    directives_file: str | os.PathLike[str] | None = None,
) -> SchedulerDirectives:
    """Create the scheduler-directive registry used by script generation."""
    directives = SchedulerDirectives()
    directives.add_directive("hash", PBS="#PBS", SLURM="#SBATCH")
    directives.load_directives_from_yaml(
        Path(directives_file) if directives_file is not None else _DEFAULT_DIRECTIVES_FILE
    )
    return directives


def calculate_variables(
    max_cores_per_node: int,
    mpi_tasks: int,
    threads_per_mpi_task: int,
) -> tuple[int, int, int]:
    """Return the legacy tasks_per_node, pes and nodes calculation."""
    tasks_per_node = max_cores_per_node // threads_per_mpi_task
    pes = mpi_tasks // threads_per_mpi_task
    nodes = (mpi_tasks + max_cores_per_node - 1) // max_cores_per_node
    return tasks_per_node, pes, nodes


def read_yaml_config(file_path: str | os.PathLike[str]) -> Any:
    """Read a YAML configuration file, preserving the legacy CLI error contract."""
    try:
        with Path(file_path).open("r") as yml_file:
            return yaml.safe_load(yml_file)
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        raise SystemExit(1)
    except Exception as exc:
        print(f"Error while reading the YAML file: {str(exc)}")
        raise SystemExit(1)


def is_key_not_present(dictionary: Mapping[str, Any], key: str) -> bool:
    """Return whether key is absent from dictionary."""
    return key not in dictionary


def create_ulimit_command(data: Mapping[str, Any]) -> list[str]:
    """Convert ulimit_* configuration entries into shell options."""
    ulimit_commands: list[str] = []

    for key, value in data.items():
        if key.startswith("ulimit_"):
            resource = key.replace("ulimit_", "")
            ulimit_commands.append(f"-{resource} {value}")

    return ulimit_commands


def merge_keys(
    standard_keys: Iterable[str], *dictionaries: Mapping[str, Any]
) -> list[str]:
    """Return configured keys that are recognized scheduler directives.

    The set-based implementation is intentionally retained because the historical
    code did not define an ordering contract for scheduler directive lines.
    """
    standard_keys = set(standard_keys)
    merged_keys: set[str] = set()

    for dictionary in dictionaries:
        merged_keys.update(key for key in dictionary.keys() if key in standard_keys)

    return list(merged_keys)


def _configured_value(
    directive: str,
    directives: Mapping[str, Any],
    machine: Mapping[str, Any],
    args: argparse.Namespace,
) -> Any:
    """Resolve one directive using legacy config < machine < CLI precedence."""
    value = None

    if directive in directives:
        value = directives[directive]
    if directive in machine:
        value = machine[directive]

    cli_value = getattr(args, directive, None)
    if cli_value is not None:
        value = cli_value

    return value


def _append_environment(
    script: str,
    export: Sequence[Mapping[str, Any]],
    shell_name: str,
) -> str:
    if not export:
        return script

    script += "\n# Define environment variables\n"
    command = "setenv" if shell_name in ("tsh", "csh") else "export"

    for item in export:
        for key, value in item.items():
            rendered_value = " " + str(value) if command == "setenv" else f"={value}"
            script += f"{command} {key}{rendered_value}\n"

    return script


def _append_modules(script: str, modules: Sequence[str]) -> str:
    if modules:
        script += "\n# Load essential modules\n"
        for module in modules:
            script += f"module load {module}\n"
    return script


def _append_commands(script: str, commands: Sequence[str]) -> str:
    if commands:
        script += "\n# Execute necessary shell commands\n"
        for command in commands:
            script += f"{command}\n"
    return script


def _render_executable(extra_info: Mapping[str, Any]) -> str:
    executable = extra_info.get("exec")
    if not executable:
        raise ValueError("Executable not configured.")

    redirect = extra_info.get("redirect_stdout")
    if redirect:
        match = re.findall(r"%[YyjJmMdDhHISs]+", redirect)
        if match:
            mask = "".join(match)
            formatted_date = datetime.now().strftime(mask)
            redirect = redirect.replace(mask, formatted_date)

        executable += " > " + redirect

    return executable


def _append_launcher(
    script: str,
    scheduler_type: str,
    processing_info: ParallelProcessingInfo,
    executable: str,
) -> str:
    script += "\n# Change to the working directory and execute the process.\n"

    if scheduler_type == "PBS":
        script += "cd $PBS_O_WORKDIR\n"
        script += (
            f"aprun -n {processing_info.pes} "
            f"-N {processing_info.tasks_per_node} "
            f"-d {processing_info.threads_per_mpi_task} ./{executable}\n"
        )
    elif scheduler_type == "SLURM":
        script += "cd $SLURM_SUBMIT_DIR\n"
        script += (
            f"srun -n {processing_info.pes} "
            f"-N {processing_info.tasks_per_node} "
            f"-c {processing_info.threads_per_mpi_task} ./{executable}\n"
        )

    return script


def generate_submission_script(
    config: Mapping[str, Any],
    args: argparse.Namespace,
    directives_file: str | os.PathLike[str] | None = None,
) -> tuple[str, str]:
    """Generate a submission script while preserving legacy output semantics."""
    try:
        scheduler = initialize_directives(directives_file)
        scheduler_type = args.scheduler

        scheduler_config = config["scheduler"]
        directives = scheduler_config.get("directives", [])
        extra_info = scheduler_config.get("extraInfo", [])

        machine_name = getattr(args, "machine")
        machine = config["machine"].get(machine_name, {})
        export = machine.get("export", [])
        modules = machine.get("modules", [])
        commands = machine.get("commands", [])

        shebang = directives.get("shell", "/bin/bash")
        shell_name = os.path.basename(shebang)

        if not machine:
            print("Machine configuration is empty. Please check your configuration.")
            print(f"Machine name: {machine_name}")

        max_cores_per_node = (
            args.max_cores_per_node
            if args.max_cores_per_node is not None
            else machine.get("max_cores_per_node")
        )
        if max_cores_per_node is None:
            raise ValueError("Maximum cores per node must be defined.")

        processing_info = ParallelProcessingInfo(
            max_cores_per_node,
            args.mpi_tasks,
            args.threads_per_mpi_task,
        )

        standard_directives = scheduler.get_directive_names()
        directives_args = {
            key: value for key, value in vars(args).items() if value is not None
        }
        all_directives = merge_keys(
            standard_directives, directives_args, directives, machine
        )

        script = f"#!{shebang}\n"
        job_name = scheduler_type

        for directive in all_directives:
            value = _configured_value(directive, directives, machine, args)

            if directive == "job_name":
                job_name = value

            scheduler_option = scheduler.get_directive(directive, scheduler_type)
            if scheduler_option:
                script += (
                    f"{scheduler.get_directive('hash', scheduler_type)} "
                    f"{scheduler_option} {value}\n"
                )

        if is_key_not_present(directives, "tasks_per_node"):
            script += (
                f"{scheduler.get_directive('hash', scheduler_type)} "
                f"{scheduler.get_directive('tasks_per_node', scheduler_type)} "
                f"{processing_info.tasks_per_node}\n"
            )

        if is_key_not_present(directives, "node_count"):
            script += (
                f"{scheduler.get_directive('hash', scheduler_type)} "
                f"{scheduler.get_directive('node_count', scheduler_type)} "
                f"{processing_info.nodes}\n"
            )

        script += "\n# Additional HPC Configuration\n"

        for option in create_ulimit_command(extra_info):
            script += f"ulimit {option}\n"

        script = _append_environment(script, export, shell_name)
        script = _append_modules(script, modules)
        script = _append_commands(script, commands)

        executable = _render_executable(extra_info)
        script = _append_launcher(script, scheduler_type, processing_info, executable)

        if args.output:
            filename = args.output
        else:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"{job_name}_{timestamp}_submission_script.sh"

        return script, filename

    except ValueError as exc:
        print(f"Error: {str(exc)}")
        raise SystemExit(1)
