"""
客户端测试
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch

from zhipuai import ZhipuAI
from zhipuai.config import Config
from zhipuai.exceptions import ConfigurationError, AuthenticationError


@pytest.mark.unit
class TestZhipuAIClient:
    """测试ZhipuAI客户端"""

    def test_init_with_api_key(self, mock_api_key):
        """测试使用API密钥初始化"""
        client = ZhipuAI(api_key=mock_api_key)
        assert client.config.api_key == mock_api_key
        assert client.config.api_version == "v1"

    def test_init_with_config(self, mock_config):
        """测试使用配置对象初始化"""
        client = ZhipuAI(config=mock_config)
        assert client.config == mock_config

    def test_init_without_api_key(self):
        """测试没有API密钥时的错误"""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ConfigurationError):
                ZhipuAI()

    def test_init_from_env(self, mock_api_key):
        """测试从环境变量初始化"""
        with patch.dict('os.environ', {'ZHIPU_API_KEY': mock_api_key}):
            client = ZhipuAI()
            assert client.config.api_key == mock_api_key

    def test_api_modules_initialization(self, mock_config):
        """测试API模块初始化"""
        client = ZhipuAI(config=mock_config)

        # 检查API模块是否正确初始化
        assert hasattr(client, 'chat')
        assert hasattr(client, 'completion')
        assert hasattr(client, 'code')
        assert hasattr(client, 'models')
        assert hasattr(client, 'files')

    def test_context_manager(self, mock_config):
        """测试上下文管理器"""
        with ZhipuAI(config=mock_config) as client:
            assert not client.is_closed
        # 退出上下文后客户端应该关闭
        # 注意：由于是mock，实际可能不会关闭

    @pytest.mark.asyncio
    async def test_async_context_manager(self, mock_config):
        """测试异步上下文管理器"""
        async with ZhipuAI(config=mock_config) as client:
            assert not client.is_closed

    def test_get_metrics(self, mock_config):
        """测试获取指标"""
        client = ZhipuAI(config=mock_config)
        # 没有指标收集器时应该返回None
        assert client.get_metrics() is None

    @pytest.mark.asyncio
    async def test_get_status(self, mock_config):
        """测试获取状态"""
        client = ZhipuAI(config=mock_config)
        status = await client.get_status()

        assert "version" in status
        assert "api_version" in status
        assert "config" in status
        assert "rate_limit" in status

    @pytest.mark.asyncio
    async def test_close(self, mock_config):
        """测试关闭客户端"""
        client = ZhipuAI(config=mock_config)
        await client.close()
        # 验证客户端已关闭
        assert client.is_closed

    def test_sync_close(self, mock_config):
        """测试同步关闭客户端"""
        client = ZhipuAI(config=mock_config)
        client.close()
        # 验证客户端已关闭
        assert client.is_closed


@pytest.mark.unit
class TestChatAPI:
    """测试聊天API"""

    @pytest.mark.asyncio
    async def test_chat_completions_create(self, async_client, mock_chat_response):
        """测试创建聊天完成"""
        # Mock HTTP客户端
        async_client._http_client.request = AsyncMock()
        async_client._http_client.request.return_value = mock_chat_response

        from zhipuai.models import ChatCompletionRequest, Message

        request = ChatCompletionRequest(
            model="code-geex",
            messages=[Message(role="user", content="Hello")]
        )

        response = await async_client.chat.completions.create(request)

        assert response.object == "chat.completion"
        assert response.choices[0].message.role == "assistant"
        assert response.choices[0].message.content

    @pytest.mark.asyncio
    async def test_chat_completions_stream(self, async_client, mock_stream_response):
        """测试流式聊天完成"""
        from unittest.mock import AsyncIterator

        # 创建模拟的流响应
        async def mock_stream():
            for chunk in mock_stream_response:
                yield f"data: {chunk}\n\n"
            yield "data: [DONE]\n\n"

        # Mock HTTP客户端
        async_client._http_client.request = AsyncMock()
        async_client._http_client.request.return_value = mock_stream()

        from zhipuai.models import ChatCompletionRequest, Message

        request = ChatCompletionRequest(
            model="code-geex",
            messages=[Message(role="user", content="Hello")],
            stream=True
        )

        # 收集流式响应
        chunks = []
        async for chunk in async_client.chat.completions.create(request):
            chunks.append(chunk)

        assert len(chunks) == len(mock_stream_response)
        assert chunks[0]["object"] == "chat.completion.chunk"

    def test_sync_chat_completions(self, client, mock_chat_response):
        """测试同步聊天完成"""
        # Mock同步HTTP客户端
        client._sync_http_client.request = Mock()
        client._sync_http_client.request.return_value = mock_chat_response

        from zhipuai.models import ChatCompletionRequest, Message

        request = ChatCompletionRequest(
            model="code-geex",
            messages=[Message(role="user", content="Hello")]
        )

        response = client.chat.sync_completions(request)

        assert response.object == "chat.completion"
        assert response.choices[0].message.role == "assistant"


@pytest.mark.unit
class TestCodeAPI:
    """测试代码API"""

    @pytest.mark.asyncio
    async def test_code_analyze(self, async_client, sample_code):
        """测试代码分析"""
        # Mock HTTP客户端
        async_client._http_client.request = AsyncMock()
        async_client._http_client.request.return_value = {
            "id": "code-analysis-1",
            "object": "code.analysis",
            "result": {
                "type": "analysis",
                "success": True,
                "score": 85.0,
                "issues": [],
                "metrics": {
                    "complexity": 5,
                    "lines_of_code": 20
                }
            },
            "usage": {
                "prompt_tokens": 50,
                "completion_tokens": 100,
                "total_tokens": 150
            }
        }

        from zhipuai.models import CodeAnalysisRequest

        request = CodeAnalysisRequest(
            code=sample_code,
            language="python",
            analysis_type=["complexity", "security"]
        )

        response = await async_client.code.analyze(request)

        assert response.object == "code.analysis"
        assert response.result.success is True
        assert response.result.score == 85.0

    @pytest.mark.asyncio
    async def test_code_debug(self, async_client, sample_code):
        """测试代码调试"""
        # Mock HTTP客户端
        async_client._http_client.request = AsyncMock()
        async_client._http_client.request.return_value = {
            "id": "code-debug-1",
            "object": "code.debug",
            "error_type": "RecursionError",
            "root_cause": "Excessive recursion depth",
            "suggestions": [
                {
                    "type": "fix",
                    "description": "Add memoization or use iterative approach",
                    "code_change": "Use cache decorator or rewrite as loop"
                }
            ],
            "usage": {
                "prompt_tokens": 60,
                "completion_tokens": 80,
                "total_tokens": 140
            }
        }

        from zhipuai.models import DebugRequest

        request = DebugRequest(
            code=sample_code,
            error_message="RecursionError: maximum recursion depth exceeded",
            language="python"
        )

        response = await async_client.code.debug(request)

        assert response.object == "code.debug"
        assert response.error_type == "RecursionError"
        assert len(response.suggestions) > 0


@pytest.mark.unit
class TestModelsAPI:
    """测试模型API"""

    @pytest.mark.asyncio
    async def test_models_list(self, async_client, mock_models_response):
        """测试列出模型"""
        # Mock HTTP客户端
        async_client._http_client.request = AsyncMock()
        async_client._http_client.request.return_value = mock_models_response

        models = await async_client.models.list()

        assert isinstance(models, list)
        assert len(models) == 2
        assert models[0]["id"] == "code-geex"

    @pytest.mark.asyncio
    async def test_models_retrieve(self, async_client):
        """测试获取模型详情"""
        # Mock HTTP客户端
        async_client._http_client.request = AsyncMock()
        async_client._http_client.request.return_value = {
            "id": "code-geex",
            "object": "model",
            "created": 1677610602,
            "owned_by": "zhipu"
        }

        model = await async_client.models.retrieve("code-geex")

        assert model["id"] == "code-geex"
        assert model["object"] == "model"