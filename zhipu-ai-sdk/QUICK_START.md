# 快速开始指南

本指南将帮助您快速开始使用智谱AI编码端点Python SDK。

## 安装

```bash
pip install zhipu-ai-sdk
```

开发环境安装：

```bash
pip install "zhipu-ai-sdk[dev]"
```

## 基础使用

### 1. 获取API密钥

1. 访问 [智谱AI开放平台](https://open.bigmodel.cn/)
2. 注册并登录账户
3. 创建应用并获取API密钥
4. 设置环境变量：

```bash
export ZHIPU_API_KEY="your-api-key-here"
```

### 2. 第一个示例

```python
import asyncio
from zhipuai import ZhipuAI
from zhipuai.models import ChatCompletionRequest, Message

async def main():
    # 创建客户端
    client = ZhipuAI(api_key="your-api-key-here")

    # 创建请求
    request = ChatCompletionRequest(
        model="code-geex",
        messages=[
            Message(role="user", content="用Python写一个快速排序算法")
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

### 3. 流式响应

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

## 高级功能

### 代码生成

```python
from zhipuai.models import CodeGenerationRequest

async def generate_code():
    client = ZhipuAI(api_key="your-api-key-here")

    request = CodeGenerationRequest(
        prompt="实现一个LRU缓存",
        language="python",
        style="oop",
        max_tokens=1000
    )

    response = await client.code.generate(request)
    print(response.code)
```

### 代码分析

```python
from zhipuai.models import CodeAnalysisRequest

async def analyze_code():
    client = ZhipuAI(api_key="your-api-key-here")

    code = """
    def fibonacci(n):
        if n <= 1:
            return n
        return fibonacci(n-1) + fibonacci(n-2)
    """

    request = CodeAnalysisRequest(
        code=code,
        language="python",
        analysis_type=["performance", "security", "complexity"]
    )

    response = await client.code.analyze(request)
    print(response.result.score)
```

### 批量处理

```python
from zhipuai.utils import AsyncBatchProcessor

async def batch_process():
    client = ZhipuAI(api_key="your-api-key-here")

    # 创建批量处理器
    processor = AsyncBatchProcessor(
        client=client,
        max_concurrency=5,
        batch_size=10
    )

    # 准备任务
    tasks = [
        "生成冒泡排序算法",
        "创建二叉树类",
        "实现装饰器",
        "写一个Web服务器"
    ]

    # 批量处理
    result = await processor.process_batch(tasks)
    print(f"成功: {len(result.successes)}, 失败: {len(result.failures)}")
```

## 配置

### 环境变量配置

```bash
export ZHIPU_API_KEY="your-api-key"
export ZHIPU_BASE_URL="https://api.zhipuai.ai"
export ZHIPU_TIMEOUT=30
export ZHIPU_MAX_RETRIES=3
```

### 配置文件

创建 `~/.zhipuai.yaml`:

```yaml
api_key: ${ZHIPU_API_KEY}
api_version: "v1"
default_model: "code-geex"

http_client:
  timeout:
    connect: 5.0
    read: 30.0
  max_retries: 3
  enable_compression: true

rate_limit:
  requests_per_second: 20
  burst_size: 100

retry:
  max_retries: 3
  backoff_strategy: "exponential"
  initial_delay: 1.0
  max_delay: 60.0
  jitter: true
```

### 代码配置

```python
from zhipuai import ZhipuAI
from zhipuai.config import Config, HttpClientConfig

# 创建自定义配置
config = Config(
    api_key="your-api-key",
    http_client=HttpClientConfig(
        timeout=30.0,
        max_retries=3,
    ),
    rate_limit=RateLimitConfig(
        requests_per_second=20
    )
)

# 使用配置创建客户端
client = ZhipuAI(config=config)
```

## 错误处理

```python
from zhipuai.exceptions import (
    RateLimitError,
    AuthenticationError,
    InvalidRequestError
)

async def handle_errors():
    client = ZhipuAI(api_key="your-api-key-here")

    try:
        response = await client.chat.completions.create(request)
    except RateLimitError as e:
        print(f"请求超限，{e.retry_after}秒后重试")
    except AuthenticationError:
        print("API密钥无效")
    except InvalidRequestError as e:
        print(f"请求无效: {e.message}")
```

## 最佳实践

### 1. 使用上下文管理器

```python
async def best_practice():
    # 推荐方式：使用上下文管理器
    async with ZhipuAI(api_key="your-api-key") as client:
        # 使用客户端
        response = await client.chat.completions.create(request)

    # 客户端会自动关闭
```

### 2. 设置合理的超时

```python
client = ZhipuAI(
    api_key="your-api-key",
    timeout=30.0  # 30秒超时
)
```

### 3. 使用批量处理提高效率

```python
# 对于大量任务，使用批量处理
processor = AsyncBatchProcessor(
    client=client,
    max_concurrency=5,  # 控制并发数
    batch_size=10,      # 控制批次大小
)

result = await processor.process_batch(large_task_list)
```

### 4. 启用指标收集

```python
from zhipuai.utils import MetricsCollector

# 创建指标收集器
metrics = MetricsCollector(sample_rate=0.1)

# 使用客户端
client = ZhipuAI(
    api_key="your-api-key",
    metrics_collector=metrics
)

# 获取指标
stats = client.get_metrics()
print(f"成功率: {stats['requests']['success_rate']}")
```

## 示例项目

查看 `examples/` 目录获取更多示例：

- [basic_chat.py](examples/basic_chat.py) - 基础聊天示例
- [streaming.py](examples/streaming.py) - 流式响应处理
- [code_generation.py](examples/code_generation.py) - 代码生成、分析、调试
- [batch_processing.py](examples/batch_processing.py) - 批量处理
- [error_handling.py](examples/error_handling.py) - 错误处理
- [performance.py](examples/performance.py) - 性能优化

## 故障排除

### 常见问题

1. **认证失败**
   - 检查API密钥是否正确
   - 确认密钥格式为 `zhipu-xxxxxxxxxxxxx`

2. **请求超时**
   - 增加timeout配置
   - 检查网络连接

3. **速率限制**
   - 降低请求频率
   - 使用批量处理
   - 实现指数退避

4. **模型不可用**
   - 检查模型名称是否正确
   - 查看支持的模型列表

### 调试模式

```python
import logging

# 启用调试日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("zhipuai")

client = ZhipuAI(
    api_key="your-api-key",
    enable_logging=True,
    log_level="DEBUG"
)
```

## 更多资源

- [完整文档](https://zhipu-ai-sdk.readthedocs.io)
- [API参考](https://open.bigmodel.cn/dev/api)
- [GitHub仓库](https://github.com/zhipu-ai/zhipu-ai-sdk)
- [问题反馈](https://github.com/zhipu-ai/zhipu-ai-sdk/issues)