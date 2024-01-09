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

description = "Orchestration interface for HELICS power simulations"

with open("README.md") as f:
    readme = f.read()

setup(
    name="oedisi",
    version="1.1.1",
    description=description,
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Joseph McKinsey",
    author_email="joseph.mckinsey@nrel.gov",
    packages=find_packages(),
    package_dir={"oedisi": "oedisi"},
    include_package_data=True,
    license="BSD 3-Clause",
    zip_safe=True,
    keywords="oedisi gadal helics",
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    # test_suite="tests",
    install_requires=[
        "helics-apps>=3.2.1",
        "helics>=3.2.1",
        "pydantic>=1.7,<2",
        "psutil",
        "click",
        "pyyaml",
    ],
    extras_require={"test": ["pytest", "httpx", "fastapi", "uvicorn", "grequests"]},
    entry_points={"console_scripts": ["oedisi = oedisi.tools:cli"]}
    # cmdclass={"develop": PostDevelopCommand},
)
