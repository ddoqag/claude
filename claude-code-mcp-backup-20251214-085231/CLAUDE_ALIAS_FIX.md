# Claude 命令别名修复说明

## 问题分析

发现您有两个不同的 Claude 安装：

1. **npm 安装版本** (工作正常)
   - 路径: `C:\Users\ddo\AppData\Roaming\npm\claude.cmd`
   - 状态栏: `🎯 Flow C:\Users\ddo\AppData\Roaming\npm` ✓

2. **native 安装版本** (其他目录无效)
   - 路径: `C:\Users\ddo\.local\bin\claude.exe`
   - 问题: 在非 npm 目录下无法正常工作

## 根本原因

1. **别名冲突**: `alias claude='claude --dangerously-skip-permissions'`
2. **路径问题**: `.local/bin/claude.exe` 在 MINGW64 环境下无法正确执行
3. **启动器错误**: 原启动器使用了 `call` 命令，在 bash 环境下无效

## 修复方案

### 1. 修复启动器脚本
修改 `C:\Users\ddo\.local\bin\claude.exe`:
```batch
@echo off
"C:\Users\ddo\AppData\Roaming\npm\claude.cmd" %*
```

### 2. 创建备用启动器
创建 `C:\Users\ddo\.local\bin\claude.bat`:
```batch
@echo off
"C:\Users\ddo\AppData\Roaming\npm\claude.cmd" %*
```

### 3. 建议的别名修正
当前别名:
```bash
alias claude='claude --dangerously-skip-permissions'
```

建议修改为:
```bash
alias claude='claude.bat --dangerously-skip-permissions'
```

或者直接使用完整路径:
```bash
alias claude='C:\Users\ddo\AppData\Roaming\npm\claude.cmd --dangerously-skip-permissions'
```

## 测试结果

✅ **npm 目录**: 直接使用 `claude.cmd` 工作正常
✅ **其他目录**: 使用修复后的启动器现在可以正常工作
✅ **版本检查**: `claude --version` 返回 `2.0.69 (Claude Code)`

## 使用建议

1. **优先使用 npm 版本**: 直接调用 `C:\Users\ddo\AppData\Roaming\npm\claude.cmd`
2. **修正别名**: 更新 bash 别名指向正确的工作版本
3. **统一启动器**: 所有目录使用相同的 claude.cmd

修复后，您可以在任何目录下正常使用 Claude 命令，状态栏也会正确显示。