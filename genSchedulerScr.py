#!/usr/bin/env python
#-----------------------------------------------------------------------------#
#                 genScheduler - HPC Submission Script Generator              #
#-----------------------------------------------------------------------------#
#BOP
#
# !MODULE: genSchedulerScr.py
#
# !DESCRIPTION:
# Command-line entry point for genScheduler.
#
# The script parses CLI arguments, loads the selected YAML configuration,
# delegates script construction to genScheduler.script_generator and writes the
# generated submission script to disk.
#
# The historical invocation remains valid and continues to read config.yml from
# the current directory when --config is not supplied.
#
# !INTERFACE:
# genSchedulerScr.py [options]
#
# Programmatic interface:
#
#     from genSchedulerScr import main
#     main(argv=None)
#
# !ARGUMENTS:
# argv
#     OPTIONAL SEQUENCE OF STRINGS. Explicit CLI arguments for testing or
#     embedding. When None, arguments are read from the running process.
#
# Important command-line arguments include:
#     --machine
#     --scheduler
#     --mpi-tasks
#     --threads-per-mpi-task
#     --max-cores-per-node
#     --output
#     --config
#
# Additional scheduler directives are generated dynamically from
# genScheduler/data/directives.yaml.
#
# !RETURN VALUE:
# main returns None.
#
# !SIDE EFFECTS:
# Reads the selected YAML configuration file.
# Creates or replaces the generated submission-script file.
#
# !REMARKS:
# The default configuration filename is config.yml for backward compatibility.
# --config is additive and allows the user to execute genScheduler from a
# directory different from the one containing the configuration file.
#
# !REVISION HISTORY:
# - 26th October 2023, J. G. de Mattos: Initial Version.
# - 03rd October 2026, J. G. de Mattos: Made argv injectable and added --config
#   support while preserving the legacy command-line behavior.
# - 03rd October 2026, J. G. de Mattos: Restored and expanded ProTeX
#   documentation.
#
# !SEE ALSO:
# genScheduler/script_generator.py
#
#EOP
#-----------------------------------------------------------------------------#
#BOC

"""Command-line entry point for genScheduler."""

from genScheduler.script_generator import (
    generate_submission_script,
    parser,
    read_yaml_config,
)


def main(argv=None):
    """Generate and save a customized scheduler submission script."""
    args = parser(argv)
    config = read_yaml_config(args.config)
    script, filename = generate_submission_script(config, args)

    with open(filename, "w") as script_file:
        script_file.write(script)


if __name__ == "__main__":
    main()


#EOC
#-----------------------------------------------------------------------------#
