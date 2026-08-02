@echo off
setlocal
rem Full gate: run the complete test suite.
set FAIL=0

python -m unittest discover -s tests -p "test_*.py"
if errorlevel 1 set FAIL=1

if %FAIL%==1 (
    echo.
    echo check_all: FAILED
    exit /b 1
)
echo.
echo check_all: PASS
exit /b 0
