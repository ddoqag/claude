"""
认证处理器

处理API请求的认证逻辑。
"""

import time
from typing import Dict, Optional
from ..auth.api_key import APIKey
from ..exceptions import AuthenticationError


class AuthHandler:
    """认证处理器"""

    def __init__(self, api_key: str, organization: Optional[str] = None):
        self.api_key = api_key
        self.organization = organization

    def get_auth_headers(self) -> Dict[str, str]:
        """获取认证请求头"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
        }

        if self.organization:
            headers["OpenAI-Organization"] = self.organization

        return headers

    def update_from_api_key(self, api_key: APIKey) -> None:
        """从APIKey对象更新认证信息"""
        self.api_key = api_key.key_value
        self.organization = api_key.organization

    def validate_credentials(self) -> bool:
        """验证凭据有效性"""
        # 基本验证
        if not self.api_key:
            raise AuthenticationError("API key is required")

        if not isinstance(self.api_key, str):
            raise AuthenticationError("API key must be a string")

        # 格式验证
        if not self.api_key.startswith("zhipu-"):
            raise AuthenticationError("Invalid API key format. Expected format: zhipu-xxxxxxxx")

        return True