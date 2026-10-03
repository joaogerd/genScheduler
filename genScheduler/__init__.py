#!/usr/bin/env python
#-----------------------------------------------------------------------------#
#                 genScheduler - HPC Submission Script Generator              #
#-----------------------------------------------------------------------------#
#BOP
#
# !MODULE: __init__.py
#
# !DESCRIPTION:
# Initializes the genScheduler Python package and exposes the package-level
# symbols historically made available by the project.
#
# This file intentionally preserves the existing import/export behavior. Any
# inconsistency between imported names and __all__ is considered part of the
# current package behavior and must be addressed, if desired, in a separate
# compatibility-reviewed change.
#
# !INTERFACE:
# import genScheduler
#
# Historically imported at package level:
#     ParallelProcessingInfo
#     SchedulerDirectives
#     initialize_directives
#     read_yaml_config
#     parser
#
# __all__ historically declares:
#     ParallelProcessingInfo
#     SchedulerDirectives
#     generate_submission_script
#
# !REMARKS:
# generate_submission_script is present in __all__ but is not imported into the
# package namespace by the historical implementation. This inconsistency is
# documented rather than silently corrected in the behavior-preserving
# refactoring.
#
# !REVISION HISTORY:
# 26 Oct 2023 - J. G. de Mattos - Initial version.
# 03 Oct 2026 - OpenAI/ChatGPT - Restored and expanded ProTeX documentation
#               without changing the historical package export behavior.
#
# !SEE ALSO:
# parallel_processing_info.py
# scheduler_directives.py
# script_generator.py
#
#EOP
#-----------------------------------------------------------------------------#
#BOC

from .parallel_processing_info import ParallelProcessingInfo
from .scheduler_directives import SchedulerDirectives
from .script_generator import SchedulerDirectives, initialize_directives, read_yaml_config, parser

__all__ = ['ParallelProcessingInfo', 'SchedulerDirectives', 'generate_submission_script']


#EOC
#-----------------------------------------------------------------------------#
