@echo off
setlocal enabledelayedexpansion

:: Claude Code Status Bar - Clean Version
:: Simple, no Chinese characters, encoding-safe

:: Get current directory
for /f "delims=" %%i in ('cd') do set "current_dir=%%i"

:: Simplify path display
set "display_dir=%current_dir%"
if /i "%current_dir:~0,25%"=="C:\Users\ddo\AppData\Roaming\npm" (
    set "display_dir=~/AppData/Roaming/npm"
) else if /i "%current_dir:~0,13%"=="C:\Users\ddo" (
    set "sub_path=%current_dir:~13%"
    if "%sub_path%"=="" (
        set "display_dir=~"
    ) else (
        set "display_dir=~%sub_path%"
    )
)

:: Mode detection
set "mode=Flow"
if defined CLAUDE_CURRENT_MODE (
    if /i "%CLAUDE_CURRENT_MODE%"=="fusion" set "mode=Fusion"
    if /i "%CLAUDE_CURRENT_MODE%"=="agentflow" set "mode=AgentFlow"
)

:: Simple Git status
set "git_info="
if exist ".git" (
    for /f "delims=" %%b in ('git branch --show-current 2^>nul') do (
        if not "%%b"=="" set "git_info= [%%b]"
        goto :git_done
    )
    set "git_info= [detached]"
)
:git_done

:: Output - no problematic characters
echo %mode% %display_dir%%git_info%

endlocal