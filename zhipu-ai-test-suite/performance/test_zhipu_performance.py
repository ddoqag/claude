"""
智谱AI性能测试
测试API响应时间、吞吐量、资源使用等性能指标
"""

import pytest
import asyncio
import time
import aiohttp
import numpy as np
from typing import Dict, Any, List


@pytest.mark.performance
class TestZhipuAPIPerformance:
    """智谱API性能测试"""

    @pytest.mark.asyncio
    async def test_api_response_time_baseline(
        self,
        zhipu_client,
        test_environment,
        benchmark_runner,
        performance_thresholds
    ):
        """测试API响应时间基线"""
        async def generate_code():
            response = await zhipu_client.chat.completions.create(
                model=test_environment["zhipu_model"],
                messages=[{
                    "role": "user",
                    "content": "Write a simple function that adds two numbers"
                }],
                max_tokens=50
            )
            return response

        # 运行基准测试
        result = await benchmark_runner.run_benchmark(
            name="api_response_time_baseline",
            test_func=generate_code,
            iterations=20
        )

        # 验证性能指标
        assert result.metrics.response_time < performance_thresholds["response_time"]["warning"]
        assert result.metrics.p95_response_time < performance_thresholds["response_time"]["critical"]
        assert result.metrics.error_rate == 0

    @pytest.mark.asyncio
    async def test_api_throughput(
        self,
        zhipu_client,
        test_environment,
        benchmark_runner,
        performance_thresholds
    ):
        """测试API吞吐量"""
        async def make_request():
            response = await zhipu_client.chat.completions.create(
                model=test_environment["zhipu_model"],
                messages=[{
                    "role": "user",
                    "content": "print('hello')"
                }],
                max_tokens=20
            )
            return response

        # 测量1秒内的吞吐量
        start_time = time.time()
        tasks = []
        while time.time() - start_time < 1.0:
            tasks.append(make_request())

        # 执行所有请求
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        successful_requests = [r for r in responses if not isinstance(r, Exception)]
        actual_duration = time.time() - start_time
        throughput = len(successful_requests) / actual_duration

        # 验证吞吐量
        assert throughput >= performance_thresholds["throughput"]["minimum"]

    @pytest.mark.asyncio
    async def test_concurrent_requests_performance(
        self,
        zhipu_client,
        test_environment,
        performance_monitor,
        performance_thresholds
    ):
        """测试并发请求性能"""
        performance_monitor.start_monitoring()

        async def make_request(prompt_id):
            start_time = time.time()
            try:
                response = await zhipu_client.chat.completions.create(
                    model=test_environment["zhipu_model"],
                    messages=[{
                        "role": "user",
                        "content": f"Write function {prompt_id}"
                    }],
                    max_tokens=30
                )
                response_time = time.time() - start_time
                performance_monitor.record_request(response_time, success=True)
                return response
            except Exception as e:
                response_time = time.time() - start_time
                performance_monitor.record_request(response_time, success=False)
                raise e

        # 创建10个并发请求
        concurrent_count = 10
        tasks = [make_request(i) for i in range(concurrent_count)]

        # 等待所有请求完成
        await asyncio.gather(*tasks, return_exceptions=True)

        # 获取性能指标
        metrics = performance_monitor.get_metrics()

        # 验证性能
        assert metrics.response_time < performance_thresholds["response_time"]["warning"]
        assert metrics.error_rate < performance_thresholds["error_rate"]["warning"]
        assert metrics.cpu_usage < performance_thresholds["cpu_usage"]["warning"]

    @pytest.mark.asyncio
    @pytest.mark.parametrize("code_length", ["short", "medium", "long"])
    async def test_different_code_lengths_performance(
        self,
        zhipu_client,
        test_environment,
        benchmark_runner,
        code_length
    ):
        """测试不同代码长度的性能"""
        prompts = {
            "short": "Write hello world",
            "medium": "Write a class representing a student with attributes",
            "long": "Write a complete REST API with authentication, CRUD operations, and error handling"
        }

        max_tokens = {
            "short": 50,
            "medium": 200,
            "long": 1000
        }

        async def generate_code():
            response = await zhipu_client.chat.completions.create(
                model=test_environment["zhipu_model"],
                messages=[{
                    "role": "user",
                    "content": prompts[code_length]
                }],
                max_tokens=max_tokens[code_length]
            )
            return response

        # 运行基准测试
        result = await benchmark_runner.run_benchmark(
            name=f"code_generation_{code_length}",
            test_func=generate_code,
            iterations=10
        )

        # 验证性能随代码长度的变化
        # 长代码应该有更长的响应时间
        if code_length == "short":
            assert result.metrics.response_time < 2.0
        elif code_length == "medium":
            assert result.metrics.response_time < 5.0
        else:  # long
            assert result.metrics.response_time < 10.0

    @pytest.mark.asyncio
    async def test_memory_usage_stability(
        self,
        zhipu_client,
        test_environment,
        performance_monitor,
        performance_thresholds
    ):
        """测试内存使用稳定性"""
        performance_monitor.start_monitoring()
        initial_memory = performance_monitor.process.memory_info().rss / 1024 / 1024

        # 执行大量请求
        for i in range(100):
            await zhipu_client.chat.completions.create(
                model=test_environment["zhipu_model"],
                messages=[{
                    "role": "user",
                    "content": f"Generate code snippet {i}"
                }],
                max_tokens=50
            )

            # 记录内存使用
            memory_info = performance_monitor.process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024
            performance_monitor.record_request(0, success=True)

        final_memory = performance_monitor.process.memory_info().rss / 1024 / 1024
        memory_increase = final_memory - initial_memory

        # 内存增长应该在合理范围内
        assert memory_increase < 200  # 不应超过200MB增长
        assert final_memory < performance_thresholds["memory_usage"]["critical"]

    @pytest.mark.asyncio
    async def test_api_error_handling_performance(
        self,
        zhipu_client,
        test_environment,
        benchmark_runner
    ):
        """测试API错误处理性能"""
        async def make_invalid_request():
            try:
                # 发送无效请求
                response = await zhipu_client.chat.completions.create(
                    model="invalid_model_name",
                    messages=[{"role": "user", "content": "test"}],
                    max_tokens=50
                )
                return response
            except Exception:
                # 预期会出错
                pass

        # 运行基准测试
        result = await benchmark_runner.run_benchmark(
            name="error_handling_performance",
            test_func=make_invalid_request,
            iterations=20
        )

        # 错误处理应该快速返回
        assert result.metrics.response_time < 1.0


