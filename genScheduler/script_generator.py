#!/usr/bin/env python
#-----------------------------------------------------------------------------#
#           Group on Data Assimilation Development - GDAD/CPTEC/INPE          #
#-----------------------------------------------------------------------------#
#BOP
#
# !SCRIPT: submission_script_generator.py
#
# !DESCRIPTION:
# This Python script generates submission scripts for job scheduling systems 
# (PBS or SLURM) used in high-performance computing (HPC) environments. It allows 
# users to create customized submission scripts with various directives, 
# machine-specific settings, and parallel processing configurations.

# !CALLING SEQUENCE:
# This script is intended to be run from the command line. Users should provide 
# specific arguments, such as the target machine, scheduler type (PBS or SLURM), 
# the number of MPI tasks, and other relevant options.

# !REVISION HISTORY: 
# - 26th October 2023, J. G. de Mattos: Initial Version

# !REMARKS:
# - This script is part of the Group on Data Assimilation Development (GDAD) project at CPTEC/INPE.
# - It facilitates the generation of submission scripts for various HPC systems.
# - Users should configure the directives, machine-specific settings, and other options in a YAML configuration file.
#EOP
#-----------------------------------------------------------------------------#
#BOC

import os
import argparse
import yaml
from datetime import datetime
import re
from .parallel_processing_info import ParallelProcessingInfo
from .scheduler_directives import SchedulerDirectives

def parser():
   # Determine the path to the package directory
    package_directory = os.path.dirname(os.path.abspath(__file__))  # Get the current script's

    # Path to the YAML file within the package directory
    yaml_file_path = os.path.join(package_directory, 'data', 'directives.yaml')

    # Read the YAML configuration including the list of directives
    with open(yaml_file_path, 'r') as yaml_file:
        data = yaml.safe_load(yaml_file)
    
    # Merge the directive options from the YAML file with the existing directive definitions
    result = {}
    for entry in data['directives']:
        result[entry['name']] = {
            'description': entry['description'],
            'type': entry['type'],
            'required': entry['required']
        }
    
    # Mapeamento de tipos para funções correspondentes
    type_mapping = {
        'str': str,
        'int': int,
        'float': float,
        'bool': bool  # Se desejar suportar 'bool'
    }

    # Initialize the argument parser
    parser = argparse.ArgumentParser(description='Generate customized submission scripts for PBS and SLURM schedulers.')

    parser.add_argument("--machine", type=str,required=True, help="Machine name (e.g., XC50, EGEON)")
    parser.add_argument("--scheduler", type=str, required=True, help="Script type (PBS or SLURM)")
    parser.add_argument("--max-cores-per-node", type=int, required=False,help="Maximum number of cores per node")
    parser.add_argument("--mpi-tasks", type=int, required=True, help="Number of MPI Tasks")
    parser.add_argument("--threads-per-mpi-task", type=int, required=True, help="Number of cores per MPI task")
    
    # Iterate through the merged directive definitions and add them as command-line arguments
    for name, arg_options in result.items():
        arg_name = f"--{name}"
        arg_type = arg_options['type']
        arg_type = type_mapping.get(arg_options['type'], str)  # Use str as the default if the type is not found in the mapping
        arg_requ = arg_options['required']
        arg_help = arg_options['description']
        parser.add_argument(arg_name,type=arg_type, required=arg_requ, help=arg_help)
    
    # Parse the command-line arguments
    return  parser.parse_args()
  

def initialize_directives():
    """
    Initializes and configures scheduler directives.

    Returns:
        SchedulerDirectives: An instance of the SchedulerDirectives class containing configured directives.
    """
    directives = SchedulerDirectives()

    # Directives for PBS and SLURM
    directives.add_directive("hash", PBS="#PBS", SLURM="#SBATCH")

    # Determine the path to the package directory
    package_directory = os.path.dirname(os.path.abspath(__file__))  # Get the current script's

    # Path to the YAML file within the package directory
    yaml_file_path = os.path.join(package_directory, 'data', 'directives.yaml')

    # Load the directives from the YAML file
    directives.load_directives_from_yaml(yaml_file_path)

    return directives

def calculate_variables(max_cores_per_node, mpi_tasks, threads_per_mpi_task):
    """
    Calculate variables such as tasks per node, pes, and nodes based on provided inputs.

    Args:
        max_cores_per_node (int): Maximum number of cores per node.
        mpi_tasks (int): Total number of MPI tasks.
        threads_per_mpi_task (int): Number of threads per MPI task.

    Returns:
        tuple: A tuple containing tasks_per_node, pes, and nodes.
    """
    tasks_per_node = max_cores_per_node // threads_per_mpi_task
    pes = mpi_tasks // threads_per_mpi_task
    nodes = (mpi_tasks + max_cores_per_node - 1) // max_cores_per_node
    return tasks_per_node, pes, nodes

