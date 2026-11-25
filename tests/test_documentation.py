#-----------------------------------------------------------------------------#
#                 genScheduler - HPC Submission Script Generator              #
#-----------------------------------------------------------------------------#
#BOP
#
# !MODULE: test_documentation.py
#
# !DESCRIPTION:
# Documentation-contract tests that enforce the mandatory ProTeX structure and
# revision-history attribution across every Python source file in the project.
#
# The test intentionally discovers Python files dynamically instead of keeping a
# manually maintained list. This prevents newly added modules or tests from
# bypassing the project documentation standard.
#
# !INTERFACE:
# Executed by pytest as part of the genScheduler automated validation suite.
#
# !RETURN VALUE:
# No application value is returned. The test fails when a Python source file
# lacks mandatory ProTeX markers, invalid block ordering or a revision entry
# attributed to J. G. de Mattos.
#
# !REVISION HISTORY:
# - 03rd October 2026, J. G. de Mattos:
#   - Added automated enforcement of the ProTeX documentation and
#     revision-history contract.
#   - Extended the documentation contract to every Python source file in the
#     repository.
#   - Enforced grouping of same-day revision entries under a single date and
#     author heading.
#   - Restricted discovery to project-owned Python sources so local virtual
#     environments and third-party files are not inspected.
#
# !SEE ALSO:
# README.md
# .github/workflows/tests.yml
#
#EOP
#-----------------------------------------------------------------------------#
#BOC

from pathlib import Path
import re

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]

PROTEX_SOURCE_FILES = sorted(
    [
        *(PROJECT_ROOT / "genScheduler").rglob("*.py"),
        *(PROJECT_ROOT / "tests").rglob("*.py"),
        *PROJECT_ROOT.glob("*.py"),
    ]
)

REQUIRED_MARKERS = [
    "#BOP",
    "# !MODULE:",
    "# !DESCRIPTION:",
    "# !REVISION HISTORY:",
    "#EOP",
    "#BOC",
    "#EOC",
]


@pytest.mark.parametrize(
    "source_file",
    PROTEX_SOURCE_FILES,
    ids=lambda path: str(path.relative_to(PROJECT_ROOT)),
)
def test_python_sources_preserve_protex_documentation_contract(source_file):
    content = source_file.read_text(encoding="utf-8")

    missing = [marker for marker in REQUIRED_MARKERS if marker not in content]

    assert not missing, (
        f"{source_file.relative_to(PROJECT_ROOT)} is missing required ProTeX "
        f"documentation markers: {', '.join(missing)}"
    )

    assert content.index("#BOP") < content.index("#EOP")
    assert content.index("#BOC") < content.rindex("#EOC")

    revision_start = content.index("# !REVISION HISTORY:")
    revision_end = content.index("#EOP", revision_start)
    revision_history = content[revision_start:revision_end]

    assert "J. G. de Mattos:" in revision_history, (
        f"{source_file.relative_to(PROJECT_ROOT)} must attribute revision-history "
        "entries to J. G. de Mattos"
    )

    dated_entries = re.findall(
        r"^# - (.+?), J\. G\. de Mattos:",
        revision_history,
        flags=re.MULTILINE,
    )
    assert len(dated_entries) == len(set(dated_entries)), (
        f"{source_file.relative_to(PROJECT_ROOT)} repeats a revision date. "
        "Group changes from the same day as subitems under one date."
    )


#EOC
#-----------------------------------------------------------------------------#
