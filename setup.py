#!/usr/bin/env python
"""Setup for autopep8_quotes."""

import ast
from setuptools import setup

try:
    # for pip >= 10
    from pip._internal.req import parse_requirements
except ImportError:
    # for pip <= 9.0.3
    from pip.req import parse_requirements


def load_requirements(fname):
    reqs = parse_requirements(fname, session="autopep8_quotes")
    return [str(ir.req) for ir in reqs]


def version():
    """Return version string."""
    import os
    print(os.listdir())
    with open("autopep8_quotes/__init__.py") as input_file:
        for line in input_file:
            if line.startswith("__version__"):
                return ast.parse(line).body[0].value.s
    return None


with open("README.md") as readme:
    setup(name="autopep8_quotes",
          version=version(),
          description="Modifies strings to all use the same "
                      "(single/double) quote where possible. "
                      "Unify prefix to lowercase. "
                      "Remove u-prefix. ",
          long_description=readme.read(),
          long_description_content_type="text/markdown",
          license="Expat License",
          author="Dmitrii",
          author_email="zoynels@gmailc.com",
          url="https://github.com/myint/autopep8_quotes",
          classifiers=["Intended Audience :: Developers",
                       "Environment :: Console",
                       "Programming Language :: Python :: 3",
                       "License :: OSI Approved :: MIT License"],
          keywords="strings, formatter, style",
          entry_points={
              "console_scripts": ["autopep8_quotes = autopep8_quotes.__init__:main"]},
          packages=["autopep8_quotes"],
          package_dir={"autopep8_quotes": "autopep8_quotes"},
          install_requires=load_requirements("requirements.txt"))
