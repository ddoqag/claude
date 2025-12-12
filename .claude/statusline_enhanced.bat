@echo off
:: 增强版智能状态栏 - 显示模式、时间和Git状态
setlocal enabledelayedexpansion

:: 尝试读取当前模式
if exist "C:\Users\ddo\AppData\Roaming\npm\.claude\current_mode.txt" (
    set /p mode=<"C:\Users\ddo\AppData\Roaming\npm\.claude\current_mode.txt"
    :: 如果文件为空，使用默认值
    if "!mode!"=="" (
        :: 基于时间动态计算
        set /a "time_based=%time:~6,1% %% 3"
        if !time_based! == 0 set "mode=🎯 Flow"
        if !time_based! == 1 set "mode=🔗 AgentFlow"
        if !time_based! == 2 set "mode=🚀 Fusion"
    )
) else (
    :: 基于时间动态计算
    set /a "time_based=%time:~6,1% %% 3"
    if !time_based! == 0 set "mode=🎯 Flow"
    if !time_based! == 1 set "mode=🔗 AgentFlow"
    if !time_based! == 2 set "mode=🚀 Fusion"
)

:: 获取当前目录并简化显示
for /f "delims=" %%i in ('cd') do set "current_dir=%%i"
set "display_dir=!current_dir:%USERPROFILE%=~!"
if "!display_dir:~-1!"=="\" set "display_dir=!display_dir:~0,-1!"

:: 检查是否在Git仓库中
set "git_info="
for /f "delims=" %%i in ('git rev-parse --is-inside-work-tree 2^>nul') do set "in_git=%%i"
if "!in_git!"=="true" (
    :: 获取当前分支
    for /f "delims=" %%i in ('git branch --show-current 2^>nul') do set "git_branch=%%i"
    if "!git_branch!" neq "" (
        :: 检查是否有未提交的更改
        for /f %%i in ('git status --porcelain 2^>nul ^| find /c /v ""') do set "git_dirty=%%i"
        if !git_dirty! gtr 0 (
            set "git_info= [!git_branch!*]"
        ) else (
            set "git_info= [!git_branch!]"
        )
    )
)

:: 获取简短时间
for /f "tokens=1-2 delims=: " %%a in ('time /t') do set "short_time=%%a:%%b"

:: 构建状态栏
set "status_line=!mode! !display_dir!!git_info!"

:: 输出状态栏
echo !status_line!

endlocal