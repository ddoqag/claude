"""
pytest配置文件

提供测试所需的fixtures和配置。
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from typing import Any, Dict

from zhipuai import ZhipuAI
from zhipuai.config import Config


@pytest.fixture
def event_loop():
    """创建事件循环"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_api_key():
    """模拟API密钥"""
    return "zhipu-test-key-1234567890"


@pytest.fixture
def mock_config(mock_api_key):
    """模拟配置"""
    return Config(
        api_key=mock_api_key,
        api_version="v1",
    )


@pytest.fixture
def client(mock_config):
    """创建测试客户端"""
    return ZhipuAI(config=mock_config)


@pytest.fixture
async def async_client(mock_config):
    """创建异步测试客户端"""
    async with ZhipuAI(config=mock_config) as client:
        yield client


@pytest.fixture
def mock_chat_response():
    """模拟聊天响应"""
    return {
        "id": "chatcmpl-test",
        "object": "chat.completion",
        "created": 1677652288,
        "model": "code-geex",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "Hello! How can I help you today?"
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 9,
            "completion_tokens": 12,
            "total_tokens": 21
        }
    }


@pytest.fixture
def mock_stream_response():
    """模拟流式响应块"""
    return [
        {"id": "chatcmpl-1", "object": "chat.completion.chunk", "choices": [{"delta": {"role": "assistant"}}]},
        {"id": "chatcmpl-1", "object": "chat.completion.chunk", "choices": [{"delta": {"content": "Hello"}}]},
        {"id": "chatcmpl-1", "object": "chat.completion.chunk", "choices": [{"delta": {"content": "!"}}]},
        {"id": "chatcmpl-1", "object": "chat.completion.chunk", "choices": [{"delta": {}, "finish_reason": "stop"}]},
    ]


@pytest.fixture
def mock_httpx_response(mock_chat_response):
    """模拟httpx响应"""
    response = Mock()
    response.is_success = True
    response.status_code = 200
    response.json.return_value = mock_chat_response
    response.headers = {"content-type": "application/json"}
    return response


@pytest.fixture
def mock_models_response():
    """模拟模型列表响应"""
    return {
        "object": "list",
        "data": [
            {
                "id": "code-geex",
                "object": "model",
                "created": 1677610602,
                "owned_by": "zhipu"
            },
            {
                "id": "glm-4",
                "object": "model",
                "created": 1677610602,
                "owned_by": "zhipu"
            }
        ]
    }


@pytest.fixture
def sample_code():
    """示例代码"""
    return """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
"""


@pytest.fixture
def error_response():
    """模拟错误响应"""
    return {
        "error": {
            "message": "Invalid API key",
            "type": "invalid_request_error",
            "param": "api_key",
            "code": "invalid_api_key"
        }
    }


@pytest.fixture
def mock_redis():
    """模拟Redis连接"""
    import fakeredis
    return fakeredis.FakeRedis(decode_responses=True)


@pytest.fixture
def temp_file(tmp_path):
    """创建临时文件"""
    file_path = tmp_path / "test.txt"
    file_path.write_text("Test content")
    return file_path


# 异步测试辅助函数
async def async_return(value):
    """异步返回值"""
    return value


# 测试标记
pytest_plugins = []

# 添加自定义标记
def pytest_configure(config):
    """配置pytest标记"""
    config.addinivalue_line(
        "markers", "unit: 单元测试"
    )
    config.addinivalue_line(
        "markers", "integration: 集成测试"
    )
    config.addinivalue_line(
        "markers", "slow: 慢速测试"
    )
    config.addinivalue_line(
        "markers", "network: 需要网络的测试"
    )