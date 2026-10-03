#!/usr/bin/env python
#-----------------------------------------------------------------------------#
#                 genScheduler - HPC Submission Script Generator              #
#-----------------------------------------------------------------------------#
#BOP
#
# !MODULE: parallel_processing_info.py
#
# !DESCRIPTION:
# Defines the ParallelProcessingInfo class used by genScheduler to calculate
# the parallel-resource values inserted into generated PBS and SLURM scripts.
#
# The calculations in this module are part of the externally observable
# behavior of genScheduler. For compatibility reasons, the formulas are kept
# exactly as in the original implementation, even where alternative formulas
# could be considered more conventional.
#
# !INTERFACE:
# from genScheduler.parallel_processing_info import ParallelProcessingInfo
#
# info = ParallelProcessingInfo(
#     max_cores_per_node,
#     mpi_tasks,
#     threads_per_mpi_task,
# )
#
# !PUBLIC MEMBER FUNCTIONS:
# ParallelProcessingInfo.__init__
#     Initializes the parallel-processing description and derives all dependent
#     quantities.
#
# ParallelProcessingInfo.calculate_tasks_per_node
#     Returns max_cores_per_node // threads_per_mpi_task.
#
# ParallelProcessingInfo.calculate_pes
#     Returns mpi_tasks // threads_per_mpi_task.
#
# ParallelProcessingInfo.calculate_nodes
#     Returns ceil(mpi_tasks / tasks_per_node).
#
# ParallelProcessingInfo.calculate_threads_per_mpi_task
#     Preserves the historical implicit-thread calculation.
#
# !ARGUMENTS:
# max_cores_per_node
#     INTEGER. Maximum number of cores available on one compute node.
#
# mpi_tasks
#     INTEGER. MPI-task quantity provided by the caller.
#
# threads_per_mpi_task
#     INTEGER or None. Number of threads assigned to each MPI task.
#
# !RETURN VALUE:
# Class instances expose:
#     tasks_per_node
#     pes
#     nodes
#     threads_per_mpi_task
#
# !REMARKS:
# The normal command-line interface always provides threads_per_mpi_task.
# The historical None path is intentionally left unchanged because correcting
# it would alter an existing error path and is therefore a behavioral change.
#
# !REVISION HISTORY:
# - 28th October 2023, J. G. de Mattos: Initial Version.
# - 03rd October 2026, J. G. de Mattos:
#   - Refactored structure and type documentation while preserving the original
#     numerical behavior.
#   - Restored and expanded ProTeX documentation.
#
# !SEE ALSO:
# script_generator.py
#
#EOP
#-----------------------------------------------------------------------------#
#BOC

"""Parallel resource calculations used by generated scheduler launch commands."""

import math
from typing import Optional


class ParallelProcessingInfo:
    """Calculate the legacy parallel-processing values used by genScheduler."""

    def __init__(
        self,
        max_cores_per_node: int,
        mpi_tasks: int,
        threads_per_mpi_task: Optional[int] = None,
    ) -> None:
        self.max_cores_per_node = max_cores_per_node
        self.mpi_tasks = mpi_tasks
        self.threads_per_mpi_task = (
            threads_per_mpi_task
            if threads_per_mpi_task is not None
            else self.calculate_threads_per_mpi_task()
        )

        self.tasks_per_node = self.calculate_tasks_per_node()
        self.pes = self.calculate_pes()
        self.nodes = self.calculate_nodes()

    def calculate_tasks_per_node(self) -> int:
        """Return tasks per node using the historical integer division."""
        return self.max_cores_per_node // self.threads_per_mpi_task

    def calculate_pes(self) -> int:
        """Return the historical process-count calculation."""
        return self.mpi_tasks // self.threads_per_mpi_task

    def calculate_nodes(self) -> int:
        """Return the historical node-count calculation."""
        return math.ceil(self.mpi_tasks / self.tasks_per_node)

    def calculate_threads_per_mpi_task(self) -> int:
        """Return the historical implicit thread calculation."""
        return self.max_cores_per_node // self.tasks_per_node


#EOC
#-----------------------------------------------------------------------------#
