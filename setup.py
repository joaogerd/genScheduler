#!/usr/bin/env python
#-----------------------------------------------------------------------------#
#                 genScheduler - HPC Submission Script Generator              #
#-----------------------------------------------------------------------------#
#BOP
#
# !MODULE: setup.py
#
# !DESCRIPTION:
# Packaging definition for genScheduler.
#
# Declares package metadata, bundled scheduler directive data, the command-line
# script and runtime/test dependencies required to install and validate the
# project.
#
# !INTERFACE:
# Standard setuptools commands may be used, although installation through pip is
# preferred:
#
#     python -m pip install .
#     python -m pip install -e ".[test]"
#
# !DEPENDENCIES:
# Runtime:
#     PyYAML
#
# Test extra:
#     pytest
#
# Python standard-library modules such as argparse and datetime are intentionally
# not declared as external dependencies.
#
# !REMARKS:
# The package metadata currently still identifies the historical MIT license.
# The project owner has decided that the project will migrate to a GNU license.
# That license change is intentionally handled as a separate explicit change so
# that the exact GNU license family/version can be selected and applied
# consistently to LICENSE, package metadata and documentation.
#
# !REVISION HISTORY:
# - 26th October 2023, J. G. de Mattos: Initial Version.
# - 03rd October 2026, J. G. de Mattos:
#   - Removed unnecessary external dependencies and used README.md as package
#     long description.
#   - Restored and expanded ProTeX documentation.
#   - Added a minimal PEP 517 build configuration while preserving setup.py
#     compatibility.
#
# !SEE ALSO:
# README.md
# genScheduler/data/directives.yaml
#
#EOP
#-----------------------------------------------------------------------------#
#BOC

from pathlib import Path

from setuptools import find_packages, setup


README = Path(__file__).with_name("README.md").read_text(encoding="utf-8")

setup(
    name="genScheduler",
    version="0.1.0",
    author="João Gerd Zell de Mattos",
    author_email="joao.gerd@inpe.br",
    description="A utility for generating job submission scripts for PBS and SLURM job schedulers.",
    long_description=README,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    package_data={"genScheduler": ["data/directives.yaml"]},
    scripts=["genSchedulerScr.py"],
    install_requires=[
        "PyYAML",
    ],
    extras_require={
        "test": ["pytest"],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
)


#EOC
#-----------------------------------------------------------------------------#
