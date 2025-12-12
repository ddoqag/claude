"""
环境变量加载器
提供安全的环境变量加载和解析
"""

import os
import re
from typing import Dict, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class EnvLoader:
    """环境变量加载器"""

    def __init__(self, env_file: Optional[str] = None):
        """
        初始化环境变量加载器

        Args:
            env_file: .env文件路径，默认为项目根目录下的.env
        """
        if env_file:
            self.env_file = Path(env_file)
        else:
            # 查找.env文件
            self.env_file = self._find_env_file()

        self._loaded = False

    def _find_env_file(self) -> Optional[Path]:
        """查找.env文件"""
        current_dir = Path(__file__).parent
        while current_dir.parent != current_dir:
            env_path = current_dir / '.env'
            if env_path.exists():
                return env_path
            current_dir = current_dir.parent
        return None

    def load(self, force: bool = False) -> None:
        """
        加载环境变量

        Args:
            force: 是否强制重新加载
        """
        if self._loaded and not force:
            return

        if not self.env_file or not self.env_file.exists():
            logger.warning(f"环境变量文件不存在: {self.env_file}")
            return

        try:
            with open(self.env_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()

                    # 跳过注释和空行
                    if not line or line.startswith('#'):
                        continue

                    # 解析键值对
                    key, value = self._parse_line(line, line_num)
                    if key and value:
                        # 不覆盖已存在的环境变量
                        if key not in os.environ:
                            os.environ[key] = value

            self._loaded = True
            logger.info(f"成功加载环境变量文件: {self.env_file}")

        except Exception as e:
            logger.error(f"加载环境变量失败: {e}")
            raise

    def _parse_line(self, line: str, line_num: int) -> tuple[Optional[str], Optional[str]]:
        """
        解析单行环境变量

        Args:
            line: 环境变量行
            line_num: 行号

        Returns:
            (键, 值)元组
        """
        # 查找等号分割键值
        match = re.match(r'^([A-Za-z_][A-Za-z0-9_]*)=(.*)$', line)
        if not match:
            logger.warning(f"第{line_num}行格式错误: {line}")
            return None, None

        key, value = match.groups()

        # 处理引号
        if value and (value[0] == value[-1]) and value[0] in ('"', "'"):
            value = value[1:-1]

        # 处理转义字符
        value = self._unescape_value(value)

        return key, value

    def _unescape_value(self, value: str) -> str:
        """处理转义字符"""
        escape_map = {
            '\\n': '\n',
            '\\r': '\r',
            '\\t': '\t',
            '\\=': '=',
            '\\#': '#',
            '\\\\': '\\'
        }

        for escaped, unescaped in escape_map.items():
            value = value.replace(escaped, unescaped)

        return value

    def interpolate(self, config_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        插值环境变量到配置字典

        Args:
            config_dict: 配置字典

        Returns:
            插值后的配置字典
        """
        def _interpolate_value(value: Any) -> Any:
            if isinstance(value, str):
                # 查找 ${VAR_NAME} 格式的环境变量
                pattern = r'\$\{([^}]+)\}'

                def replace_var(match):
                    var_name = match.group(1)
                    var_value = os.getenv(var_name)
                    if var_value is None:
                        logger.warning(f"环境变量未设置: {var_name}")
                        return match.group(0)  # 保持原样
                    return var_value

                return re.sub(pattern, replace_var, value)
            elif isinstance(value, dict):
                return {k: _interpolate_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [_interpolate_value(item) for item in value]
            else:
                return value

        return _interpolate_value(config_dict)

    def get_required(self, key: str) -> str:
        """
        获取必需的环境变量

        Args:
            key: 环境变量名

        Returns:
            环境变量值

        Raises:
            ValueError: 当环境变量不存在时
        """
        value = os.getenv(key)
        if value is None:
            raise ValueError(f"必需的环境变量未设置: {key}")
        return value

    def get_optional(self, key: str, default: str = "") -> str:
        """
        获取可选的环境变量

        Args:
            key: 环境变量名
            default: 默认值

        Returns:
            环境变量值或默认值
        """
        return os.getenv(key, default)

    def get_bool(self, key: str, default: bool = False) -> bool:
        """
        获取布尔类型的环境变量

        Args:
            key: 环境变量名
            default: 默认值

        Returns:
            布尔值
        """
        value = os.getenv(key, "").lower()
        return value in ('true', '1', 'yes', 'on') if value else default

    def get_int(self, key: str, default: int = 0) -> int:
        """
        获取整数类型的环境变量

        Args:
            key: 环境变量名
            default: 默认值

        Returns:
            整数值
        """
        try:
            return int(os.getenv(key, str(default)))
        except ValueError:
            logger.warning(f"环境变量 {key} 不是有效的整数，使用默认值: {default}")
            return default

    def get_list(self, key: str, separator: str = ",", default: list = None) -> list:
        """
        获取列表类型的环境变量

        Args:
            key: 环境变量名
            separator: 分隔符
            default: 默认值

        Returns:
            列表值
        """
        value = os.getenv(key, "")
        if not value:
            return default or []
        return [item.strip() for item in value.split(separator) if item.strip()]

    def validate_required_vars(self, required_vars: list[str]) -> None:
        """
        验证必需的环境变量

        Args:
            required_vars: 必需的环境变量列表

        Raises:
            ValueError: 当有必需的环境变量未设置时
        """
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)

        if missing_vars:
            raise ValueError(f"缺少必需的环境变量: {', '.join(missing_vars)}")

    def mask_sensitive_values(self, config_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        掩码敏感值用于日志输出

        Args:
            config_dict: 配置字典

        Returns:
            掩码后的配置字典
        """
        sensitive_keys = {
            'api_key', 'password', 'secret', 'token', 'key',
            'encryption_key', 'jwt_secret', 'dsn'
        }

        def _mask_value(key: str, value: Any) -> Any:
            if isinstance(value, str):
                # 检查键名或值是否包含敏感词
                if any(sensitive in key.lower() for sensitive in sensitive_keys):
                    return "***" if len(value) > 3 else "***"
            return value

        def _recursive_mask(obj: Any, parent_key: str = "") -> Any:
            if isinstance(obj, dict):
                return {
                    k: _recursive_mask(v, k)
                    for k, v in obj.items()
                }
            elif isinstance(obj, list):
                return [_recursive_mask(item, parent_key) for item in obj]
            else:
                return _mask_value(parent_key, obj)

        return _recursive_mask(config_dict)


# 全局环境加载器实例
env_loader = EnvLoader()