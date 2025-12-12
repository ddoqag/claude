#!/usr/bin/env python3
"""
智谱AI编码端点示例应用
演示如何使用配置系统
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# 添加config目录到Python路径
config_dir = Path(__file__).parent / "config"
sys.path.insert(0, str(config_dir))

from config import get_config, init_config
from config.security import SecureConfig


def setup_logging(config):
    """设置日志"""
    logging.basicConfig(
        level=getattr(logging, config.logging.level),
        format=config.logging.format,
        handlers=[
            logging.FileHandler(config.logging.file_path or "app.log"),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger(__name__)
    logger.info(f"日志系统初始化完成，级别: {config.logging.level}")
    return logger


async def test_zhipu_ai_api(config, logger):
    """测试智谱AI API"""
    logger.info("测试智谱AI API连接...")

    # 这里应该调用实际的API
    # 示例仅演示如何使用配置
    api_config = config.zhipu_ai
    logger.info(f"API端点: {api_config.endpoint_url}")
    logger.info(f"模型: {api_config.model_name}")
    logger.info(f"超时: {api_config.timeout}秒")
    logger.info(f"速率限制: {api_config.rate_limit}/分钟")

    # 模拟API调用
    import time
    time.sleep(1)  # 模拟网络延迟
    logger.info("✅ API测试完成（模拟）")


def test_database_connection(config, logger):
    """测试数据库连接"""
    logger.info("测试数据库连接...")

    db_config = config.database
    logger.info(f"数据库: {db_config.host}:{db_config.port}/{db_config.name}")
    logger.info(f"SSL模式: {db_config.ssl_mode}")
    logger.info(f"连接池大小: {db_config.pool_size}")

    try:
        import psycopg2
        conn = psycopg2.connect(
            host=db_config.host,
            port=db_config.port,
            database=db_config.name,
            user=db_config.username,
            password=db_config.password,
            sslmode=db_config.ssl_mode,
            connect_timeout=5
        )
        logger.info("✅ 数据库连接成功")
        conn.close()
    except ImportError:
        logger.warning("psycopg2未安装，跳过数据库连接测试")
    except Exception as e:
        logger.error(f"❌ 数据库连接失败: {e}")


def test_cache_connection(config, logger):
    """测试缓存连接"""
    logger.info("测试缓存连接...")

    cache_config = config.cache
    logger.info(f"缓存: {cache_config.host}:{cache_config.port}/{cache_config.db}")

    try:
        import redis
        r = redis.Redis(
            host=cache_config.host,
            port=cache_config.port,
            db=cache_config.db,
            password=cache_config.password,
            socket_connect_timeout=5
        )
        if r.ping():
            logger.info("✅ 缓存连接成功")
        r.close()
    except ImportError:
        logger.warning("redis未安装，跳过缓存连接测试")
    except Exception as e:
        logger.error(f"❌ 缓存连接失败: {e}")


def test_security_features(config, logger):
    """测试安全功能"""
    logger.info("测试安全功能...")

    secure = SecureConfig()

    # 测试加密
    test_data = "这是敏感测试数据"
    encrypted = secure.encrypt(test_data)
    decrypted = secure.decrypt(encrypted)

    if test_data == decrypted:
        logger.info("✅ 加密/解密功能正常")
    else:
        logger.error("❌ 加密/解密功能异常")

    # 测试密码哈希
    password = "test123"
    hash_val, salt = secure.hash_password(password)
    if secure.verify_password(password, hash_val, salt):
        logger.info("✅ 密码哈希功能正常")
    else:
        logger.error("❌ 密码哈希功能异常")


async def main():
    """主函数"""
    print("=" * 60)
    print("智谱AI编码端点示例应用")
    print("=" * 60)

    # 检测环境
    env = os.getenv("ENVIRONMENT", "development")
    print(f"\n当前环境: {env.upper()}")

    try:
        # 初始化配置
        config = init_config(env)
        print("✅ 配置加载成功")

        # 设置日志
        logger = setup_logging(config)

        # 运行测试
        print("\n🔍 运行系统测试...")
        await test_zhipu_ai_api(config, logger)
        test_database_connection(config, logger)
        test_cache_connection(config, logger)
        test_security_features(config, logger)

        # 显示配置摘要
        print("\n📊 配置摘要:")
        print(f"- 智谱AI模型: {config.zhipu_ai.model_name}")
        print(f"- 数据库: {config.database.host}:{config.database.port}/{config.database.name}")
        print(f"- 缓存: {config.cache.host}:{config.cache.port}/{config.cache.db}")
        print(f"- 会话超时: {config.security.session_timeout}秒")
        print(f"- 审计日志: {'启用' if config.security.enable_audit_log else '禁用'}")

        print("\n✅ 示例应用运行完成！")

    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    # 运行示例应用
    asyncio.run(main())