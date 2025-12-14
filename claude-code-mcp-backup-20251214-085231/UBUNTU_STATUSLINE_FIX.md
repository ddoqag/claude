# Ubuntu 风格状态栏修正说明

## 问题分析
原事件驱动方案在 MINGW64/Git Bash 环境下语法不兼容，需要重新设计。

## 修正方案

### 1. 环境兼容性
- **问题**: MINGW64 环境下 Windows cmd 脚本执行有问题
- **解决**: 简化脚本，确保 Windows cmd 原生语法兼容

### 2. 事件驱动简化
- **原方案**: 复杂的后台监控进程
- **新方案**: 基于目录缓存的轻量级检测

### 3. 核心改进

#### statusline_dynamic_v2.bat
- **目录缓存**: 使用 `%TEMP%\.claude_last_dir` 缓存上次目录
- **变化检测**: 比较当前目录与缓存，仅在变化时执行耗时操作
- **Git 优化**: 仅在目录变化时检查 Git 状态
- **路径简化**: Ubuntu 风格的相对路径显示

#### 显示格式对比
- **之前**: `🎯 Flow ~/AppData/Roaming/npm`
- **现在**: `🎯 Flow ~/AppData/Roaming/npm [main*]`

### 4. 配置更新
```json
"statusLine": {
  "type": "command",
  "command": "C:\\Users\\ddo\\AppData\\Roaming\\npm\\.claude\\statusline_dynamic_v2.bat",
  "padding": 1,
  "refreshInterval": 1000
}
```

### 5. 特性说明

#### Git 状态指示
- `main`: 干净的工作目录
- `main*`: 有未提交的更改
- `main+`: 有暂存的更改
- `detached`: 分离HEAD状态

#### 路径显示
- `~/AppData/Roaming/npm`: AppData目录简化
- `~/project`: 用户目录相对路径
- `D:\backup`: 外部路径保持原样

### 6. 性能优化
- **缓存机制**: 避免重复的 Git 操作
- **条件执行**: 仅在必要时执行耗时操作
- **轻量级**: 无需额外的后台进程

## 使用方法
1. 重启 Claude Code
2. 状态栏将自动使用新的动态检测机制
3. 切换目录时状态栏会相应更新

这个修正方案确保了与 Windows 环境的完全兼容性，同时实现了类似 Ubuntu 风格的简洁状态显示。