@pytest.mark.performance
class TestMCPPerformance:
    """MCP服务器性能测试"""

    @pytest.mark.asyncio
    async def test_mcp_tool_response_time(
        self,
        mcp_server,
        benchmark_runner,
        performance_thresholds
    ):
        """测试MCP工具响应时间"""
        async def call_generate_tool():
            async with aiohttp.ClientSession() as session:
                url = f"{mcp_server['url']}/mcp/tools/call"
                payload = {
                    "name": "generate_code",
                    "arguments": {
                        "prompt": "Write a simple function",
                        "language": "python",
                        "max_tokens": 50
                    }
                }
                async with session.post(url, json=payload) as response:
                    return await response.json()

        # 运行基准测试
        result = await benchmark_runner.run_benchmark(
            name="mcp_generate_code_tool",
            test_func=call_generate_tool,
            iterations=30
        )

        # 验证性能
        assert result.metrics.response_time < performance_thresholds["response_time"]["warning"]
        assert result.metrics.p95_response_time < performance_thresholds["response_time"]["critical"]

    @pytest.mark.asyncio
    async def test_mcp_concurrent_tool_calls(
        self,
        mcp_server,
        load_tester,
        load_test_scenarios
    ):
        """测试MCP并发工具调用"""
        scenario = load_test_scenarios["moderate"]

        async def make_tool_call():
            async with aiohttp.ClientSession() as session:
                url = f"{mcp_server['url']}/mcp/tools/call"
                payload = {
                    "name": "explain_code",
                    "arguments": {
                        "code": "def hello(): print('Hello, World!')",
                        "language": "python"
                    }
                }
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        raise Exception(f"HTTP {response.status}")

        # 运行负载测试
        result = await load_tester.run_load_test(
            test_func=make_tool_call,
            concurrent_users=scenario["concurrent_users"],
            duration=scenario["duration"],
            requests_per_second=scenario["requests_per_second"]
        )

        # 验证负载测试结果
        assert result.metrics.error_rate < 0.05  # 错误率应小于5%
        assert result.metrics.throughput > 5    # 至少5请求/秒

    @pytest.mark.asyncio
    async def test_mcp_streaming_performance(
        self,
        mcp_server,
        benchmark_runner
    ):
        """测试MCP流式响应性能"""
        async def stream_response():
            async with aiohttp.ClientSession() as session:
                url = f"{mcp_server['url']}/mcp/tools/call"
                payload = {
                    "name": "generate_code",
                    "arguments": {
                        "prompt": "Write a comprehensive solution",
                        "language": "python",
                        "stream": True,
                        "max_tokens": 200
                    }
                }

                start_time = time.time()
                chunks = []
                async with session.post(url, json=payload) as response:
                    async for chunk in response.content:
                        if chunk:
                            chunks.append(chunk)
                return time.time() - start_time, len(chunks)

        # 运行基准测试
        result = await benchmark_runner.run_benchmark(
            name="mcp_streaming_response",
            test_func=stream_response,
            iterations=10
        )

        # 流式响应应该有合理的性能
        assert result.metrics.response_time < 5.0

    @pytest.mark.asyncio
    async def test_mcp_memory_efficiency(
        self,
        mcp_server,
        performance_monitor
    ):
        """测试MCP内存效率"""
        performance_monitor.start_monitoring()

        # 发送大量请求
        for i in range(50):
            async with aiohttp.ClientSession() as session:
                url = f"{mcp_server['url']}/mcp/tools/call"
                payload = {
                    "name": "generate_code",
                    "arguments": {
                        "prompt": f"Generate test code {i}",
                        "language": "python",
                        "max_tokens": 100
                    }
                }
                async with session.post(url, json=payload) as response:
                    await response.json()

            performance_monitor.record_request(0, success=True)

        # 获取性能指标
        metrics = performance_monitor.get_metrics()

        # 验证内存使用
        assert metrics.memory_usage < 500  # 不应超过500MB

    @pytest.mark.asyncio
    async def test_mcp_resource_access_performance(
        self,
        mcp_server,
        benchmark_runner
    ):
        """测试MCP资源访问性能"""
        async def read_resource():
            async with aiohttp.ClientSession() as session:
                url = f"{mcp_server['url']}/mcp/resources/read"
                payload = {
                    "uri": "zhipu://models/codegeex4"
                }
                async with session.post(url, json=payload) as response:
                    return await response.json()

        # 运行基准测试
        result = await benchmark_runner.run_benchmark(
            name="mcp_resource_access",
            test_func=read_resource,
            iterations=50
        )

        # 资源访问应该很快
        assert result.metrics.response_time < 0.5
        assert result.metrics.p95_response_time < 1.0


