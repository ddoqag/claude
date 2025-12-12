# GLM Coding API 使用指南

## 📋 基础配置

### API信息
- **端点URL**: `https://open.bigmodel.cn/api/coding/paas/v4/chat/completions`
- **API密钥**: `13beba9abe974c7d97250b9778ca4447.8yR9f0F44Yv0YEX8`
- **支持模型**: `glm-4`

### 请求格式
```json
{
  "model": "glm-4",
  "messages": [
    {
      "role": "user",
      "content": "你的编程问题或代码需求"
    }
  ]
}
```

## 🔧 支持的编程语言

GLM Coding API 支持多种编程语言的代码生成：

- **Python** - 脚本、数据分析、机器学习
- **JavaScript/TypeScript** - Web开发、Node.js
- **Java** - 企业级应用、Android开发
- **C/C++** - 系统编程、性能优化
- **Go** - 微服务、云原生应用
- **Rust** - 系统编程、内存安全
- **PHP** - Web开发后端
- **C#** - .NET应用开发
- **Swift** - iOS开发
- **Kotlin** - Android开发
- **SQL** - 数据库查询
- **HTML/CSS** - 前端开发

## 💡 常见使用场景

### 1. 代码生成
```bash
curl -X POST "https://open.bigmodel.cn/api/coding/paas/v4/chat/completions" \
  -H "Authorization: Bearer 13beba9abe974c7d97250b9778ca4447.8yR9f0F44Yv0YEX8" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "glm-4",
    "messages": [
      {
        "role": "user",
        "content": "用Python编写一个二叉树遍历算法"
      }
    ]
  }'
```

### 2. 代码调试
```bash
# 发送有问题的代码，获取调试建议
content="帮我调试这段代码:\n\n[your code here]"
```

### 3. 代码优化
```bash
# 请求优化建议
content="优化以下代码的性能:\n\n[your code here]"
```

### 4. 代码解释
```bash
# 请求代码解释
content="请解释以下代码的作用:\n\n[your code here]"
```

### 5. 单元测试生成
```bash
# 生成单元测试
content="为以下代码生成单元测试:\n\n[your code here]"
```

## ⚙️ 高级参数配置

### 完整请求参数
```json
{
  "model": "glm-4",
  "messages": [
    {
      "role": "user",
      "content": "你的问题"
    }
  ],
  "max_tokens": 2000,
  "temperature": 0.7,
  "top_p": 0.9,
  "stream": false
}
```

### 参数说明

| 参数 | 类型 | 说明 | 推荐值 |
|------|------|------|--------|
| `model` | string | 使用的模型名称 | `glm-4` |
| `max_tokens` | integer | 最大生成token数 | 1000-4000 |
| `temperature` | float | 控制输出随机性 | 0.1-1.0 |
| `top_p` | float | 核采样参数 | 0.8-0.95 |
| `stream` | boolean | 是否流式输出 | false |

### 温度参数建议
- **0.1-0.3**: 代码生成，需要准确性和一致性
- **0.4-0.7**: 代码优化、重构建议
- **0.7-1.0**: 创意编程、算法设计

## 📝 最佳实践

### 1. 提示词技巧
- **明确语言**: "用Python编写..."
- **具体需求**: "编写一个函数，输入是..."
- **提供上下文**: 给出相关的代码片段
- **指定格式**: "请返回JSON格式的响应"

### 2. 错误处理
```python
try:
    response = client.generate_code(prompt)
    # 处理响应
except Exception as e:
    print(f"API调用失败: {e}")
    # 实现重试逻辑
```

### 3. Token管理
- 监控 `usage` 字段中的token消耗
- 大型代码项目考虑分段处理
- 设置合理的 `max_tokens` 限制

### 4. 安全考虑
- 不要在请求中包含敏感信息
- 对生成的代码进行安全审查
- 实施输入验证和输出过滤

## 🚀 集成示例

### Python Flask集成
```python
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/generate-code', methods=['POST'])
def generate_code():
    data = request.json
    prompt = data.get('prompt', '')

    # 调用GLM API
    response = requests.post(
        'https://open.bigmodel.cn/api/coding/paas/v4/chat/completions',
        headers={
            'Authorization': 'Bearer 13beba9abe974c7d97250b9778ca4447.8yR9f0F44Yv0YEX8',
            'Content-Type': 'application/json'
        },
        json={
            'model': 'glm-4',
            'messages': [{'role': 'user', 'content': prompt}]
        }
    )

    return jsonify(response.json())

if __name__ == '__main__':
    app.run(debug=True)
```

## 📊 监控和日志

### 响应结构
```json
{
  "choices": [
    {
      "message": {
        "content": "生成的代码内容",
        "role": "assistant"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 50,
    "completion_tokens": 200,
    "total_tokens": 250
  },
  "request_id": "请求唯一标识"
}
```

### 建议记录的日志
- 请求时间戳
- 提示词长度
- 响应时间
- Token消耗
- 错误信息（如有）

## 🔒 注意事项

1. **UTF-8编码**: 确保请求使用UTF-8编码
2. **字符限制**: 避免在JSON中使用特殊字符
3. **速率限制**: 注意API调用频率限制
4. **余额监控**: 定期检查账户余额
5. **错误重试**: 实现合理的重试机制

## 🆘 常见问题

### Q: 如何处理中文输入？
A: 确保JSON正确转义中文字符，或在客户端代码中使用英文请求。

### Q: 生成的代码包含错误怎么办？
A: 可以要求API重新生成，或提供错误信息请求调试帮助。

### Q: 如何限制生成代码的长度？
A: 使用 `max_tokens` 参数控制响应长度。

### Q: API响应很慢怎么办？
A: 检查网络连接，考虑使用streaming模式，或优化提示词长度。