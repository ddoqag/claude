#!/usr/bin/env python3
"""
智谱AI编码端点环境设置脚本
自动化环境初始化和配置
"""

import os
import sys
import json
import secrets
import argparse
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional

# 添加config目录到Python路径
config_dir = Path(__file__).parent.parent / "config"
sys.path.insert(0, str(config_dir))

from security import SecureConfig
from validator import ConfigValidator, ValidationResult
from env_loader import EnvLoader
from environment import EnvironmentManager, Environment


class EnvironmentSetup:
    """环境设置器"""

    def __init__(self):
        """初始化设置器"""
        self.root_dir = Path(__file__).parent.parent
        self.config_dir = self.root_dir / "config"
        self.env_manager = EnvironmentManager(self.root_dir)
        self.secure_config = SecureConfig()
        self.validator = ConfigValidator()

    def setup_environment(self, env_name: str, interactive: bool = False) -> bool:
        """
        设置环境

        Args:
            env_name: 环境名称
            interactive: 是否交互式设置

        Returns:
            是否成功
        """
        try:
            env = Environment(env_name.lower())
            print(f"\n=== 设置 {env.value.upper()} 环境 ===")

            # 检查环境是否已存在
            config_file = self.config_dir / f"{env.value}.json"
            if config_file.exists() and not interactive:
                overwrite = input(f"环境 {env.value} 已存在，是否覆盖？(y/N): ")
                if overwrite.lower() != 'y':
                    print("设置已取消")
                    return False

            # 收集配置信息
            if interactive:
                config_data = self._collect_config_interactive(env)
            else:
                config_data = self._generate_default_config(env)

            # 保存配置
            if self._save_config(env, config_data):
                print(f"\n✅ {env.value.upper()} 环境设置成功！")
                self._print_next_steps(env)
                return True
            else:
                print(f"\n❌ {env.value.upper()} 环境设置失败！")
                return False

        except ValueError as e:
            print(f"❌ 无效的环境名称: {e}")
            return False
        except Exception as e:
            print(f"❌ 设置过程中发生错误: {e}")
            return False

    def _collect_config_interactive(self, env: Environment) -> Dict[str, Any]:
        """交互式收集配置"""
        print("\n请输入配置信息（直接回车使用默认值）：")

        config = {}

        # 智谱AI配置
        print("\n--- 智谱AI配置 ---")
        config["zhipu_ai"] = {
            "api_key": input("API密钥: ").strip() or "",
            "endpoint_url": input("端点URL (默认: https://open.bigmodel.cn/api/paas/v4/chat/completions): ").strip() or "https://open.bigmodel.cn/api/paas/v4/chat/completions",
            "model_name": input("模型名称 (默认: glm-4.6): ").strip() or "glm-4.6",
            "max_retries": int(input("最大重试次数 (默认: 3): ").strip() or "3"),
            "timeout": int(input("超时时间(秒) (默认: 30): ").strip() or "30"),
            "rate_limit": int(input("速率限制(每分钟) (默认: 100): ").strip() or "100")
        }

        # 安全配置
        print("\n--- 安全配置 ---")
        encryption_key = self.secure_config.generate_key()
        jwt_secret = self.secure_config.generate_token(64)

        config["security"] = {
            "encryption_key": encryption_key,
            "jwt_secret": jwt_secret,
            "allowed_origins": input("允许的来源（逗号分隔，默认: http://localhost:3000): ").strip() or "http://localhost:3000",
            "allowed_ips": input("允许的IP（逗号分隔，默认: 127.0.0.1): ").strip() or "127.0.0.1",
            "session_timeout": int(input("会话超时时间(秒) (默认: 3600): ").strip() or "3600"),
            "enable_audit_log": input("启用审计日志 (y/N): ").strip().lower() == 'y'
        }

        # 数据库配置
        print("\n--- 数据库配置 ---")
        config["database"] = {
            "host": input("数据库主机 (默认: localhost): ").strip() or "localhost",
            "port": int(input("端口 (默认: 5432): ").strip() or "5432"),
            "name": input(f"数据库名 (默认: zhipu_ai_{env.value}): ").strip() or f"zhipu_ai_{env.value}",
            "username": input("用户名: ").strip() or "zhipu_user",
            "password": input("密码: ").strip() or "",
            "ssl_mode": input("SSL模式 (prefer/require/disable) (默认: prefer): ").strip() or "prefer",
            "pool_size": int(input("连接池大小 (默认: 5): ").strip() or "5"),
            "max_overflow": int(input("最大溢出连接 (默认: 10): ").strip() or "10")
        }

        # 缓存配置
        print("\n--- 缓存配置 ---")
        config["cache"] = {
            "host": input("缓存主机 (默认: localhost): ").strip() or "localhost",
            "port": int(input("端口 (默认: 6379): ").strip() or "6379"),
            "db": int(input("数据库索引 (默认: 0): ").strip() or "0"),
            "password": input("密码（可选）: ").strip() or None,
            "ttl": int(input("缓存TTL(秒) (默认: 3600): ").strip() or "3600")
        }

        # 日志配置
        print("\n--- 日志配置 ---")
        config["logging"] = {
            "level": input("日志级别 (DEBUG/INFO/WARNING/ERROR) (默认: INFO): ").strip() or "INFO",
            "file_path": input("日志文件路径 (默认: ./logs/app.log): ").strip() or "./logs/app.log",
            "enable_audit": input("启用审计日志 (y/N): ").strip().lower() == 'y',
            "audit_file_path": input("审计日志路径 (默认: ./logs/audit.log): ").strip() or "./logs/audit.log"
        }

        return config

    def _generate_default_config(self, env: Environment) -> Dict[str, Any]:
        """生成默认配置"""
        encryption_key = self.secure_config.generate_key()
        jwt_secret = self.secure_config.generate_token(64)

        base_config = {
            "zhipu_ai": {
                "api_key": "",
                "endpoint_url": "https://open.bigmodel.cn/api/paas/v4/chat/completions",
                "model_name": "glm-4.6",
                "max_retries": 3,
                "timeout": 30,
                "rate_limit": 100
            },
            "security": {
                "encryption_key": encryption_key,
                "jwt_secret": jwt_secret,
                "allowed_origins": ["http://localhost:3000"],
                "allowed_ips": ["127.0.0.1"],
                "session_timeout": 3600,
                "enable_audit_log": True
            },
            "database": {
                "host": "localhost",
                "port": 5432,
                "name": f"zhipu_ai_{env.value}",
                "username": "zhipu_user",
                "password": "",
                "ssl_mode": "prefer",
                "pool_size": 5,
                "max_overflow": 10
            },
            "cache": {
                "host": "localhost",
                "port": 6379,
                "db": 0,
                "password": None,
                "ttl": 3600
            },
            "logging": {
                "level": "INFO",
                "file_path": f"./logs/{env.value}.log",
                "enable_audit": True,
                "audit_file_path": f"./logs/{env.value}_audit.log"
            }
        }

        # 环境特定调整
        if env == Environment.PRODUCTION:
            base_config["security"]["allowed_origins"] = ["https://api.example.com"]
            base_config["security"]["allowed_ips"] = ["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"]
            base_config["security"]["session_timeout"] = 7200
            base_config["database"]["ssl_mode"] = "require"
            base_config["database"]["pool_size"] = 20
            base_config["database"]["max_overflow"] = 30
            base_config["cache"]["ttl"] = 7200
            base_config["logging"]["level"] = "WARNING"

        elif env == Environment.TESTING:
            base_config["zhipu_ai"]["max_retries"] = 2
            base_config["zhipu_ai"]["timeout"] = 15
            base_config["zhipu_ai"]["rate_limit"] = 50
            base_config["security"]["session_timeout"] = 1800
            base_config["database"]["ssl_mode"] = "require"
            base_config["database"]["pool_size"] = 3
            base_config["database"]["max_overflow"] = 5
            base_config["cache"]["ttl"] = 60

        return base_config

    def _save_config(self, env: Environment, config_data: Dict[str, Any]) -> bool:
        """保存配置"""
        try:
            # 创建必要的目录
            log_dir = self.root_dir / "logs"
            log_dir.mkdir(exist_ok=True)

            # 保存配置文件
            config_file = self.config_dir / f"{env.value}.json"
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)

            # 验证配置
            validation_result = self._validate_config(config_data)
            if not validation_result.is_valid:
                print("\n⚠️  警告：配置存在以下问题：")
                for error in validation_result.errors:
                    print(f"  - [{error.severity.value.upper()}] {error.field}: {error.message}")

                if validation_result.get_errors_by_severity(ValidationSeverity.ERROR):
                    print("\n❌ 配置验证失败，请修复错误后重试")
                    config_file.unlink()  # 删除无效配置
                    return False

            return True

        except Exception as e:
            print(f"保存配置失败: {e}")
            return False

    def _validate_config(self, config_data: Dict[str, Any]) -> ValidationResult:
        """验证配置"""
        # 创建验证模式
        schema = {
            "zhipu_ai": {
                "type": "object",
                "required": True,
                "properties": {
                    "api_key": {"type": "string", "required": True, "validators": ["api_key"]},
                    "endpoint_url": {"type": "string", "required": True, "validators": ["url"]},
                    "model_name": {"type": "string", "required": True},
                    "max_retries": {"type": "integer", "min": 0, "max": 10},
                    "timeout": {"type": "number", "validators": ["timeout"]},
                    "rate_limit": {"type": "integer", "validators": ["rate_limit"]}
                }
            },
            "security": {
                "type": "object",
                "required": True,
                "properties": {
                    "encryption_key": {"type": "string", "required": True, "validators": ["encryption_key"]},
                    "jwt_secret": {"type": "string", "required": True},
                    "allowed_origins": {"type": "array", "required": True},
                    "allowed_ips": {"type": "array", "validators": ["ip"]},
                    "session_timeout": {"type": "integer", "min": 0},
                    "enable_audit_log": {"type": "boolean"}
                }
            },
            "database": {
                "type": "object",
                "required": True,
                "properties": {
                    "host": {"type": "string", "required": True},
                    "port": {"type": "integer", "validators": ["port"]},
                    "name": {"type": "string", "required": True},
                    "username": {"type": "string", "required": True},
                    "password": {"type": "string", "required": True},
                    "ssl_mode": {"type": "string", "enum": ["disable", "allow", "prefer", "require", "verify-ca", "verify-full"], "validators": ["ssl_mode"]},
                    "pool_size": {"type": "integer", "min": 1, "max": 100},
                    "max_overflow": {"type": "integer", "min": 0}
                }
            },
            "cache": {
                "type": "object",
                "required": True,
                "properties": {
                    "host": {"type": "string", "required": True},
                    "port": {"type": "integer", "validators": ["port"]},
                    "db": {"type": "integer", "min": 0, "max": 15},
                    "ttl": {"type": "integer", "min": 0}
                }
            },
            "logging": {
                "type": "object",
                "required": True,
                "properties": {
                    "level": {"type": "string", "validators": ["log_level"]},
                    "file_path": {"type": "string", "required": True},
                    "enable_audit": {"type": "boolean"}
                }
            }
        }

        # 执行验证
        return self.validator.validate(config_data, schema)

    def _print_next_steps(self, env: Environment):
        """打印后续步骤"""
        print("\n📋 后续步骤：")
        print(f"\n1. 配置环境变量")
        print("   创建 .env 文件并添加以下内容：")
        print(f"   ENVIRONMENT={env.value}")
        print("   ZHIPU_AI_API_KEY=your_actual_api_key")
        print("   DB_PASSWORD=your_database_password")
        print("\n2. 安装依赖")
        print("   pip install -r requirements.txt")
        print("\n3. 运行应用")
        print("   python app.py")
        print("\n4. 测试配置")
        print(f"   python scripts/test_config.py --env {env.value}")

    def create_env_file(self, env: Environment):
        """创建环境变量文件"""
        env_file = self.root_dir / ".env.example"
        env_content = f"""# 智谱AI编码端点环境变量配置
ENVIRONMENT={env.value}

# 智谱AI API配置
ZHIPU_AI_API_KEY=your_api_key_here

# 数据库配置
DB_PASSWORD=your_db_password_here

# 缓存配置（可选）
REDIS_PASSWORD=your_redis_password_here

# 应用配置
APP_PORT=8080
APP_DEBUG={'true' if env == Environment.DEVELOPMENT else 'false'}
"""

        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(env_content)

        print(f"✅ 已创建环境变量模板文件: {env_file}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="智谱AI编码端点环境设置工具")
    parser.add_argument("env", choices=["development", "testing", "staging", "production"],
                        help="要设置的环境")
    parser.add_argument("-i", "--interactive", action="store_true",
                        help="交互式设置")
    parser.add_argument("--create-env", action="store_true",
                        help="创建环境变量文件")

    args = parser.parse_args()

    # 创建设置器
    setup = EnvironmentSetup()

    # 设置环境
    success = setup.setup_environment(args.env, args.interactive)

    # 创建环境变量文件
    if success and args.create_env:
        env = Environment(args.env)
        setup.create_env_file(env)

    # 返回适当的退出码
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()