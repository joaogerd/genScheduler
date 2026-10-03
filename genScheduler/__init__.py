#!/usr/bin/env python
#-----------------------------------------------------------------------------#
#                 genScheduler - HPC Submission Script Generator              #
#-----------------------------------------------------------------------------#
#BOP
#
# !MODULE: __init__.py
#
# !DESCRIPTION:
# Defines the public package-level interface of genScheduler.
#
# The package exports the core parallel-processing model, scheduler directive
# registry and script-generation helpers used by applications embedding
# genScheduler.
#
# !INTERFACE:
# from genScheduler import (
#     ParallelProcessingInfo,
#     SchedulerDirectives,
#     generate_submission_script,
#     initialize_directives,
#     read_yaml_config,
#     parser,
# )
#
# !PUBLIC MEMBER FUNCTIONS:
# ParallelProcessingInfo
#     Parallel resource calculations used by generated launch commands.
#
# SchedulerDirectives
#     Scheduler-specific directive registry.
#
# generate_submission_script
#     Generates submission-script text and its output filename.
#
# initialize_directives
#     Loads the scheduler directive registry.
#
# read_yaml_config
#     Loads user YAML configuration.
#
# parser
#     Parses command-line arguments.
#
# !REVISION HISTORY:
# 26 Oct 2023 - J. G. de Mattos - Initial version.
# 03 Oct 2026 - OpenAI/ChatGPT - Clarified and corrected package exports while
#               preserving the established public API.
# 03 Oct 2026 - OpenAI/ChatGPT - Restored and expanded ProTeX documentation.
#
# !SEE ALSO:
# parallel_processing_info.py
# scheduler_directives.py
# script_generator.py
#
#EOP
#-----------------------------------------------------------------------------#
#BOC

"""Public package interface for genScheduler."""

from .parallel_processing_info import ParallelProcessingInfo
from .scheduler_directives import SchedulerDirectives
from .script_generator import (
    generate_submission_script,
    initialize_directives,
    parser,
    read_yaml_config,
)

__all__ = [
    "ParallelProcessingInfo",
    "SchedulerDirectives",
    "generate_submission_script",
    "initialize_directives",
    "read_yaml_config",
    "parser",
]


#EOC
#-----------------------------------------------------------------------------#
