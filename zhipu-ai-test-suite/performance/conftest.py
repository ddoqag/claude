"""
性能测试配置文件
"""

import pytest
import asyncio
import time
import psutil
import numpy as np
from typing import Dict, Any, List, Callable
from dataclasses import dataclass
from unittest.mock import Mock, AsyncMock


@dataclass
class PerformanceMetrics:
    """性能指标数据类"""
    response_time: float
    cpu_usage: float
    memory_usage: float
    throughput: float
    error_rate: float
    p50_response_time: float
    p95_response_time: float
    p99_response_time: float


@dataclass
class BenchmarkResult:
    """基准测试结果"""
    test_name: str
    metrics: PerformanceMetrics
    timestamp: float
    metadata: Dict[str, Any]


class PerformanceMonitor:
    """性能监控器"""

    def __init__(self):
        self.process = psutil.Process()
        self.start_time = None
        self.response_times = []
        self.errors = 0
        self.total_requests = 0

    def start_monitoring(self):
        """开始监控"""
        self.start_time = time.time()
        self.response_times = []
        self.errors = 0
        self.total_requests = 0

    def record_request(self, response_time: float, success: bool = True):
        """记录请求"""
        self.response_times.append(response_time)
        self.total_requests += 1
        if not success:
            self.errors += 1

    def get_metrics(self) -> PerformanceMetrics:
        """获取性能指标"""
        if not self.response_times:
            return PerformanceMetrics(0, 0, 0, 0, 0, 0, 0, 0)

        current_time = time.time()
        duration = current_time - self.start_time

        response_times_array = np.array(self.response_times)
        cpu_percent = self.process.cpu_percent()
        memory_info = self.process.memory_info()
        memory_mb = memory_info.rss / 1024 / 1024

        return PerformanceMetrics(
            response_time=np.mean(response_times_array),
            cpu_usage=cpu_percent,
            memory_usage=memory_mb,
            throughput=self.total_requests / duration,
            error_rate=self.errors / self.total_requests,
            p50_response_time=np.percentile(response_times_array, 50),
            p95_response_time=np.percentile(response_times_array, 95),
            p99_response_time=np.percentile(response_times_array, 99)
        )


@pytest.fixture
def performance_monitor():
    """性能监控器夹具"""
    monitor = PerformanceMonitor()
    yield monitor
    # 清理资源


@pytest.fixture
def load_test_scenarios():
    """负载测试场景"""
    return {
        "light": {
            "concurrent_users": 1,
            "duration": 10,
            "requests_per_second": 1,
            "description": "轻负载测试"
        },
        "moderate": {
            "concurrent_users": 10,
            "duration": 30,
            "requests_per_second": 5,
            "description": "中等负载测试"
        },
        "heavy": {
            "concurrent_users": 50,
            "duration": 60,
            "requests_per_second": 20,
            "description": "重负载测试"
        },
        "stress": {
            "concurrent_users": 100,
            "duration": 120,
            "requests_per_second": 50,
            "description": "压力测试"
        },
        "spike": {
            "concurrent_users": 200,
            "duration": 30,
            "requests_per_second": 100,
            "description": "峰值测试"
        }
    }


@pytest.fixture
def benchmark_prompts():
    """基准测试提示词"""
    return {
        "simple_generation": [
            "Write hello world in Python",
            "Create a function to add two numbers",
            "Print current date and time",
            "Define an empty class",
            "Write a simple for loop"
        ],
        "medium_complexity": [
            "Write a function to check if a number is prime",
            "Create a class representing a bank account",
            "Implement binary search algorithm",
            "Write a REST API endpoint",
            "Create a decorator for timing functions"
        ],
        "high_complexity": [
            "Write a complete web scraper with error handling",
            "Implement a machine learning model from scratch",
            "Create a distributed task queue system",
            "Write a compiler for a simple language",
            "Implement a blockchain from scratch"
        ],
        "code_explanation": [
            "Explain this Fibonacci implementation",
            "What does this sorting algorithm do?",
            "Explain the design pattern used here",
            "What is the time complexity of this code?",
            "Explain this recursion base case"
        ],
        "code_optimization": [
            "Optimize this O(n^2) algorithm",
            "Improve memory usage of this function",
            "Make this code more Pythonic",
            "Add caching to this function",
            "Parallelize this computation"
        ]
    }


