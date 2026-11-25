#BOP
# !MODULE: job_directives.py
# !DESCRIPTION:
# Render portable non-resource job directives with explicit scheduler dialects.
# !INTERFACE:
# render_job_directives(scheduler, config=None, machine=None, cli=None)
# !REMARKS:
# Unsupported options fail explicitly; no silent translation of site extensions.
# Resource allocation and shell working directory are handled separately.
# !REVISION HISTORY:
# - 25th November 2026, J. G. de Mattos: Initial portable job directive renderer.
#EOP
#BOC

import re
from collections.abc import Mapping

_COMMON = {
    "queue": ("--partition=", "-q "),
    "job_name": ("--job-name=", "-N "),
    "wall_clock_limit": ("--time=", "-l walltime="),
    "output_file": ("--output=", "-o "),
    "error_file": ("--error=", "-e "),
    "account_to_charge": ("--account=", "-A "),
    "memory_size": ("--mem=", "-l mem="),
    "job_dependency": ("--dependency=", "-W depend="),
    "email_address": ("--mail-user=", "-M "),
    "event_notification": ("--mail-type=", "-m "),
    "job_arrays": ("--array=", "-J "),
}
_SLURM = {
    "working_directory": "--chdir=",
    "quality_of_service": "--qos=",
    "job_host_preference": "--nodelist=",
    "generic_resources": "--gres=",
    "licenses": "--licenses=",
}
_RESOURCE_KEYS = {"node_count", "tasks_per_node", "total_task_count", "cpus_per_task", "shell"}


def _value(key, value):
    if isinstance(value, bool) or not isinstance(value, (str, int)):
        raise ValueError(f"{key} requires a string or integer")
    value = str(value)
    # Conservative single-token grammar, not shell quoting.
    if not value or not re.fullmatch(r"[A-Za-z0-9_./:@%+,=\[\]-]+", value) or value.startswith("-"):
        raise ValueError(f"invalid directive value for {key}")
    return value


def render_job_directives(
    scheduler: str, *, config: Mapping | None = None,
    machine: Mapping | None = None, cli: Mapping | None = None,
) -> tuple[str, ...]:
    """Render recognized job options; explicit values override lower layers."""
    if scheduler not in ("SLURM", "PBS", "TORQUE"):
        raise ValueError("unsupported scheduler dialect")
    slurm = scheduler == "SLURM"
    prefix = "#SBATCH " if slurm else "#PBS "
    options = {}
    for layer in (config, machine, cli):
        if layer is not None:
            for key, value in layer.items():
                if value is not None and key not in _RESOURCE_KEYS:
                    options[key] = value
    lines = []
    for key, value in sorted(options.items()):
        if key in ("copy_environment", "job_restart", "combine_stdout_stderr"):
            if not isinstance(value, bool):
                raise ValueError(f"{key} requires a boolean")
            if key == "copy_environment":
                option = ("--export=ALL" if value else "--export=NONE") if slurm else ("-V" if value else None)
            elif key == "job_restart":
                option = ("--requeue" if value else "--no-requeue") if slurm else ("-r y" if value else "-r n")
            elif slurm:
                if value:
                    raise ValueError("Slurm stream joining requires output/error path policy")
                option = None
            else:
                option = "-j oe" if value else "-j n"
        elif key == "resource_sharing":
            if value not in ("exclusive", "shared"):
                raise ValueError("resource_sharing must be exclusive or shared")
            if slurm:
                if value == "shared":
                    raise ValueError("Slurm sharing depends on partition policy")
                option = "--exclusive"
            elif scheduler == "PBS":
                # Placement is already owned by the resource renderer.
                raise ValueError("PBS sharing must be resolved with placement")
            else:
                raise ValueError("Torque sharing is site dependent")
        elif key in _COMMON:
            flag = _COMMON[key][0 if slurm else 1]
            if scheduler == "TORQUE" and key == "job_arrays":
                flag = "-t "
            option = flag + _value(key, value)
        elif slurm and key in _SLURM:
            option = _SLURM[key] + _value(key, value)
        else:
            raise ValueError(f"unsupported directive {key} for {scheduler}")
        if option is not None:
            lines.append(prefix + option)
    return tuple(lines)


#EOC
