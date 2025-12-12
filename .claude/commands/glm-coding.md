---
description: 使用GLM-4模型进行专业编程对话和代码生成
argument-hint: "[prompt]"
examples:
  - /glm-coding 写一个Python快速排序算法
  - /glm-coding 用JavaScript创建一个防抖函数
  - /glm-coding 帮我调试这段代码的错误
---

# GLM-4 编程助手

使用智谱AI的GLM-4模型进行专业的编程对话、代码生成、调试和优化。

## 功能特性

- 🔥 **代码生成**: 支持多种编程语言的代码生成
- 🐛 **代码调试**: 智能识别和修复代码错误
- ⚡ **代码优化**: 性能优化和最佳实践建议
- 📚 **代码解释**: 详细解释代码逻辑和原理
- 🧪 **测试生成**: 自动生成单元测试代码

## 使用方法

### 基础语法
```bash
/glm-coding [你的编程问题或需求]
```

### 常用示例

#### 1. 代码生成
```bash
/glm-coding 用Python编写一个二叉树遍历函数
/glm-coding 创建一个React组件来显示用户列表
/glm-coding 写一个SQL查询获取过去30天的销售数据
```

#### 2. 代码调试
```bash
/glm-coding 帮我调试这段代码：
def calculate_average(numbers):
    total = 0
    for num in numbers:
        total += num
    return total / len(numbers)
```

#### 3. 代码优化
```bash
/glm-coding 优化以下代码的性能：
for i in range(len(arr)):
    for j in range(len(arr)):
        if arr[i] < arr[j]:
            arr[i], arr[j] = arr[j], arr[i]
```

#### 4. 代码解释
```bash
/glm-coding 解释这段代码的作用：
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
```

#### 5. 测试生成
```bash
/glm-coding 为以下函数生成单元测试：
def add_numbers(a, b):
    return a + b
```

## 支持的编程语言

- **Python** - 脚本、数据分析、机器学习
- **JavaScript/TypeScript** - Web开发、Node.js
- **Java** - 企业级应用、Android
- **C/C++** - 系统编程、性能优化
- **Go** - 微服务、云原生
- **Rust** - 系统编程、内存安全
- **PHP** - Web开发后端
- **C#** - .NET应用开发
- **Swift** - iOS开发
- **Kotlin** - Android开发
- **SQL** - 数据库查询
- **HTML/CSS** - 前端开发

## 高级用法

### 指定编程语言
```bash
/glm-coding 用Java创建一个单例模式类
/glm-coding 用C++实现一个链表数据结构
```

### 指定具体需求
```bash
/glm-coding 创建一个REST API端点处理用户注册
/glm-coding 写一个函数验证邮箱地址格式
/glm-cording 实现一个LRU缓存算法
```

## 技术信息

- **模型**: GLM-4
- **端点**: https://open.bigmodel.cn/api/coding/paas/v4/chat/completions
- **最大Token**: 65536
- **响应时间**: 通常2-5秒

## 最佳实践

1. **明确需求**: 清晰描述你想要实现的功能
2. **提供上下文**: 如果有现有代码，请一并提供
3. **指定语言**: 明确说明使用的编程语言
4. **逐步调试**: 对于复杂问题，分步骤描述
5. **错误信息**: 如果遇到错误，请提供完整的错误信息

## 故障排除

### 常见问题

**Q: 响应很慢怎么办？**
A: GLM-4模型处理复杂代码需要时间，请耐心等待。如果持续很慢，可能需要简化问题或提供更具体的上下文。

**Q: 生成的代码有错误？**
A: 可以重新请求生成，或者提供错误信息让模型进行调试。

**Q: 如何获得更好的代码质量？**
A: 提供更详细的需求描述，包括：
- 具体的功能要求
- 性能要求
- 兼容性要求
- 编程规范要求

---

💡 **提示**: GLM-4专门针对编程场景优化，在代码生成、调试和优化方面表现优秀。善用这个工具可以大大提高编程效率！