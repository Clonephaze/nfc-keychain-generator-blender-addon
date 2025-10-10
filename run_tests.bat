@echo off
REM Batch script to run tests for NFC Card & Keychain Generator addon
REM This script will attempt to find Blender and run the test suite

setlocal enabledelayedexpansion

REM Common Blender installation paths
set BLENDER_PATHS=^
"C:\Program Files\Blender Foundation\Blender 4.2\blender.exe";^
"C:\Program Files\Blender Foundation\Blender 4.3\blender.exe";^
"C:\Program Files\Blender Foundation\Blender 4.4\blender.exe";^
"C:\Program Files\Blender Foundation\Blender\blender.exe";^
"%ProgramFiles%\Blender Foundation\Blender 4.2\blender.exe"

set BLENDER_EXE=

REM Try to find Blender
for %%p in (%BLENDER_PATHS%) do (
    if exist %%p (
        set BLENDER_EXE=%%p
        goto :found
    )
)

REM If not found, check if blender is in PATH
where blender >nul 2>&1
if %errorlevel% equ 0 (
    set BLENDER_EXE=blender
    goto :found
)

:notfound
echo ERROR: Could not find Blender installation.
echo Please install Blender 4.2 or higher, or specify the path manually.
echo.
echo Usage: run_tests.bat "C:\Path\To\blender.exe"
echo.
pause
exit /b 1

:found
echo Found Blender at: %BLENDER_EXE%
echo.

REM If user provided custom path, use it
if not "%~1"=="" (
    set BLENDER_EXE=%~1
    echo Using custom Blender path: !BLENDER_EXE!
    echo.
)

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0

REM Run tests
echo Running tests...
echo ================================================================================
%BLENDER_EXE% --background --python "%SCRIPT_DIR%tests\run_tests.py" -- %*

REM Capture exit code
set TEST_RESULT=%errorlevel%

echo ================================================================================
echo.
if %TEST_RESULT% equ 0 (
    echo Tests completed successfully!
    echo Exit code: %TEST_RESULT%
) else (
    echo Tests failed!
    echo Exit code: %TEST_RESULT%
)
echo.
pause
exit /b %TEST_RESULT%
