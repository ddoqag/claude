"""
基础聊天示例

演示如何使用智谱AI SDK进行基础对话。
"""

import asyncio
import os
from zhipuai import ZhipuAI
from zhipuai.models import ChatCompletionRequest, Message


async def basic_chat_example():
    """基础聊天示例"""
    # 从环境变量获取API密钥
    api_key = os.getenv("ZHIPU_API_KEY")
    if not api_key:
        print("请设置环境变量 ZHIPU_API_KEY")
        return

    # 创建客户端
    async with ZhipuAI(api_key=api_key) as client:
        # 创建聊天请求
        request = ChatCompletionRequest(
            model="code-geex",
            messages=[
                Message(role="user", content="你好，请用中文介绍一下你自己")
            ],
            max_tokens=500,
            temperature=0.7,
        )

        # 发送请求
        print("发送请求...")
        response = await client.chat.completions.create(request)

        # 打印响应
        print("\n响应内容:")
        print(response.choices[0].message.content)
        print("\n使用量:")
        print(response.usage)


async def multi_turn_chat():
    """多轮对话示例"""
    api_key = os.getenv("ZHIPU_API_KEY")
    if not api_key:
        print("请设置环境变量 ZHIPU_API_KEY")
        return

    async with ZhipuAI(api_key=api_key) as client:
        # 对话历史
        messages = [
            Message(role="system", content="你是一个Python编程助手"),
        ]

        # 多轮对话
        while True:
            # 获取用户输入
            user_input = input("\n用户: ")
            if user_input.lower() in ["quit", "exit", "退出"]:
                break

            # 添加用户消息
            messages.append(Message(role="user", content=user_input))

            # 创建请求
            request = ChatCompletionRequest(
                model="code-geex",
                messages=messages,
                max_tokens=1000,
                temperature=0.7,
            )

            # 发送请求
            response = await client.chat.completions.create(request)

            # 获取助手回复
            assistant_message = response.choices[0].message.content
            print(f"\n助手: {assistant_message}")

            # 添加助手消息到历史
            messages.append(
                Message(role="assistant", content=assistant_message)
            )


async def chat_with_system_prompt():
    """带系统提示的聊天"""
    api_key = os.getenv("ZHIPU_API_KEY")
    if not api_key:
        print("请设置环境变量 ZHIPU_API_KEY")
        return

    async with ZhipuAI(api_key=api_key) as client:
        # 创建带系统提示的请求
        request = ChatCompletionRequest(
            model="code-geex",
            messages=[
                Message(
                    role="system",
                    content="你是一个专业的代码审查员。请仔细检查代码并提供改进建议。"
                ),
                Message(
                    role="user",
                    content="""请审查以下Python代码：
```python
def calculate_average(numbers):
    total = 0
    for num in numbers:
        total += num
    return total / len(numbers)
```"""
                )
            ],
            max_tokens=800,
            temperature=0.3,
        )

        response = await client.chat.completions.create(request)
        print("代码审查结果:")
        print(response.choices[0].message.content)


async def main():
    """主函数"""
    print("=== 智谱AI基础聊天示例 ===\n")

    print("\n1. 基础聊天")
    await basic_chat_example()

    print("\n2. 代码审查示例")
    await chat_with_system_prompt()

    print("\n3. 多轮对话 (输入 'quit' 退出)")
    # await multi_turn_chat()  # 注释掉以避免交互式输入


if __name__ == "__main__":
    asyncio.run(main())