#!/usr/bin/env python
#-----------------------------------------------------------------------------#
#           Group on Data Assimilation Development - GDAD/CPTEC/INPE          #
#-----------------------------------------------------------------------------#
#BOP
#
#

import math
#
# !SCRIPT:
#
class ParallelProcessingInfo:
#
#
# !DESCRIPTION:
#
    """
    Class for providing information related to parallel processing in cluster environments.

    Args:
        max_cores_per_node (int): Maximum number of cores per node.
        mpi_tasks (int): Total number of MPI tasks.
        threads_per_mpi_task (int, optional): Number of threads per MPI task. If not provided, it will be calculated internally.

    Attributes:
        max_cores_per_node (int): Maximum number of cores per node.
        mpi_tasks (int): Total number of MPI tasks.
        threads_per_mpi_task (int): Number of threads per MPI task.
        tasks_per_node (int): Number of tasks per node.
        pes (int): Total number of processes.
        nodes (int): Number of nodes needed to accommodate the tasks.

    Methods:
        calculate_tasks_per_node(): Calculate the number of tasks per node based on the number of threads per task.
        calculate_pes(): Calculate the total number of processes based on the number of threads per task.
        calculate_nodes(): Calculate the number of nodes needed to accommodate the tasks.
        calculate_threads_per_mpi_task(): Calculate the number of threads per task based on the number of tasks per node.
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
    def __init__(self, max_cores_per_node, mpi_tasks, threads_per_mpi_task=None):
        self.max_cores_per_node = max_cores_per_node
        self.mpi_tasks = mpi_tasks
        self.threads_per_mpi_task = threads_per_mpi_task if threads_per_mpi_task is not None else self.calculate_threads_per_mpi_task()

        self.tasks_per_node = self.calculate_tasks_per_node()
        self.pes = self.calculate_pes()
        self.nodes = self.calculate_nodes()

    def calculate_tasks_per_node(self):
        """
        Calculate the number of tasks per node based on the number of threads per task.

        Returns:
            int: Number of tasks per node.
        """
        return self.max_cores_per_node // self.threads_per_mpi_task

    def calculate_pes(self):
        """
        Calculate the total number of processes based on the number of threads per task.

        Returns:
            int: Total number of processes.
        """
        return self.mpi_tasks // self.threads_per_mpi_task

    def calculate_nodes(self):
        """
        Calculate the number of nodes needed to accommodate the tasks.

        Returns:
            int: Number of nodes needed.
        """
        return math.ceil(self.mpi_tasks / self.tasks_per_node)

    def calculate_threads_per_mpi_task(self):
        """
        Calculate the number of threads per task based on the number of tasks per node.

        Returns:
            int: Number of threads per task.
        """
        return self.max_cores_per_node // self.tasks_per_node


#EOC
#-----------------------------------------------------------------------------#

