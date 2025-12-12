"""
流式响应处理模块

处理SSE格式的流式响应，支持大模型输出的实时处理。
"""

import asyncio
import json
import logging
from typing import Any, AsyncIterator, Dict, List, Optional, Union, Callable
from datetime import datetime

from ..exceptions import ZhipuAIError

logger = logging.getLogger(__name__)


class StreamHandler:
    """流式响应处理器"""

    def __init__(
        self,
        on_chunk: Optional[Callable[[Dict[str, Any]], None]] = None,
        on_error: Optional[Callable[[Exception], None]] = None,
        on_complete: Optional[Callable[[], None]] = None,
    ):
        self.on_chunk = on_chunk
        self.on_error = on_error
        self.on_complete = on_complete

        # 内部状态
        self._buffer = ""
        self._chunks: List[Dict[str, Any]] = []
        self._start_time: Optional[datetime] = None
        self._end_time: Optional[datetime] = None
        self._total_tokens = 0
        self._error: Optional[Exception] = None

    async def process_stream(
        self,
        stream: AsyncIterator[str],
        parse_json: bool = True
    ) -> AsyncIterator[Dict[str, Any]]:
        """处理流式响应"""
        self._start_time = datetime.now()
        self._error = None
        self._chunks.clear()
        self._total_tokens = 0

        try:
            async for line in stream:
                # 跳过空行和注释
                if not line.strip() or line.startswith(":"):
                    continue

                # 处理SSE数据行
                if line.startswith("data: "):
                    data = line[6:]  # 移除 "data: " 前缀

                    # 检查结束标记
                    if data == "[DONE]":
                        logger.debug("Stream received [DONE] marker")
                        break

                    # 解析数据
                    try:
                        if parse_json:
                            chunk = json.loads(data)
                        else:
                            chunk = {"raw": data}

                        # 更新统计信息
                        self._update_stats(chunk)

                        # 添加到内部列表
                        self._chunks.append(chunk)

                        # 调用回调
                        if self.on_chunk:
                            if asyncio.iscoroutinefunction(self.on_chunk):
                                await self.on_chunk(chunk)
                            else:
                                self.on_chunk(chunk)

                        # 生成给调用者
                        yield chunk

                    except json.JSONDecodeError as e:
                        logger.warning(f"Failed to parse JSON chunk: {data}")
                        error = ZhipuAIError(f"Invalid JSON in stream: {data}")
                        if self.on_error:
                            if asyncio.iscoroutinefunction(self.on_error):
                                await self.on_error(error)
                            else:
                                self.on_error(error)
                        raise error

        except Exception as e:
            self._error = e
            logger.error(f"Error processing stream: {e}")
            if self.on_error:
                if asyncio.iscoroutinefunction(self.on_error):
                    await self.on_error(e)
                else:
                    self.on_error(e)
            raise

        finally:
            self._end_time = datetime.now()
            if self.on_complete:
                if asyncio.iscoroutinefunction(self.on_complete):
                    await self.on_complete()
                else:
                    self.on_complete()

    def _update_stats(self, chunk: Dict[str, Any]) -> None:
        """更新统计信息"""
        # 提取使用量信息
        usage = chunk.get("usage")
        if usage:
            self._total_tokens = usage.get("total_tokens", 0)

    @property
    def duration(self) -> Optional[float]:
        """获取流持续时间（秒）"""
        if self._start_time and self._end_time:
            return (self._end_time - self._start_time).total_seconds()
        return None

    @property
    def chunks_count(self) -> int:
        """获取chunk数量"""
        return len(self._chunks)

    @property
    def total_tokens(self) -> int:
        """获取总token数"""
        return self._total_tokens

    @property
    def error(self) -> Optional[Exception]:
        """获取错误信息"""
        return self._error

    def get_accumulated_text(self) -> str:
        """获取累积的文本内容"""
        text_parts = []

        for chunk in self._chunks:
            # 处理聊天完成响应
            if "choices" in chunk:
                for choice in chunk["choices"]:
                    if "delta" in choice:
                        delta = choice["delta"]
                        if "content" in delta:
                            text_parts.append(delta["content"])
                    elif "text" in choice:
                        text_parts.append(choice["text"])

            # 处理其他格式
            elif "text" in chunk:
                text_parts.append(chunk["text"])

        return "".join(text_parts)

    def get_chunks(self) -> List[Dict[str, Any]]:
        """获取所有chunk"""
        return self._chunks.copy()


