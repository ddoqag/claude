"""
代码生成示例

演示如何使用智谱AI SDK进行代码生成、分析和调试。
"""

import asyncio
import os
from zhipuai import ZhipuAI
from zhipuai.models import (
    CodeGenerationRequest,
    CodeAnalysisRequest,
    DebugRequest,
)
from zhipuai.utils import AsyncBatchProcessor


async def code_generation_example():
    """代码生成示例"""
    api_key = os.getenv("ZHIPU_API_KEY")
    if not api_key:
        print("请设置环境变量 ZHIPU_API_KEY")
        return

    async with ZhipuAI(api_key=api_key) as client:
        # 创建代码生成请求
        request = CodeGenerationRequest(
            prompt="创建一个Python类来实现一个简单的计算器，支持加减乘除运算",
            language="python",
            style="oop",
            max_tokens=1500,
            temperature=0.3,
        )

        print("生成代码...\n")
        response = await client.code.generate(request)

        print("生成的代码:")
        print("-" * 50)
        print(response.code)
        print("-" * 50)

        if response.explanation:
            print("\n代码说明:")
            print(response.explanation)

        if response.dependencies:
            print("\n依赖项:")
            for dep in response.dependencies:
                print(f"- {dep}")


async def code_analysis_example():
    """代码分析示例"""
    api_key = os.getenv("ZHIPU_API_KEY")
    if not api_key:
        print("请设置环境变量 ZHIPU_API_KEY")
        return

    # 示例代码
    sample_code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

def find_factorial(n):
    result = 1
    for i in range(1, n + 1):
        result *= i
    return result

class DataProcessor:
    def __init__(self):
        self.data = []

    def add_data(self, item):
        self.data.append(item)

    def get_average(self):
        return sum(self.data) / len(self.data)
"""

    async with ZhipuAI(api_key=api_key) as client:
        # 创建代码分析请求
        request = CodeAnalysisRequest(
            code=sample_code,
            language="python",
            analysis_type=["performance", "security", "complexity"],
        )

        print("分析代码...\n")
        response = await client.code.analyze(request)

        # 打印分析结果
        print("分析结果:")
        print(f"- 类型: {response.result.type}")
        print(f"- 成功: {response.result.success}")

        if response.result.score is not None:
            print(f"- 评分: {response.result.score}/100")

        if response.result.issues:
            print("\n发现的问题:")
            for i, issue in enumerate(response.result.issues, 1):
                print(f"\n{i}. {issue.type} (严重程度: {issue.severity})")
                print(f"   位置: 第{issue.line}行")
                print(f"   描述: {issue.message}")
                if issue.suggestion:
                    print(f"   建议: {issue.suggestion}")

        if response.result.metrics:
            metrics = response.result.metrics
            print("\n代码度量:")
            print(f"- 复杂度: {metrics.complexity}")
            print(f"- 代码行数: {metrics.lines_of_code}")
            print(f"- 可维护性指数: {metrics.maintainability_index}")

        if response.result.recommendations:
            print("\n改进建议:")
            for rec in response.result.recommendations:
                print(f"- {rec}")


async def debug_example():
    """代码调试示例"""
    api_key = os.getenv("ZHIPU_API_KEY")
    if not api_key:
        print("请设置环境变量 ZHIPU_API_KEY")
        return

    # 有问题的代码
    buggy_code = """
def divide_numbers(a, b):
    return a / b

def process_list(numbers):
    result = []
    for i in range(len(numbers) + 1):  # 故意的索引错误
        result.append(numbers[i] * 2)
    return result
