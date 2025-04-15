@echo off

REM Check the number of command line arguments.
IF "%~1"=="" (
    set "base_branch=dev"
) ELSE IF "%~2"=="" (
    set "base_branch=%~1"
) ELSE (
    call :display_usage
    exit /b 1
)

REM Get the commit hash of HEAD on the bash branch.
FOR /F "tokens=*" %%n IN ('git merge-base %base_branch% HEAD') DO @(set BASEBRANCHHEAD=%%n)

REM Remove any old files that use names needed in this script.
IF EXIST ".\.changed_files.txt" (del .\.changed_files.txt)
IF EXIST ".\.changed_python_files.txt" (del .\.changed_python_files.txt)

REM Get the list of files changed in this branch.
FOR /F "tokens=*" %%G IN ('git diff --name-only --diff-filter=AM %BASEBRANCHHEAD%') DO (
    echo %%G>> .\.changed_files.txt
)

REM Filter the list of changed files to get all the changed Python files from it.
FOR /F "tokens=*" %%G IN ('findstr /r "\.py$" .\.changed_files.txt') DO (
    echo|set /p="%%G " >> .\.changed_python_files.txt
)

REM Run Flake8 on the Python files modified in this branch.
IF EXIST ".\.changed_python_files.txt" (
    REM Write the changed Python files in to a variable that can be accessed by Flake8 and MyPy.
    FOR /F "tokens=*" %%G IN (.\.changed_python_files.txt) DO (set changed_python_files=%%G)
    
    REM Run Flake8 and MyPy on the changed Python files
    flake8 %changed_python_files%
    mypy %changed_python_files%
) ELSE (
    call echo No Python files modified on this branch yet.
)

REM Remove files used to run this script.
IF EXIST ".\.changed_files.txt" (del .\.changed_files.txt)
IF EXIST ".\.changed_python_files.txt" (del .\.changed_python_files.txt)

exit /b 0

REM Function to display usage.
:display_usage
echo Usage: check_changes.bat [BASEBRANCH]
echo For all files that are different between the current branch and BASEBRANCH, lint them with Flake8 and run MyPy on them.
echo.
echo With no BASEBRANCH, compare the current branch to dev.
goto :eof
