#!/usr/bin/env python
#-----------------------------------------------------------------------------#
#           Group on Data Assimilation Development - GDAD/CPTEC/INPE          #
#-----------------------------------------------------------------------------#
#BOP
#
# !SCRIPT:
#
# !SCRIPT:
import yaml
class SchedulerDirectives:
#
# !DESCRIPTION:

    """
    A class for managing directives to be used with job scheduling systems.

    This class allows you to store and retrieve scheduling directives, such as those used with job submission
    in cluster or batch processing environments.

    Attributes:
        directives (dict): A dictionary to store scheduling directives, organized by directive names and their options.

    Methods:
        add_directive(directive_name, **directive_options):
            Adds a scheduling directive with specified options to the directives dictionary.

        get_directive(key, system):
            Retrieves a scheduling directive option for a specific system associated with a directive name.

    Example Usage:
        directives = SchedulerDirectives()
        directives.add_directive("partition", systemA="highmem", systemB="standard")
        partition_option = directives.get_directive("partition", "systemA")
    """

# !CALLING SEQUENCE:

    """
        directives = SchedulerDirectives()
        directives.add_directive("partition", systemA="highmem", systemB="standard")
        partition_option = directives.get_directive("partition", "systemA")
    """

#
# !REVISION HISTORY: 
# 28 out 2023 - J. G. de Mattos - Initial Version
#
# !REMARKS:
#
#EOP
#-----------------------------------------------------------------------------#
#BOC

    def __init__(self):
        """
        Initializes an instance of the SchedulerDirectives class with an empty directives dictionary.
        """
        self.directives = {}

    def add_directive(self, directive_name, **directive_options):
        """
        Adds a scheduling directive with specified options to the directives dictionary.

        Args:
            directive_name (str): The name of the scheduling directive.
            **directive_options: Keyword arguments representing system-specific options for the directive.

        Example:
            directives.add_directive("partition", systemA="highmem", systemB="standard")
        """
        if directive_name not in self.directives:
            self.directives[directive_name] = {}
        for system, option in directive_options.items():
            self.directives[directive_name][system] = option

    def get_directive(self, key, system):
        """
        Retrieves a scheduling directive option for a specific system associated with a directive name.

        Args:
            key (str): The name of the scheduling directive.
            system (str): The name of the system for which to retrieve the option.

        Returns:
            str: The scheduling directive option for the specified system and directive name, or None if not found.

        Example:
            partition_option = directives.get_directive("partition", "systemA")
        """
        directive = self.directives.get(key)
        if directive is not None:
            return directive.get(system)
        return None
        
    def load_directives_from_yaml(self, yaml_file):
        """
        Load scheduling directives from a YAML file and populate the directives dictionary.
    
        Args:
            yaml_file (str): The path to the YAML file containing scheduling directives.
    
        Example:
            directives.load_directives_from_yaml("directives.yaml")
        """
        with open(yaml_file, 'r') as file:
            data = yaml.load(file, Loader=yaml.FullLoader)
            for directive_data in data.get('directives', []):
                directive_name = directive_data.get('name')
                scheduler_directive = directive_data.get('scheduler_directive', {})
                self.add_directive(directive_name, **scheduler_directive)
#EOC
#-----------------------------------------------------------------------------#

