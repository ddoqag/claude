@echo off
:: 切换Claude状态栏模式工具

setlocal enabledelayedexpansion

:: 定义模式数组
set "modes[0]=🎯 Flow"
set "modes[1]=🔗 AgentFlow"
set "modes[2]=🚀 Fusion"

:: 尝试读取当前模式
if exist "C:\Users\ddo\AppData\Roaming\npm\.claude\current_mode.txt" (
    set /p current_mode=<"C:\Users\ddo\AppData\Roaming\npm\.claude\current_mode.txt"
) else (
    set "current_mode="
)

:: 查找当前模式索引
set "found=0"
for /l %%i in (0,1,2) do (
    if "!modes[%%i]!"=="!current_mode!" (
        set "current_index=%%i"
        set "found=1"
    )
)

:: 如果没找到，从0开始
if "!found!"=="0" set "current_index=0"

:: 计算下一个模式索引
set /a "next_index=(!current_index! + 1) %% 3"

:: 获取下一个模式
set "next_mode=!modes[!next_index!]"

:: 写入新模式到文件
echo !next_mode!> "C:\Users\ddo\AppData\Roaming\npm\.claude\current_mode.txt"

:: 显示切换信息
echo.
echo 模式已切换: !current_mode! -^> !next_mode!
echo.
echo 可用模式:
echo   0 - 🎯 Flow (专注流畅的工作流)
echo   1 - 🔗 AgentFlow (代理协作流程)
echo   2 - 🚀 Fusion (融合加速模式)
echo.
echo 当前激活: !next_mode!
echo.

:: 创建快速切换脚本
echo @echo off > "C:\Users\ddo\AppData\Roaming\npm\.claude\quick_mode_0.bat"
echo echo 🎯 Flow^> "C:\Users\ddo\AppData\Roaming\npm\.claude\current_mode.txt" >> "C:\Users\ddo\AppData\Roaming\npm\.claude\quick_mode_0.bat"

echo @echo off > "C:\Users\ddo\AppData\Roaming\npm\.claude\quick_mode_1.bat"
echo echo 🔗 AgentFlow^> "C:\Users\ddo\AppData\Roaming\npm\.claude\current_mode.txt" >> "C:\Users\ddo\AppData\Roaming\npm\.claude\quick_mode_1.bat"

echo @echo off > "C:\Users\ddo\AppData\Roaming\npm\.claude\quick_mode_2.bat"
echo echo 🚀 Fusion^> "C:\Users\ddo\AppData\Roaming\npm\.claude\current_mode.txt" >> "C:\Users\ddo\AppData\Roaming\npm\.claude\quick_mode_2.bat"

echo 快速切换脚本已创建:
echo   quick_mode_0.bat - 切换到 🎯 Flow
echo   quick_mode_1.bat - 切换到 🔗 AgentFlow
echo   quick_mode_2.bat - 切换到 🚀 Fusion
echo.

endlocal