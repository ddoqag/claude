# 智谱AI编码端点集成 SDK

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](https://github.com/zhipu-ai/zhipu-ai-sdk)
[![Coverage](https://img.shields.io/badge/coverage-90%25-green.svg)](https://github.com/zhipu-ai/zhipu-ai-sdk)

智谱AI编码端点的官方Python SDK，提供完整、高性能、生产就绪的集成方案。

## 特性

- 🚀 **高性能**: 基于httpx的异步HTTP客户端，支持连接池和HTTP/2
- 🔄 **流式支持**: 原生支持SSE流式响应处理
- 🛡️ **错误处理**: 完善的错误处理和自动重试机制
- 📝 **类型安全**: 100%类型注解，支持Pydantic数据模型
- 🔧 **灵活配置**: 支持多种配置方式和自定义选项
- 📊 **性能优化**: 内置缓存、请求压缩和批量处理
- 🔐 **安全**: API密钥加密存储，传输层安全
- 🧪 **测试完备**: 高测试覆盖率，包含单元测试和集成测试

## 安装

```bash
pip install zhipu-ai-sdk
```

开发环境安装：

```bash
pip install "zhipu-ai-sdk[dev]"
```

## 快速开始

### 基础使用

```python
import asyncio
from zhipuai import ZhipuAI
from zhipuai.models import ChatCompletionRequest, Message

async def main():
    # 初始化客户端
    client = ZhipuAI(api_key="your-api-key-here")

    # 创建请求
    request = ChatCompletionRequest(
        model="code-geex",
        messages=[
            Message(role="user", content="编写一个Python快速排序算法")
        ],
        max_tokens=1000,
        temperature=0.7
    )

    # 发送请求
    response = await client.chat.completions.create(request)

    # 打印结果
    print(response.choices[0].message.content)

# 运行
asyncio.run(main())
```

### 流式响应

```python
async def stream_example():
    client = ZhipuAI(api_key="your-api-key-here")

    request = ChatCompletionRequest(
        model="code-geex",
        messages=[
            Message(role="user", content="解释Python的异步编程")
        ],
        stream=True
    )

    # 处理流式响应
    async for chunk in client.chat.completions.create(request):
        if chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="")
```

### 高级功能

```python
from zhipuai.models import CodeAnalysisRequest, DebugRequest
from zhipuai.utils import BatchProcessor

async def advanced_example():
    client = ZhipuAI(api_key="your-api-key-here")

    # 代码分析
    analysis = await client.code.analyze(
        code="def example(): pass",
        language="python",
        analysis_type=["complexity", "security", "performance"]
    )
    print(analysis.report)

    # 代码调试
    debug_result = await client.code.debug(
        code="def buggy():\n    return 1/0",
        error_message="division by zero"
    )
    print(debug_result.suggested_fix)

    # 批量处理
    processor = BatchProcessor(client)
    tasks = [
        "生成斐波那契数列",
        "实现二分查找",
        "创建链表结构"
    ]

    results = await processor.process_batch(tasks)
    for i, result in enumerate(results):
        print(f"Task {i+1}: {result[:100]}...")
```

## 核心模块

### 1. HTTP客户端

```python
from zhipuai.core import HttpClient

# 自定义客户端
client = HttpClient(
    api_key="your-key",
    base_url="https://api.zhipuai.ai",
    timeout=30.0,
    max_retries=3,
    enable_compression=True
)
```

### 2. 数据模型

```python
from zhipuai.models import (
    ChatCompletionRequest,
    Message,
    Function,
    Tool
)

# 使用Pydantic模型
message = Message(
    role="user",
    content="帮我写一个装饰器",
    name="python_developer"
)

function = Function(
    name="execute_code",
    description="执行Python代码",
    parameters={
        "type": "object",
        "properties": {
            "code": {"type": "string"}
        }
    }
)
```

### 3. 错误处理

```python
from zhipuai.exceptions import (
    ZhipuAIError,
    RateLimitError,
    AuthenticationError,
    InvalidRequestError
)

try:
    response = await client.chat.completions.create(request)
except RateLimitError as e:
    print(f"请求超限: {e.retry_after}秒后重试")
except AuthenticationError:
    print("API密钥无效")
except ZhipuAIError as e:
    print(f"请求失败: {e.message}")
```

## 配置选项

### 环境变量

```bash
export ZHIPU_API_KEY="your-api-key"
export ZHIPU_BASE_URL="https://api.zhipuai.ai"
export ZHIPU_TIMEOUT=30
export ZHIPU_MAX_RETRIES=3
```

### 配置文件

```yaml
# ~/.zhipuai.yaml
client:
  api_key: ${ZHIPU_API_KEY}
  base_url: "https://api.zhipuai.ai"
  timeout: 30
  max_retries: 3
  enable_compression: true
  rate_limit:
    requests_per_second: 20
    burst_size: 100
  logging:
    level: "INFO"
    file: "zhipuai.log"
```

### 代码配置

```python
from zhipuai import ZhipuAI
from zhipuai.config import Config

# 使用配置对象
config = Config.from_file("config.yaml")
client = ZhipuAI(config=config)

# 直接设置
client = ZhipuAI(
    api_key="your-key",
    timeout=30,
    max_retries=3,
    rate_limit=RateLimitConfig(
        requests_per_second=20,
        burst_size=100
    )
)
```

## 性能优化

### 连接池配置

```python
client = ZhipuAI(
    api_key="your-key",
    http_client_config=HttpClientConfig(
        limits=httpx.Limits(
            max_keepalive_connections=100,
            max_connections=1000
        ),
        timeout=httpx.Timeout(
            connect=5.0,
            read=30.0,
            write=10.0,
            pool=30.0
        )
    )
)
```

### 缓存策略

```python
from zhipuai.cache import CacheConfig, CacheBackend

# 启用缓存
client = ZhipuAI(
    api_key="your-key",
    cache_config=CacheConfig(
        backend=CacheBackend.REDIS,
        ttl=3600,
        max_size=1000
    )
)
```

### 批量请求

```python
from zhipuai.utils import BatchProcessor, BatchConfig

processor = BatchProcessor(
    client=client,
    config=BatchConfig(
        batch_size=10,
        max_concurrency=5,
        timeout=300
    )
)

# 并发处理
results = await processor.process_batch_concurrent(prompts)
```

## 最佳实践

### 1. API密钥管理

```python
# 使用环境变量
import os
from zhipuai import ZhipuAI

client = ZhipuAI(api_key=os.getenv("ZHIPU_API_KEY"))

# 或使用密钥管理器
from zhipuai.auth import APIKeyManager

manager = APIKeyManager()
manager.add_key("key1", "value1")
client = ZhipuAI(api_key_manager=manager)
```

### 2. 重试策略

```python
from zhipuai.utils import RetryConfig

retry_config = RetryConfig(
    max_retries=3,
    backoff_strategy="exponential",
    initial_delay=1.0,
    max_delay=60.0,
    jitter=True
)

client = ZhipuAI(
    api_key="your-key",
    retry_config=retry_config
)
```

### 3. 监控和日志

```python
import logging
from zhipuai import ZhipuAI

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("zhipuai")

# 启用详细日志
client = ZhipuAI(
    api_key="your-key",
    enable_logging=True,
    log_level="DEBUG"
)

# 自定义监控
from zhipuai.monitoring import MetricsCollector

collector = MetricsCollector()
client = ZhipuAI(
    api_key="your-key",
    metrics_collector=collector
)
```

## 示例项目

查看 `examples/` 目录获取更多示例：

- [基础聊天](examples/basic_chat.py)
- [流式响应](examples/streaming.py)
- [代码生成](examples/code_generation.py)
- [批量处理](examples/batch_processing.py)
- [错误处理](examples/error_handling.py)
- [性能优化](examples/performance.py)

## 测试

运行测试套件：

```bash
# 安装开发依赖
pip install "zhipu-ai-sdk[dev]"

# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_client.py

# 运行带覆盖率的测试
pytest --cov=src --cov-report=html
```

## 贡献

欢迎贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详细信息。

## 许可证

MIT License。请查看 [LICENSE](LICENSE) 文件了解详细信息。

## 支持

- [文档](https://zhipu-ai-sdk.readthedocs.io)
- [GitHub Issues](https://github.com/zhipu-ai/zhipu-ai-sdk/issues)
- [邮件支持](mailto:support@zhipuai.ai)

## 更新日志

查看 [CHANGELOG.md](CHANGELOG.md) 了解版本更新信息。