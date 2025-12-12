"""
多环境管理模块
提供开发、测试、生产环境的统一管理
"""

import os
import sys
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
from enum import Enum
import json
import yaml

from .settings import Environment, ConfigManager, get_config
from .env_loader import EnvLoader

logger = logging.getLogger(__name__)


class EnvironmentManager:
    """环境管理器"""

    def __init__(self, root_dir: Optional[Path] = None):
        """
        初始化环境管理器

        Args:
            root_dir: 项目根目录
        """
        self.root_dir = root_dir or Path(__file__).parent.parent
        self.config_dir = self.root_dir / "config"
        self.env_loader = EnvLoader()
        self._current_env: Optional[Environment] = None

    def detect_environment(self) -> Environment:
        """
        检测当前环境

        Returns:
            当前环境
        """
        # 优先从环境变量获取
        env_str = os.getenv("ENVIRONMENT", "").lower()

        # 从命令行参数获取
        if not env_str and len(sys.argv) > 1:
            for arg in sys.argv[1:]:
                if arg.startswith("--env="):
                    env_str = arg.split("=")[1].lower()
                    break

        # 根据常见模式推断
        if not env_str:
            if "pytest" in sys.modules or "unittest" in sys.modules:
                env_str = "testing"
            elif os.getenv("DEBUG", "false").lower() == "true":
                env_str = "development"
            else:
                env_str = "production"

        # 验证环境名称
        try:
            env = Environment(env_str)
        except ValueError:
            logger.warning(f"无效的环境名称: {env_str}, 使用默认环境 development")
            env = Environment.DEVELOPMENT

        self._current_env = env
        logger.info(f"当前环境: {env.value}")
        return env

    def load_environment_config(self, env: Optional[Environment] = None) -> ConfigManager:
        """
        加载指定环境的配置

        Args:
            env: 环境枚举，默认使用当前检测的环境

        Returns:
            配置管理器实例
        """
        if env is None:
            env = self.detect_environment()

        # 加载环境变量
        self.env_loader.load()

        # 加载配置
        config = ConfigManager(env)

        # 应用环境特定设置
        self._apply_environment_overrides(config, env)

        return config

    def _apply_environment_overrides(self, config: ConfigManager, env: Environment) -> None:
        """
        应用环境特定的覆盖设置

        Args:
            config: 配置管理器
            env: 环境枚举
        """
        # 从环境变量加载覆盖值
        overrides = {}

        # API配置覆盖
        if api_key := os.getenv("ZHIPU_AI_API_KEY_OVERRIDE"):
            overrides["zhipu_ai"] = overrides.get("zhipu_ai", {})
            overrides["zhipu_ai"]["api_key"] = api_key

        # 数据库配置覆盖
        if db_url := os.getenv("DATABASE_URL_OVERRIDE"):
            # 解析数据库URL
            overrides["database"] = overrides.get("database", {})
            # 这里可以添加URL解析逻辑

        # 缓存配置覆盖
        if redis_url := os.getenv("REDIS_URL_OVERRIDE"):
            overrides["cache"] = overrides.get("cache", {})
            # 解析Redis URL

        # 应用覆盖
        if overrides:
            self._apply_overrides(config, overrides)

    def _apply_overrides(self, config: ConfigManager, overrides: Dict[str, Any]) -> None:
        """
        应用配置覆盖

        Args:
            config: 配置管理器
            overrides: 覆盖配置字典
        """
        for section, values in overrides.items():
            if hasattr(config, section):
                config_section = getattr(config, section)
                for key, value in values.items():
                    if hasattr(config_section, key):
                        setattr(config_section, key, value)
                        logger.info(f"应用配置覆盖: {section}.{key} = {value}")

    def list_available_environments(self) -> List[str]:
        """
        列出可用的环境

        Returns:
            环境列表
        """
        environments = []
        for env in Environment:
            config_file = self.config_dir / f"{env.value}.json"
            if config_file.exists():
                environments.append(env.value)
        return environments

    def validate_environment(self, env: Environment) -> bool:
        """
        验证环境配置是否完整

        Args:
            env: 环境枚举

        Returns:
            是否验证通过
        """
        try:
            config_file = self.config_dir / f"{env.value}.json"
            if not config_file.exists():
                logger.error(f"环境配置文件不存在: {config_file}")
                return False

            # 加载并验证配置
            config = self.load_environment_config(env)
            return True

        except Exception as e:
            logger.error(f"环境验证失败: {e}")
            return False

    def switch_environment(self, env: Environment) -> bool:
        """
        切换环境

        Args:
            env: 目标环境

        Returns:
            是否切换成功
        """
        try:
            # 验证目标环境
            if not self.validate_environment(env):
                return False

            # 设置环境变量
            os.environ["ENVIRONMENT"] = env.value

            # 重新加载配置
            self._current_env = env
            config = self.load_environment_config(env)

            logger.info(f"成功切换到环境: {env.value}")
            return True

        except Exception as e:
            logger.error(f"切换环境失败: {e}")
            return False

    def export_environment_config(self, env: Environment, format: str = "yaml") -> str:
        """
        导出环境配置

        Args:
            env: 环境枚举
            format: 导出格式 (yaml, json)

        Returns:
            配置字符串
        """
        config = self.load_environment_config(env)
        config_dict = config.to_dict()

        if format.lower() == "yaml":
            return yaml.dump(config_dict, default_flow_style=False, allow_unicode=True)
        else:
            return json.dumps(config_dict, indent=2, ensure_ascii=False)

    def import_environment_config(self, env: Environment, config_str: str, format: str = "yaml") -> bool:
        """
        导入环境配置

        Args:
            env: 环境枚举
            config_str: 配置字符串
            format: 配置格式 (yaml, json)

        Returns:
            是否导入成功
        """
        try:
            # 解析配置
            if format.lower() == "yaml":
                config_dict = yaml.safe_load(config_str)
            else:
                config_dict = json.loads(config_str)

            # 保存配置文件
            config_file = self.config_dir / f"{env.value}.json"
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, indent=2, ensure_ascii=False)

            logger.info(f"成功导入{env.value}环境配置")
            return True

        except Exception as e:
            logger.error(f"导入配置失败: {e}")
            return False

    def create_environment_template(self, env: Environment, source_env: Optional[Environment] = None) -> bool:
        """
        创建环境配置模板

        Args:
            env: 目标环境
            source_env: 源环境（用于复制配置）

        Returns:
            是否创建成功
        """
        try:
            if source_env:
                # 从源环境复制配置
                source_config = self.load_environment_config(source_env)
                config_dict = source_config.to_dict()
            else:
                # 创建空模板
                config_dict = {
                    "zhipu_ai": {
                        "api_key": "",
                        "endpoint_url": "https://open.bigmodel.cn/api/paas/v4/chat/completions",
                        "model_name": "glm-4.6",
                        "max_retries": 3,
                        "timeout": 30,
                        "rate_limit": 100
                    },
                    "security": {
                        "encryption_key": "",
                        "allowed_origins": [],
                        "allowed_ips": [],
                        "session_timeout": 3600
                    },
                    "database": {
                        "host": "",
                        "port": 5432,
                        "name": "",
                        "username": "",
                        "password": "",
                        "ssl_mode": "require"
                    },
                    "cache": {
                        "host": "localhost",
                        "port": 6379,
                        "db": 0,
                        "ttl": 3600
                    },
                    "logging": {
                        "level": "INFO",
                        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                        "enable_audit": True
                    }
                }

            # 保存配置文件
            config_file = self.config_dir / f"{env.value}.json"
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, indent=2, ensure_ascii=False)

            logger.info(f"成功创建{env.value}环境配置模板")
            return True

        except Exception as e:
            logger.error(f"创建环境模板失败: {e}")
            return False

    def compare_environments(self, env1: Environment, env2: Environment) -> Dict[str, Any]:
        """
        比较两个环境的配置

        Args:
            env1: 环境1
            env2: 环境2

        Returns:
            比较结果字典
        """
        config1 = self.load_environment_config(env1)
        config2 = self.load_environment_config(env2)

        dict1 = config1.to_dict()
        dict2 = config2.to_dict()

        differences = {}
        for key in dict1:
            if key not in dict2:
                differences[key] = {"only_in": env1.value}
            elif dict1[key] != dict2[key]:
                differences[key] = {
                    env1.value: dict1[key],
                    env2.value: dict2[key]
                }

        for key in dict2:
            if key not in dict1:
                differences[key] = {"only_in": env2.value}

        return differences


# 全局环境管理器实例
env_manager = EnvironmentManager()