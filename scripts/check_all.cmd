@echo off
setlocal
rem Full gate: unit tests + branch registry validation + MCP self-test.
rem Mirrors .github/workflows/ci.yml so a green local gate == a green CI run.
set FAIL=0

python -m unittest discover -s tests -p "test_*.py"
if errorlevel 1 set FAIL=1

python .claude\skills\triz-innovation\scripts\triz.py branches check
if errorlevel 1 set FAIL=1

python .claude\skills\triz-innovation\mcp\triz_mcp_server.py --self-test
if errorlevel 1 set FAIL=1

if %FAIL%==1 (
    echo.
    echo check_all: FAILED
    exit /b 1
)
echo.
echo check_all: PASS
exit /b 0
