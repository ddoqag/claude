"""
代码相关数据模型

定义代码分析、调试、生成等功能的请求和响应模型。
"""

from typing import Any, Dict, List, Literal, Optional, Union
from pydantic import BaseModel, Field

from .common import BaseRequest, BaseResponse, Usage


class CodeAnalysisType(BaseModel):
    """代码分析类型"""
    name: str = Field(description="分析类型名称")
    description: Optional[str] = Field(default=None, description="描述")
    enabled: bool = Field(default=True, description="是否启用")
    options: Optional[Dict[str, Any]] = Field(default=None, description="选项")


class CodeFile(BaseModel):
    """代码文件"""
    filename: str = Field(description="文件名")
    content: str = Field(description="文件内容")
    language: str = Field(description="编程语言")
    path: Optional[str] = Field(default=None, description="文件路径")
    encoding: Optional[str] = Field(default="utf-8", description="编码")


class CodeAnalysisRequest(BaseRequest):
    """代码分析请求"""
    code: str = Field(description="代码内容")
    language: str = Field(description="编程语言")
    analysis_type: Union[str, List[str]] = Field(
        description="分析类型（如：security, performance, complexity, maintainability）"
    )
    file_path: Optional[str] = Field(
        default=None,
        description="文件路径"
    )
    context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="上下文信息"
    )
    options: Optional[Dict[str, Any]] = Field(
        default=None,
        description="分析选项"
    )


class AnalysisIssue(BaseModel):
    """分析发现的问题"""
    type: str = Field(description="问题类型")
    severity: Literal["low", "medium", "high", "critical"] = Field(
        description="严重程度"
    )
    message: str = Field(description="问题描述")
    line: Optional[int] = Field(default=None, description="行号")
    column: Optional[int] = Field(default=None, description="列号")
    rule_id: Optional[str] = Field(default=None, description="规则ID")
    suggestion: Optional[str] = Field(default=None, description="修复建议")
    code_snippet: Optional[str] = Field(default=None, description="代码片段")


class CodeMetrics(BaseModel):
    """代码度量"""
    complexity: Optional[int] = Field(default=None, description="复杂度")
    lines_of_code: Optional[int] = Field(default=None, description="代码行数")
    lines_of_comments: Optional[int] = Field(default=None, description="注释行数")
    maintainability_index: Optional[float] = Field(
        default=None,
        description="可维护性指数"
    )
    technical_debt: Optional[float] = Field(
        default=None,
        description="技术债务（小时）"
    )
    test_coverage: Optional[float] = Field(
        default=None,
        description="测试覆盖率"
    )
    duplicated_lines: Optional[int] = Field(
        default=None,
        description="重复代码行数"
    )


class SecurityVulnerability(BaseModel):
    """安全漏洞"""
    cwe_id: Optional[str] = Field(default=None, description="CWE ID")
    owasp_category: Optional[str] = Field(
        default=None,
        description="OWASP分类"
    )
    severity: Literal["low", "medium", "high", "critical"] = Field(
        description="严重程度"
    )
    description: str = Field(description="漏洞描述")
    location: Optional[str] = Field(default=None, description="位置")
    remediation: Optional[str] = Field(default=None, description="修复方案")


class CodeAnalysisResult(BaseModel):
    """代码分析结果"""
    type: str = Field(description="分析类型")
    success: bool = Field(description="是否成功")
    issues: Optional[List[AnalysisIssue]] = Field(
        default=None,
        description="问题列表"
    )
    metrics: Optional[CodeMetrics] = Field(
        default=None,
        description="代码度量"
    )
    vulnerabilities: Optional[List[SecurityVulnerability]] = Field(
        default=None,
        description="安全漏洞"
    )
    recommendations: Optional[List[str]] = Field(
        default=None,
        description="改进建议"
    )
    score: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=100.0,
        description="评分（0-100）"
    )
    details: Optional[Dict[str, Any]] = Field(
        default=None,
        description="详细信息"
    )


class CodeAnalysisResponse(BaseResponse):
    """代码分析响应"""
    object: str = Field(default="code.analysis", description="对象类型")
    result: CodeAnalysisResult = Field(description="分析结果")
    usage: Optional[Usage] = Field(default=None, description="使用量")


