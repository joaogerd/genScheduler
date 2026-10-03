# Contributing to genScheduler

genScheduler is a small HPC utility whose generated submission scripts are part of its public contract. Changes should therefore favor compatibility, clarity, and reproducibility over broad rewrites.

## Core development rules

### Preserve observable behavior

Refactoring must not silently change:

- generated PBS or SLURM directives;
- launcher commands;
- directive precedence;
- parallel-processing calculations;
- output filenames;
- shell sections and command ordering;
- documented CLI defaults;
- existing error behavior covered by characterization tests.

When a change intentionally modifies one of these behaviors, it must be treated as a separate behavioral change with dedicated tests and documentation.

### ProTeX documentation is mandatory

Every project-owned Python source file, including tests, must use the ProTeX documentation structure.

At minimum:

~~~text
#BOP
#
# !MODULE: module_name.py
#
# !DESCRIPTION:
# ...
#
# !REVISION HISTORY:
# - 26th October 2023, J. G. de Mattos: Initial Version.
# - 03rd October 2026, J. G. de Mattos:
#   - First change made on this date.
#   - Another change made on the same date.
#
#EOP
#BOC

... Python code ...

#EOC
~~~

Use additional ProTeX sections such as `!INTERFACE`, `!ARGUMENTS`, `!RETURN VALUE`, `!SIDE EFFECTS`, `!REMARKS`, and `!SEE ALSO` whenever they improve understanding.

Documentation must be updated together with the code. Removing documentation as part of cleanup or refactoring is not acceptable.

### Revision history convention

Revision history belongs to the project and is attributed to:

~~~text
J. G. de Mattos
~~~

When several modifications are made on the same date, write the date and author once and group the changes as subitems.

Do not repeat the same date/author heading for every change.

Do not remove previous revision-history entries.

## Testing strategy

Before changing established behavior, first characterize it with tests.

The current test suite covers areas including:

- PBS and SLURM generation;
- parallel-processing calculations;
- scheduler directive loading;
- config < machine < CLI precedence;
- portable configuration paths;
- explicit and derived node/task directives;
- shell environment rendering;
- ulimit ordering;
- timestamped redirects and output filenames;
- malformed YAML and missing configuration errors;
- package-level export behavior;
- mandatory ProTeX documentation.

Run the suite with:

~~~bash
python -m pip install -e ".[test]"
pytest -q
~~~

GitHub Actions validates supported Python versions on pushes and pull requests.

## Refactoring approach

Prefer small, reviewable changes.

A safe refactoring sequence is:

1. characterize the current behavior;
2. make one focused internal change;
3. update ProTeX documentation and revision history;
4. run the complete test suite;
5. only then continue to the next change.

Avoid unrelated cleanup in the same change.

## Configuration and portability

Machine-specific information belongs in user configuration rather than source code.

Scheduler syntax belongs in `genScheduler/data/directives.yaml`.

New functionality should avoid assumptions about:

- current working directory;
- a specific HPC machine;
- a specific user filesystem layout;
- locally installed modules beyond declared dependencies.

## License

The repository currently retains historical MIT metadata. The project is planned to migrate to a GNU license in a separate explicit change. License files and metadata should not be modified opportunistically as part of unrelated refactoring.
