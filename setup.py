#!/usr/bin/env python
"""Setup for autopep8_quotes."""
from typing import List
from typing import Any


import ast
from setuptools import setup  # type: ignore


try:
    # for pip >= 10
    from pip._internal.req import parse_requirements  # type: ignore
except ImportError:
    # for pip <= 9.0.3
    from pip.req import parse_requirements  # type: ignore


def load_requirements(fname: str) -> List[str]:
    try:
        reqs = parse_requirements(fname, session="autopep8_quotes")
        return [str(ir.req) for ir in reqs]
    except BaseException:
        reqs = parse_requirements(fname, session="autopep8_quotes")
        return [str(ir.requirement) for ir in reqs]


def version() -> Any:
    """Return version string."""
    import os
    print(os.listdir())
    with open("autopep8_quotes/__init__.py") as input_file:
        for line in input_file:
            if line.startswith("__version__"):
                return ast.parse(line).body[0].value.s  # type: ignore
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
          license="GNU Affero General Public License v3",
          author="Dmitrii",
          author_email="zoynels@gmail.com",
          url="https://github.com/zoynels/autopep8_quotes",
          classifiers=["Intended Audience :: Developers",
                       "Environment :: Console",
                       "Programming Language :: Python :: 3",
                       "License :: OSI Approved :: GNU Affero General Public License v3"],
          keywords="strings, formatter, style",
          entry_points={
              "console_scripts": ["autopep8_quotes = autopep8_quotes.__init__:main"],
              "autopep8_quotes.formatter": [
                  "lowercase_string_prefix = autopep8_quotes.modules.formater.lowercase_string_prefix:formatter",
                  "normalize_string_quotes = autopep8_quotes.modules.formater.normalize_string_quotes:formatter",
                  "remove_string_u_prefix = autopep8_quotes.modules.formater.remove_string_u_prefix:formatter",
                  "save_values_to_file = autopep8_quotes.modules.formater.save_values_to_file:formatter",
                  "remove_empty_lines_spaces = autopep8_quotes.modules.formater.remove_empty_lines_spaces:formatter",
                  "fix_end_file_lines = autopep8_quotes.modules.formater.fix_end_file_lines:formatter",
              ],
              "autopep8_quotes.saver": [
                  "check_soft = autopep8_quotes.modules.saver.check_soft:formatter",
                  "check_hard = autopep8_quotes.modules.saver.check_hard:formatter",
                  "diff = autopep8_quotes.modules.saver.diff:formatter",
                  "diff_to_txt = autopep8_quotes.modules.saver.diff_to_txt:formatter",
                  "in_place = autopep8_quotes.modules.saver.in_place:formatter",
                  "new_file = autopep8_quotes.modules.saver.new_file:formatter",
                  "git_smugle = autopep8_quotes.modules.saver.git_smugle:formatter",
              ],
          },
          packages=["autopep8_quotes"],
          package_dir={"autopep8_quotes": "autopep8_quotes"},
          include_package_data=True,
          install_requires=load_requirements("requirements.txt"),
          extras_require={
              "colorama": ["colorama"]
          })
