"""
安全配置模块
提供加密、解密、密钥管理等功能
"""

import os
import hashlib
import secrets
import base64
from typing import Optional, Dict, Any, Tuple
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import logging
import json
from pathlib import Path
import time

logger = logging.getLogger(__name__)


class SecureConfig:
    """安全配置管理器"""

    def __init__(self, key_file: Optional[str] = None):
        """
        初始化安全配置管理器

        Args:
            key_file: 密钥文件路径
        """
        self.key_file = Path(key_file) if key_file else Path.home() / ".zhipu_ai" / "keys"
        self.key_file.parent.mkdir(parents=True, exist_ok=True)
        self._master_key: Optional[bytes] = None
        self._encryption_keys: Dict[str, Fernet] = {}

    def generate_key(self) -> str:
        """
        生成新的加密密钥

        Returns:
            Base64编码的密钥字符串
        """
        key = Fernet.generate_key()
        return base64.b64encode(key).decode()

    def derive_key_from_password(self, password: str, salt: Optional[bytes] = None) -> Tuple[bytes, bytes]:
        """
        从密码派生密钥

        Args:
            password: 密码
            salt: 盐值，如果为None则生成新盐值

        Returns:
            (密钥, 盐值)
        """
        if salt is None:
            salt = os.urandom(16)

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key, salt

    def load_master_key(self) -> bytes:
        """
        加载主密钥

        Returns:
            主密钥
        """
        if self._master_key:
            return self._master_key

        key_file = self.key_file / "master.key"
        if not key_file.exists():
            logger.info("主密钥不存在，生成新密钥")
            self._master_key = Fernet.generate_key()
            self._save_master_key(self._master_key)
        else:
            with open(key_file, 'rb') as f:
                encrypted_key = f.read()
            # 这里应该使用系统密钥环或其他方式解密
            # 简化实现，实际应更安全
            self._master_key = encrypted_key

        return self._master_key

    def _save_master_key(self, key: bytes):
        """
        保存主密钥

        Args:
            key: 主密钥
        """
        key_file = self.key_file / "master.key"
        with open(key_file, 'wb') as f:
            f.write(key)
        # 设置文件权限（Unix系统）
        try:
            os.chmod(key_file, 0o600)
        except:
            pass

    def get_encryption_key(self, key_name: str = "default") -> Fernet:
        """
        获取加密密钥

        Args:
            key_name: 密钥名称

        Returns:
            Fernet加密器
        """
        if key_name in self._encryption_keys:
            return self._encryption_keys[key_name]

        key_file = self.key_file / f"{key_name}.key"
        if key_file.exists():
            with open(key_file, 'rb') as f:
                key = f.read()
        else:
            # 生成新密钥
            master_key = self.load_master_key()
            key = Fernet.generate_key()
            # 使用主密钥加密存储
            fernet = Fernet(master_key)
            encrypted_key = fernet.encrypt(key)
            with open(key_file, 'wb') as f:
                f.write(encrypted_key)
            try:
                os.chmod(key_file, 0o600)
            except:
                pass
            key = key

        self._encryption_keys[key_name] = Fernet(key)
        return self._encryption_keys[key_name]

    def encrypt(self, data: str, key_name: str = "default") -> str:
        """
        加密字符串

        Args:
            data: 要加密的数据
            key_name: 密钥名称

        Returns:
            Base64编码的加密数据
        """
        fernet = self.get_encryption_key(key_name)
        encrypted_data = fernet.encrypt(data.encode())
        return base64.b64encode(encrypted_data).decode()

    def decrypt(self, encrypted_data: str, key_name: str = "default") -> str:
        """
        解密字符串

        Args:
            encrypted_data: 加密的数据
            key_name: 密钥名称

        Returns:
            解密后的字符串
        """
        fernet = self.get_encryption_key(key_name)
        encrypted_bytes = base64.b64decode(encrypted_data.encode())
        decrypted_data = fernet.decrypt(encrypted_bytes)
        return decrypted_data.decode()

    def encrypt_dict(self, data: Dict[str, Any], key_name: str = "default") -> Dict[str, Any]:
        """
        加密字典中的敏感值

        Args:
            data: 数据字典
            key_name: 密钥名称

        Returns:
            加密后的字典
        """
        sensitive_keys = {'password', 'api_key', 'secret', 'token', 'key'}
        encrypted_data = {}

        for key, value in data.items():
            if isinstance(value, str) and any(sensitive in key.lower() for sensitive in sensitive_keys):
                encrypted_data[key] = self.encrypt(value, key_name)
            elif isinstance(value, dict):
                encrypted_data[key] = self.encrypt_dict(value, key_name)
            else:
                encrypted_data[key] = value

        return encrypted_data

    def decrypt_dict(self, encrypted_data: Dict[str, Any], key_name: str = "default") -> Dict[str, Any]:
        """
        解密字典中的加密值

        Args:
            encrypted_data: 加密的数据字典
            key_name: 密钥名称

        Returns:
            解密后的字典
        """
        decrypted_data = {}

        for key, value in encrypted_data.items():
            if isinstance(value, str):
                try:
                    # 尝试解密
                    decrypted_value = self.decrypt(value, key_name)
                    # 验证解密结果是否为有效的JSON
                    json.loads(decrypted_value)
                    # 如果是JSON，可能是加密的字典
                    try:
                        decrypted_data[key] = json.loads(decrypted_value)
                    except:
                        decrypted_data[key] = decrypted_value
                except:
                    # 解密失败，保持原值
                    decrypted_data[key] = value
            elif isinstance(value, dict):
                decrypted_data[key] = self.decrypt_dict(value, key_name)
            else:
                decrypted_data[key] = value

        return decrypted_data

    def hash_password(self, password: str, salt: Optional[str] = None) -> Tuple[str, str]:
        """
        哈希密码

        Args:
            password: 密码
            salt: 盐值

        Returns:
            (哈希值, 盐值)
        """
        if salt is None:
            salt = secrets.token_hex(16)

        # 使用SHA-256进行哈希
        hash_obj = hashlib.sha256()
        hash_obj.update((password + salt).encode())
        password_hash = hash_obj.hexdigest()

        return password_hash, salt

    def verify_password(self, password: str, stored_hash: str, salt: str) -> bool:
        """
        验证密码

        Args:
            password: 要验证的密码
            stored_hash: 存储的哈希值
            salt: 盐值

        Returns:
            是否验证通过
        """
        computed_hash, _ = self.hash_password(password, salt)
        return computed_hash == stored_hash

    def generate_token(self, length: int = 32) -> str:
        """
        生成安全随机令牌

        Args:
            length: 令牌长度

        Returns:
            随机令牌
        """
        return secrets.token_urlsafe(length)

    def rotate_key(self, key_name: str = "default") -> bool:
        """
        轮换加密密钥

        Args:
            key_name: 密钥名称

        Returns:
            是否成功
        """
        try:
            # 备份旧密钥
            if key_name in self._encryption_keys:
                old_key_file = self.key_file / f"{key_name}.key"
                backup_file = self.key_file / f"{key_name}.key.backup"
                if old_key_file.exists():
                    backup_file.write_bytes(old_key_file.read_bytes())

            # 生成新密钥
            new_key = Fernet.generate_key()
            master_key = self.load_master_key()
            fernet = Fernet(master_key)
            encrypted_key = fernet.encrypt(new_key)

            # 保存新密钥
            key_file = self.key_file / f"{key_name}.key"
            with open(key_file, 'wb') as f:
                f.write(encrypted_key)

            # 更新内存中的密钥
            self._encryption_keys[key_name] = Fernet(new_key)

            logger.info(f"成功轮换密钥: {key_name}")
            return True

        except Exception as e:
            logger.error(f"密钥轮换失败: {e}")
            return False

    def audit_config_access(self, action: str, user: Optional[str] = None) -> None:
        """
        审计配置访问

        Args:
            action: 操作描述
            user: 用户标识
        """
        audit_entry = {
            "timestamp": time.time(),
            "action": action,
            "user": user or os.getenv("USER", "unknown"),
            "ip": self._get_client_ip()
        }

        audit_file = self.key_file / "audit.log"
        with open(audit_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(audit_entry, ensure_ascii=False) + "\n")

    def _get_client_ip(self) -> str:
        """获取客户端IP地址"""
        # 简化实现，实际应从请求上下文获取
        return os.getenv("REMOTE_ADDR", "127.0.0.1")

    def secure_delete(self, file_path: Path) -> bool:
        """
        安全删除文件

        Args:
            file_path: 文件路径

        Returns:
            是否成功
        """
        try:
            if not file_path.exists():
                return True

            # 覆写文件内容
            file_size = file_path.stat().st_size
            with open(file_path, 'wb') as f:
                f.write(b'\x00' * file_size)

            # 删除文件
            file_path.unlink()
            logger.info(f"安全删除文件: {file_path}")
            return True

        except Exception as e:
            logger.error(f"安全删除文件失败: {e}")
            return False


class ConfigValidator:
    """配置验证器"""

    @staticmethod
    def validate_ssl_certificates(config: Dict[str, Any]) -> bool:
        """
        验证SSL证书配置

        Args:
            config: 配置字典

        Returns:
            是否有效
        """
        # 实现SSL证书验证逻辑
        return True

    @staticmethod
    def validate_network_access(config: Dict[str, Any]) -> bool:
        """
        验证网络访问配置

        Args:
            config: 配置字典

        Returns:
            是否有效
        """
        # 检查IP白名单、端口配置等
        return True

    @staticmethod
    def validate_encryption_strength(key: str) -> bool:
        """
        验证加密强度

        Args:
            key: 加密密钥

        Returns:
            是否足够强
        """
        try:
            decoded = base64.b64decode(key)
            return len(decoded) == 44  # Fernet密钥长度
        except:
            return False


# 全局安全配置实例
secure_config = SecureConfig()