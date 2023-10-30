# genScheduler

This project is a Python-based tool for generating submission scripts for job scheduling systems, with a focus on PBS and SLURM schedulers. It provides a flexible and configurable way to create submission scripts tailored to specific job requirements, making it easier to manage and automate job submissions in cluster or batch processing environments. The project also offers the ability to define machine-specific configurations, allowing users to adapt the submission scripts to different computing resources.

## Project Structure

The project is organized into the following directories and files:
```bash
.
├── genScheduler
│ ├── init.py
│ ├── parallel_processing_info.py
│ ├── scheduler_directives.py
│ └── script_generator.py
├── genSchedulerScr.py
├── LICENSE
├── README.md
├── setup.py
└── tests
```
- `genScheduler`: This directory contains the core modules of the project.
  - `__init__.py`: Package initialization file.
  - `parallel_processing_info.py`: Module for parallel processing information.
  - `scheduler_directives.py`: Module for managing scheduling directives.
  - `script_generator.py`: Module for generating submission scripts.

- `genSchedulerScr.py`: The main script of the project.

- `LICENSE`: The project's license file.

- `README.md`: This file, providing an overview of the project.

- `setup.py`: Python package setup file.

- `tests`: Directory for project tests.

## Scheduler Directives

The project uses scheduling directives to configure job submission in cluster or batch processing environments. The following scheduler directives are used:

- `hash`: Prefix for directives (e.g., `#PBS` or `#SBATCH`).
- Add more directives as needed for your specific scheduler.

## Usage

### YAML File Configuration

Directives are configured in the YAML file within the following sections:

- **scheduler > directives**: General configuration of directives.
- **scheduler > extraInfo**: Additional information for the submission script.
- **machine > <machine name>**: Specific settings for individual machines.

Make sure to adjust the directives in the YAML file as needed to meet the specific requirements of your task and machine.

Example YAML file:

```yaml
scheduler:
  directives:
    - queue: research
      node_count: 2
      total_task_count: 16
      # ... Other directives ...
  extraInfo:
    - exec: my_script.exe
      ulimit_c: unlimited
      # ... Other information ...
machine:
  XC50:
    export:
      - variable1: value1
      # ... Other configurations ...
  EGEON:
    # ... Configurations for the EGEON machine ...
```

### General Directives

- **queue**: Submission queue in the scheduler.
- **node_count**: Number of required nodes.
- **total_task_count**: Total number of MPI tasks.
- **tasks_per_node**: Number of MPI tasks per node.
- **cpus_per_task**: Number of CPUs per task (SLURM).
- **wall_clock_limit**: Execution time limit.
- **output_file**: Standard output file.
- **error_file**: Error messages output file.
- **combine_stdout_stderr**: Combine standard output and error.
- **copy_environment**: Copy the user's environment.
- **event_notification**: Notification events.
- **email_address**: Email address for notifications.
- **job_name**: Task name.
- **job_restart**: Permission to restart the task.
- **working_directory**: Working directory.
- **resource_sharing**: Resource sharing policy.
- **memory_size**: Required memory size.
- **account_to_charge**: Account to charge.
- **job_dependency**: Task dependencies.
- **job_host_preference**: Node preference (SLURM).
- **quality_of_service**: Quality of Service (QoS) (SLURM).
- **job_arrays**: Execution in array job format.
- **generic_resources**: Required generic resources (SLURM).
- **licenses**: Required licenses (SLURM).

  
## License

This project is licensed under the [License Name](LICENSE).
