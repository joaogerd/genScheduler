#!/usr/bin/env python

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
