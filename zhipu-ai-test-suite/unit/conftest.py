"""
智谱AI编码端点集成项目 - 单元测试配置文件
提供测试夹具、Mock对象和通用测试工具
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, MagicMock
from typing import Dict, Any, Generator
import tempfile
import os


@pytest.fixture
def mock_zhipu_response():
    """模拟智谱AI API响应"""
    return {
        "code": 200,
        "msg": "success",
        "data": {
            "task_id": "test_task_123",
            "model": "codegeex4",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "def hello_world():\n    print('Hello, World!')\n    return True"
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": 100,
                "completion_tokens": 50,
                "total_tokens": 150
            }
        }
    }


@pytest.fixture
def mock_api_client():
    """模拟API客户端"""
    client = Mock()
    client.post = AsyncMock()
    client.get = AsyncMock()
    client.put = AsyncMock()
    client.delete = AsyncMock()
    return client


@pytest.fixture
def sample_code_snippet():
    """示例代码片段"""
    return {
        "language": "python",
        "code": "def calculate_sum(a, b):\n    return a + b\n\nresult = calculate_sum(5, 3)\nprint(result)",
        "description": "简单求和函数"
    }


@pytest.fixture
def temp_config_file():
    """临时配置文件"""
    config_data = {
        "api_endpoint": "https://open.bigmodel.cn/api/paas/v4/codegeex4",
        "api_key": "test_api_key",
        "model": "codegeex4",
        "max_tokens": 2000,
        "temperature": 0.7,
        "timeout": 30
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config_data, f)
        temp_file = f.name

    yield temp_file

    os.unlink(temp_file)


@pytest.fixture
def mock_websocket():
    """模拟WebSocket连接"""
    ws = Mock()
    ws.send = AsyncMock()
    ws.recv = AsyncMock()
    ws.close = AsyncMock()
    return ws


@pytest.fixture
def event_loop():
    """事件循环夹具"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_logger():
    """模拟日志记录器"""
    logger = Mock()
    logger.info = Mock()
    logger.warning = Mock()
    logger.error = Mock()
    logger.debug = Mock()
    return logger


class TestHelper:
    """测试辅助工具类"""

    @staticmethod
    def assert_valid_response(response: Dict[str, Any]) -> None:
        """验证响应格式"""
        assert "code" in response
        assert "msg" in response
        assert response["code"] == 200 or response["code"] == 0

    @staticmethod
    def assert_contains_keys(data: Dict[str, Any], keys: list) -> None:
        """验证数据包含指定键"""
        for key in keys:
            assert key in data, f"Missing key: {key}"

    @staticmethod
    def create_mock_stream_response():
        """创建流式响应Mock"""
        async def mock_stream():
            chunks = [
                '{"code": 200, "data": {"task_id": "test"}}',
                '{"delta": {"content": "def "}}',
                '{"delta": {"content": "hello():"}}',
                '{"delta": {"content": "\\n    "}}',
                '{"delta": {"content": "print(\'Hello\')"}}',
                '{"finish_reason": "stop"}'
            ]
            for chunk in chunks:
                yield chunk
                await asyncio.sleep(0.01)

        return mock_stream()


@pytest.fixture
def test_helper():
    """测试辅助工具夹具"""
    return TestHelper()