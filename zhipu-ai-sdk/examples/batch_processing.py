"""
批量处理示例

演示如何使用批量处理器高效处理大量请求。
"""

import asyncio
import os
import time
from zhipuai import ZhipuAI
from zhipuai.models import ChatCompletionRequest, Message
from zhipuai.utils import AsyncBatchProcessor, BatchConfig


async def basic_batch_processing():
    """基础批量处理示例"""
    api_key = os.getenv("ZHIPU_API_KEY")
    if not api_key:
        print("请设置环境变量 ZHIPU_API_KEY")
        return

    # 准备批量任务
    prompts = [
        "解释什么是Python装饰器",
        "如何实现一个单例模式",
        "什么是RESTful API",
        "解释SQL中的JOIN操作",
        "什么是Git rebase",
    ]

    async with ZhipuAI(api_key=api_key) as client:
        # 配置批量处理
        config = BatchConfig(
            batch_size=2,
            max_concurrency=3,
            delay_between_batches=0.5,
        )

        # 创建批量处理器
        processor = AsyncBatchProcessor(
            client=client,
            config=config,
        )

        print(f"批量处理 {len(prompts)} 个任务...\n")

        start_time = time.time()

        # 执行批量处理
        result = await processor.process_batch(prompts)

        duration = time.time() - start_time

        # 打印结果统计
        print(f"\n批量处理完成:")
        print(f"- 总任务数: {len(prompts)}")
        print(f"- 成功数: {len(result.successes)}")
        print(f"- 失败数: {len(result.failures)}")
        print(f"- 总耗时: {duration:.2f}秒")
        print(f"- 平均耗时: {duration/len(prompts):.2f}秒/任务")
        print(f"- 成功率: {result.success_rate*100:.1f}%")

        # 打印成功的结果
        print("\n处理结果:")
        for i, output in enumerate(result.outputs):
            if not isinstance(output, Exception):
                prompt_index = result.inputs.index(prompts[i])
                print(f"\n{i+1}. 问题: {prompts[prompt_index]}")
                print(f"   回答: {output.choices[0].message.content[:100]}...")


async def concurrent_batch_processing():
    """并发批量处理示例"""
    api_key = os.getenv("ZHIPU_API_KEY")
    if not api_key:
        print("请设置环境变量 ZHIPU_API_KEY")
        return

    # 更多任务
    prompts = [
        f"解释Python中的概念{i+1}"
        for i in range(10)
    ]

    async with ZhipuAI(api_key=api_key) as client:
        # 创建批量处理器
        processor = AsyncBatchProcessor(
            client=client,
            max_concurrency=5,
            batch_size=10,
        )

        print(f"并发处理 {len(prompts)} 个任务...\n")

        # 使用高并发处理
        start_time = time.time()
        results = await processor.process_concurrent(prompts)
        duration = time.time() - start_time

        print(f"\n并发处理完成:")
        print(f"- 总任务数: {len(prompts)}")
        print(f"- 总耗时: {duration:.2f}秒")
        print(f"- QPS: {len(prompts)/duration:.2f}")

        # 打印部分结果
        print("\n前3个结果:")
        for i, result in enumerate(results[:3]):
            print(f"\n{i+1}. {result.choices[0].message.content[:100]}...")


async def batch_with_custom_function():
    """使用自定义函数的批量处理"""
    api_key = os.getenv("ZHIPU_API_KEY")
    if not api_key:
        print("请设置环境变量 ZHIPU_API_KEY")
        return

    # 准备翻译任务
    translation_tasks = [
        {"text": "Hello, world!", "target": "中文"},
        {"text": "智谱AI很棒", "target": "English"},
        {"text": "Machine learning", "target": "中文"},
        {"text": "人工智能", "target": "English"},
    ]

    async with ZhipuAI(api_key=api_key) as client:
        # 自定义处理函数
        async def translate_text(task):
            prompt = f"请将以下文本翻译成{task['target']}：\n\n{task['text']}"

            request = ChatCompletionRequest(
                model="code-geex",
                messages=[Message(role="user", content=prompt)],
                max_tokens=200,
                temperature=0.3,
            )

            response = await client.chat.completions.create(request)

            return {
                "original": task["text"],
                "target_language": task["target"],
                "translation": response.choices[0].message.content,
            }

        # 创建处理器
        processor = AsyncBatchProcessor(
            client=client,
            process_func=translate_text,
            max_concurrency=2,
            batch_size=2,
        )

        print("批量翻译...\n")

        # 执行批量翻译
        result = await processor.process_batch(translation_tasks)

        # 打印翻译结果
        print("\n翻译结果:")
        for i, output in enumerate(result.outputs):
            if not isinstance(output, Exception):
                print(f"\n{i+1}. 原文: {output['original']}")
                print(f"   目标语言: {output['target_language']}")
                print(f"   译文: {output['translation']}")


