"""
工具函数单元测试
"""

import pytest
import asyncio
import json
import os
from unittest.mock import Mock, patch, mock_open
from datetime import datetime, timedelta
import tempfile
from typing import Dict, Any, List


class TestConfigManager:
    """配置管理器测试"""

    @pytest.fixture
    def sample_config(self):
        """示例配置"""
        return {
            "api": {
                "endpoint": "https://open.bigmodel.cn/api/paas/v4",
                "key": "test_api_key",
                "model": "codegeex4",
                "timeout": 30
            },
            "features": {
                "code_completion": True,
                "code_explanation": True,
                "debug_mode": False
            },
            "limits": {
                "max_tokens": 2000,
                "rate_limit": 100,
                "concurrent_requests": 5
            }
        }

    def test_load_config_from_file(self, sample_config):
        """测试从文件加载配置"""
        with patch("builtins.open", mock_open(read_data=json.dumps(sample_config))):
            from utils.config_manager import ConfigManager
            manager = ConfigManager("test_config.json")
            config = manager.load()

            assert config["api"]["endpoint"] == sample_config["api"]["endpoint"]
            assert config["api"]["model"] == sample_config["api"]["model"]
            assert config["features"]["code_completion"] is True

    def test_save_config_to_file(self, sample_config):
        """测试保存配置到文件"""
        with patch("builtins.open", mock_open()) as mock_file:
            with patch("json.dump") as mock_dump:
                from utils.config_manager import ConfigManager
                manager = ConfigManager("test_config.json")
                manager.save(sample_config)

                mock_file.assert_called_once_with("test_config.json", "w", encoding="utf-8")
                mock_dump.assert_called_once()

    def test_get_nested_config_value(self, sample_config):
        """测试获取嵌套配置值"""
        with patch("builtins.open", mock_open(read_data=json.dumps(sample_config))):
            from utils.config_manager import ConfigManager
            manager = ConfigManager("test_config.json")
            manager.load()

            # 测试获取嵌套值
            api_key = manager.get("api.key")
            assert api_key == "test_api_key"

            # 测试获取不存在的键
            default_value = manager.get("nonexistent.key", "default")
            assert default_value == "default"

    def test_set_nested_config_value(self, sample_config):
        """测试设置嵌套配置值"""
        with patch("builtins.open", mock_open(read_data=json.dumps(sample_config))):
            with patch("json.dump") as mock_dump:
                from utils.config_manager import ConfigManager
                manager = ConfigManager("test_config.json")
                manager.load()

                # 设置新值
                manager.set("api.timeout", 60)
                manager.set("new_section.new_key", "new_value")

                # 验证配置已更新
                assert manager.config["api"]["timeout"] == 60
                assert manager.config["new_section"]["new_key"] == "new_value"

    def test_validate_config_schema(self, sample_config):
        """测试配置模式验证"""
        from utils.config_manager import ConfigManager

        schema = {
            "type": "object",
            "required": ["api"],
            "properties": {
                "api": {
                    "type": "object",
                    "required": ["endpoint", "key"],
                    "properties": {
                        "endpoint": {"type": "string"},
                        "key": {"type": "string"}
                    }
                }
            }
        }

        manager = ConfigManager("test_config.json")
        manager.config = sample_config

        # 有效配置
        is_valid = manager.validate(schema)
        assert is_valid is True

        # 无效配置（缺少必需字段）
        manager.config["api"].pop("key")
        is_valid = manager.validate(schema)
        assert is_valid is False


