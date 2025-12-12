"""
智谱AI MCP集成测试
测试MCP服务器与智谱AI的完整集成
"""

import pytest
import asyncio
import json
import aiohttp
from typing import Dict, Any


@pytest.mark.integration
class TestZhipuMCPEndToEnd:
    """智谱AI MCP端到端集成测试"""

    @pytest.mark.asyncio
    async def test_mcp_server_startup(self, mcp_server, test_environment):
        """测试MCP服务器启动"""
        async with aiohttp.ClientSession() as session:
            # 测试健康检查端点
            health_url = f"{mcp_server['url']}/health"
            async with session.get(health_url) as response:
                assert response.status == 200
                data = await response.json()
                assert data["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_mcp_tools_list(self, mcp_server):
        """测试MCP工具列表"""
        async with aiohttp.ClientSession() as session:
            url = f"{mcp_server['url']}/mcp/tools/list"
            async with session.post(url, json={}) as response:
                assert response.status == 200
                data = await response.json()
                assert "tools" in data["result"]

                tools = data["result"]["tools"]
                tool_names = [tool["name"] for tool in tools]
                assert "generate_code" in tool_names
                assert "explain_code" in tool_names
                assert "optimize_code" in tool_names

    @pytest.mark.asyncio
    async def test_generate_code_through_mcp(self, mcp_server, mock_api_responses):
        """测试通过MCP生成代码"""
        async with aiohttp.ClientSession() as session:
            url = f"{mcp_server['url']}/mcp/tools/call"
            payload = {
                "name": "generate_code",
                "arguments": {
                    "prompt": "Write a binary search function in Python",
                    "language": "python",
                    "max_tokens": 200
                }
            }

            async with session.post(url, json=payload) as response:
                assert response.status == 200
                data = await response.json()
                assert "content" in data["result"]

                content = data["result"]["content"][0]
                assert content["type"] == "text"
                assert "binary search" in content["text"].lower() or "binary_search" in content["text"]
                assert "def " in content["text"]  # 应该包含函数定义

    @pytest.mark.asyncio
    async def test_explain_code_through_mcp(self, mcp_server, integration_test_data):
        """测试通过MCP解释代码"""
        code_snippet = integration_test_data["code_snippets"][0]  # Python Fibonacci

        async with aiohttp.ClientSession() as session:
            url = f"{mcp_server['url']}/mcp/tools/call"
            payload = {
                "name": "explain_code",
                "arguments": {
                    "code": code_snippet["code"],
                    "language": code_snippet["language"]
                }
            }

            async with session.post(url, json=payload) as response:
                assert response.status == 200
                data = await response.json()
                content = data["result"]["content"][0]

                assert code_snippet["expected_explanation"] in content["text"] or \
                       "fibonacci" in content["text"].lower()

    @pytest.mark.asyncio
    async def test_optimize_code_through_mcp(self, mcp_server):
        """测试通过MCP优化代码"""
        inefficient_code = """
def find_duplicates(arr):
    duplicates = []
    for i in range(len(arr)):
        for j in range(len(arr)):
            if i != j and arr[i] == arr[j] and arr[i] not in duplicates:
                duplicates.append(arr[i])
    return duplicates
        """

        async with aiohttp.ClientSession() as session:
            url = f"{mcp_server['url']}/mcp/tools/call"
            payload = {
                "name": "optimize_code",
                "arguments": {
                    "code": inefficient_code,
                    "language": "python",
                    "optimization_goal": "performance"
                }
            }

            async with session.post(url, json=payload) as response:
                assert response.status == 200
                data = await response.json()
                content = data["result"]["content"][0]["text"]

                # 优化后的代码应该更高效
                assert "set" in content or "dict" in content or "O(n)" in content

    @pytest.mark.asyncio
    async def test_concurrent_mcp_requests(self, mcp_server):
        """测试并发MCP请求"""
        async def make_request(prompt):
            async with aiohttp.ClientSession() as session:
                url = f"{mcp_server['url']}/mcp/tools/call"
                payload = {
                    "name": "generate_code",
                    "arguments": {
                        "prompt": prompt,
                        "language": "python",
                        "max_tokens": 100
                    }
                }
                async with session.post(url, json=payload) as response:
                    return await response.json()

        # 创建多个并发请求
        prompts = [
            "Write hello world function",
            "Write factorial function",
            "Write palindrome checker",
            "Write bubble sort",
            "Write prime number checker"
        ]

        tasks = [make_request(prompt) for prompt in prompts]
        responses = await asyncio.gather(*tasks)

        # 验证所有请求都成功
        for response in responses:
            assert response["result"]["content"][0]["type"] == "text"
            assert len(response["result"]["content"][0]["text"]) > 0

    @pytest.mark.asyncio
    async def test_mcp_error_handling(self, mcp_server):
        """测试MCP错误处理"""
        async with aiohttp.ClientSession() as session:
            # 测试不存在的工具
            url = f"{mcp_server['url']}/mcp/tools/call"
            payload = {
                "name": "nonexistent_tool",
                "arguments": {}
            }

            async with session.post(url, json=payload) as response:
                assert response.status == 200
                data = await response.json()
                assert "error" in data
                assert "not found" in data["error"]["message"].lower()

            # 测试缺少必需参数
            payload = {
                "name": "generate_code",
                "arguments": {}  # 缺少prompt
            }

            async with session.post(url, json=payload) as response:
                assert response.status == 200
                data = await response.json()
                assert "error" in data

    @pytest.mark.asyncio
    async def test_mcp_resources_access(self, mcp_server):
        """测试MCP资源访问"""
        async with aiohttp.ClientSession() as session:
            # 列出资源
            list_url = f"{mcp_server['url']}/mcp/resources/list"
            async with session.post(list_url, json={}) as response:
                assert response.status == 200
                data = await response.json()
                assert "resources" in data["result"]

            # 读取特定资源
            read_url = f"{mcp_server['url']}/mcp/resources/read"
            payload = {
                "uri": "zhipu://models/codegeex4"
            }
            async with session.post(read_url, json=payload) as response:
                assert response.status == 200
                data = await response.json()
                assert "contents" in data["result"]
                assert len(data["result"]["contents"]) > 0

    @pytest.mark.asyncio
    async def test_mcp_streaming_response(self, mcp_server):
        """测试MCP流式响应"""
        async with aiohttp.ClientSession() as session:
            url = f"{mcp_server['url']}/mcp/tools/call"
            payload = {
                "name": "generate_code",
                "arguments": {
                    "prompt": "Write a comprehensive Python class for managing a todo list",
                    "language": "python",
                    "stream": True,
                    "max_tokens": 500
                }
            }

            async with session.post(url, json=payload) as response:
                assert response.status == 200

                # 读取流式响应
                chunks = []
                async for chunk in response.content:
                    if chunk:
                        chunks.append(chunk.decode())

                # 验证至少接收到一些数据
                assert len(chunks) > 0
                combined_content = "".join(chunks)
                assert "class" in combined_content or "def" in combined_content


@pytest.mark.integration
class TestZhipuAPIIntegration:
    """智谱AI API集成测试"""

    @pytest.mark.asyncio
    async def test_api_authentication(self, zhipu_client, test_environment):
        """测试API认证"""
        response = await zhipu_client.chat.completions.create(
            model=test_environment["zhipu_model"],
            messages=[{"role": "user", "content": "test"}],
            max_tokens=10
        )

        # 如果使用了真实API密钥，应该得到成功响应
        if test_environment["zhipu_api_key"] != "test_api_key":
            assert response is not None
            assert hasattr(response, 'choices')

    @pytest.mark.asyncio
    async def test_api_rate_limit(self, zhipu_client, test_environment):
        """测试API速率限制"""
        if test_environment["zhipu_api_key"] == "test_api_key":
            pytest.skip("Skipping rate limit test with mock API key")

        # 快速发送多个请求
        tasks = []
        for _ in range(10):
            task = zhipu_client.chat.completions.create(
                model=test_environment["zhipu_model"],
                messages=[{"role": "user", "content": "print('hello')"}],
                max_tokens=10
            )
            tasks.append(task)

        # 等待所有请求完成
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 检查是否有速率限制错误
        rate_limit_errors = [r for r in results if isinstance(r, Exception) and "429" in str(r)]
        # 注意：实际测试时可能需要调整请求数量

    @pytest.mark.asyncio
    async def test_api_token_usage(self, zhipu_client, test_environment):
        """测试API Token使用跟踪"""
        if test_environment["zhipu_api_key"] == "test_api_key":
            pytest.skip("Skipping token usage test with mock API key")

        response = await zhipu_client.chat.completions.create(
            model=test_environment["zhipu_model"],
            messages=[
                {"role": "user", "content": "Write a function that calculates the area of a circle"}
            ],
            max_tokens=100
        )

        # 验证使用量信息
        if hasattr(response, 'usage'):
            assert response.usage.prompt_tokens > 0
            assert response.usage.completion_tokens > 0
            assert response.usage.total_tokens > 0

    @pytest.mark.asyncio
    async def test_api_model_capabilities(self, zhipu_client, test_environment):
        """测试API模型能力"""
        if test_environment["zhipu_api_key"] == "test_api_key":
            pytest.skip("Skipping model capabilities test with mock API key")

        # 测试不同编程语言的代码生成
        languages = ["Python", "JavaScript", "Java", "Go"]
        tasks = []

        for lang in languages:
            task = zhipu_client.chat.completions.create(
                model=test_environment["zhipu_model"],
                messages=[{
                    "role": "user",
                    "content": f"Write a hello world program in {lang}"
                }],
                max_tokens=50
            )
            tasks.append((lang, task))

        # 验证每种语言的代码生成
        for lang, task in tasks:
            response = await task
            if hasattr(response, 'choices') and response.choices:
                content = response.choices[0].message.content
                # 验证生成的代码包含正确的语言特征
                if lang.lower() == "python":
                    assert "print(" in content or "def " in content
                elif lang.lower() == "javascript":
                    assert "console.log" in content or "function" in content


@pytest.mark.integration
@pytest.mark.database
class TestDatabaseIntegration:
    """数据库集成测试"""

    @pytest.mark.asyncio
    async def test_postgres_connection(self, postgres_container, integration_helper):
        """测试PostgreSQL连接"""
        conn = integration_helper.create_test_database(postgres_container)
        assert conn is not None
        conn.close()

    @pytest.mark.asyncio
    async def test_redis_connection(self, redis_container):
        """测试Redis连接"""
        import redis.asyncio as redis

        client = redis.Redis(
            host=redis_container["host"],
            port=redis_container["port"],
            password=redis_container["password"]
        )

        # 测试设置和获取
        await client.set("test_key", "test_value")
        value = await client.get("test_key")
        assert value == b"test_value"

        await client.close()

    @pytest.mark.asyncio
    async def test_session_persistence(self, postgres_container, integration_helper):
        """测试会话持久化"""
        conn = integration_helper.create_test_database(postgres_container)

        try:
            with conn.cursor() as cur:
                # 插入会话记录
                cur.execute("""
                    INSERT INTO user_sessions (session_id, total_requests)
                    VALUES (%s, %s)
                    RETURNING id
                """, ("test_session_123", 5))

                session_id = cur.fetchone()[0]
                conn.commit()

                # 查询会话记录
                cur.execute("""
                    SELECT session_id, total_requests
                    FROM user_sessions
                    WHERE id = %s
                """, (session_id,))

                result = cur.fetchone()
                assert result[0] == "test_session_123"
                assert result[1] == 5

        finally:
            conn.close()

    @pytest.mark.asyncio
    async def test_code_generation_logging(self, postgres_container, integration_helper):
        """测试代码生成日志记录"""
        conn = integration_helper.create_test_database(postgres_container)

        try:
            with conn.cursor() as cur:
                # 插入代码生成记录
                cur.execute("""
                    INSERT INTO code_generation_logs
                    (prompt, generated_code, tokens_used, model)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                """, (
                    "Write fibonacci function",
                    "def fibonacci(n): return n if n <= 1 else fibonacci(n-1) + fibonacci(n-2)",
                    50,
                    "codegeex4"
                ))

                log_id = cur.fetchone()[0]
                conn.commit()

                # 查询日志记录
                cur.execute("""
                    SELECT prompt, tokens_used, model
                    FROM code_generation_logs
                    WHERE id = %s
                """, (log_id,))

                result = cur.fetchone()
                assert result[0] == "Write fibonacci function"
                assert result[1] == 50
                assert result[2] == "codegeex4"

        finally:
            conn.close()


@pytest.mark.integration
@pytest.mark.performance
class TestIntegrationPerformance:
    """集成性能测试"""

    @pytest.mark.asyncio
    async def test_response_time_benchmark(self, mcp_server, integration_helper):
        """测试响应时间基准"""
        async def make_request():
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

        # 测量多个请求的响应时间
        response_times = []
        for _ in range(10):
            result = await integration_helper.measure_response_time(make_request)
            response_times.append(result["response_time"])

        # 计算统计信息
        avg_time = sum(response_times) / len(response_times)
        max_time = max(response_times)
        min_time = min(response_times)

        # 性能断言（根据实际情况调整阈值）
        assert avg_time < 5.0  # 平均响应时间应小于5秒
        assert max_time < 10.0  # 最大响应时间应小于10秒
        assert min_time < 2.0  # 最小响应时间应小于2秒

    @pytest.mark.asyncio
    async def test_concurrent_request_throughput(self, mcp_server):
        """测试并发请求吞吐量"""
        async def make_request(session, prompt_id):
            url = f"{mcp_server['url']}/mcp/tools/call"
            payload = {
                "name": "generate_code",
                "arguments": {
                    "prompt": f"Write function {prompt_id}",
                    "language": "python",
                    "max_tokens": 30
                }
            }
            async with session.post(url, json=payload) as response:
                return await response.json()

        import time
        start_time = time.time()

        # 创建20个并发请求
        async with aiohttp.ClientSession() as session:
            tasks = [make_request(session, i) for i in range(20)]
            results = await asyncio.gather(*tasks)

        end_time = time.time()
        total_time = end_time - start_time

        # 验证所有请求都成功
        successful_requests = [r for r in results if "result" in r]
        assert len(successful_requests) == 20

        # 计算吞吐量（请求/秒）
        throughput = len(successful_requests) / total_time
        assert throughput > 2  # 应该至少每秒处理2个请求

    @pytest.mark.asyncio
    async def test_memory_usage_stability(self, mcp_server):
        """测试内存使用稳定性"""
        import psutil
        import os

        # 获取当前进程的内存使用
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # 执行大量请求
        for i in range(50):
            async with aiohttp.ClientSession() as session:
                url = f"{mcp_server['url']}/mcp/tools/call"
                payload = {
                    "name": "generate_code",
                    "arguments": {
                        "prompt": f"Test request {i}",
                        "language": "python",
                        "max_tokens": 20
                    }
                }
                async with session.post(url, json=payload) as response:
                    await response.json()

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        # 内存增长应该在合理范围内（小于50MB）
        assert memory_increase < 50