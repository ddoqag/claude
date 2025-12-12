"""
批量处理器

提供高效的批量请求处理功能。
"""

import asyncio
import time
from typing import Any, Callable, Generic, List, Optional, TypeVar, Union
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed

T = TypeVar('T')
R = TypeVar('R')


@dataclass
class BatchConfig:
    """批量处理配置"""
    batch_size: int = 10
    max_concurrency: int = 5
    timeout: float = 300.0
    delay_between_batches: float = 0.1
    retry_failed: bool = True
    max_retries: int = 3
    fail_fast: bool = False


class BatchResult(Generic[T, R]):
    """批量处理结果"""

    def __init__(
        self,
        inputs: List[T],
        outputs: List[Union[R, Exception]],
        successes: List[int],
        failures: List[int],
        duration: float,
    ):
        self.inputs = inputs
        self.outputs = outputs
        self.successes = successes
        self.failures = failures
        self.duration = duration

    @property
    def success_rate(self) -> float:
        """成功率"""
        if not self.inputs:
            return 0.0
        return len(self.successes) / len(self.inputs)

    @property
    def failed_outputs(self) -> List[tuple[int, Exception]]:
        """获取失败的输出"""
        return [(i, output) for i, output in enumerate(self.outputs)
                if isinstance(output, Exception) and i in self.failures]

    def get_successful_outputs(self) -> List[R]:
        """获取成功的输出"""
        return [output for output in self.outputs if not isinstance(output, Exception)]


class AsyncBatchProcessor(Generic[T, R]):
    """异步批量处理器"""

    def __init__(
        self,
        client: Any,
        config: Optional[BatchConfig] = None,
        process_func: Optional[Callable] = None,
    ):
        self.client = client
        self.config = config or BatchConfig()
        self.process_func = process_func or self._default_process

    async def _default_process(self, item: T) -> R:
        """默认处理函数"""
        # 如果客户端有process方法，使用它
        if hasattr(self.client, 'process'):
            return await self.client.process(item)
        # 否则直接调用客户端
        if callable(self.client):
            return await self.client(item)
        raise ValueError("No process function available")

    async def process_batch(
        self,
        items: List[T],
        **kwargs
    ) -> BatchResult[T, R]:
        """处理批量项目"""
        start_time = time.time()
        outputs: List[Union[R, Exception]] = []
        successes: List[int] = []
        failures: List[int] = []

        # 分批处理
        batches = [
            items[i:i + self.config.batch_size]
            for i in range(0, len(items), self.config.batch_size)
        ]

        # 创建信号量控制并发
        semaphore = asyncio.Semaphore(self.config.max_concurrency)

        async def process_batch_with_semaphore(
            batch: List[T],
            batch_index: int
        ) -> List[Union[R, Exception]]:
            async with semaphore:
                return await self._process_single_batch(batch, **kwargs)

        # 并发处理所有批次
        batch_tasks = [
            process_batch_with_semaphore(batch, i)
            for i, batch in enumerate(batches)
        ]

        # 收集结果
        batch_results = await asyncio.gather(*batch_tasks)

        # 合并结果
        for i, batch_output in enumerate(batch_results):
            for output in batch_output:
                outputs.append(output)
                index = len(outputs) - 1

                if isinstance(output, Exception):
                    failures.append(index)
                else:
                    successes.append(index)

            # 批次间延迟
            if i < len(batch_results) - 1 and self.config.delay_between_batches > 0:
                await asyncio.sleep(self.config.delay_between_batches)

        duration = time.time() - start_time
        return BatchResult(
            inputs=items,
            outputs=outputs,
            successes=successes,
            failures=failures,
            duration=duration,
        )

    async def _process_single_batch(
        self,
        batch: List[T],
        **kwargs
    ) -> List[Union[R, Exception]]:
        """处理单个批次"""
        # 并发处理批次中的项目
        tasks = [self._process_item_with_retry(item, **kwargs) for item in batch]
        return await asyncio.gather(*tasks, return_exceptions=True)

    async def _process_item_with_retry(
        self,
        item: T,
        **kwargs
    ) -> Union[R, Exception]:
        """处理单个项目（带重试）"""
        last_error = None

        for attempt in range(self.config.max_retries + 1):
            try:
                return await self.process_func(item, **kwargs)
            except Exception as e:
                last_error = e
                if attempt < self.config.max_retries:
                    # 指数退避
                    delay = 2 ** attempt * 0.1
                    await asyncio.sleep(delay)
                else:
                    break

        return last_error

    async def process_concurrent(
        self,
        items: List[T],
        max_concurrency: Optional[int] = None,
        **kwargs
    ) -> List[R]:
        """并发处理所有项目（不分批）"""
        max_concurrency = max_concurrency or self.config.max_concurrency
        semaphore = asyncio.Semaphore(max_concurrency)

        async def process_with_semaphore(item: T) -> R:
            async with semaphore:
                return await self.process_func(item, **kwargs)

        tasks = [process_with_semaphore(item) for item in items]
        return await asyncio.gather(*tasks)

    async def process_stream(
        self,
        items_stream,
        **kwargs
    ) -> AsyncBatchResult[T, R]:
        """流式处理项目"""
        start_time = time.time()
        outputs: List[Union[R, Exception]] = []
        successes: List[int] = []
        failures: List[int] = []
        processed_items: List[T] = []

        # 处理流
        async for item in items_stream:
            result = await self._process_item_with_retry(item, **kwargs)
            index = len(outputs)
            outputs.append(result)
            processed_items.append(item)

            if isinstance(result, Exception):
                failures.append(index)
            else:
                successes.append(index)

        duration = time.time() - start_time
        return BatchResult(
            inputs=processed_items,
            outputs=outputs,
            successes=successes,
            failures=failures,
            duration=duration,
        )


