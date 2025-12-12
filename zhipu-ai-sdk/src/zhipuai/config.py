"""
配置管理模块

提供灵活的配置管理，支持环境变量、配置文件和代码配置。
"""

import os
import json
import yaml
from pathlib import Path
from typing import Any, Dict, Optional, Union
from dataclasses import dataclass, field
from httpx import Limits, Timeout


@dataclass
class HttpClientConfig:
    """HTTP客户端配置"""
    base_url: str = "https://api.zhipuai.ai"
    timeout: Timeout = field(default_factory=lambda: Timeout(
        connect=5.0,
        read=30.0,
        write=10.0,
        pool=30.0
    ))
    limits: Limits = field(default_factory=lambda: Limits(
        max_keepalive_connections=50,
        max_connections=100,
        keepalive_expiry=30.0
    ))
    headers: Dict[str, str] = field(default_factory=dict)
    proxy: Optional[str] = None
    verify_ssl: bool = True
    follow_redirects: bool = True
    enable_compression: bool = True


@dataclass
class RetryConfig:
    """重试配置"""
    max_retries: int = 3
    backoff_strategy: str = "exponential"  # linear, exponential, fixed
    initial_delay: float = 1.0
    max_delay: float = 60.0
    jitter: bool = True
    retry_on_status: set[int] = field(default_factory=lambda: {429, 500, 502, 503, 504})
    retry_after_header: bool = True


@dataclass
class RateLimitConfig:
    """速率限制配置"""
    requests_per_second: float = 20.0
    burst_size: int = 100
    auto_adjust: bool = True
    backoff_on_limit: bool = True


@dataclass
class CacheConfig:
    """缓存配置"""
    enabled: bool = False
    backend: str = "memory"  # memory, redis, file
    ttl: int = 3600  # 秒
    max_size: int = 1000
    redis_url: Optional[str] = None
    file_path: Optional[str] = None


@dataclass
class LoggingConfig:
    """日志配置"""
    enabled: bool = True
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file: Optional[str] = None
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    enable_request_log: bool = False
    enable_response_log: bool = False


