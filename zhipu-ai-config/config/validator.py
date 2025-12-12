"""
配置验证和错误处理模块
提供全面的配置验证和错误处理机制
"""

import re
import json
import logging
from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum
import socket
import urllib.parse
from datetime import datetime

logger = logging.getLogger(__name__)


class ValidationSeverity(Enum):
    """验证严重程度"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ValidationError:
    """验证错误"""
    field: str
    message: str
    severity: ValidationSeverity = ValidationSeverity.ERROR
    value: Any = None
    expected: Any = None
    code: str = "VALIDATION_ERROR"

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "field": self.field,
            "message": self.message,
            "severity": self.severity.value,
            "value": self.value,
            "expected": self.expected,
            "code": self.code,
            "timestamp": datetime.now().isoformat()
        }


@dataclass
class ValidationResult:
    """验证结果"""
    is_valid: bool
    errors: List[ValidationError] = field(default_factory=list)

    def add_error(self, error: ValidationError):
        """添加错误"""
        self.errors.append(error)
        if error.severity in [ValidationSeverity.ERROR, ValidationSeverity.CRITICAL]:
            self.is_valid = False

    def get_errors_by_severity(self, severity: ValidationSeverity) -> List[ValidationError]:
        """按严重程度获取错误"""
        return [e for e in self.errors if e.severity == severity]

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "is_valid": self.is_valid,
            "total_errors": len(self.errors),
            "errors": [e.to_dict() for e in self.errors],
            "critical_errors": len(self.get_errors_by_severity(ValidationSeverity.CRITICAL)),
            "error_errors": len(self.get_errors_by_severity(ValidationSeverity.ERROR)),
            "warning_errors": len(self.get_errors_by_severity(ValidationSeverity.WARNING)),
            "info_errors": len(self.get_errors_by_severity(ValidationSeverity.INFO))
        }


class ConfigValidator:
    """配置验证器"""

    def __init__(self):
        """初始化验证器"""
        self.validators: Dict[str, List[Callable]] = {}
        self.custom_validators: Dict[str, Callable] = {}
        self._register_default_validators()

    def _register_default_validators(self):
        """注册默认验证器"""
        self.validators.update({
            "url": [self._validate_url],
            "email": [self._validate_email],
            "api_key": [self._validate_api_key],
            "port": [self._validate_port],
            "ip": [self._validate_ip_address],
            "ssl_mode": [self._validate_ssl_mode],
            "log_level": [self._validate_log_level],
            "timeout": [self._validate_timeout],
            "rate_limit": [self._validate_rate_limit],
            "encryption_key": [self._validate_encryption_key]
        })

    def validate(self, config: Dict[str, Any], schema: Dict[str, Any]) -> ValidationResult:
        """
        验证配置

        Args:
            config: 配置字典
            schema: 验证模式

        Returns:
            验证结果
        """
        result = ValidationResult(is_valid=True)

        try:
            # 验证必需字段
            self._validate_required_fields(config, schema, result)

            # 验证字段类型
            self._validate_field_types(config, schema, result)

            # 验证字段值
            self._validate_field_values(config, schema, result)

            # 验证依赖关系
            self._validate_dependencies(config, schema, result)

            # 运行自定义验证器
            self._run_custom_validators(config, schema, result)

            logger.info(f"配置验证完成: 有效={result.is_valid}, 错误数={len(result.errors)}")

        except Exception as e:
            result.add_error(ValidationError(
                field="system",
                message=f"验证过程发生错误: {str(e)}",
                severity=ValidationSeverity.CRITICAL,
                code="VALIDATION_SYSTEM_ERROR"
            ))

        return result

    def _validate_required_fields(self, config: Dict[str, Any], schema: Dict[str, Any], result: ValidationResult):
        """验证必需字段"""
        for field_name, field_schema in schema.items():
            if field_schema.get("required", False) and field_name not in config:
                result.add_error(ValidationError(
                    field=field_name,
                    message="必需字段缺失",
                    severity=ValidationSeverity.ERROR,
                    code="REQUIRED_FIELD_MISSING"
                ))

    def _validate_field_types(self, config: Dict[str, Any], schema: Dict[str, Any], result: ValidationResult):
        """验证字段类型"""
        for field_name, field_schema in schema.items():
            if field_name not in config:
                continue

            value = config[field_name]
            expected_type = field_schema.get("type")

            if expected_type:
                if not self._check_type(value, expected_type):
                    result.add_error(ValidationError(
                        field=field_name,
                        message=f"类型错误: 期望 {expected_type}, 实际 {type(value).__name__}",
                        severity=ValidationSeverity.ERROR,
                        value=type(value).__name__,
                        expected=expected_type,
                        code="TYPE_MISMATCH"
                    ))

    def _validate_field_values(self, config: Dict[str, Any], schema: Dict[str, Any], result: ValidationResult):
        """验证字段值"""
        for field_name, field_schema in schema.items():
            if field_name not in config:
                continue

            value = config[field_name]
            field_path = field_name

            # 验证枚举值
            if "enum" in field_schema:
                if value not in field_schema["enum"]:
                    result.add_error(ValidationError(
                        field=field_path,
                        message=f"无效值: 必须是 {field_schema['enum']} 之一",
                        severity=ValidationSeverity.ERROR,
                        value=value,
                        expected=field_schema["enum"],
                        code="INVALID_ENUM_VALUE"
                    ))

            # 验证范围
            if "min" in field_schema and value < field_schema["min"]:
                result.add_error(ValidationError(
                    field=field_path,
                    message=f"值太小: 最小值 {field_schema['min']}",
                    severity=ValidationSeverity.ERROR,
                    value=value,
                    expected=f">= {field_schema['min']}",
                    code="VALUE_TOO_SMALL"
                ))

            if "max" in field_schema and value > field_schema["max"]:
                result.add_error(ValidationError(
                    field=field_path,
                    message=f"值太大: 最大值 {field_schema['max']}",
                    severity=ValidationSeverity.ERROR,
                    value=value,
                    expected=f"<= {field_schema['max']}",
                    code="VALUE_TOO_LARGE"
                ))

            # 验证正则表达式
            if "pattern" in field_schema:
                if not re.match(field_schema["pattern"], str(value)):
                    result.add_error(ValidationError(
                        field=field_path,
                        message="格式不匹配",
                        severity=ValidationSeverity.ERROR,
                        value=value,
                        expected=field_schema["pattern"],
                        code="PATTERN_MISMATCH"
                    ))

            # 验证长度
            if isinstance(value, (str, list)):
                if "min_length" in field_schema and len(value) < field_schema["min_length"]:
                    result.add_error(ValidationError(
                        field=field_path,
                        message=f"长度太短: 最小长度 {field_schema['min_length']}",
                        severity=ValidationSeverity.ERROR,
                        value=len(value),
                        expected=f">= {field_schema['min_length']}",
                        code="LENGTH_TOO_SHORT"
                    ))

                if "max_length" in field_schema and len(value) > field_schema["max_length"]:
                    result.add_error(ValidationError(
                        field=field_path,
                        message=f"长度太长: 最大长度 {field_schema['max_length']}",
                        severity=ValidationSeverity.ERROR,
                        value=len(value),
                        expected=f"<= {field_schema['max_length']}",
                        code="LENGTH_TOO_LONG"
                    ))

            # 运行特定验证器
            validators = field_schema.get("validators", [])
            if isinstance(validators, str):
                validators = [validators]

            for validator_name in validators:
                if validator_name in self.validators:
                    for validator_func in self.validators[validator_name]:
                        validator_result = validator_func(value, field_path)
                        if validator_result:
                            result.add_error(validator_result)

    def _validate_dependencies(self, config: Dict[str, Any], schema: Dict[str, Any], result: ValidationResult):
        """验证依赖关系"""
        dependencies = schema.get("_dependencies", {})

        for field, conditions in dependencies.items():
            if field not in config:
                continue

            for condition, required_fields in conditions.items():
                if condition == "equals" and config[field] == required_fields.get("value"):
                    for req_field in required_fields.get("requires", []):
                        if req_field not in config:
                            result.add_error(ValidationError(
                                field=req_field,
                                message=f"字段 {field}={config[field]} 时必需",
                                severity=ValidationSeverity.ERROR,
                                code="DEPENDENCY_ERROR"
                            ))

    def _run_custom_validators(self, config: Dict[str, Any], schema: Dict[str, Any], result: ValidationResult):
        """运行自定义验证器"""
        custom_validators = schema.get("_custom_validators", {})

        for validator_name, validator_func in custom_validators.items():
            try:
                errors = validator_func(config)
                for error in errors:
                    result.add_error(error)
            except Exception as e:
                logger.error(f"自定义验证器 {validator_name} 执行失败: {e}")

    def _check_type(self, value: Any, expected_type: str) -> bool:
        """检查类型"""
        type_map = {
            "string": str,
            "integer": int,
            "number": (int, float),
            "boolean": bool,
            "array": list,
            "object": dict,
            "null": type(None)
        }

        expected = type_map.get(expected_type)
        if expected is None:
            return True

        return isinstance(value, expected)

    # 默认验证器方法
    def _validate_url(self, value: Any, field_path: str) -> Optional[ValidationError]:
        """验证URL"""
        if not isinstance(value, str):
            return ValidationError(
                field=field_path,
                message="URL必须是字符串",
                severity=ValidationSeverity.ERROR,
                code="URL_TYPE_ERROR"
            )

        try:
            parsed = urllib.parse.urlparse(value)
            if not all([parsed.scheme, parsed.netloc]):
                raise ValueError
            if parsed.scheme not in ["http", "https"]:
                raise ValueError
            return None
        except:
            return ValidationError(
                field=field_path,
                message="无效的URL格式",
                severity=ValidationSeverity.ERROR,
                value=value,
                expected="有效的URL",
                code="INVALID_URL"
            )

    def _validate_email(self, value: Any, field_path: str) -> Optional[ValidationError]:
        """验证邮箱"""
        if not isinstance(value, str):
            return ValidationError(
                field=field_path,
                message="邮箱必须是字符串",
                severity=ValidationSeverity.ERROR,
                code="EMAIL_TYPE_ERROR"
            )

        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, value):
            return ValidationError(
                field=field_path,
                message="无效的邮箱格式",
                severity=ValidationSeverity.ERROR,
                value=value,
                expected="有效的邮箱地址",
                code="INVALID_EMAIL"
            )
        return None

    def _validate_api_key(self, value: Any, field_path: str) -> Optional[ValidationError]:
        """验证API密钥"""
        if not isinstance(value, str):
            return ValidationError(
                field=field_path,
                message="API密钥必须是字符串",
                severity=ValidationSeverity.ERROR,
                code="API_KEY_TYPE_ERROR"
            )

        if len(value) < 20:
            return ValidationError(
                field=field_path,
                message="API密钥太短",
                severity=ValidationSeverity.WARNING,
                value=len(value),
                expected=">= 20字符",
                code="API_KEY_TOO_SHORT"
            )

        # 检查是否包含常见的占位符
        placeholders = ["your_", "xxx", "placeholder", "example"]
        if any(placeholder in value.lower() for placeholder in placeholders):
            return ValidationError(
                field=field_path,
                message="API密钥包含占位符文本",
                severity=ValidationSeverity.ERROR,
                code="API_KEY_PLACEHOLDER"
            )

        return None

    def _validate_port(self, value: Any, field_path: str) -> Optional[ValidationError]:
        """验证端口"""
        if not isinstance(value, int):
            return ValidationError(
                field=field_path,
                message="端口必须是整数",
                severity=ValidationSeverity.ERROR,
                code="PORT_TYPE_ERROR"
            )

        if not 1 <= value <= 65535:
            return ValidationError(
                field=field_path,
                message="端口超出范围",
                severity=ValidationSeverity.ERROR,
                value=value,
                expected="1-65535",
                code="PORT_OUT_OF_RANGE"
            )

        return None

    def _validate_ip_address(self, value: Any, field_path: str) -> Optional[ValidationError]:
        """验证IP地址"""
        if not isinstance(value, str):
            return ValidationError(
                field=field_path,
                message="IP地址必须是字符串",
                severity=ValidationSeverity.ERROR,
                code="IP_TYPE_ERROR"
            )

        # 支持单个IP和CIDR格式
        ip_pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(?:/(?:[0-9]|[1-2][0-9]|3[0-2]))?$'
        if not re.match(ip_pattern, value):
            return ValidationError(
                field=field_path,
                message="无效的IP地址格式",
                severity=ValidationSeverity.ERROR,
                value=value,
                expected="有效的IP地址或CIDR",
                code="INVALID_IP"
            )

        return None

    def _validate_ssl_mode(self, value: Any, field_path: str) -> Optional[ValidationError]:
        """验证SSL模式"""
        valid_modes = ["disable", "allow", "prefer", "require", "verify-ca", "verify-full"]
        if value not in valid_modes:
            return ValidationError(
                field=field_path,
                message="无效的SSL模式",
                severity=ValidationSeverity.ERROR,
                value=value,
                expected=valid_modes,
                code="INVALID_SSL_MODE"
            )
        return None

    def _validate_log_level(self, value: Any, field_path: str) -> Optional[ValidationError]:
        """验证日志级别"""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if value.upper() not in valid_levels:
            return ValidationError(
                field=field_path,
                message="无效的日志级别",
                severity=ValidationSeverity.ERROR,
                value=value,
                expected=valid_levels,
                code="INVALID_LOG_LEVEL"
            )
        return None

    def _validate_timeout(self, value: Any, field_path: str) -> Optional[ValidationError]:
        """验证超时时间"""
        if not isinstance(value, (int, float)):
            return ValidationError(
                field=field_path,
                message="超时时间必须是数字",
                severity=ValidationSeverity.ERROR,
                code="TIMEOUT_TYPE_ERROR"
            )

        if value < 0:
            return ValidationError(
                field=field_path,
                message="超时时间不能为负数",
                severity=ValidationSeverity.ERROR,
                value=value,
                expected=">= 0",
                code="NEGATIVE_TIMEOUT"
            )

        if value > 3600:
            return ValidationError(
                field=field_path,
                message="超时时间过长（超过1小时）",
                severity=ValidationSeverity.WARNING,
                value=value,
                expected="<= 3600秒",
                code="TIMEOUT_TOO_LONG"
            )

        return None

    def _validate_rate_limit(self, value: Any, field_path: str) -> Optional[ValidationError]:
        """验证速率限制"""
        if not isinstance(value, int):
            return ValidationError(
                field=field_path,
                message="速率限制必须是整数",
                severity=ValidationSeverity.ERROR,
                code="RATE_LIMIT_TYPE_ERROR"
            )

        if value < 1:
            return ValidationError(
                field=field_path,
                message="速率限制必须大于0",
                severity=ValidationSeverity.ERROR,
                value=value,
                expected=">= 1",
                code="RATE_LIMIT_TOO_LOW"
            )

        if value > 10000:
            return ValidationError(
                field=field_path,
                message="速率限制过高",
                severity=ValidationSeverity.WARNING,
                value=value,
                expected="<= 10000",
                code="RATE_LIMIT_TOO_HIGH"
            )

        return None

    def _validate_encryption_key(self, value: Any, field_path: str) -> Optional[ValidationError]:
        """验证加密密钥"""
        if not isinstance(value, str):
            return ValidationError(
                field=field_path,
                message="加密密钥必须是字符串",
                severity=ValidationSeverity.ERROR,
                code="ENCRYPTION_KEY_TYPE_ERROR"
            )

        try:
            import base64
            decoded = base64.b64decode(value)
            if len(decoded) != 44:  # Fernet密钥长度
                return ValidationError(
                    field=field_path,
                    message="加密密钥长度无效",
                    severity=ValidationSeverity.ERROR,
                    value=len(decoded),
                    expected=44,
                    code="INVALID_ENCRYPTION_KEY_LENGTH"
                )
        except:
            return ValidationError(
                field=field_path,
                message="加密密钥格式无效",
                severity=ValidationSeverity.ERROR,
                code="INVALID_ENCRYPTION_KEY_FORMAT"
            )

        return None

    def register_validator(self, name: str, validator_func: Callable):
        """注册自定义验证器"""
        if name not in self.validators:
            self.validators[name] = []
        self.validators[name].append(validator_func)


class ConfigurationError(Exception):
    """配置错误异常"""

    def __init__(self, message: str, errors: List[ValidationError] = None):
        super().__init__(message)
        self.errors = errors or []
        self.timestamp = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "message": str(self),
            "errors": [e.to_dict() for e in self.errors],
            "timestamp": self.timestamp.isoformat()
        }


# 全局验证器实例
config_validator = ConfigValidator()