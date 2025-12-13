@echo off
REM Node.js环境修复包装器
REM 解决Git Bash环境下Node.js路径问题

setlocal enabledelayedexpansion

REM 设置Node.js路径
set "NODE_PATH=C:\Program Files\nodejs"
set "NODE_EXE=%NODE_PATH%\node.exe"
set "NPX_CMD=%NODE_PATH%\npx.cmd"

REM 检查Node.js是否存在
if not exist "%NODE_EXE%" (
    echo Error: Node.js not found at %NODE_EXE%
    echo Please install Node.js from https://nodejs.org/
    exit /b 1
)

REM 解析参数
set "command=%1"
set "args="

:parse_args
if "%~2"=="" goto :execute
set "args=%args% %~2"
shift /2
goto :parse_args

:execute
REM 执行对应的命令
if "%command%"=="node" (
    "%NODE_EXE%" %args%
) else if "%command%"=="npx" (
    "%NPX_CMD%" %args%
) else if "%command%"=="npm" (
    "%NODE_PATH%\npm.cmd" %args%
) else if "%command%"=="--version" (
    "%NODE_EXE%" --version
) else if "%command%"=="--help" (
    echo Node.js Wrapper for Claude Code
    echo Usage: nodejs_wrapper.cmd [node^|npx^|npm] [args...]
    echo.
    echo Examples:
    echo   nodejs_wrapper.cmd node --version
    echo   nodejs_wrapper.cmd npx --version
    echo   nodejs_wrapper.cmd npm --version
) else (
    echo Unknown command: %command%
    echo Use --help for usage information
    exit /b 1
)

endlocal