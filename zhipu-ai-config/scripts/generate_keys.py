#!/usr/bin/env python3
"""
密钥生成工具
用于生成和加密配置所需的密钥
"""

import sys
import secrets
import base64
import argparse
from pathlib import Path

# 添加config目录到Python路径
config_dir = Path(__file__).parent.parent / "config"
sys.path.insert(0, str(config_dir))

from security import SecureConfig


def generate_fernet_key():
    """生成Fernet加密密钥"""
    return SecureConfig().generate_key()


def generate_jwt_secret(length=64):
    """生成JWT密钥"""
    return SecureConfig().generate_token(length)


def generate_password_hash(password):
    """生成密码哈希"""
    secure_config = SecureConfig()
    password_hash, salt = secure_config.hash_password(password)
    return password_hash, salt


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="密钥生成工具")
    parser.add_argument("--type", choices=["fernet", "jwt", "password", "all"],
                        default="all", help="生成的密钥类型")
    parser.add_argument("--password", help="要哈希的密码")
    parser.add_argument("--length", type=int, default=64,
                        help="JWT密钥长度")
    parser.add_argument("--save", action="store_true",
                        help="保存到文件")

    args = parser.parse_args()

    print("=== 密钥生成工具 ===\n")

    results = {}

    if args.type in ["fernet", "all"]:
        fernet_key = generate_fernet_key()
        print(f"Fernet加密密钥: {fernet_key}")
        results["fernet_key"] = fernet_key

    if args.type in ["jwt", "all"]:
        jwt_secret = generate_jwt_secret(args.length)
        print(f"JWT密钥({args.length}字符): {jwt_secret}")
        results["jwt_secret"] = jwt_secret

    if args.type == "password" and args.password:
        password_hash, salt = generate_password_hash(args.password)
        print(f"\n密码哈希结果:")
        print(f"密码: {args.password}")
        print(f"哈希值: {password_hash}")
        print(f"盐值: {salt}")
        results["password_hash"] = password_hash
        results["salt"] = salt

    # 保存到文件
    if args.save and results:
        import json
        output_file = Path("generated_keys.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\n✅ 密钥已保存到: {output_file}")


if __name__ == "__main__":
    main()