"""
通用数据模型

定义所有API共用的基础模型。
"""

from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class BaseRequest(BaseModel):
    """请求基类"""
    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        extra="forbid"
    )


class BaseResponse(BaseModel):
    """响应基类"""
    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        extra="allow"
    )

    id: Optional[str] = None
    object: str
    created: Optional[datetime] = None
    model: str


class Usage(BaseModel):
    """API使用量统计"""
    prompt_tokens: int = Field(description="提示词token数量")
    completion_tokens: int = Field(description="完成token数量")
    total_tokens: int = Field(description="总token数量")

    def __add__(self, other: "Usage") -> "Usage":
        """合并使用量"""
        if not isinstance(other, Usage):
            return self
        return Usage(
            prompt_tokens=self.prompt_tokens + other.prompt_tokens,
            completion_tokens=self.completion_tokens + other.completion_tokens,
            total_tokens=self.total_tokens + other.total_tokens,
        )


class Error(BaseModel):
    """错误信息"""
    message: str = Field(description="错误消息")
    type: Optional[str] = Field(default=None, description="错误类型")
    param: Optional[str] = Field(default=None, description="相关参数")
    code: Optional[Union[str, int]] = Field(default=None, description="错误代码")


class Model(BaseModel):
    """模型信息"""
    id: str = Field(description="模型ID")
    object: str = Field(default="model", description="对象类型")
    created: Optional[datetime] = Field(default=None, description="创建时间")
    owned_by: Optional[str] = Field(default=None, description="所有者")
    permission: Optional[List[Any]] = Field(default=None, description="权限列表")
    root: Optional[str] = Field(default=None, description="根模型")
    parent: Optional[str] = Field(default=None, description="父模型")

    # 模型能力
    capabilities: Optional[Dict[str, Any]] = Field(
        default=None,
        description="模型能力描述"
    )

    # 限制信息
    max_prompt_tokens: Optional[int] = Field(
        default=None,
        description="最大提示词token数"
    )
    max_completion_tokens: Optional[int] = Field(
        default=None,
        description="最大完成token数"
    )

    # 价格信息（每1K tokens）
    prompt_price: Optional[float] = Field(
        default=None,
        description="提示词价格（元/1K tokens）"
    )
    completion_price: Optional[float] = Field(
        default=None,
        description="完成价格（元/1K tokens）"
    )


class TokenCount(BaseModel):
    """Token计数结果"""
    count: int = Field(description="Token数量")
    model: str = Field(description="使用的模型")
    text: Optional[str] = Field(default=None, description="原始文本")
    tokens: Optional[List[str]] = Field(default=None, description="Token列表")


class EmbeddingUsage(BaseModel):
    """嵌入向量使用量"""
    prompt_tokens: int = Field(description="提示词token数量")
    total_tokens: int = Field(description="总token数量")


class Timestamp(BaseModel):
    """时间戳信息"""
    created: datetime = Field(description="创建时间")
    started: Optional[datetime] = Field(default=None, description="开始时间")
    completed: Optional[datetime] = Field(default=None, description="完成时间")
    duration: Optional[float] = Field(default=None, description="持续时间（秒）")


class PaginationInfo(BaseModel):
    """分页信息"""
    page: int = Field(description="当前页码")
    page_size: int = Field(description="每页大小")
    total: int = Field(description="总记录数")
    total_pages: int = Field(description="总页数")
    has_next: bool = Field(description="是否有下一页")
    has_prev: bool = Field(description="是否有上一页")


class RequestMetadata(BaseModel):
    """请求元数据"""
    request_id: Optional[str] = Field(default=None, description="请求ID")
    user_id: Optional[str] = Field(default=None, description="用户ID")
    session_id: Optional[str] = Field(default=None, description="会话ID")
    client_ip: Optional[str] = Field(default=None, description="客户端IP")
    user_agent: Optional[str] = Field(default=None, description="用户代理")
    tags: Optional[Dict[str, str]] = Field(default=None, description="标签")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="额外元数据")


class RateLimitInfo(BaseModel):
    """速率限制信息"""
    limit: int = Field(description="请求限制")
    remaining: int = Field(description="剩余请求次数")
    reset: datetime = Field(description="重置时间")
    retry_after: Optional[int] = Field(default=None, description="重试等待时间（秒）")


class ServerInfo(BaseModel):
    """服务器信息"""
    version: str = Field(description="API版本")
    environment: str = Field(description="环境")
    region: Optional[str] = Field(default=None, description="区域")
    instance_id: Optional[str] = Field(default=None, description="实例ID")
    uptime: Optional[float] = Field(default=None, description="运行时间（秒）")
    health_status: Optional[str] = Field(default=None, description="健康状态")