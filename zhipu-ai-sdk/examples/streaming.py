"""
流式响应示例

演示如何处理流式响应。
"""

import asyncio
import os
from zhipuai import ZhipuAI
from zhipuai.models import ChatCompletionRequest, Message
from zhipuai.core.streaming import AccumulatorStreamHandler


async def basic_streaming_example():
    """基础流式响应示例"""
    api_key = os.getenv("ZHIPU_API_KEY")
    if not api_key:
        print("请设置环境变量 ZHIPU_API_KEY")
        return

    async with ZhipuAI(api_key=api_key) as client:
        # 创建流式请求
        request = ChatCompletionRequest(
            model="code-geex",
            messages=[
                Message(role="user", content="请详细解释Python的生成器（generator）概念")
            ],
            stream=True,
            max_tokens=1000,
            temperature=0.7,
        )

        print("AI回复: ", end="", flush=True)

        # 处理流式响应
        async for chunk in client.chat.completions.create(request):
            if chunk.choices[0].delta.content:
                print(chunk.choices[0].delta.content, end="", flush=True)

        print("\n\n流式响应完成！")


async def custom_stream_handler():
    """自定义流处理器示例"""
    api_key = os.getenv("ZHIPU_API_KEY")
    if not api_key:
        print("请设置环境变量 ZHIPU_API_KEY")
        return

    # 创建自定义处理器
    handler = AccumulatorStreamHandler()

    async with ZhipuAI(api_key=api_key) as client:
        request = ChatCompletionRequest(
            model="code-geex",
            messages=[
                Message(role="user", content="写一个Python快速排序算法")
            ],
            stream=True,
            max_tokens=800,
        )

        print("处理流式响应...\n")

        # 使用自定义处理器
        async for text in handler.process_stream(
            await client.chat.completions.create(request),
            parse_json=True
        ):
            print(text, end="", flush=True)

        print("\n\n完整回复:")
        print(handler.accumulated_text)


async def stream_with_callback():
    """带回调的流处理"""
    api_key = os.getenv("ZHIPU_API_KEY")
    if not api_key:
        print("请设置环境变量 ZHIPU_API_KEY")
        return

    from zhipuai.core.streaming import StreamHandler

    # 定义回调函数
    def on_chunk(chunk):
        print(f"\n[收到数据块] 大小: {len(str(chunk))} 字节")

    def on_complete():
        print("\n\n[流式响应完成]")

    # 创建带回调的处理器
    handler = StreamHandler(
        on_chunk=on_chunk,
        on_complete=on_complete,
    )

    async with ZhipuAI(api_key=api_key) as client:
        request = ChatCompletionRequest(
            model="code-geex",
            messages=[
                Message(role="user", content="什么是机器学习？")
            ],
            stream=True,
        )

        print("开始处理流式响应...")

        # 处理响应
        async for chunk in handler.process_stream(
            await client.chat.completions.create(request)
        ):
            if "choices" in chunk and chunk["choices"]:
                delta = chunk["choices"][0].get("delta", {})
                if "content" in delta:
                    print(delta["content"], end="", flush=True)


async def buffered_stream_example():
    """缓冲流处理示例"""
    from zhipuai.core.streaming import BufferedStreamHandler

    api_key = os.getenv("ZHIPU_API_KEY")
    if not api_key:
        print("请设置环境变量 ZHIPU_API_KEY")
        return

    # 创建缓冲处理器
    handler = BufferedStreamHandler(
        buffer_size=5,  # 每5个chunk处理一次
        flush_interval=0.5,  # 或每0.5秒处理一次
    )

    async with ZhipuAI(api_key=api_key) as client:
        request = ChatCompletionRequest(
            model="code-geex",
            messages=[
                Message(role="user", content="解释HTTP/2协议的主要特性")
            ],
            stream=True,
        )

        print("缓冲处理流式响应:\n")

        # 处理响应
        batch_count = 0
        async for batch in handler.process_stream(
            await client.chat.completions.create(request)
        ):
            batch_count += 1
            print(f"\n--- 批次 {batch_count} ({len(batch)} 个数据块) ---")

            # 提取并打印批次中的所有文本
            batch_text = ""
            for chunk in batch:
                if "choices" in chunk and chunk["choices"]:
                    delta = chunk["choices"][0].get("delta", {})
                    if "content" in delta:
                        batch_text += delta["content"]

            if batch_text:
                print(batch_text)


async def stream_collector_example():
    """流收集器示例"""
    from zhipuai.core.streaming import StreamCollector

    api_key = os.getenv("ZHIPU_API_KEY")
    if not api_key:
        print("请设置环境变量 ZHIPU_API_KEY")
        return

    # 创建收集器
    collector = StreamCollector()

    async with ZhipuAI(api_key=api_key) as client:
        request = ChatCompletionRequest(
            model="code-geex",
            messages=[
                Message(role="user", content="写一个Python装饰器的例子")
            ],
            stream=True,
        )

        print("收集流式响应...")

        # 收集所有响应
        chunks = await collector.collect(
            client.chat.completions.create(request)
        )

        # 打印统计信息
        print(f"\n统计信息:")
        print(f"- 总数据块数: {collector.total_chunks}")
        print(f"- 处理时间: {collector.duration:.2f} 秒")
        print(f"- 总文本长度: {len(collector.get_text())} 字符")

        # 打印使用量
        usage = collector.get_usage()
        if usage:
            print(f"- Token使用: {usage}")


async def main():
    """主函数"""
    print("=== 智谱AI流式响应示例 ===\n")

    print("\n1. 基础流式响应")
    await basic_streaming_example()

    print("\n2. 自定义流处理器")
    await custom_stream_handler()

    print("\n3. 带回调的流处理")
    await stream_with_callback()

    print("\n4. 缓冲流处理")
    await buffered_stream_example()

    print("\n5. 流收集器")
    await stream_collector_example()


if __name__ == "__main__":
    asyncio.run(main())