class TestLogger:
    """日志记录器测试"""

    @pytest.fixture
    def log_file(self):
        """临时日志文件"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            yield f.name
        os.unlink(f.name)

    def test_logger_initialization(self, log_file):
        """测试日志记录器初始化"""
        from utils.logger import Logger

        logger = Logger(
            name="test_logger",
            level="INFO",
            file_path=log_file
        )

        assert logger.name == "test_logger"
        assert logger.level == 20  # INFO level
        assert logger.file_path == log_file

    def test_log_levels(self, log_file):
        """测试不同日志级别"""
        from utils.logger import Logger

        logger = Logger(name="test", file_path=log_file)

        # 测试各级别日志
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        logger.critical("Critical message")

        # 验证日志文件
        with open(log_file, 'r') as f:
            content = f.read()
            assert "Info message" in content
            assert "Warning message" in content
            assert "Error message" in content
            assert "Critical message" in content
            # Debug消息默认不显示
            assert "Debug message" not in content

    def test_log_rotation(self, log_file):
        """测试日志轮转"""
        from utils.logger import Logger

        # 设置小的最大文件大小以触发轮转
        logger = Logger(
            name="test",
            file_path=log_file,
            max_bytes=100,
            backup_count=3
        )

        # 写入足够的日志以触发轮转
        for i in range(20):
            logger.info(f"This is log message number {i} with some additional text")

        # 验证备份文件存在
        backup_file = f"{log_file}.1"
        assert os.path.exists(backup_file)

    def test_structured_logging(self, log_file):
        """测试结构化日志"""
        from utils.logger import Logger

        logger = Logger(name="test", file_path=log_file)

        # 使用额外参数记录结构化日志
        logger.info(
            "API request completed",
            extra={
                "endpoint": "/api/generate",
                "method": "POST",
                "status_code": 200,
                "duration_ms": 250
            }
        )

        with open(log_file, 'r') as f:
            content = f.read()
            assert "endpoint" in content
            assert "status_code" in content
            assert "250" in content


class TestTokenManager:
    """Token管理器测试"""

    def test_token_counting(self):
        """测试Token计数"""
        from utils.token_manager import TokenManager

        manager = TokenManager()

        # 简单文本
        count = manager.count_tokens("Hello world")
        assert count > 0

        # 代码片段
        code = """def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)"""
        count = manager.count_tokens(code)
        assert count > 10

    def test_token_limit_validation(self):
        """测试Token限制验证"""
        from utils.token_manager import TokenManager

        manager = TokenManager(max_tokens=1000)

        # 在限制内
        is_valid = manager.validate_token_limit("Short text")
        assert is_valid is True

        # 超出限制
        long_text = "word " * 200  # 创建长文本
        is_valid = manager.validate_token_limit(long_text)
        assert is_valid is False

    def test_token_usage_tracking(self):
        """测试Token使用量跟踪"""
        from utils.token_manager import TokenManager

        manager = TokenManager()

        # 记录使用量
        manager.record_usage(prompt_tokens=100, completion_tokens=50)
        manager.record_usage(prompt_tokens=200, completion_tokens=100)

        # 获取总使用量
        usage = manager.get_total_usage()
        assert usage["prompt_tokens"] == 300
        assert usage["completion_tokens"] == 150
        assert usage["total_tokens"] == 450

    def test_token_budget_management(self):
        """测试Token预算管理"""
        from utils.token_manager import TokenManager

        manager = TokenManager(budget_tokens=1000)

        # 检查预算
        has_budget = manager.check_budget(500)
        assert has_budget is True

        has_budget = manager.check_budget(1500)
        assert has_budget is False

        # 消耗预算
        manager.consume_budget(300)
        assert manager.get_remaining_budget() == 700

    def test_daily_token_reset(self):
        """测试每日Token重置"""
        from utils.token_manager import TokenManager
        from datetime import datetime, timedelta

        manager = TokenManager(daily_limit=1000)

        # 使用一些Token
        manager.record_usage(prompt_tokens=500, completion_tokens=200)
        assert manager.get_daily_usage() == 700

        # 模拟日期变更
        yesterday = datetime.now() - timedelta(days=1)
        manager.last_reset = yesterday

        # 检查是否重置
        if manager.should_reset_daily():
            manager.reset_daily_usage()

        assert manager.get_daily_usage() == 0


class TestCacheManager:
    """缓存管理器测试"""

    def test_cache_set_and_get(self):
        """测试缓存设置和获取"""
        from utils.cache_manager import CacheManager

        cache = CacheManager(max_size=100)

        # 设置缓存
        cache.set("key1", "value1")
        cache.set("key2", {"nested": "data"})

        # 获取缓存
        value1 = cache.get("key1")
        value2 = cache.get("key2")

        assert value1 == "value1"
        assert value2 == {"nested": "data"}

    def test_cache_expiration(self):
        """测试缓存过期"""
        from utils.cache_manager import CacheManager
        import time

        cache = CacheManager(default_ttl=1)  # 1秒过期

        # 设置缓存
        cache.set("test_key", "test_value")

        # 立即获取
        value = cache.get("test_key")
        assert value == "test_value"

        # 等待过期
        time.sleep(2)

        # 再次获取应该返回None
        value = cache.get("test_key")
        assert value is None

    def test_cache_lru_eviction(self):
        """测试LRU缓存淘汰"""
        from utils.cache_manager import CacheManager

        cache = CacheManager(max_size=3)

        # 填满缓存
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")

        # 访问key1使其成为最近使用
        cache.get("key1")

        # 添加新项，应该淘汰key2（最久未使用）
        cache.set("key4", "value4")

        assert cache.get("key1") == "value1"  # 仍在缓存
        assert cache.get("key2") is None      # 被淘汰
        assert cache.get("key4") == "value4"  # 新项

    def test_cache_clear(self):
        """测试缓存清理"""
        from utils.cache_manager import CacheManager

        cache = CacheManager()

        # 添加多个项
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")

        # 清空缓存
        cache.clear()

        # 验证所有项都被清除
        assert cache.get("key1") is None
        assert cache.get("key2") is None
        assert cache.get("key3") is None
        assert cache.size() == 0

    def test_cache_stats(self):
        """测试缓存统计"""
        from utils.cache_manager import CacheManager

        cache = CacheManager()

        # 添加和获取项
        cache.set("key1", "value1")
        cache.get("key1")
        cache.get("nonexistent_key")

        # 获取统计信息
        stats = cache.get_stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["hit_rate"] == 0.5


class TestRateLimiter:
    """速率限制器测试"""

    def test_rate_limit_basic(self):
        """测试基本速率限制"""
        from utils.rate_limiter import RateLimiter
        import time

        limiter = RateLimiter(max_requests=2, window_seconds=1)

        # 前两个请求应该通过
        assert limiter.is_allowed() is True
        assert limiter.is_allowed() is True

        # 第三个请求应该被限制
        assert limiter.is_allowed() is False

        # 等待窗口重置
        time.sleep(1.1)

        # 现在应该再次允许
        assert limiter.is_allowed() is True

    def test_rate_limit_multiple_keys(self):
        """测试多键速率限制"""
        from utils.rate_limiter import RateLimiter

        limiter = RateLimiter(max_requests=2, window_seconds=1)

        # 不同键应该有独立的限制
        assert limiter.is_allowed(key="user1") is True
        assert limiter.is_allowed(key="user1") is True
        assert limiter.is_allowed(key="user1") is False

        # 新键应该有自己的限制
        assert limiter.is_allowed(key="user2") is True

    def test_rate_limit_burst(self):
        """测试突发请求处理"""
        from utils.rate_limiter import RateLimiter

        limiter = RateLimiter(max_requests=10, window_seconds=1, burst_size=5)

        # 突发请求应该被允许
        for i in range(5):
            assert limiter.is_allowed() is True

        # 继续请求应该受速率限制
        for i in range(6):
            is_allowed = limiter.is_allowed()
            if i < 5:
                assert is_allowed is True
            else:
                # 第11个请求应该被限制
                assert is_allowed is False

    def test_rate_limit_stats(self):
        """测试速率限制统计"""
        from utils.rate_limiter import RateLimiter

        limiter = RateLimiter(max_requests=10, window_seconds=1)

        # 执行一些请求
        for i in range(5):
            limiter.is_allowed()

        # 尝试更多请求（会被限制）
        for i in range(10):
            limiter.is_allowed()

        # 获取统计信息
        stats = limiter.get_stats()
        assert stats["total_requests"] == 15
        assert stats["allowed_requests"] == 10
        assert stats["blocked_requests"] == 5


class TestValidators:
    """验证器测试"""

    def test_code_validator(self):
        """测试代码验证"""
        from utils.validators import CodeValidator

        validator = CodeValidator()

        # 有效Python代码
        is_valid = validator.validate_python("def hello(): return 'world'")
        assert is_valid is True

        # 无效Python代码
        is_valid = validator.validate_python("def hello( return 'world'")
        assert is_valid is False

        # 有效JavaScript代码
        is_valid = validator.validate_javascript("function hello() { return 'world'; }")
        assert is_valid is True

    def test_api_key_validator(self):
        """测试API密钥验证"""
        from utils.validators import APIKeyValidator

        validator = APIKeyValidator()

        # 有效API密钥
        is_valid = validator.validate("abc123.def456.ghi789")
        assert is_valid is True

        # 无效API密钥（太短）
        is_valid = validator.validate("short")
        assert is_valid is False

        # 无效API密钥（包含非法字符）
        is_valid = validator.validate("invalid@key")
        assert is_valid is False

    def test_input_sanitizer(self):
        """测试输入清理"""
        from utils.validators import InputSanitizer

        sanitizer = InputSanitizer()

        # 清理HTML标签
        clean = sanitizer.sanitize_html("<script>alert('xss')</script>Hello")
        assert "<script>" not in clean
        assert "Hello" in clean

        # 清理SQL注入
        clean = sanitizer.sanitize_sql("'; DROP TABLE users; --")
        assert "DROP" not in clean

    def test_path_validator(self):
        """测试路径验证"""
        from utils.validators import PathValidator

        validator = PathValidator()

        # 安全路径
        is_safe = validator.is_safe_path("/home/user/file.txt")
        assert is_safe is True

        # 危险路径（路径遍历）
        is_safe = validator.is_safe_path("../../../etc/passwd")
        assert is_safe is False

        # 危险路径（空字节注入）
        is_safe = validator.is_safe_path("file.txt\x00.jpg")
        assert is_safe is False