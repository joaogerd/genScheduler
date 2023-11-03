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

## Installing the genScheduler

This guide provides instructions for installing the Python script `genScheduler` on your system using the `setup.py` file. The `genScheduler` script is a flexible tool for generating submission scripts for task scheduling systems, with a focus on PBS and SLURM schedulers. You can install it in the standard way or in a custom directory.

### Standard Installation

To install the Python script in the standard way, follow these steps:

1. **Get the Source Code**:
   - Download the source code of the `genScheduler` script from the project's GitHub repository.

2. **Navigate to the Project Directory**:
   - Open your terminal or command prompt.
   - Navigate to the directory where you downloaded the project's source code.

3. **Install the Script**:
   - Execute the following command to install the script:

     ```bash
     python setup.py install
     ```

   - The script will be installed on your system.

4. **Verify the Installation**:
   - To verify if the script was installed correctly, you can run it using the following command:

     ```bash
     genSchedulerScr.py --help
     ```

   - This will display the available options and the script's help.

### Custom Directory Installation

If you want to install the `genScheduler` Python script in a custom directory, follow these steps:

1. **Get the Source Code**:
   - Download the source code of the `genScheduler` script from the project's GitHub repository.

2. **Navigate to the Project Directory**:
   - Open your terminal or command prompt.
   - Navigate to the directory where you downloaded the project's source code.

3. **Install in a Custom Directory**:
   - Execute the following command, replacing `/Path/To/Directory` with the absolute path to the directory where you want to install the script:

     ```bash
     python setup.py install --prefix=/Path/To/Directory
     ```

   - The script will be installed in the specified custom directory.

4. **Verify the Installation**:
   - To verify if the script was installed correctly in the custom directory, you can run it using the following command:

     ```bash
     /Path/To/Directory/bin/genSchedulerScr.py --help
     ```

   - This will display the available options and the script's help.

Now you have the `genScheduler` script installed on your system or in a custom directory, ready to generate submission scripts for PBS and SLURM schedulers.

## Usage


### Scheduler Directives

The project uses scheduling directives to configure job submission in cluster or batch processing environments. The following scheduler directives are used:

- `queue`: Submission queue in the scheduler.
- `node_count`: Number of required nodes.
- `total_task_count`: Total number of MPI tasks.
- `tasks_per_node`: Number of MPI tasks per node.
- `cpus_per_task`: Number of CPUs per task (SLURM).
- `wall_clock_limit`: Execution time limit.
- `output_file`: Standard output file.
- `error_file`: Error messages output file.
- `combine_stdout_stderr`: Combine standard output and error.
- `copy_environment`: Copy the user's environment.
- `event_notification`: Notification events.
- `email_address`: Email address for notifications.
- `job_name`: Task name.
- `job_restart`: Permission to restart the task.
- `working_directory`: Working directory.
- `resource_sharing`: Resource sharing policy.
- `memory_size`: Required memory size.
- `account_to_charge`: Account to charge.
- `job_dependency`: Task dependencies.
- `job_host_preference`: Node preference (SLURM).
- `quality_of_service`: Quality of Service (QoS) (SLURM).
- `job_arrays`: Execution in array job format.
- `generic_resources`: Required generic resources (SLURM).
- `licenses`: Required licenses (SLURM).

### YAML File Configuration

Directives are configured in the YAML file within the following sections:

- `**scheduler > directives**`: General configuration of directives.
- `**scheduler > extraInfo**`: Additional information for the submission script.
- `**machine > <machine name>`**: Specific settings for individual machines.

Make sure to adjust the directives in the YAML file as needed to meet the specific requirements of your task and machine.
### Running the Script

Assuming that you have already installed the genScheduler package and have the `genSchedulerScr.py` script in your system's PATH, here are the steps to generate a submission script:

1. **Preparation of the `config.yml` File**:
   - Create or edit a `config.yml` file that contains the desired configurations for the submission script. You can follow the example format provided below:

   ```yaml
   scheduler:
     directives:
       - job_name: myJob
         queue: myQueue
         wall_clock_time: 01:00:00

     extraInfo:
       - exec: myExecutable
         ulimit_c: unlimited
         ulimit_s: unlimited
         redirect_stdout: myJob_%Y%m%d%H.log
     commands:
       - shell command 1
       - shell command 2

   machine:
     MY_MACHINE:
       queue: machine_specific_queue
       wall_clock_time: specific_walltime
       export:
         - my_environment_var: my_value
       modules:
         - my_module
       commands:
         - machine specific shell command 1
         - machine specific shell command 2
   ```
2. **Execute the Script**:
   - Open your terminal or command prompt.
   - Navigate to the directory where your `config.yml` file is located.

   To generate the submission script, use the following command:

   ```bash
   genSchedulerScr.py --machine YOUR_MACHINE --scheduler SCHEDULER --max-cores-per-node MAX_CORES --mpi-tasks MPI_TASKS --threads-per-mpi-task THREADS
   ```
   
   - `YOUR_MACHINE`: Replace it with the name of the target machine as defined in your config.yml.
   - `SCHEDULER`: Choose the type of scheduler you want to use (PBS or SLURM).
   - `MAX_CORES`: Set the maximum number of cores per node.
   - `MPI_TASKS`: Specify the number of MPI tasks.
   - `THREADS`: Specify the number of cores per MPI task.

   ##### Script Generation:
      Upon executing the script, you will receive the generated submission script as output. The script will include all the specified directives, options, and configurations from your config.yml file and the command-line arguments.

      The generated submission script will be saved as a separate file in the same directory where your config.yml file is located. You can customize the output filename as needed. The filename will typically reflect your job name, timestamp, or other specified naming conventions.

      Now you have a customized submission script ready for use with your chosen scheduler.

      Please ensure that you provide the appropriate settings in your config.yml file and follow the instructions for running the script. Make sure that the Python environment used for execution is compatible with the environment where you intend to use the submission script.

## License

This project is licensed under the [License Name](LICENSE).
