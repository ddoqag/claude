"""
集成测试配置文件
"""

import pytest
import asyncio
import os
import json
import tempfile
from typing import Dict, Any, Generator
from unittest.mock import Mock, AsyncMock
import docker
from docker.client import DockerClient


@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def docker_client():
    """Docker客户端"""
    try:
        client = docker.from_env()
        yield client
    except docker.errors.DockerException:
        pytest.skip("Docker not available")


@pytest.fixture(scope="session")
def test_environment():
    """测试环境配置"""
    return {
        "zhipu_api_endpoint": os.getenv("ZHIPU_API_ENDPOINT", "https://open.bigmodel.cn/api/paas/v4"),
        "zhipu_api_key": os.getenv("ZHIPU_API_KEY", "test_api_key"),
        "zhipu_model": os.getenv("ZHIPU_MODEL", "codegeex4"),
        "mcp_server_port": int(os.getenv("MCP_SERVER_PORT", "8080")),
        "redis_host": os.getenv("REDIS_HOST", "localhost"),
        "redis_port": int(os.getenv("REDIS_PORT", "6379")),
        "postgres_host": os.getenv("POSTGRES_HOST", "localhost"),
        "postgres_port": int(os.getenv("POSTGRES_PORT", "5432")),
        "postgres_db": os.getenv("POSTGRES_DB", "test_zhipu"),
        "postgres_user": os.getenv("POSTGRES_USER", "test"),
        "postgres_password": os.getenv("POSTGRES_PASSWORD", "test")
    }


@pytest.fixture(scope="session")
def redis_container(docker_client, test_environment):
    """Redis测试容器"""
    container = None
    try:
        container = docker_client.containers.run(
            "redis:7-alpine",
            detach=True,
            ports={f'{test_environment["redis_port"]}/tcp': test_environment["redis_port"]},
            environment={
                "REDIS_PASSWORD": "testredis"
            }
        )

        # 等待Redis启动
        import time
        time.sleep(5)

        yield {
            "host": "localhost",
            "port": test_environment["redis_port"],
            "password": "testredis"
        }
    finally:
        if container:
            container.stop()
            container.remove()


@pytest.fixture(scope="session")
def postgres_container(docker_client, test_environment):
    """PostgreSQL测试容器"""
    container = None
    try:
        container = docker_client.containers.run(
            "postgres:15-alpine",
            detach=True,
            ports={f'{test_environment["postgres_port"]}/tcp': test_environment["postgres_port"]},
            environment={
                "POSTGRES_DB": test_environment["postgres_db"],
                "POSTGRES_USER": test_environment["postgres_user"],
                "POSTGRES_PASSWORD": test_environment["postgres_password"]
            }
        )

        # 等待PostgreSQL启动
        import time
        time.sleep(10)

        yield {
            "host": "localhost",
            "port": test_environment["postgres_port"],
            "database": test_environment["postgres_db"],
            "user": test_environment["postgres_user"],
            "password": test_environment["postgres_password"]
        }
    finally:
        if container:
            container.stop()
            container.remove()


@pytest.fixture
async def zhipu_client(test_environment):
    """智谱AI客户端实例"""
    from zhipuai import ZhipuAI
    client = ZhipuAI(
        api_key=test_environment["zhipu_api_key"],
        base_url=test_environment["zhipu_api_endpoint"]
    )
    yield client
    # 清理资源
    await client.close() if hasattr(client, 'close') else None


