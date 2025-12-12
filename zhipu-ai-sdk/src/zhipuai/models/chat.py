"""
聊天相关数据模型

定义聊天完成API的请求和响应模型。
"""

from typing import Any, Dict, List, Literal, Optional, Union
from pydantic import BaseModel, Field

from .common import BaseRequest, BaseResponse, Usage


class Message(BaseModel):
    """聊天消息"""
    role: Literal["system", "user", "assistant", "tool"] = Field(
        description="消息角色"
    )
    content: Union[str, List[Dict[str, Any]]] = Field(
        description="消息内容"
    )
    name: Optional[str] = Field(
        default=None,
        description="发送者名称"
    )
    tool_calls: Optional[List["ToolCall"]] = Field(
        default=None,
        description="工具调用列表"
    )
    tool_call_id: Optional[str] = Field(
        default=None,
        description="工具调用ID"
    )

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典，处理多模态内容"""
        result = {
            "role": self.role,
            "content": self.content,
        }

        if self.name:
            result["name"] = self.name

        if self.tool_calls:
            result["tool_calls"] = [tc.model_dump() for tc in self.tool_calls]

        if self.tool_call_id:
            result["tool_call_id"] = self.tool_call_id

        return result


class Function(BaseModel):
    """函数定义"""
    name: str = Field(description="函数名称")
    description: Optional[str] = Field(
        default=None,
        description="函数描述"
    )
    parameters: Optional[Dict[str, Any]] = Field(
        default=None,
        description="参数定义（JSON Schema）"
    )
    strict: Optional[bool] = Field(
        default=None,
        description="是否严格匹配参数"
    )


class ToolCall(BaseModel):
    """工具调用"""
    id: str = Field(description="工具调用ID")
    type: Literal["function"] = Field(
        default="function",
        description="工具类型"
    )
    function: "FunctionCall" = Field(
        description="函数调用信息"
    )


class FunctionCall(BaseModel):
    """函数调用"""
    name: str = Field(description="函数名称")
    arguments: str = Field(description="函数参数（JSON字符串）")


class Tool(BaseModel):
    """工具定义"""
    type: Literal["function"] = Field(
        default="function",
        description="工具类型"
    )
    function: Function = Field(
        description="函数定义"
    )


class ResponseFormat(BaseModel):
    """响应格式"""
    type: Literal["text", "json_object"] = Field(
        description="响应类型"
    )
    schema_: Optional[Dict[str, Any]] = Field(
        default=None,
        alias="schema",
        description="JSON Schema（当type=json_object时）"
    )


class ChatCompletionRequest(BaseRequest):
    """聊天完成请求"""
    model: str = Field(description="使用的模型")
    messages: List[Message] = Field(description="消息列表")

    # 基本参数
    max_tokens: Optional[int] = Field(
        default=None,
        ge=1,
        le=8192,
        description="最大完成token数"
    )
    temperature: Optional[float] = Field(
        default=1.0,
        ge=0.0,
        le=2.0,
        description="采样温度"
    )
    top_p: Optional[float] = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="核采样概率"
    )

    # 高级参数
    n: Optional[int] = Field(
        default=1,
        ge=1,
        le=5,
        description="生成数量"
    )
    stream: Optional[bool] = Field(
        default=False,
        description="是否流式返回"
    )
    stop: Optional[Union[str, List[str]]] = Field(
        default=None,
        description="停止序列"
    )
    presence_penalty: Optional[float] = Field(
        default=0.0,
        ge=-2.0,
        le=2.0,
        description="存在惩罚"
    )
    frequency_penalty: Optional[float] = Field(
        default=0.0,
        ge=-2.0,
        le=2.0,
        description="频率惩罚"
    )

    # 功能开关
    logit_bias: Optional[Dict[str, float]] = Field(
        default=None,
        description="Logit偏置"
    )
    user: Optional[str] = Field(
        default=None,
        description="用户标识"
    )

    # 响应格式
    response_format: Optional[ResponseFormat] = Field(
        default=None,
        description="响应格式"
    )

    # 工具调用
    tools: Optional[List[Tool]] = Field(
        default=None,
        description="可用工具列表"
    )
    tool_choice: Optional[Union[Literal["none", "auto"], Dict[str, Any]]] = Field(
        default=None,
        description="工具选择策略"
    )

    # 并行工具调用
    parallel_tool_calls: Optional[bool] = Field(
        default=None,
        description="是否启用并行工具调用"
    )

    # 其他参数
    seed: Optional[int] = Field(
        default=None,
        description="随机种子"
    )
    logprobs: Optional[bool] = Field(
        default=None,
        description="是否返回概率"
    )
    top_logprobs: Optional[int] = Field(
        default=None,
        ge=0,
        le=20,
        description="返回概率数量"
    )


class Delta(BaseModel):
    """流式响应增量"""
    role: Optional[str] = Field(default=None, description="角色")
    content: Optional[str] = Field(default=None, description="内容")
    tool_calls: Optional[List[ToolCall]] = Field(
        default=None,
        description="工具调用"
    )


class LogProb(BaseModel):
    """对数概率"""
    token: str = Field(description="Token")
    logprob: float = Field(description="对数概率")
    bytes: Optional[List[int]] = Field(default=None, description="字节表示")


class TopLogProb(BaseModel):
    """最高概率Token"""
    token: str = Field(description="Token")
    logprob: float = Field(description="对数概率")
    bytes: Optional[List[int]] = Field(default=None, description="字节表示")


class ChatCompletionLogProbs(BaseModel):
    """聊天完成概率信息"""
    content: Optional[List[TopLogProb]] = Field(
        default=None,
        description="内容概率"
    )
    refusal: Optional[List[TopLogProb]] = Field(
        default=None,
        description="拒绝概率"
    )


class ChatCompletionChoice(BaseModel):
    """聊天完成选项"""
    index: int = Field(description="选项索引")
    message: Optional[Message] = Field(
        default=None,
        description="消息内容"
    )
    delta: Optional[Delta] = Field(
        default=None,
        description="增量内容（流式）"
    )
    finish_reason: Optional[Literal[
        "stop", "length", "tool_calls", "content_filter", "function_call"
    ]] = Field(
        default=None,
        description="结束原因"
    )
    logprobs: Optional[ChatCompletionLogProbs] = Field(
        default=None,
        description="概率信息"
    )


class ChatCompletionResponse(BaseResponse):
    """聊天完成响应"""
    object: str = Field(default="chat.completion", description="对象类型")
    choices: List[ChatCompletionChoice] = Field(description="完成选项列表")
    usage: Optional[Usage] = Field(default=None, description="使用量信息")
    system_fingerprint: Optional[str] = Field(
        default=None,
        description="系统指纹"
    )


class ChatCompletionStreamResponse(BaseResponse):
    """聊天完成流式响应"""
    object: str = Field(default="chat.completion.chunk", description="对象类型")
    choices: List[ChatCompletionChoice] = Field(description="完成选项列表")
    usage: Optional[Usage] = Field(default=None, description="使用量信息")


# 更新前向引用
Message.model_rebuild()
ToolCall.model_rebuild()