"""
重试机制模块

提供灵活的重试策略和错误处理机制。
"""

import asyncio
import random
import time
import logging
from typing import Any, Callable, Optional, Set, Type, Union
from functools import wraps

from ..config import RetryConfig
from ..exceptions import (
    ZhipuAIError,
    RateLimitError,
    APIError,
    NetworkError,
    TimeoutError,
)

logger = logging.getLogger(__name__)


class RetryStrategy:
    """重试策略基类"""

    def __init__(self, config: RetryConfig):
        self.config = config
        self._attempt = 0

    async def get_delay(self, attempt: int, error: Optional[Exception] = None) -> float:
        """获取重试延迟时间"""
        raise NotImplementedError

    def should_retry(self, error: Exception) -> bool:
        """判断是否应该重试"""
        return self._attempt < self.config.max_retries

    def reset(self) -> None:
        """重置重试计数"""
        self._attempt = 0

    def increment(self) -> int:
        """增加重试次数"""
        self._attempt += 1
        return self._attempt

    @property
    def attempts(self) -> int:
        """获取当前重试次数"""
        return self._attempt


class LinearBackoffStrategy(RetryStrategy):
    """线性退避策略"""

    async def get_delay(self, attempt: int, error: Optional[Exception] = None) -> float:
        """线性增长延迟"""
        delay = self.config.initial_delay * attempt
        return min(delay, self.config.max_delay)


class ExponentialBackoffStrategy(RetryStrategy):
    """指数退避策略"""

    def __init__(self, config: RetryConfig):
        super().__init__(config)
        self._base = 2.0  # 指数基数

    async def get_delay(self, attempt: int, error: Optional[Exception] = None) -> float:
        """指数增长延迟"""
        delay = self.config.initial_delay * (self._base ** (attempt - 1))

        # 添加抖动
        if self.config.jitter:
            delay *= random.uniform(0.5, 1.5)

        return min(delay, self.config.max_delay)


class FixedDelayStrategy(RetryStrategy):
    """固定延迟策略"""

    async def get_delay(self, attempt: int, error: Optional[Exception] = None) -> float:
        """固定延迟"""
        return self.config.initial_delay


class AdaptiveBackoffStrategy(RetryStrategy):
    """自适应退避策略"""

    def __init__(self, config: RetryConfig):
        super().__init__(config)
        self._success_count = 0
        self._error_history = []

    async def get_delay(self, attempt: int, error: Optional[Exception] = None) -> float:
        """自适应延迟"""
        # 记录错误
        self._error_history.append(time.time())

        # 计算错误频率
        recent_errors = sum(
            1 for t in self._error_history
            if time.time() - t < 60  # 1分钟内
        )

        # 基础延迟
        base_delay = self.config.initial_delay

        # 根据错误频率调整
        if recent_errors > 10:
            base_delay *= 3  # 错误频繁时增加延迟
        elif recent_errors > 5:
            base_delay *= 2

        # 指数增长
        delay = base_delay * (2 ** (attempt - 1))

        # 处理速率限制错误
        if isinstance(error, RateLimitError) and error.retry_after:
            delay = error.retry_after

        # 添加抖动
        if self.config.jitter:
            delay *= random.uniform(0.5, 1.5)

        return min(delay, self.config.max_delay)

    def record_success(self) -> None:
        """记录成功"""
        self._success_count += 1
        # 成功后减少错误历史
        self._error_history = self._error_history[-5:]


