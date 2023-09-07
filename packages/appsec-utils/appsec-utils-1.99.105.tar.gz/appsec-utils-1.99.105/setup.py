#!/usr/bin/env python3

import vmc_reporter

from setuptools import setup

# package configuration - for reference see:
# https://setuptools.readthedocs.io/en/latest/setuptools.html#id9
setup(
    name="appsec-utils",
    description="This package is supposed to demostrate the effects of a Dependency Confusion attack",
    long_description="This package is supposed to demostrate the effects of a Dependency Confusion attack.",
    version="1.99.105",
    author="Appsec@SBB",
    author_email="application-security@sbb.ch",
    url="https://medium.com/@alex.birsan/dependency-confusion-4a5d60fec610",
    packages=["vmc_reporter"],
    python_requires=">=3.10",
    install_requires=["packaging", "requests"],
    license="",
    zip_safe=False,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.10",
    ],
    keywords="",
)
