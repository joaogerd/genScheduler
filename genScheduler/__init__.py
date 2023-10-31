#!/usr/bin/env python
#-----------------------------------------------------------------------------#
#           Group on Data Assimilation Development - GDAD/CPTEC/INPE          #
#-----------------------------------------------------------------------------#
#BOP
#
# !SCRIPT:
#
# !DESCRIPTION:
#               Este é o arquivo __init__.py para a biblioteca gen_script_subm.
#               Ele indica que este diretório é um pacote Python.
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
# Import the necessary modules and functions from within the package
from .parallel_processing_info import ParallelProcessingInfo
from .scheduler_directives import SchedulerDirectives
from .script_generator import SchedulerDirectives, initialize_directives, read_yaml_config, parser

# Optionally, you can make functions or classes available at the package level
__all__ = ['ParallelProcessingInfo', 'SchedulerDirectives', 'generate_submission_script']


#EOC
#-----------------------------------------------------------------------------#

