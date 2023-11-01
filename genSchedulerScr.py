#!/usr/bin/env python
#-----------------------------------------------------------------------------#
#           Group on Data Assimilation Development - GDAD/CPTEC/INPE          #
#-----------------------------------------------------------------------------#
#BOP
#
# !SCRIPT: generate_submission_script.py
#
# !DESCRIPTION:
# This script is part of the genScheduler package, and it generates a customized
# submission script for job scheduling systems in high-performance computing (HPC)
# environments. It uses the provided configuration and command-line arguments to
# create a submission script suitable for the specified scheduler (PBS or SLURM).
# The script can be used as a standalone tool or integrated into other workflows
# for managing HPC job submissions.
#
# !CALLING SEQUENCE:
# To execute this script, run it as a standalone Python program. The script will
# read the configuration from the "config.yml" file and create a submission script
# based on the specified scheduler type (PBS or SLURM) and the provided command-line
# arguments.
#
# Example Usage:
#   python generate_submission_script.py --machine [MachineName] --scheduler [PBS/SLURM]
#   [--max-cores-per-node MaxCores] --mpi-tasks MpiTasks --threads-per-mpi-task ThreadsPerTask
#
# !REVISION HISTORY: 
# - October 26, 2023, J. G. de Mattos: Initial Version
#
# !REMARKS:
# - The "genScheduler" package is developed as part of the Group on Data Assimilation
#   Development (GDAD) project at CPTEC/INPE. It simplifies the process of creating
#   and customizing submission scripts for different HPC systems.
# - This script is a standalone utility to generate submission scripts based on
#   configuration and user-provided arguments, making it suitable for various HPC
# environments.
#
#EOP
#-----------------------------------------------------------------------------#
#BOC
from genScheduler.script_generator import read_yaml_config, generate_submission_script, parser

def main():
    """
    Main function to generate and save a customized submission script.

    This function reads the user's command-line arguments, loads the configuration
    from the "config.yml" file, generates a submission script based on the specified
    scheduler type and provided arguments, and saves the script to a file.

    Example Usage:
    - Run this script to generate a submission script for job scheduling.

    Returns:
    - None
    """
    
    args   = parser()
    config = read_yaml_config('config.yml')
    script, filename = generate_submission_script(config, args)

    # Save the generated submission script to the generated filename
    with open(filename, 'w') as script_file:
        script_file.write(script)

if __name__ == '__main__':
    main()

#EOC
#-----------------------------------------------------------------------------#

