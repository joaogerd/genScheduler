#!/usr/bin/env python
#-----------------------------------------------------------------------------#
#                 genScheduler - HPC Submission Script Generator              #
#-----------------------------------------------------------------------------#
#BOP
#
# !MODULE: scheduler_directives.py
#
# !DESCRIPTION:
# Provides the SchedulerDirectives registry used to map logical scheduler
# directive names to their PBS- and SLURM-specific command-line representations.
#
# Directive metadata is loaded from YAML so that scheduler syntax remains
# separated from the script-generation logic. This keeps the generator reusable
# across machines while preserving the existing PBS/SLURM output contract.
#
# !INTERFACE:
# from genScheduler.scheduler_directives import SchedulerDirectives
#
# directives = SchedulerDirectives()
# directives.add_directive("queue", PBS="-q", SLURM="-p")
# value = directives.get_directive("queue", "SLURM")
#
# !PUBLIC MEMBER FUNCTIONS:
# SchedulerDirectives.__init__
#     Creates an empty directive registry.
#
# SchedulerDirectives.get_directive_names
#     Returns registered directive names in dictionary insertion order.
#
# SchedulerDirectives.add_directive
#     Adds or extends scheduler-specific representations for one logical name.
#
# SchedulerDirectives.get_directive
#     Returns the representation for a scheduler, or None when unavailable.
#
# SchedulerDirectives.load_directives_from_yaml
#     Loads directive definitions from a YAML file.
#
# !ARGUMENTS:
# directive_name
#     STRING. Logical directive name used by genScheduler.
#
# directive_options
#     KEYWORD MAPPING. Scheduler name to scheduler-specific option text.
#
# key
#     STRING. Logical directive name to retrieve.
#
# system
#     STRING. Scheduler identifier, currently PBS or SLURM.
#
# yaml_file
#     PATH-LIKE. YAML file containing the directives list.
#
# !RETURN VALUE:
# get_directive_names returns a list of strings.
# get_directive returns a scheduler option string or None.
# Other methods modify the registry in place and return None.
#
# !REMARKS:
# yaml.FullLoader is intentionally retained here to preserve the behavior of the
# original implementation for existing directive-definition files.
#
# !REVISION HISTORY:
# - 28th October 2023, J. G. de Mattos: Initial Version.
# - 03rd October 2026, J. G. de Mattos: Simplified the registry implementation
#   without changing lookup behavior.
# - 03rd October 2026, J. G. de Mattos: Restored and expanded ProTeX
#   documentation.
#
# !SEE ALSO:
# data/directives.yaml
# script_generator.py
#
#EOP
#-----------------------------------------------------------------------------#
#BOC

"""Scheduler directive registry used by genScheduler."""

from typing import Any, Dict, List, Optional

import yaml


class SchedulerDirectives:
    """Store and retrieve scheduler-specific directive strings."""

    def __init__(self) -> None:
        self.directives: Dict[str, Dict[str, Any]] = {}

    def get_directive_names(self) -> List[str]:
        """Return directive names in registry insertion order."""
        return list(self.directives.keys())

    def add_directive(self, directive_name: str, **directive_options: Any) -> None:
        """Add or extend scheduler-specific options for one directive."""
        if directive_name not in self.directives:
            self.directives[directive_name] = {}

        for system, option in directive_options.items():
            self.directives[directive_name][system] = option

    def get_directive(self, key: str, system: str) -> Optional[Any]:
        """Return one directive option, or None when it is not configured."""
        directive = self.directives.get(key)
        if directive is not None:
            return directive.get(system)
        return None

    def load_directives_from_yaml(self, yaml_file: Any) -> None:
        """Load scheduler mappings from a YAML directive definition file."""
        with open(yaml_file, "r") as file:
            data = yaml.load(file, Loader=yaml.FullLoader)

        for directive_data in data.get("directives", []):
            directive_name = directive_data.get("name")
            scheduler_directive = directive_data.get("scheduler_directive", {})
            self.add_directive(directive_name, **scheduler_directive)


#EOC
#-----------------------------------------------------------------------------#
