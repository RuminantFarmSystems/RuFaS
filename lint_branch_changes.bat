@echo off

REM Check the number of command line arguments
IF "%~1"=="" (
    set "base_branch=master"
) ELSE IF "%~2"=="" (
    set "base_branch=%~1"
) ELSE (
    Set "SubStr=%here%"
    echo %SubStr%
    call :display_usage
    exit /b 1
)

REM Get the list of changed Python files
REM cmd /k "git merge-base master HEAD"
@REM set HELLO=hello
@REM call echo %%HELLO%%
FOR /F "tokens=*" %%n IN ('git merge-base master HEAD') DO @(set BASEBRANCHHEAD=%%n)
call echo %%BASEBRANCHHEAD%%

del .\.changed_files.txt

FOR /F "tokens=*" %%G IN ('git diff --name-only %BASEBRANCHHEAD%') DO (
    echo %%G >> .\.changed_files.txt
)
call type .\.changed_files.txt

FOR /F "tokens=*" %%G IN ('findstr /r "\.py$" .\.changed_files.txt') DO (
    call echo here
    echo %%G >> .\.changed_python_files.txt
)
call type .\.changed_python_files.txt

REM Exit if there are no Python files to lint
@REM IF "%changed_files%"=="" (
@REM     exit /b 0
@REM )
@REM
@REM REM Run Flake8 on the changed Python files
@REM flake8 %changed_files%

exit /b 0

REM Function to display usage
:display_usage
echo Usage: cleanup.bat [BASEBRANCH]
echo Lint all files different between current branch and BASEBRANCH with Flake8.
echo.
echo With no BASEBRANCH, compare the current branch to master.
goto :eof