@echo off
setlocal EnableDelayedExpansion

set "ENV_FILE=%~dp0.env.claude.profiles"

if not exist "%ENV_FILE%" (
    echo Error: Config file not found '%ENV_FILE%'
    exit /b 1
)

:: Check if profile name provided as argument
if "%~1"=="" goto :interactive
set "TARGET_PROFILE=%~1"
goto :load_profile

:interactive
echo Loading config: %ENV_FILE%
echo ----------------------------------------

:: 1. Extract all Profile names
set count=0
for /f "usebackq eol=# delims=" %%a in ("%ENV_FILE%") do (
    set "line=%%a"
    if "!line:~0,1!"=="[" (
        set /a count+=1
        set "raw=%%a"
        set "profile=!raw:[=!"
        set "profile=!profile:]=!"
        set "PROFILE_!count!=!profile!"
    )
)

if %count%==0 (
    echo Error: No [Profile] found in config
    pause
    exit /b 1
)

:: 2. Display options
echo Select profile to load:
echo ----------------------------------------
for /L %%i in (1,1,%count%) do (
    echo   [%%i] !PROFILE_%%i!
)
echo   [0] Cancel
echo ----------------------------------------
set /p CHOICE="Enter number: "

if "%CHOICE%"=="0" exit /b 0
if not defined PROFILE_%CHOICE% (
    echo Invalid choice.
    pause
    exit /b 1
)

set "TARGET_PROFILE=!PROFILE_%CHOICE%!"

:load_profile
echo.
echo Selected: %TARGET_PROFILE%
echo Setting environment variables...

:: 3. Parse and set variables
set "IN_SECTION=0"
set "TEMP_SETTER=%TEMP%\set_env_tmp_%RANDOM%.bat"
if exist "%TEMP_SETTER%" del "%TEMP_SETTER%"

for /f "usebackq eol=# tokens=1,* delims==" %%k in ("%ENV_FILE%") do (
    set "line=%%k"
    
    if "!line:~0,1!"=="[" (
        if "!line!"=="[%TARGET_PROFILE%]" (
            set "IN_SECTION=1"
        ) else (
            set "IN_SECTION=0"
        )
    ) else (
        if "!IN_SECTION!"=="1" (
            if not "%%l"=="" (
                >>"%TEMP_SETTER%" echo set "%%k=%%l"
                echo   [Parsed] %%k
            )
        )
    )
)

if not exist "%TEMP_SETTER%" (
    echo Error: No variables found in profile [%TARGET_PROFILE%]
    endlocal
    exit /b 1
)

:: 4. Export variables - call the temp file AFTER endlocal to persist variables
endlocal & call "%TEMP_SETTER%"

if exist "%TEMP_SETTER%" del "%TEMP_SETTER%"

echo ----------------------------------------
echo Environment configured!
echo.
echo Current settings:
set ANTHROPIC_
echo.
echo Now you can run: claude
