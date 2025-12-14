# Ubuntu 20.04 风格 Claude Code 状态栏

## 概述
基于 Ubuntu 20.04 的 Claude Code 状态栏实现，从定时刷新改为事件驱动的目录变化检测系统。

## 文件说明

### 1. statusline_eventdriven.bat
**主要的状态栏脚本，事件驱动版本**
- 多层次模式检测（环境变量 + 临时文件 + 本地文件）
- Git 状态信息（分支名 + 文件变更统计）
- 上下文使用百分比
- 智能路径简化
- 性能优化和缓存机制

### 2. statusline_monitor.bat
**后台监控脚本**
- 监控目录变化
- 检测 Git 状态变化
- 触发状态栏更新
- 避免频繁刷新，提高性能

### 3. statusline_ubuntu_style.bat
**Ubuntu 风格的简化版本**
- 简洁的路径显示
- 快速 Git 状态检查
- 模式图标显示
- 上下文使用情况

### 4. start_statusline_monitor.bat
**启动器脚本**
- 启动后台监控进程
- 检查重复运行
- 提供使用说明

## 配置更新

settings.json 已更新为：
```json
"statusLine": {
  "type": "command",
  "command": "C:\\Users\\ddo\\AppData\\Roaming\\npm\\.claude\\statusline_eventdriven.bat",
  "padding": 1,
  "refreshInterval": 2000,
  "eventDriven": true
}
```

## 主要改进

### 从定时刷新到事件驱动
- **之前**: 每 500ms 刷新一次
- **现在**: 目录变化时才更新，2秒作为后备刷新

### Ubuntu 20.4 风格特性
1. **简洁路径显示**: `~/AppData/Roaming/npm` 而不是完整路径
2. **Git 信息集成**: `main | S: 0 | U: 1 | A: 0`
3. **上下文百分比**: 显示当前会话的上下文使用情况
4. **性能优化**: 使用缓存和快速检查

### 显示格式对比

**之前 (statusline_smart.bat)**:
```
🎯 Flow ~/AppData/Roaming/npm
```

**现在 (事件驱动版本)**:
```
🎯 ~/AppData/Roaming/npm | main | S: 0 | U: 1 | A: 0 | 15.2%
```

## 使用方法

1. **自动启动**: Claude Code 启动时自动使用新的状态栏
2. **手动监控**: 运行 `start_statusline_monitor.bat` 启动后台监控
3. **切换样式**: 修改 settings.json 中的 command 路径可切换不同样式

## 性能优化

- 使用哈希比较检测目录变化
- Git 状态使用 `--porcelain` 快速检查
- 缓存机制减少重复计算
- 事件驱动避免无谓刷新

## 故障排除

如果状态栏不更新：
1. 检查文件权限
2. 运行 `start_statusline_monitor.bat` 手动启动监控
3. 重新启动 Claude Code
4. 检查 TEMP 目录访问权限