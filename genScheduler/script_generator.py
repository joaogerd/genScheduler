#!/usr/bin/env python
#-----------------------------------------------------------------------------#
#           Group on Data Assimilation Development - GDAD/CPTEC/INPE          #
#-----------------------------------------------------------------------------#
#BOP
#
# !SCRIPT:
#
# !DESCRIPTION:
#
# !CALLING SEQUENCE:
#
# !REVISION HISTORY: 
# 26 out 2023 - J. G. de Mattos - Initial Version
#
# !REMARKS:
#
#EOP
#-----------------------------------------------------------------------------#
#BOC

import yaml
from datetime import datetime
import re
from .parallel_processing_info import ParallelProcessingInfo
from .scheduler_directives import SchedulerDirectives

def initialize_directives():
    """
    Initializes and configures scheduler directives.

    Returns:
        SchedulerDirectives: An instance of the SchedulerDirectives class containing configured directives.
    """
    directives = SchedulerDirectives()

    # Directives for PBS and SLURM
    directives.add_directive("hash", PBS="#PBS", SLURM="#SBATCH")
    # Add more directives as needed for your specific scheduler.

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

def generate_submission_script(config, machine_name, scheduler_type, mpi_tasks, threads_per_mpi_task=None, max_cores_per_node=None):
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
        scheduler = initialize_directives()

        # Extract relevant information from the configuration.
        userDirectives = config['scheduler']['directives'][0]
        extra_info = config['scheduler']['extraInfo'][0]
        machine = config['machine'].get(machine_name, {})
        export = machine.get('export', [])
        modules = machine.get('modules', [])

        if max_cores_per_node is None:
            max_cores_per_node = config['machine'][machine_name].get('max_cores_per_node')
            if max_cores_per_node is None:
                raise ValueError('Maximum cores per node must be defined.')

        processing_info = ParallelProcessingInfo(max_cores_per_node, mpi_tasks, threads_per_mpi_task)


        # Start building the submission script.
        script = f"#!{userDirectives.get('shell', '/bin/bash')}\n"

        # Insert directives.
        for key, value in userDirectives.items():
            if scheduler.get_directive(key, scheduler_type):
                script += f"{scheduler.get_directive('hash', scheduler_type)} {scheduler.get_directive(key, scheduler_type)} {value}\n"

        # Handle special cases and optional directives.
        if is_key_not_present(userDirectives, 'tasks_per_node'):
            script += f"{scheduler.get_directive('hash', scheduler_type)} {scheduler.get_directive('tasks_per_node', scheduler_type)} {processing_info.tasks_per_node}\n"

        if is_key_not_present(userDirectives, 'node_count'):
            script += f"{scheduler.get_directive('hash', scheduler_type)} {scheduler.get_directive('node_count', scheduler_type)} {processing_info.nodes}\n"

        script += "\n# Extra information\n"
        ulimit_c = extra_info.get('ulimit_c')
        ulimit_s = extra_info.get('ulimit_s')
        if ulimit_c:
            script += f"ulimit -c {ulimit_c}\n"
        if ulimit_s:
            script += f"ulimit -s {ulimit_s}\n"

        if export:
            script += "\n# Set environment variables\n"
            for item in export:
                for key, value in item.items():
                    script += f"export {key}={value}\n"

        if modules:
            script += "\n# Load necessary modules\n"
            for module in modules:
                script += f"module load {module}\n"

        exec = extra_info.get('exec')
        if not exec:
            raise ValueError("Executable not configured.")

        redirect = extra_info.get('redirect_stdout')
        if redirect:
            # Find the mask in redirect using regular expression
            match = re.findall(r'%[YyjJmMdDhHISs]+', redirect)
            if match:
                mask = ''.join(match)
                # Get the current date and time
                current_datetime = datetime.now()
                # Format the date according to the specified mask
                formatted_date = current_datetime.strftime(mask)
                # Replace the mask with the formatted date
                redirect = redirect.replace(mask, formatted_date)

            exec += ' > ' + redirect

        script += "\n# Change to the working directory and execute the process.\n"
        if scheduler_type == 'PBS':
            script += "cd $PBS_O_WORKDIR\n"
            script += f"aprun -n {processing_info.pes} -N {processing_info.tasks_per_node} -d {processing_info.threads_per_mpi_task} ./{exec}\n"
        elif scheduler_type == 'SLURM':
            script += "cd $SLURM_SUBMIT_DIR\n"
            script += f"srun -n {processing_info.pes} -N {processing_info.tasks_per_node} -c {processing_info.threads_per_mpi_task} ./{exec}\n"

        return script

    except ValueError as ve:
        print(f"Error: {str(ve)}")
        exit(1)

#EOC
#-----------------------------------------------------------------------------#