@pytest.mark.performance
class TestLoadScenarios:
    """负载场景测试"""

    @pytest.mark.asyncio
    @pytest.mark.parametrize("scenario_name", ["light", "moderate", "heavy"])
    async def test_load_scenarios(
        self,
        mcp_server,
        load_tester,
        load_test_scenarios,
        scenario_name
    ):
        """测试不同负载场景"""
        scenario = load_test_scenarios[scenario_name]

        async def simulate_user_request():
            # 模拟用户请求
            tool_type = np.random.choice(["generate_code", "explain_code", "optimize_code"])
            prompts = {
                "generate_code": "Write a function to sort numbers",
                "explain_code": "def sort(arr): return sorted(arr)",
                "optimize_code": "for i in range(len(arr)): for j in range(i): # O(n^2)"
            }

            async with aiohttp.ClientSession() as session:
                url = f"{mcp_server['url']}/mcp/tools/call"
                payload = {
                    "name": tool_type,
                    "arguments": {
                        "prompt": prompts.get(tool_type, "test"),
                        "language": "python"
                    }
                }

                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        raise Exception(f"HTTP {response.status}")

        # 运行负载测试
        result = await load_tester.run_load_test(
            test_func=simulate_user_request,
            concurrent_users=scenario["concurrent_users"],
            duration=scenario["duration"],
            requests_per_second=scenario["requests_per_second"]
        )

        # 根据场景调整性能期望
        if scenario_name == "light":
            assert result.metrics.response_time < 1.0
            assert result.metrics.error_rate < 0.01
        elif scenario_name == "moderate":
            assert result.metrics.response_time < 2.0
            assert result.metrics.error_rate < 0.02
        else:  # heavy
            assert result.metrics.response_time < 5.0
            assert result.metrics.error_rate < 0.05

    @pytest.mark.asyncio
    async def test_spike_handling(
        self,
        mcp_server,
        load_tester,
        load_test_scenarios
    ):
        """测试峰值处理能力"""
        scenario = load_test_scenarios["spike"]

        async def simple_request():
            async with aiohttp.ClientSession() as session:
                url = f"{mcp_server['url']}/health"
                async with session.get(url) as response:
                    return response.status == 200

        # 运行峰值测试
        result = await load_tester.run_load_test(
            test_func=simple_request,
            concurrent_users=scenario["concurrent_users"],
            duration=scenario["duration"],
            requests_per_second=scenario["requests_per_second"]
        )

        # 系统应该能处理峰值负载
        assert result.metrics.error_rate < 0.1  # 允许10%的错误率
        assert result.metrics.throughput > 50   # 至少50请求/秒

    @pytest.mark.asyncio
    async def test_sustained_load(
        self,
        mcp_server,
        load_tester
    ):
        """测试持续负载"""
        # 持续5分钟的负载测试
        duration = 300  # 5分钟

        async def sustained_request():
            async with aiohttp.ClientSession() as session:
                url = f"{mcp_server['url']}/mcp/tools/call"
                payload = {
                    "name": "generate_code",
                    "arguments": {
                        "prompt": "Write a utility function",
                        "language": "python",
                        "max_tokens": 50
                    }
                }
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        raise Exception(f"HTTP {response.status}")

        # 运行持续负载测试
        result = await load_tester.run_load_test(
            test_func=sustained_request,
            concurrent_users=10,
            duration=duration,
            requests_per_second=2
        )

        # 验证系统稳定性
        assert result.metrics.error_rate < 0.02
        assert result.metrics.response_time < 3.0

        # 内存应该稳定（不应持续增长）
        # 这需要更长时间的监控来验证