class DebugRequest(BaseRequest):
    """代码调试请求"""
    code: str = Field(description="待调试的代码")
    error_message: Optional[str] = Field(
        default=None,
        description="错误消息"
    )
    error_traceback: Optional[str] = Field(
        default=None,
        description="错误堆栈"
    )
    language: str = Field(description="编程语言")
    context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="运行上下文"
    )
    inputs: Optional[Dict[str, Any]] = Field(
        default=None,
        description="输入参数"
    )
    expected_output: Optional[Any] = Field(
        default=None,
        description="期望输出"
    )
    debug_level: Literal["basic", "detailed", "comprehensive"] = Field(
        default="basic",
        description="调试级别"
    )


class ErrorLocation(BaseModel):
    """错误位置"""
    file: Optional[str] = Field(default=None, description="文件名")
    line: Optional[int] = Field(default=None, description="行号")
    column: Optional[int] = Field(default=None, description="列号")
    function: Optional[str] = Field(default=None, description="函数名")
    code_snippet: Optional[str] = Field(default=None, description="代码片段")


class DebugSuggestion(BaseModel):
    """调试建议"""
    type: Literal["fix", "improvement", "warning"] = Field(
        description="建议类型"
    )
    description: str = Field(description="建议描述")
    location: Optional[ErrorLocation] = Field(
        default=None,
        description="相关位置"
    )
    code_change: Optional[str] = Field(
        default=None,
        description="代码修改建议"
    )
    explanation: Optional[str] = Field(
        default=None,
        description="解释说明"
    )


class FixedCode(BaseModel):
    """修复后的代码"""
    content: str = Field(description="修复后的代码")
    changes: List[str] = Field(description="修改说明")
    verified: Optional[bool] = Field(
        default=None,
        description="是否验证通过"
    )


class DebugResponse(BaseResponse):
    """代码调试响应"""
    object: str = Field(default="code.debug", description="对象类型")
    error_type: Optional[str] = Field(default=None, description="错误类型")
    root_cause: Optional[str] = Field(default=None, description="根本原因")
    error_location: Optional[ErrorLocation] = Field(
        default=None,
        description="错误位置"
    )
    suggestions: List[DebugSuggestion] = Field(description="修复建议")
    fixed_code: Optional[FixedCode] = Field(
        default=None,
        description="修复后的代码"
    )
    usage: Optional[Usage] = Field(default=None, description="使用量")


class CodeGenerationRequest(BaseRequest):
    """代码生成请求"""
    prompt: str = Field(description="生成提示")
    language: str = Field(description="目标编程语言")
    style: Optional[Literal["functional", "oop", "procedural"]] = Field(
        default=None,
        description="代码风格"
    )
    framework: Optional[str] = Field(
        default=None,
        description="框架名称"
    )
    libraries: Optional[List[str]] = Field(
        default=None,
        description="依赖库"
    )
    constraints: Optional[List[str]] = Field(
        default=None,
        description="约束条件"
    )
    examples: Optional[List[str]] = Field(
        default=None,
        description="示例代码"
    )
    context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="上下文信息"
    )
    max_tokens: Optional[int] = Field(
        default=2000,
        description="最大token数"
    )
    temperature: Optional[float] = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="采样温度"
    )


class GeneratedFile(BaseModel):
    """生成的文件"""
    filename: str = Field(description="文件名")
    content: str = Field(description="文件内容")
    language: str = Field(description="编程语言")
    description: Optional[str] = Field(
        default=None,
        description="文件说明"
    )


class CodeGenerationResponse(BaseResponse):
    """代码生成响应"""
    object: str = Field(default="code.generation", description="对象类型")
    code: str = Field(description="生成的代码")
    files: Optional[List[GeneratedFile]] = Field(
        default=None,
        description="生成的文件列表"
    )
    explanation: Optional[str] = Field(
        default=None,
        description="生成说明"
    )
    dependencies: Optional[List[str]] = Field(
        default=None,
        description="依赖项"
    )
    usage: Optional[Usage] = Field(default=None, description="使用量")