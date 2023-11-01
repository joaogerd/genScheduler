#!/usr/bin/env python
#-----------------------------------------------------------------------------#
#           Group on Data Assimilation Development - GDAD/CPTEC/INPE          #
#-----------------------------------------------------------------------------#
#BOP
#
# !SCRIPT:
# This is the __init__.py file for the gen_script_subm library. It serves as an
# indicator that this directory is a Python package.
#
# !DESCRIPTION:
# This file defines the package for generating customized submission scripts for
# job schedulers in high-performance computing environments (HPC). The package
# provides modules and functions to create, manage, and customize job submission
# scripts for various HPC systems.
#
# !CALLING SEQUENCE:
# This package is designed to be imported and used in other Python scripts and
# projects for creating HPC job submission scripts.
#
# !REVISION HISTORY: 
# - October 26, 2023, J. G. de Mattos: Initial Version
#
# !REMARKS:
# - The "gen_script_subm" library is part of the Group on Data Assimilation
#   Development (GDAD) project at CPTEC/INPE. It simplifies the process of
#   generating and customizing submission scripts for different HPC systems.
#
#EOP
#-----------------------------------------------------------------------------#
#BOC
# Import the necessary modules and functions from within the package
from .parallel_processing_info import ParallelProcessingInfo
from .scheduler_directives import SchedulerDirectives
from .script_generator import SchedulerDirectives, initialize_directives, read_yaml_config, parser

# Optionally, you can make functions or classes available at the package level
__all__ = ['ParallelProcessingInfo', 'SchedulerDirectives', 'generate_submission_script']

#EOC
#-----------------------------------------------------------------------------#

