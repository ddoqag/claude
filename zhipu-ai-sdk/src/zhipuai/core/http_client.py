"""
HTTP客户端实现

基于httpx的高性能异步HTTP客户端，支持连接池、HTTP/2、代理等特性。
"""

import json
import logging
import time
from typing import Any, Dict, Optional, Union, AsyncIterator, Iterator
from urllib.parse import urljoin

import httpx
from httpx import Response, Limits, Timeout

from ..config import HttpClientConfig
from ..exceptions import (
    ZhipuAIError,
    APIError,
    NetworkError,
    TimeoutError,
    create_error_from_response,
)
from ..utils.metrics import MetricsCollector

logger = logging.getLogger(__name__)


class HttpClient:
    """智谱AI HTTP客户端"""

    def __init__(
        self,
        config: HttpClientConfig,
        api_key: str,
        organization: Optional[str] = None,
        metrics_collector: Optional[MetricsCollector] = None,
    ):
        self.config = config
        self.api_key = api_key
        self.organization = organization
        self.metrics_collector = metrics_collector

        # 创建httpx客户端
        self._client = httpx.AsyncClient(
            base_url=config.base_url,
            timeout=config.timeout,
            limits=config.limits,
            headers=self._build_headers(),
            proxy=config.proxy,
            verify=config.verify_ssl,
            follow_redirects=config.follow_redirects,
            http2=True,  # 启用HTTP/2
            default_encoding="utf-8",
        )

        # 记录创建时间
        self._created_at = time.time()

    async def __aenter__(self):
        """异步上下文管理器入口"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close()

    def _build_headers(self) -> Dict[str, str]:
        """构建请求头"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": self._get_user_agent(),
        }

        if self.organization:
            headers["OpenAI-Organization"] = self.organization

        # 添加自定义头
        headers.update(self.config.headers)

        # 启用压缩
        if self.config.enable_compression:
            headers["Accept-Encoding"] = "gzip, deflate"

        return headers

    def _get_user_agent(self) -> str:
        """获取用户代理字符串"""
        from ..version import __version__, PROJECT_NAME

        if self.config.user_agent:
            return self.config.user_agent

        return f"{PROJECT_NAME}/{__version__} (Python)"

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        stream: bool = False,
        timeout: Optional[Timeout] = None,
        **kwargs
    ) -> Union[Response, AsyncIterator[Dict[str, Any]]]:
        """发送HTTP请求"""

        # 记录请求开始时间
        start_time = time.time()

        # 构建URL
        url = urljoin(str(self.config.base_url), path.lstrip("/"))

        # 准备请求数据
        request_data = {
            "method": method.upper(),
            "url": url,
            "params": params,
            "headers": self._build_headers(),
            "files": files,
        }

        # 处理请求体
        if json_data:
            request_data["json"] = json_data
        elif data:
            request_data["data"] = data

        # 处理超时
        if timeout:
            request_data["timeout"] = timeout
        else:
            request_data["timeout"] = self.config.timeout

        # 添加其他参数
        request_data.update(kwargs)

        # 记录请求
        logger.debug(f"Sending request: {method} {url}")

        try:
            # 发送请求
            if stream:
                response = self._client.stream(**request_data)
            else:
                response = await self._client.request(**request_data)

            # 记录响应时间
            duration = time.time() - start_time

            # 收集指标
            if self.metrics_collector:
                self.metrics_collector.record_request(
                    method=method.upper(),
                    path=path,
                    status_code=response.status_code,
                    duration=duration,
                )

            # 处理响应
            if not stream:
                await self._handle_response(response)
                return response
            else:
                return self._handle_stream_response(response, start_time)

        except httpx.TimeoutException as e:
            duration = time.time() - start_time
            logger.error(f"Request timeout after {duration:.2f}s: {e}")
            if self.metrics_collector:
                self.metrics_collector.record_error("timeout", duration)
            raise TimeoutError(f"Request timeout: {e}") from e

        except httpx.NetworkError as e:
            duration = time.time() - start_time
            logger.error(f"Network error after {duration:.2f}s: {e}")
            if self.metrics_collector:
                self.metrics_collector.record_error("network", duration)
            raise NetworkError(f"Network error: {e}") from e

        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Unexpected error after {duration:.2f}s: {e}")
            if self.metrics_collector:
                self.metrics_collector.record_error("unknown", duration)
            raise ZhipuAIError(f"Unexpected error: {e}") from e

    async def _handle_response(self, response: Response) -> None:
        """处理非流式响应"""
        # 检查状态码
        if not response.is_success:
            try:
                error_data = response.json()
            except Exception:
                error_data = {"message": response.text}

            error = create_error_from_response(
                status_code=response.status_code,
                response=error_data,
                headers=dict(response.headers),
            )
            raise error

    async def _handle_stream_response(
        self,
        response: Response,
        start_time: float
    ) -> AsyncIterator[Dict[str, Any]]:
        """处理流式响应"""
        buffer = ""
        async with response:
            async for line in response.aiter_lines():
                if not line.strip():
                    continue

                # 处理SSE格式
                if line.startswith("data: "):
                    data = line[6:]  # 去掉 "data: " 前缀

                    # 检查结束标记
                    if data == "[DONE]":
                        break

                    try:
                        # 尝试解析JSON
                        chunk = json.loads(data)
                        yield chunk
                    except json.JSONDecodeError:
                        # 如果不是JSON，可能是错误消息
                        logger.warning(f"Invalid JSON in stream: {data}")
                        continue

    async def get(
        self,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Response:
        """发送GET请求"""
        return await self.request("GET", path, params=params, **kwargs)

    async def post(
        self,
        path: str,
        *,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Response:
        """发送POST请求"""
        return await self.request(
            "POST",
            path,
            data=data,
            json_data=json_data,
            **kwargs
        )

    async def put(
        self,
        path: str,
        *,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Response:
        """发送PUT请求"""
        return await self.request(
            "PUT",
            path,
            data=data,
            json_data=json_data,
            **kwargs
        )

    async def delete(
        self,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Response:
        """发送DELETE请求"""
        return await self.request("DELETE", path, params=params, **kwargs)

    async def close(self) -> None:
        """关闭客户端"""
        if self._client:
            await self._client.aclose()
            logger.debug("HTTP client closed")

    @property
    def is_closed(self) -> bool:
        """检查客户端是否已关闭"""
        return self._client.is_closed

    async def __del__(self):
        """析构函数"""
        if hasattr(self, '_client') and not self._client.is_closed:
            await self._client.aclose()


class SyncHttpClient:
    """同步HTTP客户端包装器"""

    def __init__(
        self,
        config: HttpClientConfig,
        api_key: str,
        organization: Optional[str] = None,
        metrics_collector: Optional[MetricsCollector] = None,
    ):
        self.config = config
        self.api_key = api_key
        self.organization = organization
        self.metrics_collector = metrics_collector

        # 创建httpx同步客户端
        self._client = httpx.Client(
            base_url=config.base_url,
            timeout=config.timeout,
            limits=config.limits,
            headers=self._build_headers(),
            proxy=config.proxy,
            verify=config.verify_ssl,
            follow_redirects=config.follow_redirects,
            http2=True,
            default_encoding="utf-8",
        )

    def _build_headers(self) -> Dict[str, str]:
        """构建请求头"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": self._get_user_agent(),
        }

        if self.organization:
            headers["OpenAI-Organization"] = self.organization

        headers.update(self.config.headers)

        if self.config.enable_compression:
            headers["Accept-Encoding"] = "gzip, deflate"

        return headers

    def _get_user_agent(self) -> str:
        """获取用户代理字符串"""
        from ..version import __version__, PROJECT_NAME

        if self.config.user_agent:
            return self.config.user_agent

        return f"{PROJECT_NAME}/{__version__} (Python)"

    def request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        stream: bool = False,
        **kwargs
    ) -> Union[Response, Iterator[Dict[str, Any]]]:
        """发送HTTP请求"""
        start_time = time.time()
        url = urljoin(str(self.config.base_url), path.lstrip("/"))

        request_data = {
            "method": method.upper(),
            "url": url,
            "params": params,
            "headers": self._build_headers(),
            "files": files,
        }

        if json_data:
            request_data["json"] = json_data
        elif data:
            request_data["data"] = data

        request_data.update(kwargs)

        logger.debug(f"Sending request: {method} {url}")

        try:
            if stream:
                response = self._client.stream(**request_data)
            else:
                response = self._client.request(**request_data)

            duration = time.time() - start_time

            if self.metrics_collector:
                self.metrics_collector.record_request(
                    method=method.upper(),
                    path=path,
                    status_code=response.status_code,
                    duration=duration,
                )

            if not stream:
                self._handle_response(response)
                return response
            else:
                return self._handle_stream_response(response, start_time)

        except httpx.TimeoutException as e:
            duration = time.time() - start_time
            logger.error(f"Request timeout after {duration:.2f}s: {e}")
            if self.metrics_collector:
                self.metrics_collector.record_error("timeout", duration)
            raise TimeoutError(f"Request timeout: {e}") from e

        except httpx.NetworkError as e:
            duration = time.time() - start_time
            logger.error(f"Network error after {duration:.2f}s: {e}")
            if self.metrics_collector:
                self.metrics_collector.record_error("network", duration)
            raise NetworkError(f"Network error: {e}") from e

        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Unexpected error after {duration:.2f}s: {e}")
            if self.metrics_collector:
                self.metrics_collector.record_error("unknown", duration)
            raise ZhipuAIError(f"Unexpected error: {e}") from e

    def _handle_response(self, response: Response) -> None:
        """处理响应"""
        if not response.is_success:
            try:
                error_data = response.json()
            except Exception:
                error_data = {"message": response.text}

            error = create_error_from_response(
                status_code=response.status_code,
                response=error_data,
                headers=dict(response.headers),
            )
            raise error

    def _handle_stream_response(
        self,
        response: Response,
        start_time: float
    ) -> Iterator[Dict[str, Any]]:
        """处理流式响应"""
        with response:
            for line in response.iter_lines():
                if not line.strip():
                    continue

                if line.startswith("data: "):
                    data = line[6:]

                    if data == "[DONE]":
                        break

                    try:
                        chunk = json.loads(data)
                        yield chunk
                    except json.JSONDecodeError:
                        logger.warning(f"Invalid JSON in stream: {data}")
                        continue

    def close(self) -> None:
        """关闭客户端"""
        if self._client:
            self._client.close()
            logger.debug("Sync HTTP client closed")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()