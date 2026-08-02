@echo off
setlocal
rem Install the commit-time mirror drift gate (pre-commit hook).
git config core.hooksPath hooks
if errorlevel 1 (
    echo FAILED: could not set core.hooksPath
    exit /b 1
)
echo Mirror drift gate installed.
echo   Pre-commit now runs: python scripts/build_mirror.py --check
echo   If it fails: run python scripts/build_mirror.py, review the diff, then re-commit.
echo   Full gate (tests + mirror check): run scripts\check_all.cmd
exit /b 0
