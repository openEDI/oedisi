# -*- coding: utf-8 -*-
"""
setup.py
"""
import os
from codecs import open
from setuptools import setup, find_packages
from setuptools.command.develop import develop
from subprocess import check_call
import shlex
from warnings import warn

here = os.path.abspath(os.path.dirname(__file__))

# test_requires = ["pytest>=5.2", ]
description = (
    "HELICS component framework to generate runner configs" "and map inputs to outputs"
)

setup(
    name="componentversion",
    # version="0.0.1",
    description=description,
    # long_description=readme,
    author="Joseph McKinsey",
    author_email="joseph.mckinsey@nrel.gov",
    packages=find_packages(),
    package_dir={"componentframework": "componentframework"},
    include_package_data=True,
    # license="MIT",
    zip_safe=True,
    keywords="componentframework helics",
    python_requires=">=3.7,<=3.10",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    # test_suite="tests",
    install_requires=["helics-apps", "helics", "pydantic"],
    # extras_require={
    # "test": test_requires,
    # "dev": test_requires + ["flake8", "pre-commit", "pylint"],
    # },
    # cmdclass={"develop": PostDevelopCommand},
)