@pytest.fixture
def code_samples():
    """代码样本用于测试"""
    return {
        "python": {
            "small": "def add(a, b): return a + b",
            "medium": """
class Calculator:
    def __init__(self):
        self.history = []

    def add(self, a, b):
        result = a + b
        self.history.append(f"{a} + {b} = {result}")
        return result

    def get_history(self):
        return self.history
            """,
            "large": """
import numpy as np
from typing import List, Tuple, Optional

class NeuralNetwork:
    def __init__(self, layer_sizes: List[int], activation: str = 'relu'):
        self.layer_sizes = layer_sizes
        self.activation = activation
        self.weights = []
        self.biases = []

        for i in range(len(layer_sizes) - 1):
            self.weights.append(np.random.randn(layer_sizes[i], layer_sizes[i+1]) * 0.01)
            self.biases.append(np.zeros((1, layer_sizes[i+1])))

    def forward(self, X: np.ndarray) -> np.ndarray:
        self.activations = [X]
        self.zs = []

        for W, b in zip(self.weights, self.biases):
            z = np.dot(self.activations[-1], W) + b
            self.zs.append(z)

            if self.activation == 'relu':
                self.activations.append(np.maximum(0, z))
            elif self.activation == 'sigmoid':
                self.activations.append(1 / (1 + np.exp(-z)))
            else:
                self.activations.append(z)

        return self.activations[-1]
            """
        },
        "javascript": {
            "small": "const add = (a, b) => a + b;",
            "medium": """
class TodoList {
    constructor() {
        this.todos = [];
        this.nextId = 1;
    }

    add(text) {
        const todo = {
            id: this.nextId++,
            text,
            completed: false,
            createdAt: new Date()
        };
        this.todos.push(todo);
        return todo;
    }

    toggle(id) {
        const todo = this.todos.find(t => t.id === id);
        if (todo) {
            todo.completed = !todo.completed;
        }
        return todo;
    }
}
            """
        },
        "java": {
            "small": "public int add(int a, int b) { return a + b; }",
            "medium": """
public class BinaryTree<T extends Comparable<T>> {
    private static class Node<E> {
        E data;
        Node<E> left, right;

        Node(E data) {
            this.data = data;
            this.left = this.right = null;
        }
    }

    private Node<T> root;

    public void insert(T data) {
        root = insertRecursive(root, data);
    }

    private Node<T> insertRecursive(Node<T> current, T data) {
        if (current == null) {
            return new Node<>(data);
        }

        if (data.compareTo(current.data) < 0) {
            current.left = insertRecursive(current.left, data);
        } else if (data.compareTo(current.data) > 0) {
            current.right = insertRecursive(current.right, data);
        }

        return current;
    }
}
            """
        }
    }


@pytest.fixture
def performance_thresholds():
    """性能阈值配置"""
    return {
        "response_time": {
            "warning": 2.0,  # 秒
            "critical": 5.0   # 秒
        },
        "throughput": {
            "minimum": 10,    # 请求/秒
            "target": 50      # 请求/秒
        },
        "error_rate": {
            "warning": 0.01,  # 1%
            "critical": 0.05  # 5%
        },
        "cpu_usage": {
            "warning": 70,    # 百分比
            "critical": 90    # 百分比
        },
        "memory_usage": {
            "warning": 500,   # MB
            "critical": 1000  # MB
        }
    }


