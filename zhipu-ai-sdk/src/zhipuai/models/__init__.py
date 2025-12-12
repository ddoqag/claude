"""
数据模型定义

包含所有请求和响应的Pydantic模型定义。
"""

from .chat import (
    Message,
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatCompletionChoice,
    ChatCompletionStreamResponse,
    Delta,
    Function,
    Tool,
)
from .completion import (
    CompletionRequest,
    CompletionResponse,
    CompletionChoice,
    CompletionLogprobs,
)
from .code import (
    CodeAnalysisRequest,
    CodeAnalysisResponse,
    DebugRequest,
    DebugResponse,
    CodeGenerationRequest,
    CodeGenerationResponse,
)
from .common import (
    Usage,
    BaseResponse,
    BaseRequest,
    Error,
    Model,
)

__all__ = [
    # 通用模型
    "BaseRequest",
    "BaseResponse",
    "Usage",
    "Error",
    "Model",

    # 聊天模型
    "Message",
    "ChatCompletionRequest",
    "ChatCompletionResponse",
    "ChatCompletionChoice",
    "ChatCompletionStreamResponse",
    "Delta",
    "Function",
    "Tool",

    # 补全模型
    "CompletionRequest",
    "CompletionResponse",
    "CompletionChoice",
    "CompletionLogprobs",

    # 代码相关模型
    "CodeAnalysisRequest",
    "CodeAnalysisResponse",
    "DebugRequest",
    "DebugResponse",
    "CodeGenerationRequest",
    "CodeGenerationResponse",
]