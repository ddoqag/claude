"""
速率限制器

提供多种速率限制算法实现。
"""

import asyncio
import time
from abc import ABC, abstractmethod
from collections import deque
from typing import Optional


class RateLimiter(ABC):
    """速率限制器基类"""

    @abstractmethod
    async def acquire(self) -> None:
        """获取许可"""
        pass

    @abstractmethod
    def sync_acquire(self) -> None:
        """同步获取许可"""
        pass


class TokenBucketRateLimiter(RateLimiter):
    """令牌桶限流器"""

    def __init__(
        self,
        requests_per_second: float,
        burst_size: Optional[int] = None,
    ):
        self.rate = requests_per_second
        self.burst_size = burst_size or int(requests_per_second * 2)
        self.tokens = self.burst_size
        self.last_update = time.time()
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        """异步获取许可"""
        async with self._lock:
            now = time.time()
            # 添加新令牌
            elapsed = now - self.last_update
            self.tokens += elapsed * self.rate
            self.tokens = min(self.tokens, self.burst_size)
            self.last_update = now

            # 消耗令牌
            if self.tokens >= 1:
                self.tokens -= 1
                return

            # 计算等待时间
            wait_time = 1.0 - self.tokens
            self.tokens = 0
            await asyncio.sleep(wait_time)

    def sync_acquire(self) -> None:
        """同步获取许可"""
        now = time.time()
        # 添加新令牌
        elapsed = now - self.last_update
        self.tokens += elapsed * self.rate
        self.tokens = min(self.tokens, self.burst_size)
        self.last_update = now

        # 消耗令牌
        if self.tokens >= 1:
            self.tokens -= 1
            return

        # 计算等待时间
        wait_time = 1.0 - self.tokens
        self.tokens = 0
        time.sleep(wait_time)

    @property
    def remaining_tokens(self) -> float:
        """获取剩余令牌数"""
        now = time.time()
        elapsed = now - self.last_update
        tokens = self.tokens + elapsed * self.rate
        return min(tokens, self.burst_size)


class SlidingWindowRateLimiter(RateLimiter):
    """滑动窗口限流器"""

    def __init__(
        self,
        requests_per_second: float,
        window_size: float = 1.0,
    ):
        self.rate = requests_per_second
        self.window_size = window_size
        self.max_requests = int(requests_per_second * window_size)
        self.requests = deque()
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        """异步获取许可"""
        async with self._lock:
            now = time.time()
            # 清理过期的请求
            while self.requests and self.requests[0] <= now - self.window_size:
                self.requests.popleft()

            # 检查是否超过限制
            if len(self.requests) >= self.max_requests:
                # 计算等待时间
                oldest_request = self.requests[0]
                wait_time = self.window_size - (now - oldest_request)
                await asyncio.sleep(wait_time)
                await self.acquire()  # 递归重试
                return

            # 记录当前请求
            self.requests.append(now)

    def sync_acquire(self) -> None:
        """同步获取许可"""
        now = time.time()
        # 清理过期的请求
        while self.requests and self.requests[0] <= now - self.window_size:
            self.requests.popleft()

        # 检查是否超过限制
        if len(self.requests) >= self.max_requests:
            # 计算等待时间
            oldest_request = self.requests[0]
            wait_time = self.window_size - (now - oldest_request)
            time.sleep(wait_time)
            self.sync_acquire()  # 递归重试
            return

        # 记录当前请求
        self.requests.append(now)

    @property
    def remaining_tokens(self) -> int:
        """获取剩余请求数"""
        now = time.time()
        while self.requests and self.requests[0] <= now - self.window_size:
            self.requests.popleft()
        return self.max_requests - len(self.requests)


class FixedWindowRateLimiter(RateLimiter):
    """固定窗口限流器"""

    def __init__(
        self,
        requests_per_second: float,
        window_size: float = 1.0,
    ):
        self.rate = requests_per_second
        self.window_size = window_size
        self.max_requests = int(requests_per_second * window_size)
        self.current_requests = 0
        self.window_start = time.time()
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        """异步获取许可"""
        async with self._lock:
            now = time.time()
            # 检查是否需要重置窗口
            if now - self.window_start >= self.window_size:
                self.current_requests = 0
                self.window_start = now

            # 检查是否超过限制
            if self.current_requests >= self.max_requests:
                # 计算等待时间
                wait_time = self.window_size - (now - self.window_start)
                await asyncio.sleep(wait_time)
                await self.acquire()  # 递归重试
                return

            # 增加请求计数
            self.current_requests += 1

    def sync_acquire(self) -> None:
        """同步获取许可"""
        now = time.time()
        # 检查是否需要重置窗口
        if now - self.window_start >= self.window_size:
            self.current_requests = 0
            self.window_start = now

        # 检查是否超过限制
        if self.current_requests >= self.max_requests:
            # 计算等待时间
            wait_time = self.window_size - (now - self.window_start)
            time.sleep(wait_time)
            self.sync_acquire()  # 递归重试
            return

        # 增加请求计数
        self.current_requests += 1

    @property
    def remaining_tokens(self) -> int:
        """获取剩余请求数"""
        now = time.time()
        if now - self.window_start >= self.window_size:
            return self.max_requests
        return self.max_requests - self.current_requests


# 为了向后兼容，使用令牌桶作为默认实现
RateLimiter = TokenBucketRateLimiter