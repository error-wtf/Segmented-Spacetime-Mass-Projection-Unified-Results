#!/usr/bin/env python3

import os
from setuptools import setup, find_packages

# Read README if available
long_description = ""
if os.path.exists("docs/README.md"):
    with open("docs/README.md", "r", encoding="utf-8") as f:
        long_description = f.read()

setup(
    name="ssz-projection-suite",
    version="1.0",
    description="Anti-Capitalist Segmented Spacetime Analysis Suite",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Carmen Wrede und Lino Casu",
    author_email="research@ssz-projection.org",
    url="https://github.com/ssz-research/segmented-spacetime",
    packages=find_packages(),
    package_data={
        "ssz_projection_suite": ["*.py"],
    },
    data_files=[
        ("share/ssz-projection-suite/data", [
            "data/real_data_full_expanded.csv",
            "data/sources.json",
            "data/LICENSE"
        ]),
    ],
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Physics",
    ],
    scripts=["bin/ssz-projection"],
)
