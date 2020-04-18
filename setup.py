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
              "console_scripts": ["autopep8_quotes = autopep8_quotes.__init__:main"],
              'autopep8_quotes.formatter': [
                  'lowercase_string_prefix = autopep8_quotes.modules.formater.lowercase_string_prefix:formatter',
                  'normalize_string_quotes = autopep8_quotes.modules.formater.normalize_string_quotes:formatter',
                  'remove_string_u_prefix = autopep8_quotes.modules.formater.remove_string_u_prefix:formatter',
                  'save_values_to_file = autopep8_quotes.modules.formater.save_values_to_file:formatter',
              ],
              'autopep8_quotes.saver': [
                  'check_soft = autopep8_quotes.modules.saver.check_soft:formatter',
                  'check_hard = autopep8_quotes.modules.saver.check_hard:formatter',
                  'diff = autopep8_quotes.modules.saver.diff:formatter',
                  'diff_to_txt = autopep8_quotes.modules.saver.diff_to_txt:formatter',
                  'in_place = autopep8_quotes.modules.saver.in_place:formatter',
                  'new_file = autopep8_quotes.modules.saver.new_file:formatter',
              ],
          },
          packages=["autopep8_quotes"],
          package_dir={"autopep8_quotes": "autopep8_quotes"},
          include_package_data=True,
          install_requires=load_requirements("requirements.txt"),
          extras_require = {
              'colorama':  ["colorama"]
          })