def read_yaml_config(file_path):
    """
    Read and parse a YAML configuration file.

    Args:
        file_path (str): Path to the YAML configuration file.

    Returns:
        dict: Parsed configuration as a dictionary.
    """
    try:
        with open(file_path, 'r') as yml_file:
            return yaml.safe_load(yml_file)
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        exit(1)
    except Exception as e:
        print(f"Error while reading the YAML file: {str(e)}")
        exit(1)

def is_key_not_present(dictionary, key):
    """
    Check if a key is not present in a dictionary.

    Args:
        dictionary (dict): The dictionary to check.
        key (str): The key to check for.

    Returns:
        bool: True if the key is not present in the dictionary, False otherwise.
    """
    return key not in dictionary

def create_ulimit_command(data):
    """
    Create ulimit commands based on keys and values from a YAML file.

    Parameters:
    - data (dict): A dictionary containing keys and values from a YAML file.

    Returns:
    - list: A list of ulimit commands generated from the YAML data.

    This function parses a dictionary with keys that start with "ulimit_" and their corresponding values,
    and converts them into ulimit commands. Each ulimit command is in the form of "-[resource] [value]".

    Example:
    If the input data is:
    {
        'ulimit_c': 'unlimited',
        'ulimit_s': 'unlimited'
    }

    The function will return:
    ['-c unlimited', '-s unlimited']
    """
    ulimit_commands = []

    for key, value in data.items():
        if key.startswith('ulimit_'):
            resource = key.replace('ulimit_', '')
            ulimit_option = f"-{resource} {value}"
            ulimit_commands.append(ulimit_option)

    return ulimit_commands

def merge_keys(standard_keys, *dictionaries):
    """
    Merges keys from multiple dictionaries while filtering them against a list of standard keys.

    Parameters:
    standard_keys (list): A list of standard keys to filter against.
    *dictionaries (dict): Any number of dictionaries to merge.

    Returns:
    list: A list containing unique keys found in the input dictionaries that are also present in the standard keys list.

    Example:
    standard_keys = ['job_name', 'account_to_charge', 'shell', 'wall_clock_limit', 'max_cores_per_node', 'queue']
    directives = {'job_name': 'gsiAnl', 'account_to_charge': 'CPTEC', 'shell': '/bin/bash', 'wall_clock_limit': '01:00:00'}
    machine = {'max_cores_per_node': 64, 'queue': 'batch', 'export': [{'OMP_NUM_THREADS': 1}], 'modules': ['ohpc', 'netcdf', 'netcdf-fortran', 'scalapack', 'openblas', 'openmpi4/4.1.1'], 'commands': ['cd directory_A', 'rm file_B']}
    another_dict = {'key1': 'value1', 'key2': 'value2'}

    merged_keys = merge_keys(standard_keys, directives, machine, another_dict)
    print(merged_keys)
    # Output: ['queue', 'max_cores_per_node', 'wall_clock_limit', 'job_name', 'shell', 'account_to_charge']

    This function takes a list of standard keys and any number of dictionaries as input.
    It returns a list of unique keys found in the input dictionaries that are also present in the standard keys list.
    """
    merged_keys = set()
    
    for dictionary in dictionaries:
        merged_keys.update(key for key in dictionary.keys() if key in standard_keys)
    
    return list(merged_keys)



