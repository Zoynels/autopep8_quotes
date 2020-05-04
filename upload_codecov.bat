codecov.exe --required --verbose -f coverage.xml -t %CODECOV_TOKEN__autopep8_quotes%

if errorlevel 1 (
    pause
) ELSE (
    exit
)
