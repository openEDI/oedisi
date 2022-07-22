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
    "HELICS component framework to generate runner configs "
    "and map inputs to outputs"
)

setup(
    name="gadal",
    version="0.1.0",
    description=description,
    # long_description=readme,
    author="Joseph McKinsey",
    author_email="joseph.mckinsey@nrel.gov",
    packages=find_packages(),
    package_dir={"gadal": "gadal"},
    include_package_data=True,
    # license="MIT",
    zip_safe=True,
    keywords="gadal helics",
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        #"License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    # test_suite="tests",
    install_requires=["helics-apps>=3.1.0", "helics>=3.1.0", "pydantic", "psutil"],
    extras_require={"test":["pytest"]},
    # cmdclass={"develop": PostDevelopCommand},
)
