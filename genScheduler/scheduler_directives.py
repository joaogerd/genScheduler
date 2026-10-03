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
        """Load scheduler mappings from a YAML directive definition file.

        FullLoader is intentionally retained to preserve the parser behavior of
        the original implementation for existing directive files.
        """
        with open(yaml_file, "r") as file:
            data = yaml.load(file, Loader=yaml.FullLoader)

        for directive_data in data.get("directives", []):
            directive_name = directive_data.get("name")
            scheduler_directive = directive_data.get("scheduler_directive", {})
            self.add_directive(directive_name, **scheduler_directive)