@pytest.fixture
async def mcp_server(test_environment):
    """MCP服务器实例"""
    import subprocess
    import time

    # 启动MCP服务器
    server_process = subprocess.Popen(
        ["python", "-m", "zhipu_mcp_server"],
        env={
            "MCP_SERVER_PORT": str(test_environment["mcp_server_port"]),
            "ZHIPU_API_KEY": test_environment["zhipu_api_key"]
        },
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    # 等待服务器启动
    time.sleep(3)

    yield {
        "url": f"http://localhost:{test_environment['mcp_server_port']}",
        "process": server_process
    }

    # 清理
    server_process.terminate()
    server_process.wait(timeout=5)


@pytest.fixture
def sample_code_repository():
    """示例代码仓库"""
    import tempfile
    import os

    # 创建临时目录作为代码仓库
    repo_dir = tempfile.mkdtemp(prefix="test_repo_")

    # 创建示例文件
    files = {
        "main.py": """
def main():
    print("Hello, World!")
    if __name__ == "__main__":
        main()
        """,
        "utils.py": """
def calculate_fibonacci(n):
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)

def calculate_factorial(n):
    if n <= 1:
        return 1
    return n * calculate_factorial(n-1)
        """,
        "tests/test_main.py": """
import unittest
from main import main

class TestMain(unittest.TestCase):
    def test_main(self):
        # Test that main runs without error
        main()
        """,
        "README.md": """
# Test Repository

This is a test repository for integration testing.

## Features

- Fibonacci calculation
- Factorial calculation
- Unit tests
        """
    }

    for filename, content in files.items():
        file_path = os.path.join(repo_dir, filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as f:
            f.write(content)

    yield repo_dir

    # 清理
    import shutil
    shutil.rmtree(repo_dir)


@pytest.fixture
def mock_api_responses():
    """模拟API响应集合"""
    return {
        "code_generation": {
            "code": 200,
            "data": {
                "task_id": "test_task_123",
                "model": "codegeex4",
                "choices": [{
                    "message": {
                        "content": """def quick_sort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quick_sort(left) + middle + quick_sort(right)"""
                    }
                }]
            }
        },
        "code_explanation": {
            "code": 200,
            "data": {
                "task_id": "test_task_124",
                "explanation": "这段代码实现了快速排序算法..."
            }
        },
        "error_response": {
            "code": 400,
            "msg": "Invalid request parameters"
        },
        "rate_limit": {
            "code": 429,
            "msg": "Rate limit exceeded"
        }
    }


@pytest.fixture
def integration_test_data():
    """集成测试数据集"""
    return {
        "code_snippets": [
            {
                "language": "python",
                "code": "def fibonacci(n): return n if n <= 1 else fibonacci(n-1) + fibonacci(n-2)",
                "expected_explanation": "斐波那契数列实现"
            },
            {
                "language": "javascript",
                "code": "const factorial = n => n <= 1 ? 1 : n * factorial(n-1)",
                "expected_explanation": "阶乘函数实现"
            },
            {
                "language": "java",
                "code": "public static boolean isPrime(int n) { if(n <= 1) return false; for(int i=2; i*i<=n; i++) if(n%i==0) return false; return true; }",
                "expected_explanation": "素数判断函数"
            }
        ],
        "test_prompts": [
            "Write a function to reverse a string",
            "Create a class for a simple calculator",
            "Implement a binary search algorithm",
            "Generate a REST API endpoint",
            "Write unit tests for a function"
        ]
    }


class IntegrationTestHelper:
    """集成测试辅助类"""

    @staticmethod
    async def wait_for_service(url: str, timeout: int = 30) -> bool:
        """等待服务可用"""
        import aiohttp
        import asyncio

        async with aiohttp.ClientSession() as session:
            start_time = asyncio.get_event_loop().time()
            while True:
                try:
                    async with session.get(url, timeout=5) as response:
                        if response.status == 200:
                            return True
                except:
                    pass

                if asyncio.get_event_loop().time() - start_time > timeout:
                    return False

                await asyncio.sleep(1)

    @staticmethod
    def create_test_database(postgres_config: Dict[str, Any]):
        """创建测试数据库表"""
        import psycopg2
        from psycopg2.extras import execute_values

        conn = psycopg2.connect(
            host=postgres_config["host"],
            port=postgres_config["port"],
            database=postgres_config["database"],
            user=postgres_config["user"],
            password=postgres_config["password"]
        )

        with conn.cursor() as cur:
            # 创建表
            cur.execute("""
                CREATE TABLE IF NOT EXISTS code_generation_logs (
                    id SERIAL PRIMARY KEY,
                    prompt TEXT NOT NULL,
                    generated_code TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    tokens_used INTEGER,
                    model VARCHAR(50)
                )
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS user_sessions (
                    id SERIAL PRIMARY KEY,
                    session_id VARCHAR(100) UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    total_requests INTEGER DEFAULT 0
                )
            """)

            conn.commit()

        return conn

    @staticmethod
    async def measure_response_time(func, *args, **kwargs):
        """测量响应时间"""
        import time
        start_time = time.time()
        result = await func(*args, **kwargs)
        end_time = time.time()
        return {
            "result": result,
            "response_time": end_time - start_time
        }

    @staticmethod
    def assert_code_quality(code: str, language: str):
        """断言代码质量"""
        import ast
        import re

        if language.lower() == "python":
            try:
                ast.parse(code)
            except SyntaxError:
                pytest.fail("Generated Python code has syntax errors")

        # 检查常见的代码质量问题
        issues = []

        # 检查是否有硬编码的秘密
        secret_patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'api_key\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']'
        ]
        for pattern in secret_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                issues.append("Potential hardcoded secret found")

        # 检查是否有未处理的异常
        if "except:" in code and "except Exception" not in code:
            issues.append("Bare except clause found")

        if issues:
            pytest.fail(f"Code quality issues: {', '.join(issues)}")


@pytest.fixture
def integration_helper():
    """集成测试辅助工具夹具"""
    return IntegrationTestHelper()