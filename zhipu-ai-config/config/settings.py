"""
智谱AI编码端点配置管理模块
提供安全、灵活的多环境配置管理
"""

import os
import json
from typing import Dict, Any, Optional, List
from pathlib import Path
from dataclasses import dataclass, field
from cryptography.fernet import Fernet
import logging
from enum import Enum

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Environment(Enum):
    """环境枚举"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


@dataclass
class ZhipuAISettings:
    """智谱AI配置"""
    api_key: str
    endpoint_url: str
    model_name: str = "glm-4.6"
    max_retries: int = 3
    timeout: int = 30
    rate_limit: int = 100  # 每分钟请求限制
    organization_id: Optional[str] = None
    project_id: Optional[str] = None


@dataclass
class SecuritySettings:
    """安全配置"""
    encryption_key: str
    allowed_origins: List[str] = field(default_factory=list)
    allowed_ips: List[str] = field(default_factory=list)
    jwt_secret: Optional[str] = None
    session_timeout: int = 3600  # 秒
    enable_audit_log: bool = True


@dataclass
class DatabaseSettings:
    """数据库配置"""
    host: str
    port: int
    name: str
    username: str
    password: str
    ssl_mode: str = "require"
    pool_size: int = 5
    max_overflow: int = 10


@dataclass
class CacheSettings:
    """缓存配置"""
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    ttl: int = 3600  # 缓存过期时间（秒）


@dataclass
class LoggingSettings:
    """日志配置"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = None
    max_file_size: str = "10MB"
    backup_count: int = 5
    enable_audit: bool = True
    audit_file_path: Optional[str] = None


class ConfigManager:
    """配置管理器"""

    def __init__(self, env: Environment = Environment.DEVELOPMENT):
        self.env = env
        self.config_dir = Path(__file__).parent
        self.root_dir = self.config_dir.parent
        self._encryption_key: Optional[Fernet] = None

        # 加载配置
        self._load_config()

    def _load_config(self):
        """加载配置"""
        try:
            # 加载基础配置
            config_file = self.config_dir / f"{self.env.value}.json"
            if not config_file.exists():
                raise FileNotFoundError(f"配置文件不存在: {config_file}")

            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)

            # 初始化各配置模块
            self.zhipu_ai = ZhipuAISettings(**config_data.get("zhipu_ai", {}))
            self.security = SecuritySettings(**config_data.get("security", {}))
            self.database = DatabaseSettings(**config_data.get("database", {}))
            self.cache = CacheSettings(**config_data.get("cache", {}))
            self.logging = LoggingSettings(**config_data.get("logging", {}))

            # 验证配置
            self._validate_config()

            logger.info(f"成功加载{self.env.value}环境配置")

        except Exception as e:
            logger.error(f"加载配置失败: {e}")
            raise

    def _validate_config(self):
        """验证配置"""
        errors = []

        # 验证必需的配置
        if not self.zhipu_ai.api_key:
            errors.append("智谱AI API密钥未配置")

        if not self.database.host:
            errors.append("数据库主机未配置")

        if self.env == Environment.PRODUCTION and not self.security.allowed_origins:
            errors.append("生产环境必须配置允许的来源")

        if errors:
            raise ValueError(f"配置验证失败: {', '.join(errors)}")

    @property
    def encryption_key(self) -> Fernet:
        """获取加密密钥"""
        if not self._encryption_key:
            key = self.security.encryption_key.encode()
            self._encryption_key = Fernet(key)
        return self._encryption_key

    def encrypt(self, data: str) -> str:
        """加密数据"""
        return self.encryption_key.encrypt(data.encode()).decode()

    def decrypt(self, encrypted_data: str) -> str:
        """解密数据"""
        return self.encryption_key.decrypt(encrypted_data.encode()).decode()

    def get_database_url(self) -> str:
        """获取数据库连接URL"""
        password = self.encrypt(self.database.password) if self.env == Environment.PRODUCTION else self.database.password
        return f"postgresql://{self.database.username}:{password}@{self.database.host}:{self.database.port}/{self.database.name}"

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "environment": self.env.value,
            "zhipu_ai": {
                "model_name": self.zhipu_ai.model_name,
                "max_retries": self.zhipu_ai.max_retries,
                "timeout": self.zhipu_ai.timeout,
                "rate_limit": self.zhipu_ai.rate_limit,
                "endpoint_url": self.zhipu_ai.endpoint_url,
                # API密钥在日志中隐藏
                "api_key": "***" if self.zhipu_ai.api_key else None
            },
            "security": {
                "allowed_origins": self.security.allowed_origins,
                "allowed_ips": self.security.allowed_ips,
                "session_timeout": self.security.session_timeout,
                "enable_audit_log": self.security.enable_audit_log
            },
            "database": {
                "host": self.database.host,
                "port": self.database.port,
                "name": self.database.name,
                "username": self.database.username,
                "ssl_mode": self.database.ssl_mode,
                "pool_size": self.database.pool_size,
                "max_overflow": self.database.max_overflow
                # 密码在日志中隐藏
            },
            "cache": {
                "host": self.cache.host,
                "port": self.cache.port,
                "db": self.cache.db,
                "ttl": self.cache.ttl
                # 密码在日志中隐藏
            },
            "logging": {
                "level": self.logging.level,
                "format": self.logging.format,
                "file_path": self.logging.file_path,
                "enable_audit": self.logging.enable_audit
            }
        }


class ConfigValidator:
    """配置验证器"""

    @staticmethod
    def validate_endpoint_url(url: str) -> bool:
        """验证端点URL格式"""
        return url.startswith(("https://", "http://"))

    @staticmethod
    def validate_ip_address(ip: str) -> bool:
        """验证IP地址格式"""
        parts = ip.split('.')
        if len(parts) != 4:
            return False
        try:
            return all(0 <= int(part) <= 255 for part in parts)
        except ValueError:
            return False

    @staticmethod
    def validate_rate_limit(rate_limit: int) -> bool:
        """验证速率限制"""
        return 1 <= rate_limit <= 10000


# 全局配置实例
config: Optional[ConfigManager] = None


def get_config(env: Optional[str] = None) -> ConfigManager:
    """获取配置实例"""
    global config

    if config is None or env:
        environment = Environment(env or os.getenv("ENVIRONMENT", "development"))
        config = ConfigManager(environment)

    return config


def init_config(env: str = "development"):
    """初始化配置"""
    global config
    config = ConfigManager(Environment(env))
    return config