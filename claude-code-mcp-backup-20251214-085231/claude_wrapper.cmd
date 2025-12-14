@echo off
:: ===================================================================
:: Claude Code Universal Wrapper - 终极别名解决方案
:: 解决MINGW64/WSL环境下的状态栏脚本执行问题
:: ===================================================================

:: 设置关键环境变量，确保Claude能正确识别环境
set "CLAUDE_WRAPPER_MODE=true"
set "CLAUDE_NATIVE_WINDOWS=true"

:: 传递当前工作目录信息
for /f "delims=" %%i in ('cd') do set "CLAUDE_WORKING_DIR=%%i"

:: 调用原始的claude.cmd，传递所有参数
"C:\Users\ddo\AppData\Roaming\npm\claude.cmd" %*