def generate_submission_script(config, args):
    """
    Generate a submission script for job scheduling systems (PBS/SLURM) based on the provided configuration and inputs.

    Args:
        config (dict): Configuration data obtained from a YAML file.
        machine_name (str): Name of the target machine defined in the configuration.
        scheduler_type (str): Type of scheduler (PBS or SLURM).
        mpi_tasks (int): Total number of MPI tasks.
        threads_per_mpi_task (int): Number of threads per MPI task.
        max_cores_per_node (int, optional): Maximum number of cores per node. If not provided, it will be retrieved from the configuration.

    Returns:
        str: The generated submission script as a string.
    """
    try:
        # - This part of the script initializes and organizes key information needed for script generation and execution.
        # - It includes configuration directives, machine-specific settings, shell information, and handling of core allocation.
        # - The script ensures that required values are defined and sets up parallel processing information.

        # Initialize Scheduler and Gather Relevant Information
        scheduler = initialize_directives()
        scheduler_type = args.scheduler
        
        # Extract and Organize Information from Configuration
        # - Directives are configuration options for the scheduler.
        # - ExtraInfo may include additional information for script execution.
        # - Machine-specific settings are based on the provided machine name.
        # - Export, modules, and commands are machine-specific configuration details.
        # - Shebang specifies the shell used in the script.
        # - Shell name is determined from the shebang.
        directives   = config['scheduler'].get('directives', [])
        extra_info   = config['scheduler'].get('extraInfo', [])
        machine_name = getattr(args, 'machine')
        machine      = config['machine'].get(machine_name, {})
        export       = machine.get('export', [])
        modules      = machine.get('modules', [])
        commands     = machine.get('commands', [])
        shebang      = directives.get('shell', '/bin/bash')
        shell_name   = os.path.basename(shebang)
        
        # Handle Maximum Cores per Node Configuration
        max_cores_per_node = args.max_cores_per_node if args.max_cores_per_node is not None else machine.get('max_cores_per_node')
        if max_cores_per_node is None:
            raise ValueError('Maximum cores per node must be defined.')
        
        # Initialize Parallel Processing Information
        # - This section sets up information related to parallel processing, including
        #   maximum cores per node, MPI tasks, and threads per MPI task.
        processing_info = ParallelProcessingInfo(max_cores_per_node, args.mpi_tasks, args.threads_per_mpi_task)

        # Retrieve all available scheduling directives from the configuration file (directives.yaml).
        standard_directives = scheduler.get_directive_names()
        
        # Extract and filter scheduling directives from the command-line arguments provided by the user.
        directives_args = {key: value for key, value in vars(args).items() if value is not None}
        
        # Merge and prioritize scheduling directives, combining standard directives, user-provided directives,
        # and machine-specific directives for optimal scheduling decisions.
        all_directives = merge_directives(standard_directives, directives_args, directives, machine)

        # Start building the submission script.
        script = f"#!{shebang}\n"

        # Process the list of directives from the file
        for directive in all_directives:
            value = None

            # Handle default values from the YAML file
            if directive in directives:
                value = directives[directive]
        
            # Handle machine-specific values
            if directive in machine:
                value = machine[directive]
        
            # Handle command line values
            if getattr(args, directive, None) is not None:
                value = getattr(args, directive)

            # Insert directives.
            if scheduler.get_directive(directive, scheduler_type):
                script += f"{scheduler.get_directive('hash', scheduler_type)} {scheduler.get_directive(directive, scheduler_type)} {value}\n"

        # Handle Special Cases and Optional Directives
        # - Set tasks_per_node if not specified in directives
        # - Set node_count if not specified in directives
        if is_key_not_present(directives, 'tasks_per_node'):
            script += f"{scheduler.get_directive('hash', scheduler_type)} {scheduler.get_directive('tasks_per_node', scheduler_type)} {processing_info.tasks_per_node}\n"
        
        if is_key_not_present(directives, 'node_count'):
            script += f"{scheduler.get_directive('hash', scheduler_type)} {scheduler.get_directive('node_count', scheduler_type)} {processing_info.nodes}\n"
        
        script += "\n# Additional HPC Configuration\n"
        
        # Include additional HPC-specific options here
        # Example:
        # - Set GPU options
        # - Configure memory allocation
        # - Specify HPC-specific directives
        
        # Extract ulimit options from 'extra_info' and append them to a script.
        ulimit_options = create_ulimit_command(extra_info)
        for option in ulimit_options:
            script += f"ulimit {option}\n"
            
        # Export Environment Variables
        if export:
            script += "\n# Define environment variables\n"
            cmd = "setenv" if shell_name in ("tsh", "csh") else "export"
            for item in export:
                for key, value in item.items():
                    script += f"{cmd} {key}{' ' + str(value) if cmd == 'setenv' else f'={value}'}\n"

        # Load Required Modules
        if modules:
            script += "\n# Load essential modules\n"
            for module in modules:
                script += f"module load {module}\n"

        # Include Shell Commands
        if commands:
            script += "\n# Execute necessary shell commands\n"
            for command in commands:
                script += f"{command}\n"

        # Execute the Process
        # - Ensure the executable (exec) is configured
        exec = extra_info.get('exec')
        if not exec:
            raise ValueError("Executable not configured.")
        
        # Redirect Standard Output (Optional)
        redirect = extra_info.get('redirect_stdout')
        if redirect:
            # Identify placeholders in the redirect string using regular expressions
            match = re.findall(r'%[YyjJmMdDhHISs]+', redirect)
            if match:
                mask = ''.join(match)
                # Get the current date and time
                current_datetime = datetime.now()
                # Format the date according to the specified mask
                formatted_date = current_datetime.strftime(mask)
                # Replace the mask with the formatted date
                redirect = redirect.replace(mask, formatted_date)
        
            # Append the redirection of standard output to the executable command
            exec += ' > ' + redirect
        
        # Configure Working Directory and Execute the Process
        script += "\n# Change to the working directory and execute the process.\n"
        if scheduler_type == 'PBS':
            script += "cd $PBS_O_WORKDIR\n"
            script += f"aprun -n {processing_info.pes} -N {processing_info.tasks_per_node} -d {processing_info.threads_per_mpi_task} ./{exec}\n"
        elif scheduler_type == 'SLURM':
            script += "cd $SLURM_SUBMIT_DIR\n"
            script += f"srun -n {processing_info.pes} -N {processing_info.tasks_per_node} -c {processing_info.threads_per_mpi_task} ./{exec}\n"
        
        # Additional Information:
        # - This section prepares and executes the specified process within the HPC environment.
        # - It includes handling the executable, potential standard output redirection, and setting the working directory.
        # - The script is designed to work with both PBS and SLURM job schedulers, ensuring compatibility with various HPC systems.

        return script

    except ValueError as ve:
        print(f"Error: {str(ve)}")
        exit(1)

#EOC
#-----------------------------------------------------------------------------#

