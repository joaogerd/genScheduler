#!/usr/bin/env python
"""Command-line entry point for genScheduler."""

from genScheduler.script_generator import (
    generate_submission_script,
    parser,
    read_yaml_config,
)


def main(argv=None):
    """Generate and save a customized scheduler submission script.

    With no argument, command-line parsing is identical to the historical CLI.
    Passing argv is supported for tests and embedding.
    """
    args = parser(argv)
    config = read_yaml_config(args.config)
    script, filename = generate_submission_script(config, args)

    with open(filename, "w") as script_file:
        script_file.write(script)


if __name__ == "__main__":
    main()
