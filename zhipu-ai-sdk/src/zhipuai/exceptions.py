"""
异常定义模块

定义所有SDK相关的异常类型。
"""

from typing import Any, Dict, Optional


class ZhipuAIError(Exception):
    """智谱AI SDK基础异常类"""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response = response
        self.headers = headers or {}

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"message={self.message!r}, "
            f"status_code={self.status_code}, "
            f"response={self.response!r}"
            f")"
        )


class APIError(ZhipuAIError):
    """API错误基类"""
    pass


class AuthenticationError(APIError):
    """认证错误"""
    pass


class PermissionDeniedError(APIError):
    """权限不足错误"""
    pass


class NotFoundError(APIError):
    """资源不存在错误"""
    pass


class RateLimitError(APIError):
    """速率限制错误"""

    def __init__(
        self,
        message: str,
        retry_after: Optional[int] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.retry_after = retry_after


class InvalidRequestError(APIError):
    """无效请求错误"""

    def __init__(
        self,
        message: str,
        param: Optional[str] = None,
        type: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.param = param
        self.type = type


class InternalServerError(APIError):
    """服务器内部错误"""
    pass


class ServiceUnavailableError(APIError):
    """服务不可用错误"""
    pass


class TimeoutError(APIError):
    """请求超时错误"""
    pass


class NetworkError(ZhipuAIError):
    """网络错误"""
    pass


class ConfigurationError(ZhipuAIError):
    """配置错误"""
    pass


class ValidationError(ZhipuAIError):
    """数据验证错误"""
    pass


class CacheError(ZhipuAIError):
    """缓存错误"""
    pass


class AuthenticationError(APIError):
    """认证错误"""
    pass


# 错误码映射
ERROR_CODE_MAP: Dict[int, type] = {
    400: InvalidRequestError,
    401: AuthenticationError,
    403: PermissionDeniedError,
    404: NotFoundError,
    429: RateLimitError,
    500: InternalServerError,
    502: ServiceUnavailableError,
    503: ServiceUnavailableError,
    504: TimeoutError,
}


def create_error_from_response(
    status_code: int,
    response: Dict[str, Any],
    headers: Optional[Dict[str, str]] = None
) -> ZhipuAIError:
    """从API响应创建相应的错误对象"""

    error_class = ERROR_CODE_MAP.get(status_code, APIError)

    # 提取错误信息
    error_info = response.get("error", {})
    message = error_info.get("message", f"HTTP {status_code} error")

    # 特殊处理速率限制错误
    if status_code == 429:
        retry_after = None
        if headers:
            retry_after = headers.get("retry-after")
            if retry_after:
                try:
                    retry_after = int(retry_after)
                except ValueError:
                    retry_after = None
        return RateLimitError(
            message=message,
            status_code=status_code,
            response=response,
            headers=headers,
            retry_after=retry_after
        )

    # 特殊处理无效请求错误
    if status_code == 400:
        param = error_info.get("param")
        error_type = error_info.get("type")
        return InvalidRequestError(
            message=message,
            status_code=status_code,
            response=response,
            headers=headers,
            param=param,
            type=error_type
        )

    # 创建通用错误
    return error_class(
        message=message,
        status_code=status_code,
        response=response,
        headers=headers
    )