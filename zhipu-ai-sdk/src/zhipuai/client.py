"""
智谱AI SDK主客户端

提供统一的API接口，封装所有智谱AI服务功能。
"""

import logging
from typing import Any, AsyncIterator, Dict, List, Optional, Union

from .version import __version__, API_VERSION
from .config import Config, Config
from .core import HttpClient, SyncHttpClient
from .core.streaming import StreamHandler, AccumulatorStreamHandler
from .core.retry import RetryHandler, CircuitBreaker
from .auth import AuthHandler, APIKeyManager
from .utils import RateLimiter, MetricsCollector, AsyncBatchProcessor
from .models import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    CodeAnalysisRequest,
    CodeAnalysisResponse,
    DebugRequest,
    DebugResponse,
    CompletionRequest,
    CompletionResponse,
)
from .exceptions import ZhipuAIError, ConfigurationError

logger = logging.getLogger(__name__)


class ZhipuAI:
    """智谱AI主客户端"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        *,
        config: Optional[Config] = None,
        api_key_manager: Optional[APIKeyManager] = None,
        metrics_collector: Optional[MetricsCollector] = None,
        **kwargs
    ):
        """初始化客户端

        Args:
            api_key: API密钥
            config: 配置对象
            api_key_manager: API密钥管理器
            metrics_collector: 指标收集器
            **kwargs: 其他配置参数
        """
        # 处理配置
        if config:
            self.config = config
        elif api_key:
            # 从参数创建配置
            self.config = Config(api_key=api_key, **kwargs)
        else:
            # 尝试从环境变量加载
            try:
                self.config = Config.from_env()
            except ValueError:
                raise ConfigurationError(
                    "API key is required. "
                    "Please provide api_key parameter or set ZHIPU_API_KEY environment variable."
                )

        # 初始化组件
        self._init_components()

        # 如果提供了外部API密钥管理器，使用它
        if api_key_manager:
            self.api_key_manager = api_key_manager

        # 设置指标收集器
        self.metrics_collector = metrics_collector

        # 初始化API模块
        self._init_api_modules()

    def _init_components(self) -> None:
        """初始化核心组件"""
        # 认证处理器
        self.auth = AuthHandler(
            api_key=self.config.api_key,
            organization=self.config.organization
        )

        # HTTP客户端
        self._http_client = HttpClient(
            config=self.config.http_client,
            api_key=self.config.api_key,
            organization=self.config.organization,
            metrics_collector=self.metrics_collector,
        )

        # 同步HTTP客户端
        self._sync_http_client = SyncHttpClient(
            config=self.config.http_client,
            api_key=self.config.api_key,
            organization=self.config.organization,
            metrics_collector=self.metrics_collector,
        )

        # 重试处理器
        self._retry_handler = RetryHandler(self.config.retry)

        # 断路器
        self._circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=60.0,
        )

        # 速率限制器
        self._rate_limiter = RateLimiter(
            requests_per_second=self.config.rate_limit.requests_per_second,
            burst_size=self.config.rate_limit.burst_size,
        )

        # API密钥管理器
        self.api_key_manager = APIKeyManager()

        # 批量处理器
        self._batch_processor = AsyncBatchProcessor(
            client=self,
            max_concurrency=5,
            batch_size=10,
        )

    def _init_api_modules(self) -> None:
        """初始化API模块"""
        # 聊天API
        self.chat = ChatAPI(self)

        # 补全API
        self.completion = CompletionAPI(self)

        # 代码API
        self.code = CodeAPI(self)

        # 模型API
        self.models = ModelsAPI(self)

        # 文件API（如果支持）
        self.files = FilesAPI(self)

    async def __aenter__(self):
        """异步上下文管理器入口"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close()

    def __enter__(self):
        """同步上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """同步上下文管理器出口"""
        self.close()

    async def close(self) -> None:
        """关闭客户端"""
        if hasattr(self, '_http_client') and self._http_client:
            await self._http_client.close()
        if hasattr(self, '_sync_http_client') and self._sync_http_client:
            self._sync_http_client.close()

    def close(self) -> None:
        """同步关闭客户端"""
        if hasattr(self, '_sync_http_client') and self._sync_http_client:
            self._sync_http_client.close()

    @property
    def http_client(self) -> HttpClient:
        """获取HTTP客户端"""
        return self._http_client

    @property
    def is_closed(self) -> bool:
        """检查客户端是否已关闭"""
        return self._http_client.is_closed

    async def _request(
        self,
        method: str,
        path: str,
        *,
        json_data: Optional[Dict[str, Any]] = None,
        stream: bool = False,
        **kwargs
    ) -> Union[Dict[str, Any], AsyncIterator[Dict[str, Any]]]:
        """发送API请求（内部方法）"""
        # 速率限制
        await self._rate_limiter.acquire()

        # 断路器保护
        async def do_request():
            response = await self._http_client.request(
                method=method,
                path=path,
                json_data=json_data,
                stream=stream,
                **kwargs
            )

            if stream:
                return response
            else:
                return response.json()

        # 带重试的请求
        return await self._retry_handler.execute_with_retry(do_request)

    def _sync_request(
        self,
        method: str,
        path: str,
        *,
        json_data: Optional[Dict[str, Any]] = None,
        stream: bool = False,
        **kwargs
    ) -> Union[Dict[str, Any], Any]:
        """发送同步API请求（内部方法）"""
        # 速率限制
        self._rate_limiter.sync_acquire()

        # 断路器保护
        def do_request():
            response = self._sync_http_client.request(
                method=method,
                path=path,
                json_data=json_data,
                stream=stream,
                **kwargs
            )

            if stream:
                return response
            else:
                return response.json()

        # 带重试的请求
        return self._retry_handler.execute_with_retry(do_request)

    def get_metrics(self) -> Optional[Dict[str, Any]]:
        """获取指标信息"""
        if self.metrics_collector:
            return self.metrics_collector.get_metrics()
        return None

    async def get_status(self) -> Dict[str, Any]:
        """获取客户端状态"""
        return {
            "version": __version__,
            "api_version": API_VERSION,
            "config": {
                "base_url": self.config.http_client.base_url,
                "timeout": str(self.config.http_client.timeout),
                "model": self.config.default_model,
            },
            "metrics": self.get_metrics(),
            "rate_limit": {
                "remaining": self._rate_limiter.remaining_tokens,
                "limit": self._rate_limiter.limit,
            },
        }


class APIBase:
    """API基类"""

    def __init__(self, client: ZhipuAI):
        self.client = client
        self.base_path = ""

    def _get_path(self, path: str) -> str:
        """构建完整路径"""
        return f"{self.base_path}{path}"


class ChatAPI(APIBase):
    """聊天API"""

    def __init__(self, client: ZhipuAI):
        super().__init__(client)
        self.base_path = f"/{API_VERSION}/chat"

    async def completions(
        self,
        request: ChatCompletionRequest,
        **kwargs
    ) -> Union[ChatCompletionResponse, AsyncIterator[Dict[str, Any]]]:
        """创建聊天完成"""
        # 转换请求为字典
        data = request.model_dump(exclude_none=True)

        # 发送请求
        if request.stream:
            # 流式响应
            response = await self.client._request(
                "POST",
                f"{self.base_path}/completions",
                json_data=data,
                stream=True,
                **kwargs
            )
            return response
        else:
            # 非流式响应
            response_data = await self.client._request(
                "POST",
                f"{self.base_path}/completions",
                json_data=data,
                **kwargs
            )
            return ChatCompletionResponse(**response_data)

    def sync_completions(
        self,
        request: ChatCompletionRequest,
        **kwargs
    ) -> Union[ChatCompletionResponse, Any]:
        """同步创建聊天完成"""
        data = request.model_dump(exclude_none=True)

        if request.stream:
            return self.client._sync_request(
                "POST",
                f"{self.base_path}/completions",
                json_data=data,
                stream=True,
                **kwargs
            )
        else:
            response_data = self.client._sync_request(
                "POST",
                f"{self.base_path}/completions",
                json_data=data,
                **kwargs
            )
            return ChatCompletionResponse(**response_data)


class CodeAPI(APIBase):
    """代码API"""

    def __init__(self, client: ZhipuAI):
        super().__init__(client)
        self.base_path = f"/{API_VERSION}/code"

    async def analyze(
        self,
        request: CodeAnalysisRequest,
        **kwargs
    ) -> CodeAnalysisResponse:
        """分析代码"""
        data = request.model_dump(exclude_none=True)
        response_data = await self.client._request(
            "POST",
            f"{self.base_path}/analyze",
            json_data=data,
            **kwargs
        )
        return CodeAnalysisResponse(**response_data)

    async def debug(
        self,
        request: DebugRequest,
        **kwargs
    ) -> DebugResponse:
        """调试代码"""
        data = request.model_dump(exclude_none=True)
        response_data = await self.client._request(
            "POST",
            f"{self.base_path}/debug",
            json_data=data,
            **kwargs
        )
        return DebugResponse(**response_data)


class CompletionAPI(APIBase):
    """补全API"""

    def __init__(self, client: ZhipuAI):
        super().__init__(client)
        self.base_path = f"/{API_VERSION}/completions"

    async def create(
        self,
        request: CompletionRequest,
        **kwargs
    ) -> CompletionResponse:
        """创建补全"""
        data = request.model_dump(exclude_none=True)
        response_data = await self.client._request(
            "POST",
            self.base_path,
            json_data=data,
            **kwargs
        )
        return CompletionResponse(**response_data)


class ModelsAPI(APIBase):
    """模型API"""

    def __init__(self, client: ZhipuAI):
        super().__init__(client)
        self.base_path = f"/{API_VERSION}/models"

    async def list(self) -> List[Dict[str, Any]]:
        """列出可用模型"""
        response_data = await self.client._request("GET", self.base_path)
        return response_data.get("data", [])

    async def retrieve(self, model_id: str) -> Dict[str, Any]:
        """获取模型详情"""
        response_data = await self.client._request(
            "GET",
            f"{self.base_path}/{model_id}"
        )
        return response_data


class FilesAPI(APIBase):
    """文件API"""

    def __init__(self, client: ZhipuAI):
        super().__init__(client)
        self.base_path = f"/{API_VERSION}/files"

    async def list(self) -> List[Dict[str, Any]]:
        """列出文件"""
        response_data = await self.client._request("GET", self.base_path)
        return response_data.get("data", [])

    async def upload(
        self,
        file_path: str,
        purpose: str,
        **kwargs
    ) -> Dict[str, Any]:
        """上传文件"""
        # TODO: 实现文件上传
        raise NotImplementedError("File upload not implemented yet")

    async def delete(self, file_id: str) -> Dict[str, Any]:
        """删除文件"""
        response_data = await self.client._request(
            "DELETE",
            f"{self.base_path}/{file_id}"
        )
        return response_data

    async def retrieve(self, file_id: str) -> Dict[str, Any]:
        """获取文件信息"""
        response_data = await self.client._request(
            "GET",
            f"{self.base_path}/{file_id}"
        )
        return response_data

    async def content(self, file_id: str) -> str:
        """获取文件内容"""
        response_data = await self.client._request(
            "GET",
            f"{self.base_path}/{file_id}/content"
        )
        return response_data.get("content", "")