@dataclass
class MonitoringConfig:
    """监控配置"""
    enabled: bool = False
    metrics_endpoint: Optional[str] = None
    sample_rate: float = 0.1
    custom_tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class Config:
    """主配置类"""
    # API配置
    api_key: str
    api_version: str = "v1"

    # 子配置
    http_client: HttpClientConfig = field(default_factory=HttpClientConfig)
    retry: RetryConfig = field(default_factory=RetryConfig)
    rate_limit: RateLimitConfig = field(default_factory=RateLimitConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)

    # 其他配置
    default_model: str = "code-geex"
    organization: Optional[str] = None
    user_agent: Optional[str] = None

    @classmethod
    def from_env(cls) -> "Config":
        """从环境变量创建配置"""
        api_key = os.getenv("ZHIPU_API_KEY")
        if not api_key:
            raise ValueError("ZHIPU_API_KEY environment variable is required")

        return cls(
            api_key=api_key,
            api_version=os.getenv("ZHIPU_API_VERSION", "v1"),
            http_client=HttpClientConfig(
                base_url=os.getenv("ZHIPU_BASE_URL", "https://api.zhipuai.ai"),
                proxy=os.getenv("ZHIPU_PROXY"),
                verify_ssl=os.getenv("ZHIPU_VERIFY_SSL", "true").lower() == "true",
            ),
            retry=RetryConfig(
                max_retries=int(os.getenv("ZHIPU_MAX_RETRIES", "3")),
                initial_delay=float(os.getenv("ZHIPU_RETRY_INITIAL_DELAY", "1.0")),
                max_delay=float(os.getenv("ZHIPU_RETRY_MAX_DELAY", "60.0")),
            ),
            rate_limit=RateLimitConfig(
                requests_per_second=float(os.getenv("ZHIPU_RPS", "20.0")),
                burst_size=int(os.getenv("ZHIPU_BURST_SIZE", "100")),
            ),
            cache=CacheConfig(
                enabled=os.getenv("ZHIPU_CACHE_ENABLED", "false").lower() == "true",
                backend=os.getenv("ZHIPU_CACHE_BACKEND", "memory"),
                ttl=int(os.getenv("ZHIPU_CACHE_TTL", "3600")),
                redis_url=os.getenv("ZHIPU_REDIS_URL"),
                file_path=os.getenv("ZHIPU_CACHE_FILE_PATH"),
            ),
            logging=LoggingConfig(
                enabled=os.getenv("ZHIPU_LOG_ENABLED", "true").lower() == "true",
                level=os.getenv("ZHIPU_LOG_LEVEL", "INFO"),
                file=os.getenv("ZHIPU_LOG_FILE"),
                enable_request_log=os.getenv("ZHIPU_LOG_REQUESTS", "false").lower() == "true",
                enable_response_log=os.getenv("ZHIPU_LOG_RESPONSES", "false").lower() == "true",
            ),
            monitoring=MonitoringConfig(
                enabled=os.getenv("ZHIPU_MONITORING_ENABLED", "false").lower() == "true",
                metrics_endpoint=os.getenv("ZHIPU_METRICS_ENDPOINT"),
                sample_rate=float(os.getenv("ZHIPU_METRICS_SAMPLE_RATE", "0.1")),
            ),
            default_model=os.getenv("ZHIPU_DEFAULT_MODEL", "code-geex"),
            organization=os.getenv("ZHIPU_ORGANIZATION"),
        )

    @classmethod
    def from_file(cls, path: Union[str, Path]) -> "Config":
        """从配置文件创建配置"""
        path = Path(path)

        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            if path.suffix.lower() in [".yml", ".yaml"]:
                data = yaml.safe_load(f)
            elif path.suffix.lower() == ".json":
                data = json.load(f)
            else:
                raise ValueError(f"Unsupported config file format: {path.suffix}")

        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Config":
        """从字典创建配置"""
        # 处理环境变量替换
        data = cls._expand_env_vars(data)

        # 解析各个子配置
        http_client_data = data.get("http_client", {})
        if http_client_data:
            http_client = HttpClientConfig(**http_client_data)
        else:
            http_client = HttpClientConfig()

        retry_data = data.get("retry", {})
        retry = RetryConfig(**retry_data) if retry_data else RetryConfig()

        rate_limit_data = data.get("rate_limit", {})
        rate_limit = RateLimitConfig(**rate_limit_data) if rate_limit_data else RateLimitConfig()

        cache_data = data.get("cache", {})
        cache = CacheConfig(**cache_data) if cache_data else CacheConfig()

        logging_data = data.get("logging", {})
        logging = LoggingConfig(**logging_data) if logging_data else LoggingConfig()

        monitoring_data = data.get("monitoring", {})
        monitoring = MonitoringConfig(**monitoring_data) if monitoring_data else MonitoringConfig()

        # 主配置
        api_key = data.get("api_key") or os.getenv("ZHIPU_API_KEY")
        if not api_key:
            raise ValueError("API key is required")

        return cls(
            api_key=api_key,
            api_version=data.get("api_version", "v1"),
            http_client=http_client,
            retry=retry,
            rate_limit=rate_limit,
            cache=cache,
            logging=logging,
            monitoring=monitoring,
            default_model=data.get("default_model", "code-geex"),
            organization=data.get("organization"),
            user_agent=data.get("user_agent"),
        )

    @staticmethod
    def _expand_env_vars(obj: Any) -> Any:
        """递归展开环境变量"""
        if isinstance(obj, dict):
            return {k: Config._expand_env_vars(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [Config._expand_env_vars(item) for item in obj]
        elif isinstance(obj, str):
            # 支持 ${VAR} 和 $VAR 格式
            import re

            def replace_var(match):
                var_name = match.group(1) or match.group(2)
                return os.getenv(var_name, match.group(0))

            # 先处理 ${VAR} 格式
            obj = re.sub(r'\$\{([^}]+)\}', replace_var, obj)
            # 再处理 $VAR 格式
            obj = re.sub(r'\$([A-Za-z_][A-Za-z0-9_]*)', replace_var, obj)
            return obj
        else:
            return obj

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "api_key": self.api_key,
            "api_version": self.api_version,
            "http_client": {
                "base_url": self.http_client.base_url,
                "timeout": {
                    "connect": self.http_client.timeout.connect,
                    "read": self.http_client.timeout.read,
                    "write": self.http_client.timeout.write,
                    "pool": self.http_client.timeout.pool,
                },
                "limits": {
                    "max_keepalive_connections": self.http_client.limits.max_keepalive_connections,
                    "max_connections": self.http_client.limits.max_connections,
                    "keepalive_expiry": self.http_client.limits.keepalive_expiry,
                },
                "headers": self.http_client.headers,
                "proxy": self.http_client.proxy,
                "verify_ssl": self.http_client.verify_ssl,
                "follow_redirects": self.http_client.follow_redirects,
                "enable_compression": self.http_client.enable_compression,
            },
            "retry": {
                "max_retries": self.retry.max_retries,
                "backoff_strategy": self.retry.backoff_strategy,
                "initial_delay": self.retry.initial_delay,
                "max_delay": self.retry.max_delay,
                "jitter": self.retry.jitter,
                "retry_on_status": list(self.retry.retry_on_status),
                "retry_after_header": self.retry.retry_after_header,
            },
            "rate_limit": {
                "requests_per_second": self.rate_limit.requests_per_second,
                "burst_size": self.rate_limit.burst_size,
                "auto_adjust": self.rate_limit.auto_adjust,
                "backoff_on_limit": self.rate_limit.backoff_on_limit,
            },
            "cache": {
                "enabled": self.cache.enabled,
                "backend": self.cache.backend,
                "ttl": self.cache.ttl,
                "max_size": self.cache.max_size,
                "redis_url": self.cache.redis_url,
                "file_path": self.cache.file_path,
            },
            "logging": {
                "enabled": self.logging.enabled,
                "level": self.logging.level,
                "format": self.logging.format,
                "file": self.logging.file,
                "max_file_size": self.logging.max_file_size,
                "backup_count": self.logging.backup_count,
                "enable_request_log": self.logging.enable_request_log,
                "enable_response_log": self.logging.enable_response_log,
            },
            "monitoring": {
                "enabled": self.monitoring.enabled,
                "metrics_endpoint": self.monitoring.metrics_endpoint,
                "sample_rate": self.monitoring.sample_rate,
                "custom_tags": self.monitoring.custom_tags,
            },
            "default_model": self.default_model,
            "organization": self.organization,
            "user_agent": self.user_agent,
        }

    def save_to_file(self, path: Union[str, Path]) -> None:
        """保存到配置文件"""
        path = Path(path)
        data = self.to_dict()

        # 移除敏感信息
        data.pop("api_key", None)

        with open(path, "w", encoding="utf-8") as f:
            if path.suffix.lower() in [".yml", ".yaml"]:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
            elif path.suffix.lower() == ".json":
                json.dump(data, f, indent=2, ensure_ascii=False)
            else:
                raise ValueError(f"Unsupported config file format: {path.suffix}")