class SyncBatchProcessor(Generic[T, R]):
    """同步批量处理器"""

    def __init__(
        self,
        client: Any,
        config: Optional[BatchConfig] = None,
        process_func: Optional[Callable] = None,
    ):
        self.client = client
        self.config = config or BatchConfig()
        self.process_func = process_func or self._default_process

    def _default_process(self, item: T) -> R:
        """默认处理函数"""
        if hasattr(self.client, 'process'):
            return self.client.process(item)
        if callable(self.client):
            return self.client(item)
        raise ValueError("No process function available")

    def process_batch(
        self,
        items: List[T],
        **kwargs
    ) -> BatchResult[T, R]:
        """处理批量项目"""
        start_time = time.time()
        outputs: List[Union[R, Exception]] = []
        successes: List[int] = []
        failures: List[int] = []

        # 使用线程池并发处理
        with ThreadPoolExecutor(max_workers=self.config.max_concurrency) as executor:
            # 提交所有任务
            future_to_index = {
                executor.submit(self._process_item_with_retry, item, **kwargs): i
                for i, item in enumerate(items)
            }

            # 收集结果
            for future in as_completed(future_to_index):
                index = future_to_index[future]
                try:
                    result = future.result()
                    outputs.append(result)
                    if isinstance(result, Exception):
                        failures.append(index)
                    else:
                        successes.append(index)
                except Exception as e:
                    outputs.append(e)
                    failures.append(index)

        duration = time.time() - start_time
        return BatchResult(
            inputs=items,
            outputs=outputs,
            successes=successes,
            failures=failures,
            duration=duration,
        )

    def _process_item_with_retry(
        self,
        item: T,
        **kwargs
    ) -> Union[R, Exception]:
        """处理单个项目（带重试）"""
        last_error = None

        for attempt in range(self.config.max_retries + 1):
            try:
                return self.process_func(item, **kwargs)
            except Exception as e:
                last_error = e
                if attempt < self.config.max_retries:
                    time.sleep(2 ** attempt * 0.1)

        return last_error


class AsyncBatchResult(Generic[T, R]):
    """异步批量结果包装器"""

    def __init__(self, result: BatchResult[T, R]):
        self._result = result
        self._index = 0

    def __aiter__(self):
        """异步迭代器"""
        return self

    async def __anext__(self):
        """异步迭代下一个结果"""
        if self._index >= len(self._result.outputs):
            raise StopAsyncIteration

        output = self._result.outputs[self._index]
        self._index += 1
        return output

    @property
    def result(self) -> BatchResult[T, R]:
        """获取原始结果"""
        return self._result

    async def collect_all(self) -> List[R]:
        """收集所有成功的结果"""
        return [
            output for output in self._result.outputs
            if not isinstance(output, Exception)
        ]

    async def collect_successful(self) -> List[tuple[T, R]]:
        """收集成功的输入输出对"""
        successful_pairs = []
        for i, output in enumerate(self._result.outputs):
            if not isinstance(output, Exception) and i in self._result.successes:
                successful_pairs.append((self._result.inputs[i], output))
        return successful_pairs

    async def collect_failed(self) -> List[tuple[T, Exception]]:
        """收集失败的输入异常对"""
        failed_pairs = []
        for i, output in enumerate(self._result.outputs):
            if isinstance(output, Exception) and i in self._result.failures:
                failed_pairs.append((self._result.inputs[i], output))
        return failed_pairs