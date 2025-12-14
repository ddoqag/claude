# Claude Code 跨平台环境差异修复

## 问题根因分析

您的分析完全正确！问题确实是环境差异：

### 环境差异对比

1. **直接运行 claude.cmd**
   - 环境: Windows CMD
   - 工作目录: `C:\Users\ddo\AppData\Roaming\npm`
   - 路径格式: Windows 原生格式
   - 状态栏: `🎯 Flow C:\Users\ddo\AppData\Roaming\npm` ✅

2. **通过别名运行 claude**
   - 环境: MINGW64/Git Bash
   - 工作目录: `/c/Users/ddo` (Unix格式)
   - 路径格式: Unix 格式转换为 Windows 格式
   - 状态栏: 路径解析失败 ❌

## 解决方案

### 创建跨平台状态栏脚本
`statusline_crossplatform.bat` 包含：

#### 1. 路径标准化函数
```batch
:normalize_path
:: 处理MINGW64格式 /c/path -> C:\path
if "%input:~0,1%"=="/" (
    set "drive=%input:~1,1%"
    set "path=%input:~2%"
    set "output=!drive!:\!path:/=\!"
)
```

#### 2. 路径简化函数
```batch
:simplify_path
:: C:\Users\ddo\AppData\Roaming\npm -> ~/AppData/Roaming/npm
:: C:\Users\ddo\project -> ~/project
```

#### 3. 环境兼容处理
- 自动检测运行环境
- 统一路径格式处理
- 保持原有功能不变

### 配置更新
```json
"command": "C:\\Users\\ddo\\AppData\\Roaming\\npm\\.claude\\statusline_crossplatform.bat"
```

## 预期效果

### 在任何环境下都能正确显示：
- **npm 目录**: `🎯 Flow ~/AppData/Roaming/npm`
- **用户目录**: `🎯 Flow ~/project`
- **其他目录**: `🎯 Flow D:\backup [main]`

### 支持的运行方式：
1. 直接运行: `C:\Users\ddo\AppData\Roaming\npm\claude.cmd`
2. 别名运行: `claude` (在任何目录)
3. Git Bash: 通过 MINGW64 环境

## 测试验证

重启 Claude Code 后，以下命令都应该显示相同的状态栏格式：

```bash
# 在 npm 目录
cd /c/Users/ddo/AppData/Roaming/npm
claude

# 在其他目录
cd /tmp
claude

# 直接运行
"C:\Users\ddo\AppData\Roaming\npm\claude.cmd"
```

这个修复确保了无论在什么环境下运行 Claude，状态栏都能正确显示和工作。