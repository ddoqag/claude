# Claude Code 状态栏脚本执行环境差异分析报告

## 问题概述

直接运行 `claude.cmd` 时状态栏正常显示，但通过 `claude` 别名运行时状态栏脚本无效。

## 根本原因分析

### 1. 执行环境差异

#### 直接运行 `claude.cmd`
- **执行环境**: Windows 原生 cmd.exe
- **进程层级**: cmd.exe → node.exe → cli.js
- **环境变量**: 标准 Windows 环境变量
- **路径格式**: `C:\path\to\directory`
- **工作目录**: 直接继承自启动 shell

#### 通过 `claude` 别名运行
- **执行环境**: 可能是 MINGW64/WSL/bash
- **进程层级**: bash → cmd.exe (别名脚本) → node.exe → cli.js
- **环境变量**: 包含 MSYSTEM, PATH 可能包含 Unix 风格路径
- **路径格式**: `/c/path/to/directory` 或混合格式
- **工作目录**: 可能经过路径转换

### 2. 关键技术细节

#### 别名脚本分析
```batch
@echo off
:: Claude Code Native Launcher
"C:\Users\ddo\AppData\Roaming\npm\claude.cmd" %*
```
- 简单的参数转发，但没有处理环境差异
- 没有标准化工作目录格式
- 没有处理路径格式转换

#### 状态栏脚本触发机制
1. **配置位置**: `settings.json` 中的 `statusLine.command`
2. **执行方式**: Claude Code 定期调用指定的命令
3. **问题点**: 在不同执行环境下，路径解析和工作目录获取方式不同

### 3. 具体问题点

1. **路径格式不兼容**
   - MINGW64: `/c/Users/ddo`
   - Windows: `C:\Users\ddo`

2. **环境变量检测失败**
   - `CLAUDE_CURRENT_MODE` 可能未在跨环境传递
   - 临时文件路径不一致

3. **工作目录解析错误**
   - `cd` 命令在混合环境下返回不同格式
   - Git 命令路径解析失败

## 解决方案

### 方案1: 增强别名脚本（推荐）

修改 `/c/Users/ddo/.local/bin/claude`:

```batch
@echo off
:: Claude Code Enhanced Launcher
:: 确保跨环境兼容性

:: 检测并标准化执行环境
if not "%MSYSTEM%"=="" (
    :: 在 MINGW64/MSYS2 环境中
    call :mingw_compat_setup
)

:: 标准化工作目录
for /f "delims=" %%i in ('cd') do set "ORIGINAL_CD=%%i"

:: 设置环境变量以传递给子进程
set "CLAUDE_LAUNCHER=alias"
set "CLAUDE_WORK_DIR=%ORIGINAL_CD%"

:: 执行实际的 claude.cmd
"C:\Users\ddo\AppData\Roaming\npm\claude.cmd" %*

goto :eof

:mingw_compat_setup
:: MINGW64 兼容性设置
set "PATH=%PATH:C:\=/c/%"
goto :eof
```

### 方案2: 使用增强的状态栏脚本

使用已创建的 `statusline_universal_v3.bat`，更新 `settings.json`:

```json
{
  "statusLine": {
    "type": "command",
    "command": "C:\\Users\\ddo\\AppData\\Roaming\\npm\\.claude\\statusline_universal_v3.bat",
    "padding": 1,
    "refreshInterval": 1000
  }
}
```

### 方案3: PowerShell 包装器（高级方案）

创建 PowerShell 包装器处理所有环境差异:

```powershell
# claude-wrapper.ps1
param(
    [Parameter(ValueFromRemainingArguments=$true)]
    $Arguments
)

# 检测执行环境
$IsMingw = $env:MSYSTEM -ne ""
$IsWSL = $env:WSL_DISTRO_NAME -ne ""

# 标准化环境
if ($IsMingw) {
    $env:CLAUDE_EXECUTION_ENV = "mingw"
} elseif ($IsWSL) {
    $env:CLAUDE_EXECUTION_ENV = "wsl"
} else {
    $env:CLAUDE_EXECUTION_ENV = "native"
}

# 执行 claude.cmd
& "C:\Users\ddo\AppData\Roaming\npm\claude.cmd" $Arguments
```

## 实施步骤

### 立即修复（方案2）

1. 备份当前状态栏脚本:
   ```batch
   copy "C:\Users\ddo\AppData\Roaming\npm\.claude\statusline_crossplatform.bat" "C:\Users\ddo\AppData\Roaming\npm\.claude\statusline_crossplatform.bat.backup"
   ```

2. 更新 settings.json 使用新的状态栏脚本

3. 测试验证:
   ```batch
   # 测试直接运行
   "C:\Users\ddo\AppData\Roaming\npm\claude.cmd" --version

   # 测试别名运行
   claude --version

   # 检查状态栏输出
   "C:\Users\ddo\AppData\Roaming\npm\.claude\statusline_universal_v3.bat"
   ```

### 长期优化（方案1）

1. 更新别名脚本包含环境检测
2. 添加环境变量传递机制
3. 实现路径标准化

## 测试验证

使用提供的测试脚本:
```batch
"C:\Users\ddo\AppData\Roaming\npm\.claude\test_execution_context.bat"
```

## 监控和维护

1. 添加调试模式支持:
   ```batch
   set CLAUDE_STATUS_DEBUG=1
   claude
   ```

2. 定期检查状态栏输出格式

3. 监控不同环境下的执行日志

## 结论

问题的根本原因是跨执行环境（Windows 原生 vs MINGW64/WSL）导致的路径格式、环境变量和工作目录解析差异。通过增强状态栏脚本的跨环境兼容性，可以解决别名运行时状态栏不显示的问题。

建议立即实施方案2作为临时修复，同时考虑实施方案1作为长期解决方案。