"""

    async with ZhipuAI(api_key=api_key) as client:
        # 创建调试请求
        request = DebugRequest(
            code=buggy_code,
            error_message="division by zero" or "list index out of range",
            language="python",
            debug_level="detailed",
        )

        print("调试代码...\n")
        response = await client.code.debug(request)

        # 打印调试结果
        if response.error_type:
            print(f"错误类型: {response.error_type}")

        if response.root_cause:
            print(f"\n根本原因: {response.root_cause}")

        if response.error_location:
            loc = response.error_location
            print(f"\n错误位置:")
            if loc.file:
                print(f"- 文件: {loc.file}")
            if loc.line:
                print(f"- 行号: {loc.line}")
            if loc.function:
                print(f"- 函数: {loc.function}")

        if response.suggestions:
            print("\n修复建议:")
            for i, suggestion in enumerate(response.suggestions, 1):
                print(f"\n{i}. {suggestion.type}")
                print(f"   描述: {suggestion.description}")
                if suggestion.code_change:
                    print(f"   修改建议: {suggestion.code_change}")
                if suggestion.explanation:
                    print(f"   说明: {suggestion.explanation}")

        if response.fixed_code:
            print("\n修复后的代码:")
            print("-" * 50)
            print(response.fixed_code.content)
            print("-" * 50)

            if response.fixed_code.changes:
                print("\n修改说明:")
                for change in response.fixed_code.changes:
                    print(f"- {change}")


async def batch_code_generation():
    """批量代码生成示例"""
    api_key = os.getenv("ZHIPU_API_KEY")
    if not api_key:
        print("请设置环境变量 ZHIPU_API_KEY")
        return

    # 准备多个生成任务
    tasks = [
        "实现一个冒泡排序算法",
        "创建一个二叉树类",
        "写一个装饰器来计算函数执行时间",
        "实现一个LRU缓存",
        "创建一个简单的Web服务器",
    ]

    async with ZhipuAI(api_key=api_key) as client:
        # 创建批量处理器
        processor = AsyncBatchProcessor(
            client=client,
            max_concurrency=3,
            batch_size=2,
        )

        print(f"批量生成 {len(tasks)} 个代码示例...\n")

        # 定义处理函数
        async def generate_code(prompt: str):
            request = CodeGenerationRequest(
                prompt=prompt,
                language="python",
                max_tokens=800,
                temperature=0.3,
            )
            response = await client.code.generate(request)
            return {
                "prompt": prompt,
                "code": response.code,
                "explanation": response.explanation,
            }

        # 批量处理
        result = await processor.process_batch(tasks, process_func=generate_code)

        # 打印结果
        print(f"批量处理完成:")
        print(f"- 总数: {len(result.inputs)}")
        print(f"- 成功: {len(result.successes)}")
        print(f"- 失败: {len(result.failures)}")
        print(f"- 耗时: {result.duration:.2f}秒")
        print(f"- 成功率: {result.success_rate * 100:.1f}%")

        # 显示成功的结果
        print("\n生成的代码:")
        for i, output in enumerate(result.outputs):
            if not isinstance(output, Exception) and i in result.successes:
                print(f"\n{i+1}. {output['prompt']}")
                print("-" * 40)
                print(output['code'][:200] + "..." if len(output['code']) > 200 else output['code'])


async def advanced_code_features():
    """高级代码功能示例"""
    api_key = os.getenv("ZHIPU_API_KEY")
    if not api_key:
        print("请设置环境变量 ZHIPU_API_KEY")
        return

    async with ZhipuAI(api_key=api_key) as client:
        # 生成带特定框架的代码
        request = CodeGenerationRequest(
            prompt="创建一个REST API端点来获取用户列表",
            language="python",
            framework="fastapi",
            libraries=["fastapi", "pydantic", "sqlalchemy"],
            constraints=[
                "使用异步函数",
                "支持分页",
                "包含错误处理",
                "添加类型注解"
            ],
            max_tokens=1000,
            temperature=0.2,
        )

        print("生成FastAPI代码...\n")
        response = await client.code.generate(request)

        print("生成的FastAPI代码:")
        print("-" * 50)
        print(response.code)
        print("-" * 50)

        # 如果生成了多个文件
        if response.files:
            print(f"\n生成了 {len(response.files)} 个文件:")
            for file in response.files:
                print(f"\n{file.filename}:")
                print("-" * 30)
                print(file.content[:300] + "..." if len(file.content) > 300 else file.content)


async def main():
    """主函数"""
    print("=== 智谱AI代码功能示例 ===\n")

    print("\n1. 代码生成")
    await code_generation_example()

    print("\n2. 代码分析")
    await code_analysis_example()

    print("\n3. 代码调试")
    await debug_example()

    print("\n4. 批量代码生成")
    await batch_code_generation()

    print("\n5. 高级代码功能")
    await advanced_code_features()


if __name__ == "__main__":
    asyncio.run(main())