class AccumulatorStreamHandler(StreamHandler):
    """累积式流处理器"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._accumulated = ""

    async def process_stream(
        self,
        stream: AsyncIterator[str],
        parse_json: bool = True
    ) -> AsyncIterator[str]:
        """处理流式响应并累积文本"""
        async for chunk in super().process_stream(stream, parse_json):
            # 提取文本内容
            text = self._extract_text(chunk)
            if text:
                self._accumulated += text
                yield text

    def _extract_text(self, chunk: Dict[str, Any]) -> str:
        """从chunk中提取文本"""
        # 处理聊天完成响应
        if "choices" in chunk:
            for choice in chunk["choices"]:
                if "delta" in choice:
                    delta = choice["delta"]
                    return delta.get("content", "")
                elif "text" in choice:
                    return choice["text"]

        # 处理其他格式
        return chunk.get("text", "")

    @property
    def accumulated_text(self) -> str:
        """获取累积的文本"""
        return self._accumulated


class FilteredStreamHandler(StreamHandler):
    """过滤式流处理器"""

    def __init__(
        self,
        filter_func: Callable[[Dict[str, Any]], bool],
        **kwargs
    ):
        super().__init__(**kwargs)
        self.filter_func = filter_func

    async def process_stream(
        self,
        stream: AsyncIterator[str],
        parse_json: bool = True
    ) -> AsyncIterator[Dict[str, Any]]:
        """处理流式响应并过滤chunk"""
        async for chunk in super().process_stream(stream, parse_json):
            if self.filter_func(chunk):
                yield chunk


class BufferedStreamHandler(StreamHandler):
    """缓冲式流处理器"""

    def __init__(
        self,
        buffer_size: int = 5,
        flush_interval: float = 0.1,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.buffer_size = buffer_size
        self.flush_interval = flush_interval
        self._buffer: List[Dict[str, Any]] = []

    async def process_stream(
        self,
        stream: AsyncIterator[str],
        parse_json: bool = True
    ) -> AsyncIterator[List[Dict[str, Any]]]:
        """处理流式响应并缓冲"""
        last_flush = asyncio.get_event_loop().time()

        async for chunk in super().process_stream(stream, parse_json):
            self._buffer.append(chunk)

            current_time = asyncio.get_event_loop().time()
            should_flush = (
                len(self._buffer) >= self.buffer_size or
                current_time - last_flush >= self.flush_interval
            )

            if should_flush:
                yield self._buffer.copy()
                self._buffer.clear()
                last_flush = current_time

        # 刷新剩余的buffer
        if self._buffer:
            yield self._buffer
            self._buffer.clear()


class StreamBuffer:
    """流响应缓冲器"""

    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self._buffer: List[Dict[str, Any]] = []
        self._lock = asyncio.Lock()

    async def add(self, chunk: Dict[str, Any]) -> None:
        """添加chunk到缓冲区"""
        async with self._lock:
            self._buffer.append(chunk)
            # 保持缓冲区大小
            if len(self._buffer) > self.max_size:
                self._buffer = self._buffer[-self.max_size:]

    async def get_all(self) -> List[Dict[str, Any]]:
        """获取所有buffer内容"""
        async with self._lock:
            return self._buffer.copy()

    async def get_last(self, n: int) -> List[Dict[str, Any]]:
        """获取最后n个chunk"""
        async with self._lock:
            return self._buffer[-n:] if n > 0 else []

    async def clear(self) -> None:
        """清空缓冲区"""
        async with self._lock:
            self._buffer.clear()

    async def size(self) -> int:
        """获取缓冲区大小"""
        async with self._lock:
            return len(self._buffer)


class StreamCollector:
    """流响应收集器"""

    def __init__(self):
        self.chunks: List[Dict[str, Any]] = []
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.error: Optional[Exception] = None

    async def collect(
        self,
        stream: AsyncIterator[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """收集所有流响应"""
        self.start_time = datetime.now()
        self.chunks.clear()
        self.error = None

        try:
            async for chunk in stream:
                self.chunks.append(chunk)
        except Exception as e:
            self.error = e
            raise
        finally:
            self.end_time = datetime.now()

        return self.chunks

    def get_text(self) -> str:
        """获取所有文本内容"""
        parts = []

        for chunk in self.chunks:
            if "choices" in chunk:
                for choice in chunk["choices"]:
                    if "delta" in choice:
                        content = choice["delta"].get("content")
                        if content:
                            parts.append(content)
                    elif "text" in choice:
                        parts.append(choice["text"])
            elif "text" in chunk:
                parts.append(chunk["text"])

        return "".join(parts)

    def get_usage(self) -> Optional[Dict[str, Any]]:
        """获取使用量信息"""
        if self.chunks:
            # 返回最后一个chunk中的使用量
            return self.chunks[-1].get("usage")
        return None

    @property
    def duration(self) -> Optional[float]:
        """获取持续时间"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None

    @property
    def total_chunks(self) -> int:
        """获取总chunk数"""
        return len(self.chunks)