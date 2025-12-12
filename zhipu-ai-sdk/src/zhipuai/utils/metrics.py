"""
指标收集器

收集和统计API调用指标。
"""

import time
import threading
from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any


class Metrics:
    """指标数据结构"""

    def __init__(self):
        self.reset()

    def reset(self) -> None:
        """重置所有指标"""
        # 基础统计
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.total_errors = 0

        # 时间统计
        self.total_duration = 0.0
        self.min_duration = float('inf')
        self.max_duration = 0.0

        # 错误统计
        self.errors_by_type = defaultdict(int)
        self.errors_by_status = defaultdict(int)

        # 端点统计
        self.requests_by_endpoint = defaultdict(int)
        self.duration_by_endpoint = defaultdict(float)

        # 时间序列数据
        self.request_times = deque()
        self.error_times = deque()

    def record_request(
        self,
        method: str,
        endpoint: str,
        status_code: int,
        duration: float,
        error: Optional[str] = None
    ) -> None:
        """记录请求指标"""
        now = datetime.now()

        # 基础统计
        self.total_requests += 1
        self.request_times.append(now)

        # 成功/失败统计
        if 200 <= status_code < 400:
            self.successful_requests += 1
        else:
            self.failed_requests += 1
            self.error_times.append(now)

        # 时间统计
        self.total_duration += duration
        self.min_duration = min(self.min_duration, duration)
        self.max_duration = max(self.max_duration, duration)

        # 端点统计
        endpoint_key = f"{method} {endpoint}"
        self.requests_by_endpoint[endpoint_key] += 1
        self.duration_by_endpoint[endpoint_key] += duration

        # 错误统计
        if error:
            self.total_errors += 1
            self.errors_by_type[error] += 1
        if status_code >= 400:
            self.errors_by_status[status_code] += 1

    def record_error(self, error_type: str, duration: float) -> None:
        """记录错误指标"""
        now = datetime.now()
        self.total_errors += 1
        self.errors_by_type[error_type] += 1
        self.error_times.append(now)
        self.request_times.append(now)

        # 更新时间统计
        self.total_requests += 1
        self.total_duration += duration
        self.min_duration = min(self.min_duration, duration)
        self.max_duration = max(self.max_duration, duration)

    def get_summary(self, window_minutes: int = 5) -> Dict[str, Any]:
        """获取指标摘要"""
        now = datetime.now()
        window_start = now - timedelta(minutes=window_minutes)

        # 过滤时间窗口内的数据
        recent_requests = [
            t for t in self.request_times
            if t >= window_start
        ]
        recent_errors = [
            t for t in self.error_times
            if t >= window_start
        ]

        # 计算平均响应时间
        avg_duration = (
            self.total_duration / self.total_requests
            if self.total_requests > 0 else 0
        )

        # 计算成功率
        success_rate = (
            self.successful_requests / self.total_requests
            if self.total_requests > 0 else 0
        )

        # 计算RPS
        rps = len(recent_requests) / window_minutes / 60

        # 计算P95响应时间
        response_times = sorted([
            self.duration_by_endpoint[e] / self.requests_by_endpoint[e]
            for e in self.requests_by_endpoint
            if self.requests_by_endpoint[e] > 0
        ])
        p95_duration = response_times[int(len(response_times) * 0.95)] if response_times else 0

        return {
            "time_window_minutes": window_minutes,
            "requests": {
                "total": self.total_requests,
                "successful": self.successful_requests,
                "failed": self.failed_requests,
                "recent": len(recent_requests),
                "rps": rps,
                "success_rate": success_rate,
            },
            "duration": {
                "average": avg_duration,
                "min": self.min_duration if self.min_duration != float('inf') else 0,
                "max": self.max_duration,
                "p95": p95_duration,
            },
            "errors": {
                "total": self.total_errors,
                "recent": len(recent_errors),
                "by_type": dict(self.errors_by_type),
                "by_status": dict(self.errors_by_status),
            },
            "endpoints": {
                e: {
                    "requests": self.requests_by_endpoint[e],
                    "average_duration": (
                        self.duration_by_endpoint[e] / self.requests_by_endpoint[e]
                    ),
                }
                for e in self.requests_by_endpoint
            },
            "timestamp": now.isoformat(),
        }


class MetricsCollector:
    """指标收集器"""

    def __init__(
        self,
        enabled: bool = True,
        sample_rate: float = 0.1,
        max_history: int = 1000,
    ):
        self.enabled = enabled
        self.sample_rate = sample_rate
        self.max_history = max_history

        self.metrics = Metrics()
        self._lock = threading.Lock()

        # 历史数据
        self.history: List[Dict[str, Any]] = []

    def should_sample(self) -> bool:
        """判断是否应该采样"""
        if not self.enabled:
            return False
        return random.random() < self.sample_rate

    def record_request(
        self,
        method: str,
        path: str,
        status_code: int,
        duration: float,
        error: Optional[str] = None,
    ) -> None:
        """记录请求指标"""
        if not self.should_sample():
            return

        with self._lock:
            self.metrics.record_request(method, path, status_code, duration, error)

    def record_error(self, error_type: str, duration: float) -> None:
        """记录错误指标"""
        if not self.should_sample():
            return

        with self._lock:
            self.metrics.record_error(error_type, duration)

    def get_metrics(self, window_minutes: int = 5) -> Optional[Dict[str, Any]]:
        """获取指标数据"""
        if not self.enabled:
            return None

        with self._lock:
            return self.metrics.get_summary(window_minutes)

    def save_snapshot(self) -> None:
        """保存当前快照到历史"""
        if not self.enabled:
            return

        with self._lock:
            snapshot = self.metrics.get_summary()
            self.history.append(snapshot)

            # 限制历史记录数量
            if len(self.history) > self.max_history:
                self.history = self.history[-self.max_history:]

    def get_history(self, count: int = 10) -> List[Dict[str, Any]]:
        """获取历史快照"""
        with self._lock:
            return self.history[-count:]

    def reset(self) -> None:
        """重置所有指标"""
        with self._lock:
            self.metrics.reset()
            self.history.clear()

    def export_metrics(self) -> Dict[str, Any]:
        """导出所有指标数据"""
        with self._lock:
            return {
                "current": self.metrics.get_summary(),
                "history": self.history.copy(),
                "config": {
                    "enabled": self.enabled,
                    "sample_rate": self.sample_rate,
                    "max_history": self.max_history,
                },
            }


# 添加缺失的导入
import random