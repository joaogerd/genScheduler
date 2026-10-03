from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]

PROTEX_SOURCE_FILES = [
    PROJECT_ROOT / "genScheduler" / "__init__.py",
    PROJECT_ROOT / "genScheduler" / "parallel_processing_info.py",
    PROJECT_ROOT / "genScheduler" / "scheduler_directives.py",
    PROJECT_ROOT / "genScheduler" / "script_generator.py",
    PROJECT_ROOT / "genSchedulerScr.py",
    PROJECT_ROOT / "setup.py",
]

REQUIRED_MARKERS = [
    "#BOP",
    "# !MODULE:",
    "# !DESCRIPTION:",
    "# !REVISION HISTORY:",
    "#EOP",
    "#BOC",
    "#EOC",
]


@pytest.mark.parametrize("source_file", PROTEX_SOURCE_FILES, ids=lambda path: path.name)
def test_main_python_sources_preserve_protex_documentation_contract(source_file):
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
