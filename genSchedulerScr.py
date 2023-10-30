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
from genScheduler.script_generator import read_yaml_config, generate_submission_script
import argparse

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--machine", required=True, help="Nome da máquina (por exemplo, XC50, EGEON)")
    parser.add_argument("--scheduler", required=True, help="Tipo de script (PBS ou SLURM)")
    parser.add_argument("--max-cores-per-node", type=int, help="Número máximo de cores por nó")
    parser.add_argument("--mpi-tasks", type=int, required=True, help="Número de MPI Tasks")
    parser.add_argument("--threads-per-mpi-task", type=int, required=True, help="Número de cores por tarefa MPI")
    args = parser.parse_args()


    config = read_yaml_config('config.yml')
    script = generate_submission_script(config, args.machine, args.scheduler, args.mpi_tasks, args.threads_per_mpi_task, args.max_cores_per_node)


    with open(f'{args.scheduler}_submission_script.sh', 'w') as script_file:
        script_file.write(script)

if __name__ == '__main__':
    
    main()


#EOC
#-----------------------------------------------------------------------------#

