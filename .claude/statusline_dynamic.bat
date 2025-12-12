@echo off
:: 智能状态栏脚本 - 根据实际情况显示当前工作模式
setlocal enabledelayedexpansion

:: 检测当前的工作环境和状态

:: 1. 检查是否在Git仓库中
set "is_git_repo=0"
for /f "delims=" %%i in ('git rev-parse --is-inside-work-tree 2^>nul') do (
    if "%%i"=="true" set "is_git_repo=1"
)

:: 2. 检查是否有未完成的任务（Todo文件）
set "has_todos=0"
if exist "IMPLEMENTATION_PLAN.md" set "has_todos=1"
if exist "TODO.md" set "has_todos=1"

:: 3. 检查当前目录类型
set "dir_type=文件夹"
if exist "package.json" set "dir_type=Node.js"
if exist "requirements.txt" set "dir_type=Python"
if exist "Cargo.toml" set "dir_type=Rust"
if exist "go.mod" set "dir_type=Go"

:: 根据检测到的状态确定当前模式
if !has_todos! equ 1 (
    set "mode=🎯 Flow"
) else if !is_git_repo! equ 1 (
    for /f %%i in ('git status --porcelain 2^>nul ^| find /c /v ""') do set "git_dirty=%%i"
    if !git_dirty! gtr 0 (
        set "mode=🎯 Flow"
    ) else (
        set "mode=🎯 Flow"
    )
) else (
    set "mode=🎯 Flow"
)

:: 获取当前目录并简化显示
for /f "delims=" %%i in ('cd') do set "current_dir=%%i"
set "display_dir=!current_dir:%USERPROFILE%=~!"
if "!display_dir:~-1!"=="\" set "display_dir=!display_dir:~0,-1!"

:: 添加额外状态信息
set "status_extra="
if !is_git_repo! equ 1 (
    for /f "delims=" %%i in ('git branch --show-current 2^>nul') do set "git_branch=%%i"
    if "!git_branch!" neq "" (
        for /f %%i in ('git status --porcelain 2^>nul ^| find /c /v ""') do set "git_dirty=%%i"
        if !git_dirty! gtr 0 (
            set "status_extra=[!git_branch!*]"
        ) else (
            set "status_extra=[!git_branch!]"
        )
    )
)

:: 显示项目类型
if "!dir_type!" neq "文件夹" (
    set "status_extra=!status_extra![!dir_type!]"
)

:: 输出状态栏
echo !mode! !display_dir!!status_extra!

endlocal