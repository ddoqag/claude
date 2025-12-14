@echo off
setlocal enabledelayedexpansion

:: ===================================================================
:: Claude Code Ultimate Status Bar - 跨平台终极版本
:: 基于远程仓库最佳实践，支持所有Windows环境
:: ===================================================================

:: 从stdin读取JSON输入（符合官方标准）
set "input="
setlocal enabledelayedexpansion
for /f "delims=" %%a in ('more') do (
    set "line=%%a"
    set "input=!input!!line!"
)
endlocal

:: 如果没有JSON输入，使用fallback模式
if "%input%"=="" (
    call :fallback_mode
    goto :eof
)

:: 使用环境变量传递JSON（避免字符转义问题）
set "CLAUDE_STATUS_JSON=%input%"

:: 解析基本信息
call :parse_json_field "%input%" "model.display_name" MODEL_NAME
call :parse_json_field "%input%" "workspace.current_dir" CURRENT_DIR

:: 路径标准化和美化
call :beautify_path "%CURRENT_DIR%" DISPLAY_PATH

:: Git状态检测
call :get_git_status GIT_INFO

:: 模式检测
call :detect_claude_mode MODE_DISPLAY

:: 构建最终状态栏
call :build_statusline "%MODEL_NAME%" "%DISPLAY_PATH%" "%GIT_INFO%" "%MODE_DISPLAY%" FINAL_STATUS

:: 输出结果
echo %FINAL_STATUS%

endlocal
goto :eof

:: ===================================================================
:: 函数定义区域
:: ===================================================================

:fallback_mode
:: 当无JSON输入时的fallback模式
for /f "delims=" %%i in ('cd') do set "current_dir=%%i"

:: 环境检测和路径标准化
call :normalize_path "%current_dir%" normalized_dir
call :beautify_path "%normalized_dir%" display_path

:: Git状态
call :get_git_status git_info

:: 模式检测
call :detect_claude_mode mode_display

:: 构建fallback状态栏
echo %mode_display% %display_path%%git_info%
goto :eof

:normalize_path
set "input=%~1"
set "output=%input%"

:: 处理MINGW64 /c/path -> C:\path 格式转换
if "%input:~0,1%"=="/" (
    set "drive=%input:~1,1%"
    set "rest_path=%input:~2%"
    set "output=!drive!:\!rest_path:/=\!"
)

:: 处理Cygwin /cygdrive/c/path -> C:\path 格式转换
if /i "%input:~0,10%"=="/cygdrive/" (
    set "drive=%input:~11,1%"
    set "rest_path=%input:~12%"
    set "output=!drive!:\!rest_path:/=\!"
)

:: 设置返回值
set "%~2=%output%"
goto :eof

:beautify_path
set "input=%~1"
set "output=%input%"

:: Ubuntu风格路径简化
if /i "%input%"=="C:\Users\ddo\AppData\Roaming\npm" (
    set "output=~/AppData/Roaming/npm"
) else if /i "%input:~0,13%"=="C:\Users\ddo" (
    set "sub_path=%input:~13%"
    if "%sub_path%"=="" (
        set "output=~"
    ) else (
        set "output=~%sub_path%"
    )
) else if /i "%input:~0,3%"=="C:\" (
    set "sub_path=%input:~3%"
    set "output=C:/%sub_path:\=/%"
)

set "%~2=%output%"
goto :eof

:get_git_status
set "git_info="

:: 快速Git检测
if not exist ".git" (
    set "%~2="
    goto :eof
)

:: 获取当前分支
for /f "delims=" %%b in ('git rev-parse --abbrev-ref HEAD 2^>nul') do set "branch=%%b"
if "%branch%"=="" set "branch=detached"

:: 检查工作目录状态
git diff --quiet 2>nul
if errorlevel 1 (
    :: 有未提交的更改
    git diff --cached --quiet 2>nul
    if errorlevel 1 (
        set "git_info= [%branch%*+]"  :: 同时有暂存和未暂存
    ) else (
        set "git_info= [%branch%*]"   :: 仅有未暂存更改
    )
) else (
    git diff --cached --quiet 2>nul
    if errorlevel 1 (
        set "git_info= [%branch%+]"  :: 仅有暂存更改
    ) else (
        set "git_info= [%branch%]"   :: 干净状态
    )
)

set "%~2=%git_info%"
goto :eof

:detect_claude_mode
set "mode=🎯 Flow"

:: 方法1：环境变量检测
if defined CLAUDE_CURRENT_MODE (
    if /i "%CLAUDE_CURRENT_MODE%"=="fusion" set "mode=🚀 Fusion"
    if /i "%CLAUDE_CURRENT_MODE%"=="flow" set "mode=🎯 Flow"
    if /i "%CLAUDE_CURRENT_MODE%"=="agentflow" set "mode=🔗 AgentFlow"
)

:: 方法2：临时文件检测
if exist "%TEMP%\.claude_mode.txt" (
    set /p temp_mode=<"%TEMP%\.claude_mode.txt"
    if not "%temp_mode%"=="" set "mode=%temp_mode%"
)

:: 方法3：本地文件检测
if exist ".claude\current_mode.txt" (
    set /p local_mode=<".claude\current_mode.txt"
    if not "%local_mode%"=="" set "mode=%local_mode%"
)

set "%~2=%mode%"
goto :eof

:parse_json_field
:: 简单的JSON字段解析（避免依赖jq）
set "json=%~1"
set "field=%~2"
set "result="

:: 使用findstr进行模式匹配
echo %json% | findstr "\"%field%\":\" >nul
if not errorlevel 1 (
    for /f "tokens=2 delims=:" %%a in ('echo %json% ^| findstr "\"%field%\":"') do (
        set "temp=%%a"
        set "temp=!temp:"=!"
        set "temp=!temp:,=!"
        for /f "delims=" %%b in ("!temp!") do set "result=%%b"
    )
)

set "%~3=%result%"
goto :eof

:build_statusline
set "model=%~1"
set "path=%~2"
set "git=%~3"
set "mode=%~4"

:: 如果没有模型名称，使用默认值
if "%model%"=="" set "model=Claude"

:: 构建最终状态栏（参考远程仓库最佳实践）
if "%git%"=="" (
    set "final=%mode% %path%"
) else (
    set "final=%mode% %path%%git%"
)

set "%~5=%final%"
goto :eof