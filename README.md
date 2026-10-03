# genScheduler

genScheduler generates PBS and SLURM submission scripts from a YAML configuration plus command-line overrides. It is intentionally small: scheduler syntax lives in package data, machine details live in user configuration, and the generated launcher preserves the historical genScheduler output contract.

## What it does

The tool combines three sources of information:

1. scheduler directives from genScheduler/data/directives.yaml;
2. scheduler and machine defaults from a user YAML file;
3. command-line overrides.

For recognized scheduler directives, precedence is:

user YAML < machine configuration < command line

The generated script also includes configured ulimit values, environment variables, modules, machine commands, the scheduler working directory, and the PBS/SLURM launcher command.

## Installation

From a checkout:

~~~bash
python -m pip install .
~~~

For development and tests:

~~~bash
python -m pip install -e ".[test]"
pytest -q
~~~

The only runtime dependency outside the Python standard library is PyYAML.

## Configuration

By default the CLI reads config.yml from the current directory. A different file can now be supplied explicitly with --config, so generation no longer depends on running from the directory that contains the YAML file.

Example:

~~~yaml
scheduler:
  directives:
    job_name: gsiAnl
    queue: pesq
    account_to_charge: CPTEC
    shell: /bin/bash
    wall_clock_limit: 01:00:00

  extraInfo:
    exec: gsi.exe
    ulimit_c: unlimited
    ulimit_s: unlimited
    redirect_stdout: gsiStdout_%Y%m%d%H.log

machine:
  EGEON:
    max_cores_per_node: 64
    queue: batch
    export:
      - OMP_NUM_THREADS: 1
    modules:
      - openmpi4/4.1.1
    commands:
      - echo ready
~~~

## Usage

The historical invocation remains valid:

~~~bash
genSchedulerScr.py \
  --machine EGEON \
  --scheduler SLURM \
  --mpi-tasks 64 \
  --threads-per-mpi-task 2
~~~

To use a configuration stored elsewhere:

~~~bash
genSchedulerScr.py \
  --config /path/to/config.yml \
  --machine EGEON \
  --scheduler SLURM \
  --mpi-tasks 64 \
  --threads-per-mpi-task 2 \
  --output submit.sh
~~~

Use genSchedulerScr.py --help for the complete list of scheduler directives exposed as command-line options.

## Configuration sections

scheduler.directives contains scheduler defaults such as job_name, queue, account_to_charge, wall_clock_limit and shell.

scheduler.extraInfo contains execution details such as exec, ulimit_* entries and redirect_stdout.

machine.<NAME> contains machine-specific values such as max_cores_per_node, queue, export, modules and commands.

## Package structure

~~~text
.
├── .github/workflows/tests.yml
├── .gitignore
├── genScheduler/
│   ├── __init__.py
│   ├── data/directives.yaml
│   ├── parallel_processing_info.py
│   ├── scheduler_directives.py
│   └── script_generator.py
├── genSchedulerScr.py
├── pyproject.toml
├── setup.py
└── tests/
    ├── config.yml
    ├── test_characterization.py
    ├── test_cli.py
    ├── test_documentation.py
    └── test_generation_compatibility.py
~~~

## Documentation standard

Source-code documentation is part of the project contract, not optional cleanup. genScheduler uses the ProTeX convention maintained in [joaogerd/ProTexApp](https://github.com/joaogerd/ProTexApp).

Every Python source file, including tests, must preserve a complete ProTeX prologue using Python comment markers, including at least:

~~~text
#BOP
# !MODULE: ...
# !DESCRIPTION: ...
# !INTERFACE: ...
# !REVISION HISTORY: ...
#EOP
#BOC
...
#EOC
~~~

Additional markers such as `!ARGUMENTS`, `!RETURN VALUE`, `!SIDE EFFECTS`, `!REMARKS` and `!SEE ALSO` should be used whenever they clarify the contract of a module. Refactoring must update this documentation rather than remove it.

The CI suite discovers Python files dynamically and includes a documentation-contract test so newly added modules or tests cannot bypass the required ProTeX structure. Revision-history entries are also required to use the project attribution convention with `J. G. de Mattos`.

## Compatibility policy

The current generated script is treated as the compatibility reference. Refactoring therefore preserves the existing parallel calculations, directive formatting, precedence rules, error messages covered by characterization tests, shell sections, launcher commands and output content.

Scheduler directive ordering is not currently guaranteed because the legacy implementation combines directive names through a set. The test suite deliberately does not invent a new order contract. Making the order deterministic should be treated as a separate behavioral change.

## Tests

The repository includes characterization tests for:

- parallel processing calculations;
- scheduler directive loading;
- directive precedence;
- ulimit generation;
- missing configuration and executable errors;
- generated SLURM script content;
- portable --config handling;
- end-to-end CLI generation.

GitHub Actions runs the suite on pull requests and on pushes to main.

## Contributing

Development and refactoring rules, including the mandatory ProTeX documentation and revision-history conventions, are documented in [CONTRIBUTING.md](CONTRIBUTING.md).

## License

The repository currently retains the historical MIT metadata and an incomplete LICENSE file. The project owner has decided to migrate genScheduler to a GNU license. That migration will be made as a separate explicit change so the exact GNU license family/version can be selected and applied consistently to the LICENSE file, package metadata, source documentation and README.