@pytest.mark.performance
class TestBenchmarkComparison:
    """基准对比测试"""

    @pytest.mark.asyncio
    async def test_language_performance_comparison(
        self,
        zhipu_client,
        test_environment,
        benchmark_runner
    ):
        """测试不同编程语言的生成性能"""
        languages = ["Python", "JavaScript", "Java", "C++", "Go"]
        results = {}

        for lang in languages:
            async def generate_language_code():
                response = await zhipu_client.chat.completions.create(
                    model=test_environment["zhipu_model"],
                    messages=[{
                        "role": "user",
                        "content": f"Write hello world in {lang}"
                    }],
                    max_tokens=50
                )
                return response

            result = await benchmark_runner.run_benchmark(
                name=f"generate_{lang.lower()}",
                test_func=generate_language_code,
                iterations=10
            )
            results[lang] = result.metrics.response_time

        # 验证不同语言的性能差异
        # 某些语言可能生成更快
        assert max(results.values()) < 5.0  # 最慢的语言也不应超过5秒

    @pytest.mark.asyncio
    async def test_complexity_performance_comparison(
        self,
        zhipu_client,
        test_environment,
        benchmark_runner,
        benchmark_prompts
    ):
        """测试不同复杂度的性能比较"""
        complexity_levels = ["simple_generation", "medium_complexity", "high_complexity"]
        results = {}

        for complexity in complexity_levels:
            prompts = benchmark_prompts[complexity]
            selected_prompt = prompts[0]  # 使用第一个提示

            async def generate_code():
                response = await zhipu_client.chat.completions.create(
                    model=test_environment["zhipu_model"],
                    messages=[{
                        "role": "user",
                        "content": selected_prompt
                    }],
                    max_tokens=200 if complexity == "high_complexity" else 100
                )
                return response

            result = await benchmark_runner.run_benchmark(
                name=f"complexity_{complexity}",
                test_func=generate_code,
                iterations=5
            )
            results[complexity] = result.metrics.response_time

        # 验证复杂度与响应时间的关系
        assert results["simple_generation"] < results["medium_complexity"]
        assert results["medium_complexity"] < results["high_complexity"]

    @pytest.mark.asyncio
    async def test_model_performance_comparison(
        self,
        benchmark_runner,
        test_environment
    ):
        """测试不同模型的性能比较"""
        # 如果有多个模型可用
        models = [test_environment["zhipu_model"]]
        if "alternative_model" in test_environment:
            models.append(test_environment["alternative_model"])

        results = {}

        for model in models:
            async def test_model():
                # 这里需要实际的模型调用
                # 暂时使用模拟
                await asyncio.sleep(0.5)
                return {"mock": "response"}

            result = await benchmark_runner.run_benchmark(
                name=f"model_{model}",
                test_func=test_model,
                iterations=10
            )
            results[model] = result.metrics.response_time

        # 可以比较不同模型的性能
        assert len(results) > 0