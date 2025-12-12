#!/usr/bin/env python3
"""
配置测试脚本
用于验证配置是否正确加载和工作
"""

import sys
import json
import argparse
from pathlib import Path

# 添加config目录到Python路径
config_dir = Path(__file__).parent.parent / "config"
sys.path.insert(0, str(config_dir))

from settings import get_config, init_config
from environment import EnvironmentManager, Environment
from validator import ConfigValidator
from security import SecureConfig


def test_config_loading(env_name):
    """测试配置加载"""
    print(f"\n=== 测试 {env_name.upper()} 环境配置加载 ===\n")

    try:
        # 初始化配置
        config = init_config(env_name)
        print("✅ 配置加载成功")

        # 显示配置（隐藏敏感信息）
        print("\n配置摘要:")
        config_dict = config.to_dict()
        print(json.dumps(config_dict, indent=2, ensure_ascii=False))

        return True, None

    except Exception as e:
        error_msg = f"配置加载失败: {e}"
        print(f"❌ {error_msg}")
        return False, error_msg


def test_config_validation(env_name):
    """测试配置验证"""
    print(f"\n=== 测试 {env_name.upper()} 环境配置验证 ===\n")

    try:
        # 加载配置
        config_manager = EnvironmentManager()
        config = config_manager.load_environment_config(Environment(env_name))
        config_dict = config.to_dict()

        # 创建验证器
        validator = ConfigValidator()

        # 验证模式
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
                    "session_timeout": {"type": "integer", "min": 0}
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
                    "ssl_mode": {"type": "string", "enum": ["disable", "allow", "prefer", "require", "verify-ca", "verify-full"]},
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
            }
        }

        # 执行验证
        result = validator.validate(config_dict, schema)

        if result.is_valid:
            print("✅ 配置验证通过")
        else:
            print("❌ 配置验证失败:")
            for error in result.errors:
                print(f"  - [{error.severity.value.upper()}] {error.field}: {error.message}")

        return result.is_valid, result

    except Exception as e:
        error_msg = f"配置验证失败: {e}"
        print(f"❌ {error_msg}")
        return False, error_msg


def test_security_features():
    """测试安全功能"""
    print("\n=== 测试安全功能 ===\n")

    try:
        secure_config = SecureConfig()

        # 测试加密/解密
        test_data = "这是敏感数据"
        encrypted = secure_config.encrypt(test_data)
        decrypted = secure_config.decrypt(encrypted)

        if test_data == decrypted:
            print("✅ 加密/解密功能正常")
        else:
            print("❌ 加密/解密功能异常")
            return False

        # 测试密码哈希
        password = "test123"
        password_hash, salt = secure_config.hash_password(password)
        if secure_config.verify_password(password, password_hash, salt):
            print("✅ 密码哈希/验证功能正常")
        else:
            print("❌ 密码哈希/验证功能异常")
            return False

        # 测试令牌生成
        token = secure_config.generate_token()
        if len(token) > 30:
            print(f"✅ 令牌生成功能正常 (长度: {len(token)})")
        else:
            print("❌ 令牌生成功能异常")
            return False

        return True, None

    except Exception as e:
        error_msg = f"安全功能测试失败: {e}"
        print(f"❌ {error_msg}")
        return False, error_msg


def test_database_connection(config):
    """测试数据库连接"""
    print("\n=== 测试数据库连接 ===\n")

    try:
        import psycopg2
        from psycopg2.extras import execute_batch

        # 获取数据库配置
        db_config = config.database

        # 尝试连接
        conn = psycopg2.connect(
            host=db_config.host,
            port=db_config.port,
            database=db_config.name,
            user=db_config.username,
            password=db_config.password,
            sslmode=db_config.ssl_mode,
            connect_timeout=5
        )

        print("✅ 数据库连接成功")

        # 测试查询
        with conn.cursor() as cursor:
            cursor.execute("SELECT version()")
            version = cursor.fetchone()[0]
            print(f"\n数据库版本: {version[:50]}...")

        conn.close()
        return True, None

    except ImportError:
        print("⚠️  psycopg2未安装，跳过数据库连接测试")
        return True, None
    except Exception as e:
        error_msg = f"数据库连接失败: {e}"
        print(f"❌ {error_msg}")
        return False, error_msg


def test_cache_connection(config):
    """测试缓存连接"""
    print("\n=== 测试缓存连接 ===\n")

    try:
        import redis

        # 获取缓存配置
        cache_config = config.cache

        # 尝试连接
        r = redis.Redis(
            host=cache_config.host,
            port=cache_config.port,
            db=cache_config.db,
            password=cache_config.password,
            socket_connect_timeout=5
        )

        # 测试ping
        if r.ping():
            print("✅ Redis缓存连接成功")

            # 测试读写
            test_key = "test_key"
            test_value = "test_value"
            r.set(test_key, test_value, ex=10)
            retrieved = r.get(test_key)

            if retrieved and retrieved.decode() == test_value:
                print("✅ 缓存读写测试成功")
            else:
                print("❌ 缓存读写测试失败")
                return False, "缓存读写失败"
        else:
            print("❌ Redis缓存连接失败")
            return False, "Redis ping失败"

        r.close()
        return True, None

    except ImportError:
        print("⚠️  redis未安装，跳过缓存连接测试")
        return True, None
    except Exception as e:
        error_msg = f"缓存连接失败: {e}"
        print(f"❌ {error_msg}")
        return False, error_msg


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="配置测试工具")
    parser.add_argument("--env", default="development",
                        choices=["development", "testing", "staging", "production"],
                        help="要测试的环境")
    parser.add_argument("--skip-db", action="store_true",
                        help="跳过数据库连接测试")
    parser.add_argument("--skip-cache", action="store_true",
                        help="跳过缓存连接测试")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="显示详细输出")

    args = parser.parse_args()

    print("=" * 50)
    print("智谱AI编码端点配置测试")
    print("=" * 50)

    results = []

    # 测试配置加载
    success, error = test_config_loading(args.env)
    results.append(("配置加载", success, error))

    if not success:
        print("\n❌ 配置加载失败，终止测试")
        sys.exit(1)

    # 获取配置对象
    config = get_config(args.env)

    # 测试配置验证
    success, result = test_config_validation(args.env)
    results.append(("配置验证", success, result if not success else None))

    # 测试安全功能
    success, error = test_security_features()
    results.append(("安全功能", success, error))

    # 测试数据库连接
    if not args.skip_db:
        success, error = test_database_connection(config)
        results.append(("数据库连接", success, error))

    # 测试缓存连接
    if not args.skip_cache:
        success, error = test_cache_connection(config)
        results.append(("缓存连接", success, error))

    # 输出测试结果摘要
    print("\n" + "=" * 50)
    print("测试结果摘要")
    print("=" * 50)

    all_passed = True
    for test_name, success, error in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{test_name:20} {status}")
        if not success and error and args.verbose:
            print(f"  错误: {error}")
        if not success:
            all_passed = False

    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 所有测试通过！")
        sys.exit(0)
    else:
        print("❌ 部分测试失败，请检查配置")
        sys.exit(1)


if __name__ == "__main__":
    main()