class RetryHandler:
    """重试处理器"""

    def __init__(self, config: Optional[RetryConfig] = None):
        self.config = config or RetryConfig()
        self.strategy = self._create_strategy()

    def _create_strategy(self) -> RetryStrategy:
        """创建重试策略"""
        if self.config.backoff_strategy == "linear":
            return LinearBackoffStrategy(self.config)
        elif self.config.backoff_strategy == "exponential":
            return ExponentialBackoffStrategy(self.config)
        elif self.config.backoff_strategy == "fixed":
            return FixedDelayStrategy(self.config)
        elif self.config.backoff_strategy == "adaptive":
            return AdaptiveBackoffStrategy(self.config)
        else:
            raise ValueError(f"Unknown backoff strategy: {self.config.backoff_strategy}")

    def should_retry(self, error: Exception) -> bool:
        """判断是否应该重试"""
        # 检查重试次数
        if self.strategy.attempts >= self.config.max_retries:
            return False

        # 检查错误类型
        if isinstance(error, (APIError, NetworkError, TimeoutError)):
            # 检查状态码
            if hasattr(error, 'status_code'):
                return error.status_code in self.config.retry_on_status
            return True

        # 速率限制错误总是重试
        if isinstance(error, RateLimitError):
            return True

        # 其他错误不重试
        return False

    async def execute_with_retry(
        self,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """执行函数并在失败时重试"""
        self.strategy.reset()
        last_error = None

        while True:
            try:
                # 执行函数
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)

                # 记录成功（用于自适应策略）
                if isinstance(self.strategy, AdaptiveBackoffStrategy):
                    self.strategy.record_success()

                return result

            except Exception as error:
                last_error = error
                self.strategy.increment()

                # 记录重试日志
                logger.warning(
                    f"Attempt {self.strategy.attempts} failed: {error}. "
                    f"Retrying..."
                )

                # 检查是否应该重试
                if not self.should_retry(error):
                    logger.error(f"Max retries reached. Last error: {error}")
                    break

                # 等待重试延迟
                delay = await self.strategy.get_delay(
                    self.strategy.attempts,
                    error
                )
                logger.debug(f"Waiting {delay:.2f}s before retry...")
                await asyncio.sleep(delay)

        # 所有重试都失败了，抛出最后一个错误
        raise last_error


class CircuitBreaker:
    """断路器模式实现"""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exception: Type[BaseException] = Exception,
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception

        self._failure_count = 0
        self._last_failure_time: Optional[float] = None
        self._state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """通过断路器调用函数"""
        if self._state == "OPEN":
            if self._should_attempt_reset():
                self._state = "HALF_OPEN"
                logger.info("Circuit breaker entering HALF_OPEN state")
            else:
                raise ZhipuAIError("Circuit breaker is OPEN")

        try:
            result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            self._on_success()
            return result

        except self.expected_exception as e:
            self._on_failure()
            raise e

    def _should_attempt_reset(self) -> bool:
        """检查是否应该尝试重置"""
        if self._last_failure_time is None:
            return True
        return time.time() - self._last_failure_time >= self.recovery_timeout

    def _on_success(self) -> None:
        """处理成功调用"""
        self._failure_count = 0
        self._state = "CLOSED"
        logger.debug("Circuit breaker is CLOSED")

    def _on_failure(self) -> None:
        """处理失败调用"""
        self._failure_count += 1
        self._last_failure_time = time.time()

        if self._failure_count >= self.failure_threshold:
            self._state = "OPEN"
            logger.warning(
                f"Circuit breaker is OPEN after {self._failure_count} failures"
            )

    @property
    def state(self) -> str:
        """获取当前状态"""
        return self._state

    def reset(self) -> None:
        """重置断路器"""
        self._failure_count = 0
        self._state = "CLOSED"
        self._last_failure_time = None
        logger.info("Circuit breaker has been reset")


def retry(
    max_retries: int = 3,
    backoff_strategy: str = "exponential",
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    jitter: bool = True,
    retry_on_status: Optional[Set[int]] = None
):
    """重试装饰器"""
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            config = RetryConfig(
                max_retries=max_retries,
                backoff_strategy=backoff_strategy,
                initial_delay=initial_delay,
                max_delay=max_delay,
                jitter=jitter,
                retry_on_status=retry_on_status or {429, 500, 502, 503, 504},
            )
            handler = RetryHandler(config)
            return await handler.execute_with_retry(func, *args, **kwargs)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # 同步函数的重试实现
            config = RetryConfig(
                max_retries=max_retries,
                backoff_strategy=backoff_strategy,
                initial_delay=initial_delay,
                max_delay=max_delay,
                jitter=jitter,
                retry_on_status=retry_on_status or {429, 500, 502, 503, 504},
            )
            strategy = ExponentialBackoffStrategy(config)
            strategy.reset()
            last_error = None

            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as error:
                    last_error = error
                    strategy.increment()

                    if strategy.attempts >= config.max_retries:
                        break

                    delay = strategy.initial_delay * (2 ** (strategy.attempts - 1))
                    if jitter:
                        delay *= random.uniform(0.5, 1.5)
                    delay = min(delay, config.max_delay)

                    time.sleep(delay)

            raise last_error

        # 根据函数类型返回合适的包装器
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


class Bulkhead:
    """舱壁隔离模式实现"""

    def __init__(self, max_concurrent: int = 10):
        self.max_concurrent = max_concurrent
        self._semaphore = asyncio.Semaphore(max_concurrent)

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """通过舱壁隔离调用函数"""
        async with self._semaphore:
            return await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)