#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速Token管理器 - 优化版本
直接从本地配置文件读取，避免重复路径解析
"""

import os
import json
import hashlib
import base64
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

class FastTokenManager:
    """快速Token管理器 - 优化加载速度"""

    def __init__(self):
        # 使用全局配置路径，避免路径解析开销
        self.config_dir = "/home/ddo/.config/claude-tools"
        self.token_file = os.path.join(self.config_dir, "token_config.json")
        self.cache_tokens = {}
        self.last_load_time = 0
        self.cache_duration = 60  # 缓存60秒

        # 预加载Token配置
        self._fast_load_tokens()

    def _fast_load_tokens(self):
        """快速加载Token配置"""
        current_time = time.time()

        # 使用缓存，避免频繁文件读取
        if (self.cache_tokens and
            current_time - self.last_load_time < self.cache_duration):
            return

        try:
            if os.path.exists(self.token_file):
                with open(self.token_file, 'r', encoding='utf-8') as f:
                    self.cache_tokens = json.load(f)
                self.last_load_time = current_time
        except Exception as e:
            # 静默处理错误，避免输出干扰
            pass

    def get_token(self, name: str) -> Optional[str]:
        """快速获取Token"""
        self._fast_load_tokens()

        if name in self.cache_tokens:
            token_info = self.cache_tokens[name]

            # 检查Token是否过期
            try:
                expires_at = datetime.fromisoformat(token_info["expires_at"])
                if datetime.now() > expires_at:
                    return None
            except:
                return None

            # 快速更新使用记录（异步方式）
            token_info["last_used"] = datetime.now().isoformat()
            token_info["usage_count"] = token_info.get("usage_count", 0) + 1

            # 延迟保存，避免阻塞
            self._async_save_config()

            return token_info.get("token")

        return None

    def _async_save_config(self):
        """异步保存配置（简化版本）"""
        try:
            # 在后台线程中保存，这里简化为直接保存
            with open(self.token_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache_tokens, f, ensure_ascii=False, indent=2)
        except:
            pass  # 静默处理保存错误

    def list_tokens(self) -> Dict[str, Any]:
        """快速列出活跃Token"""
        self._fast_load_tokens()

        active_tokens = {}
        current_time = datetime.now()

        for name, info in self.cache_tokens.items():
            if not info.get("is_active", False):
                continue

            try:
                expires_at = datetime.fromisoformat(info["expires_at"])
                if current_time < expires_at:
                    active_tokens[name] = info
            except:
                continue

        return active_tokens

    def get_best_token(self) -> Optional[str]:
        """获取最佳Token（使用次数最少的活跃Token）"""
        self._fast_load_tokens()

        active_tokens = self.list_tokens()
        if not active_tokens:
            return None

        # 选择使用次数最少的Token
        best_token = min(active_tokens.items(),
                        key=lambda x: x[1].get("usage_count", 0))

        return best_token[0]

# 全局单例，避免重复初始化
_global_manager = None

def get_token_manager() -> FastTokenManager:
    """获取全局Token管理器单例"""
    global _global_manager
    if _global_manager is None:
        _global_manager = FastTokenManager()
    return _global_manager

def fast_get_token(name: str = None) -> Optional[str]:
    """快速获取Token的便捷函数"""
    manager = get_token_manager()

    if name:
        return manager.get_token(name)
    else:
        # 自动选择最佳Token
        best_name = manager.get_best_token()
        return manager.get_token(best_name) if best_name else None

def fast_list_tokens() -> Dict[str, Any]:
    """快速列出Token的便捷函数"""
    return get_token_manager().list_tokens()

# 命令行接口
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "get":
            token_name = sys.argv[2] if len(sys.argv) > 2 else None
            token = fast_get_token(token_name)
            if token:
                print(token)
            else:
                sys.exit(1)

        elif command == "list":
            tokens = fast_list_tokens()
            for name, info in tokens.items():
                status = "✅" if info.get("is_active", False) else "❌"
                usage = info.get("usage_count", 0)
                expires = info.get("expires_at", "")[:10]
                print(f"{status} {name}: {usage}次 | {expires}")

        elif command == "best":
            manager = get_token_manager()
            best_name = manager.get_best_token()
            if best_name:
                token = manager.get_token(best_name)
                if token:
                    print(f"{best_name}:{token}")
            else:
                sys.exit(1)

        else:
            print(f"用法: {sys.argv[0]} [get|list|best] [token_name]")
            sys.exit(1)
    else:
        print("可用命令:")
        print("  get [name]  - 获取指定Token")
        print("  list        - 列出所有Token")
        print("  best        - 获取最佳Token")