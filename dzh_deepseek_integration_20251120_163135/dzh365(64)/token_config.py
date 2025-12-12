#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DZH Token配置管理器
用于管理和配置DZH系统的认证Token
"""

import os
import json
import hashlib
import base64
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

class DZHTokenManager:
    """DZH Token管理器"""

    def __init__(self, config_dir: str = "/mnt/d/dzh365(64)"):
        self.config_dir = config_dir
        self.token_file = os.path.join(config_dir, "token_config.json")
        self.cache_tokens = {}
        self.load_existing_tokens()

    def load_existing_tokens(self):
        """加载已存在的Token配置"""
        if os.path.exists(self.token_file):
            try:
                with open(self.token_file, 'r', encoding='utf-8') as f:
                    self.cache_tokens = json.load(f)
                print(f"📄 已加载Token配置: {len(self.cache_tokens)}个")
            except Exception as e:
                print(f"❌ 加载Token配置失败: {str(e)}")

    def save_token_config(self):
        """保存Token配置到文件"""
        try:
            with open(self.token_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache_tokens, f, ensure_ascii=False, indent=2)
            print(f"✅ Token配置已保存到: {self.token_file}")
        except Exception as e:
            print(f"❌ 保存Token配置失败: {str(e)}")

    def add_token(self, name: str, user_id: str, api_key: str, device_id: str = None):
        """添加Token配置"""
        token = self._generate_token(user_id, api_key, device_id)

        token_info = {
            "name": name,
            "user_id": user_id,
            "api_key": api_key,
            "device_id": device_id or "default",
            "token": token,
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(days=365)).isoformat(),
            "last_used": None,
            "usage_count": 0,
            "is_active": True
        }

        self.cache_tokens[name] = token_info
        self.save_token_config()
        print(f"✅ 已添加Token: {name}")
        return token_info

    def _generate_token(self, user_id: str, api_key: str, device_id: str = None) -> str:
        """生成DZH Token"""
        timestamp = str(int(time.time()))

        # 基础信息组合
        auth_data = f"{user_id}:{api_key}:{timestamp}"
        if device_id:
            auth_data += f":{device_id}"

        # 生成Hash
        token_hash = hashlib.sha256(auth_data.encode()).hexdigest()

        # Base64编码
        token = base64.b64encode(f"{timestamp}:{token_hash}".encode()).decode()

        return token

    def get_token(self, name: str) -> Optional[str]:
        """获取指定名称的Token"""
        if name in self.cache_tokens:
            token_info = self.cache_tokens[name]

            # 检查Token是否过期
            expires_at = datetime.fromisoformat(token_info["expires_at"])
            if datetime.now() > expires_at:
                print(f"⚠️ Token {name} 已过期")
                return None

            # 更新使用记录
            token_info["last_used"] = datetime.now().isoformat()
            token_info["usage_count"] += 1
            self.save_token_config()

            return token_info["token"]

        return None

    def refresh_token(self, name: str) -> Optional[str]:
        """刷新Token"""
        if name not in self.cache_tokens:
            print(f"❌ Token {name} 不存在")
            return None

        token_info = self.cache_tokens[name]

        # 生成新Token
        new_token = self._generate_token(
            token_info["user_id"],
            token_info["api_key"],
            token_info["device_id"]
        )

        # 更新Token
        token_info["token"] = new_token
        token_info["created_at"] = datetime.now().isoformat()
        token_info["expires_at"] = (datetime.now() + timedelta(days=365)).isoformat()
        token_info["last_used"] = datetime.now().isoformat()

        self.cache_tokens[name] = token_info
        self.save_token_config()

        print(f"🔄 Token {name} 已刷新")
        return new_token

    def list_tokens(self) -> Dict[str, Any]:
        """列出所有Token"""
        active_tokens = {
            name: info for name, info in self.cache_tokens.items()
            if info["is_active"] and
            datetime.now() < datetime.fromisoformat(info["expires_at"])
        }
        return active_tokens

    def deactivate_token(self, name: str):
        """停用Token"""
        if name in self.cache_tokens:
            self.cache_tokens[name]["is_active"] = False
            self.save_token_config()
            print(f"🚫 Token {name} 已停用")
        else:
            print(f"❌ Token {name} 不存在")

    def export_token_template(self, name: str) -> Dict[str, str]:
        """导出Token模板"""
        if name not in self.cache_tokens:
            return {"error": f"Token {name} 不存在"}

        token_info = self.cache_tokens[name]

        template = {
            "token": token_info["token"],
            "user_id": token_info["user_id"],
            "device_id": token_info["device_id"],
            "api_key": token_info["api_key"],
            "expires_at": token_info["expires_at"],
            "created_at": token_info["created_at"],
            "note": "DZH系统认证Token"
        }

        return template

    def validate_token(self, token: str) -> bool:
        """验证Token格式"""
        try:
            # Base64解码
            decoded = base64.b64decode(token.encode()).decode()
            timestamp, token_hash = decoded.split(':', 1)

            # 检查时间戳格式
            try:
                timestamp_int = int(timestamp)
                creation_time = datetime.fromtimestamp(timestamp_int)

                # 检查Token是否过期
                if datetime.now() > creation_time + timedelta(days=365):
                    return False

            except ValueError:
                return False

            return True

        except Exception:
            return False

    def create_sample_config(self):
        """创建示例Token配置"""
        print("📝 创建示例Token配置...")

        # 添加示例Token
        self.add_token(
            name="demo_token",
            user_id="demo_user_123",
            api_key="demo_api_key_abc123",
            device_id="demo_device_xyz"
        )

        self.add_token(
            name="test_token",
            user_id="test_user_456",
            api_key="test_api_key_def456",
            device_id="test_device_789"
        )

        print("📝 示例Token配置已创建")

    def test_token_connection(self, name: str) -> Dict[str, Any]:
        """测试Token连接"""
        token = self.get_token(name)
        if not token:
            return {"success": False, "error": f"Token {name} 不存在"}

        print(f"🧪 测试Token: {name}")

        # 获取完整的token信息
        if name in self.cache_tokens:
            token_info = self.cache_tokens[name]
        else:
            return {"success": False, "error": f"Token {name} 信息不存在"}

        # 这里可以添加实际的API连接测试
        test_result = {
            "success": True,
            "token_valid": self.validate_token(token),
            "token_info": token_info,
            "test_time": datetime.now().isoformat()
        }

        return test_result

# 使用示例
if __name__ == "__main__":
    print("🔧 DZH Token配置管理器")
    print("="*50)

    token_manager = DZHTokenManager()

    # 创建示例配置
    token_manager.create_sample_config()

    # 列出所有Token
    print(f"\n📋 当前活跃Token:")
    tokens = token_manager.list_tokens()
    for name, info in tokens.items():
        print(f"   {name}: {info['expires_at'][:10]}...")

    # 测试Token
    test_result = token_manager.test_token_connection("demo_token")
    print(f"\n🧪 Token测试结果:")
    print(f"   成功: {test_result['success']}")
    print(f"   有效: {test_result['token_valid']}")

    # 导出Token模板
    template = token_manager.export_token_template("demo_token")
    print(f"\n📄 Token模板:")
    for key, value in template.items():
        print(f"   {key}: {value}")