class BenchmarkRunner:
    """基准测试运行器"""

    def __init__(self):
        self.results = []

    async def run_benchmark(
        self,
        name: str,
        test_func: Callable,
        iterations: int = 10,
        warmup_iterations: int = 3
    ) -> BenchmarkResult:
        """运行基准测试"""
        # 预热
        for _ in range(warmup_iterations):
            await test_func()

        # 实际测试
        response_times = []
        cpu_usages = []
        memory_usages = []

        monitor = PerformanceMonitor()
        monitor.start_monitoring()

        for _ in range(iterations):
            start_time = time.time()
            await test_func()
            response_time = time.time() - start_time

            response_times.append(response_time)
            cpu_usages.append(monitor.process.cpu_percent())
            memory_info = monitor.process.memory_info()
            memory_usages.append(memory_info.rss / 1024 / 1024)

        metrics = PerformanceMetrics(
            response_time=np.mean(response_times),
            cpu_usage=np.mean(cpu_usages),
            memory_usage=np.mean(memory_usages),
            throughput=iterations / (time.time() - monitor.start_time),
            error_rate=0.0,
            p50_response_time=np.percentile(response_times, 50),
            p95_response_time=np.percentile(response_times, 95),
            p99_response_time=np.percentile(response_times, 99)
        )

        result = BenchmarkResult(
            test_name=name,
            metrics=metrics,
            timestamp=time.time(),
            metadata={"iterations": iterations}
        )

        self.results.append(result)
        return result

    def get_summary(self) -> Dict[str, Any]:
        """获取测试摘要"""
        if not self.results:
            return {}

        summary = {
            "total_tests": len(self.results),
            "average_response_time": np.mean([r.metrics.response_time for r in self.results]),
            "average_throughput": np.mean([r.metrics.throughput for r in self.results]),
            "average_cpu_usage": np.mean([r.metrics.cpu_usage for r in self.results]),
            "average_memory_usage": np.mean([r.metrics.memory_usage for r in self.results]),
            "test_results": []
        }

        for result in self.results:
            summary["test_results"].append({
                "name": result.test_name,
                "response_time": result.metrics.response_time,
                "throughput": result.metrics.throughput,
                "cpu_usage": result.metrics.cpu_usage,
                "memory_usage": result.metrics.memory_usage
            })

        return summary


@pytest.fixture
def benchmark_runner():
    """基准测试运行器夹具"""
    runner = BenchmarkRunner()
    yield runner
    # 可以在这里保存结果或生成报告


class LoadTester:
    """负载测试器"""

    def __init__(self):
        self.results = []

    async def run_load_test(
        self,
        test_func: Callable,
        concurrent_users: int,
        duration: int,
        requests_per_second: int
    ) -> BenchmarkResult:
        """运行负载测试"""
        monitor = PerformanceMonitor()
        monitor.start_monitoring()

        # 创建信号量控制并发数
        semaphore = asyncio.Semaphore(concurrent_users)
        tasks = []

        async def worker():
            async with semaphore:
                while time.time() - monitor.start_time < duration:
                    start_time = time.time()
                    try:
                        await test_func()
                        response_time = time.time() - start_time
                        monitor.record_request(response_time, success=True)
                    except Exception as e:
                        response_time = time.time() - start_time
                        monitor.record_request(response_time, success=False)

                    # 控制请求速率
                    await asyncio.sleep(1 / requests_per_second)

        # 启动工作协程
        for _ in range(concurrent_users):
            tasks.append(worker())

        # 等待所有任务完成
        await asyncio.gather(*tasks, return_exceptions=True)

        metrics = monitor.get_metrics()

        result = BenchmarkResult(
            test_name=f"load_test_{concurrent_users}users_{duration}s",
            metrics=metrics,
            timestamp=time.time(),
            metadata={
                "concurrent_users": concurrent_users,
                "duration": duration,
                "requests_per_second": requests_per_second
            }
        )

        self.results.append(result)
        return result


@pytest.fixture
def load_tester():
    """负载测试器夹具"""
    tester = LoadTester()
    yield tester