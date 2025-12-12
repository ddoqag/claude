"""
智谱AI编码端点集成 SDK

提供完整、高性能、生产就绪的智谱AI API集成方案。
"""

from .client import ZhipuAI
from .version import __version__, VERSION
from .models import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    Message,
    CompletionRequest,
    CompletionResponse,
    CodeAnalysisRequest,
    CodeAnalysisResponse,
    DebugRequest,
    DebugResponse,
)
from .exceptions import (
    ZhipuAIError,
    APIError,
    AuthenticationError,
    PermissionDeniedError,
    NotFoundError,
    RateLimitError,
    InvalidRequestError,
    InternalServerError,
    ServiceUnavailableError,
    TimeoutError,
)
from .config import Config, HttpClientConfig, RetryConfig, RateLimitConfig
from .auth import APIKey, APIKeyManager
from .utils import (
    AsyncBatchProcessor,
    SyncBatchProcessor,
    RateLimiter,
    RetryStrategy,
    MetricsCollector,
)

__all__ = [
    # 版本
    "__version__",
    "VERSION",

    # 核心客户端
    "ZhipuAI",

    # 数据模型
    "ChatCompletionRequest",
    "ChatCompletionResponse",
    "Message",
    "CompletionRequest",
    "CompletionResponse",
    "CodeAnalysisRequest",
    "CodeAnalysisResponse",
    "DebugRequest",
    "DebugResponse",

    # 异常
    "ZhipuAIError",
    "APIError",
    "AuthenticationError",
    "PermissionDeniedError",
    "NotFoundError",
    "RateLimitError",
    "InvalidRequestError",
    "InternalServerError",
    "ServiceUnavailableError",
    "TimeoutError",

    # 配置
    "Config",
    "HttpClientConfig",
    "RetryConfig",
    "RateLimitConfig",

    # 认证
    "APIKey",
    "APIKeyManager",

    # 工具
    "AsyncBatchProcessor",
    "SyncBatchProcessor",
    "RateLimiter",
    "RetryStrategy",
    "MetricsCollector",
]