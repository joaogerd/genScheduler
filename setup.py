#!/usr/bin/env python
#-----------------------------------------------------------------------------#
#           Group on Data Assimilation Development - GDAD/CPTEC/INPE          #
#-----------------------------------------------------------------------------#
#BOP
#
# !SCRIPT:
#
# !DESCRIPTION:
#
# !CALLING SEQUENCE:
#
# !REVISION HISTORY: 
# 26 out 2023 - J. G. de Mattos - Initial Version
#
# !REMARKS:
#
#EOP
#-----------------------------------------------------------------------------#
#BOC
from setuptools import setup, find_packages

setup(
    name='genScheduler',
    version='0.1.0',
    author='João Gerd Zell de Mattos',
    author_email='joao.gerd@inpe.br',
    description='A utility for generating job submission scripts for PBS and SLURM job schedulers.',
    long_description='Please refer to the README.md for more information.',
    packages=find_packages(),
    tests_require=["pytest"],
    package_data={'genScheduler': ['data/directives.yaml']},
    scripts=['genSchedulerScr.py'],
    install_requires=[
        'argparse',
        'PyYAML',
        'datetime',
        'regex',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
)

#EOC
#-----------------------------------------------------------------------------#

