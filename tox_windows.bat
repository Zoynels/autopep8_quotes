::tox
::tox -e check, mypy
::tox -e pep8
::tox -e check_manifest
tox -e autopep8_quotes

pause
tox_windows.bat