async def stream_batch_processing():
    """流式批量处理示例"""
    api_key = os.getenv("ZHIPU_API_KEY")
    if not api_key:
        print("请设置环境变量 ZHIPU_API_KEY")
        return

    # 模拟数据流
    async def data_stream():
        """模拟数据流生成器"""
        items = [
            "生成一个斐波那契数列函数",
            "创建一个链表数据结构",
            "实现一个快速排序算法",
            "写一个二叉树遍历函数",
            "创建一个LRU缓存",
        ]

        for item in items:
            yield item
            await asyncio.sleep(0.5)  # 模拟数据到达间隔

    async with ZhipuAI(api_key=api_key) as client:
        # 创建批量处理器
        processor = AsyncBatchProcessor(
            client=client,
            max_concurrency=2,
            batch_size=2,
        )

        print("流式批量处理...\n")

        # 处理数据流
        async result in processor.process_stream(data_stream()):
            print(f"收到批次: {len(result.inputs)} 个任务")
            print(f"成功: {len(result.successes)}, 失败: {len(result.failures)}")


async def batch_with_retry_and_monitoring():
    """带重试和监控的批量处理"""
    api_key = os.getenv("ZHIPU_API_KEY")
    if not api_key:
        print("请设置环境变量 ZHIPU_API_KEY")
        return

    # 包含一些可能失败的任务
    prompts = [
        "正常的任务1",
        "",  # 空提示可能导致错误
        "正常的任务2",
        "x" * 10000,  # 超长提示
        "正常的任务3",
    ]

    async with ZhipuAI(api_key=api_key) as client:
        # 配置带重试的批量处理
        config = BatchConfig(
            batch_size=2,
            max_concurrency=3,
            retry_failed=True,
            max_retries=2,
            fail_fast=False,  # 不因单个失败而停止
        )

        # 创建处理器
        processor = AsyncBatchProcessor(
            client=client,
            config=config,
        )

        print("带重试和监控的批量处理...\n")

        # 执行批量处理
        result = await processor.process_batch(prompts)

        # 打印详细结果
        print(f"\n处理结果:")
        print(f"- 总任务: {len(result.inputs)}")
        print(f"- 成功: {len(result.successes)}")
        print(f"- 失败: {len(result.failures)}")

        # 显示失败的任务
        if result.failures:
            print("\n失败的任务:")
            for i, (index, error) in enumerate(result.failed_outputs):
                print(f"{i+1}. 任务 {index}: {error}")

        # 显示成功的任务
        print("\n成功的任务预览:")
        for i, output in enumerate(result.outputs):
            if not isinstance(output, Exception):
                content = output.choices[0].message.content
                print(f"{i+1}. {content[:50]}...")


async def performance_comparison():
    """性能对比示例"""
    api_key = os.getenv("ZHIPU_API_KEY")
    if not api_key:
        print("请设置环境变量 ZHIPU_API_KEY")
        return

    # 相同的任务列表
    prompts = [
        f"简单解释概念{i+1}"
        for i in range(6)
    ]

    async with ZhipuAI(api_key=api_key) as client:
        print("性能对比测试...\n")

        # 1. 顺序处理
        print("1. 顺序处理:")
        start_time = time.time()
        sequential_results = []
        for prompt in prompts:
            request = ChatCompletionRequest(
                model="code-geex",
                messages=[Message(role="user", content=prompt)],
                max_tokens=100,
            )
            response = await client.chat.completions.create(request)
            sequential_results.append(response)
        sequential_time = time.time() - start_time
        print(f"   耗时: {sequential_time:.2f}秒")

        # 2. 批量处理
        print("\n2. 批量处理:")
        processor = AsyncBatchProcessor(
            client=client,
            max_concurrency=3,
            batch_size=2,
        )
        start_time = time.time()
        batch_result = await processor.process_batch(prompts)
        batch_time = time.time() - start_time
        print(f"   耗时: {batch_time:.2f}秒")

        # 3. 并发处理
        print("\n3. 并发处理:")
        start_time = time.time()
        concurrent_results = await processor.process_concurrent(prompts)
        concurrent_time = time.time() - start_time
        print(f"   耗时: {concurrent_time:.2f}秒")

        # 计算性能提升
        print("\n性能对比:")
        print(f"- 批量处理比顺序处理快 {((sequential_time - batch_time) / sequential_time * 100):.1f}%")
        print(f"- 并发处理比顺序处理快 {((sequential_time - concurrent_time) / sequential_time * 100):.1f}%")


async def main():
    """主函数"""
    print("=== 智谱AI批量处理示例 ===\n")

    print("\n1. 基础批量处理")
    await basic_batch_processing()

    print("\n2. 并发批量处理")
    await concurrent_batch_processing()

    print("\n3. 自定义函数批量处理")
    await batch_with_custom_function()

    print("\n4. 流式批量处理")
    await stream_batch_processing()

    print("\n5. 带重试和监控的批量处理")
    await batch_with_retry_and_monitoring()

    print("\n6. 性能对比")
    await performance_comparison()


if __name__ == "__main__":
    asyncio.run(main())