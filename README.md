# autopep8_quotes

[![codecov](https://codecov.io/gh/Zoynels/autopep8_quotes/branch/master/graph/badge.svg?token=LJS5MWQZVB)](https://codecov.io/gh/Zoynels/autopep8_quotes)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)

Unify strings to all use the same quote where possible.  
Unify all prefixex to lowercase where possible.  
Remove u"" prefixes where possible.  
Remove spaces in empty lines.  

## CLI


```shell
$ autopep8_quotes --help

usage: autopep8_quotes [-h] [-f FILE]
                       [-a] [-i] [-d] [-c] [-r]
                       [--filename FILENAME [FILENAME ...]]
                       [--normalize-string-quotes] [--inline-quotes {',"}] [--multiline-quotes {''',"""}]
                       [--lowercase-string-prefix]
                       [--remove-string-u-prefix]
                       [--version]
                       [--show-args]
                       [--debug]
                       files [files ...]

Unify strings to all use the same quote.
Unify all prefixex to lowercase.
Remove u"" prefixes.

positional arguments:
  files
                        Files to format

optional arguments:
  -h, --help
                        Show this help message and exit
  -f FILE, --config-file FILE
                        Specify config file
                        (default: None)
  -a, --autodetect-conf
                        Try to detect config file: *.ini, *.cfg
                        (default: True)
  -i, --in-place
                        Make changes to files. 
                        Could be combined with --diff and can't combined with --in-place.
                        If --inplace --new-file then will be used only --new-file.
                        (default: False)
  -n, --new-file
                        Make changes to files and create new file with .autopep8_quotesing extention.
                        Could be combined with --diff and can't combined with --in-place.
                        If --inplace --new-file then will be used only --new-file.
                        (default: False)
  -d, --diff
                        Print changes without make changes.
                        Could be combined with --in-place.
                        (default: False)
  -c, --check-only
                        Exit with a status code of 1 if any changes are still needed
                        (default: False)
  -r, --recursive
                        Drill down directories recursively
                        (default: False)
  --filename FILENAME [FILENAME ...]
                        Check only for filenames matching the patterns. (default: ['.*\\.py$'])
  --normalize-string-quotes
                        Normalize all quotes to standart by options --multiline-quotes and --inline-quotes
                        (default: True)
  --inline-quotes {',"}
                        Preferred inline-quotes. Works only when --normalize-string-quotes is True
                        (default: ")
  --multiline-quotes {''',"""}
                        Preferred multiline-quotes. Works only when --normalize-string-quotes is True
                        (default: """)
  --lowercase-string-prefix
                        Make FURB prefixes lowercase: B"sometext" to b"sometext"
                        (default: True)
  --remove-string-u-prefix
                        Removes any u prefix from the string: u"sometext" to "sometext"
                        (default: True)
  --version
                        Show program's version number and exit
  --show-args
                        Show readed args for script and exit
                        (default: False)
```

## Config load

Options could be set by several ways (with this order if one option exist several times):

    1. Load all config files founded by sorted(os.listdir()) when --autodetect-conf is enabled
        Find all *.ini or *.cfg files and read them by ConfigParser
    2. Load --config-file file
    3. Options from command-line

In config files options could be stored in several sections (with this order if one option exist several times):

    1. pep8
    2. flake8
    3. autopep8
    4. autopep8_quotes

## Example

After running:

    $ autopep8_quotes --in-place example.py

this code

```python
    x = "abc"
    y = 'hello'
```
gets formatted into this

```python
    x = "abc"
    y = "hello"
```

## Limitations

1. Not all strings could be transformed in right way. If you find such, please send it to me.
2. String checked with ast.literal_eval() which has limitations. Known issues:
2.1. f-string couldn't be checked perfect, so check without prefix at all.
3. String with prefix r"" didn't replace escaped quotes.
