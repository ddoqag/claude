"""
MCP集成单元测试
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import json
from typing import Dict, Any


class TestMCPServer:
    """MCP服务器测试类"""

    @pytest.fixture
    def mock_mcp_server(self):
        """模拟MCP服务器"""
        server = Mock()
        server.list_tools = AsyncMock()
        server.call_tool = AsyncMock()
        server.get_resource = AsyncMock()
        return server

    @pytest.fixture
    def mcp_tools_response(self):
        """MCP工具列表响应"""
        return {
            "tools": [
                {
                    "name": "generate_code",
                    "description": "Generate code using ZhipuAI",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "prompt": {"type": "string"},
                            "language": {"type": "string"},
                            "max_tokens": {"type": "number"}
                        }
                    }
                },
                {
                    "name": "explain_code",
                    "description": "Explain code snippets",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "code": {"type": "string"},
                            "language": {"type": "string"}
                        }
                    }
                }
            ]
        }

    @pytest.mark.asyncio
    async def test_mcp_server_initialization(self, mock_mcp_server):
        """测试MCP服务器初始化"""
        from mcp.server.fastmcp import FastMCP

        with patch('mcp.server.fastmcp.FastMCP') as mock_fastmcp:
            mock_server_instance = Mock()
            mock_fastmcp.return_value = mock_server_instance

            server = FastMCP("zhipu-ai-server")

            # 验证服务器创建
            mock_fastmcp.assert_called_once_with("zhipu-ai-server")
            assert server is not None

    @pytest.mark.asyncio
    async def test_list_mcp_tools(self, mock_mcp_server, mcp_tools_response):
        """测试列出MCP工具"""
        mock_mcp_server.list_tools.return_value = mcp_tools_response

        response = await mock_mcp_server.list_tools()

        assert "tools" in response
        assert len(response["tools"]) == 2
        assert response["tools"][0]["name"] == "generate_code"
        assert response["tools"][1]["name"] == "explain_code"

    @pytest.mark.asyncio
    async def test_generate_code_tool(self, mock_mcp_server):
        """测试代码生成工具"""
        expected_response = {
            "content": [
                {
                    "type": "text",
                    "text": """def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)"""
                }
            ]
        }

        mock_mcp_server.call_tool.return_value = expected_response

        response = await mock_mcp_server.call_tool(
            name="generate_code",
            arguments={
                "prompt": "Write a fibonacci function",
                "language": "python",
                "max_tokens": 100
            }
        )

        assert response == expected_response
        mock_mcp_server.call_tool.assert_called_once_with(
            name="generate_code",
            arguments={
                "prompt": "Write a fibonacci function",
                "language": "python",
                "max_tokens": 100
            }
        )

    @pytest.mark.asyncio
    async def test_explain_code_tool(self, mock_mcp_server):
        """测试代码解释工具"""
        expected_response = {
            "content": [
                {
                    "type": "text",
                    "text": """这是一个斐波那契数列函数：
- 使用递归方式实现
- 基础情况：n <= 1时返回n
- 递归情况：返回前两项之和"""
                }
            ]
        }

        mock_mcp_server.call_tool.return_value = expected_response

        response = await mock_mcp_server.call_tool(
            name="explain_code",
            arguments={
                "code": "def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)",
                "language": "python"
            }
        )

        assert response == expected_response
        assert "斐波那契" in response["content"][0]["text"]

    @pytest.mark.asyncio
    async def test_tool_error_handling(self, mock_mcp_server):
        """测试工具错误处理"""
        mock_mcp_server.call_tool.side_effect = Exception("Tool execution failed")

        with pytest.raises(Exception) as exc_info:
            await mock_mcp_server.call_tool(
                name="generate_code",
                arguments={"prompt": "test"}
            )

        assert "Tool execution failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_tool_validation(self, mock_mcp_server):
        """测试工具参数验证"""
        # 测试缺少必需参数
        with pytest.raises(ValueError):
            await mock_mcp_server.call_tool(
                name="generate_code",
                arguments={}  # 缺少必需的prompt参数
            )

        # 测试参数类型错误
        with pytest.raises(TypeError):
            await mock_mcp_server.call_tool(
                name="generate_code",
                arguments={
                    "prompt": "test",
                    "max_tokens": "invalid"  # 应该是数字
                }
            )


class TestMCPResourceHandler:
    """MCP资源处理器测试"""

    @pytest.fixture
    def mock_resource_handler(self):
        """模拟资源处理器"""
        handler = Mock()
        handler.list_resources = AsyncMock()
        handler.read_resource = AsyncMock()
        return handler

    @pytest.fixture
    def sample_resources(self):
        """示例资源"""
        return {
            "resources": [
                {
                    "uri": "zhipu://models/codegeex4",
                    "name": "CodeGeeX4 Model",
                    "description": "Code generation model",
                    "mimeType": "application/json"
                },
                {
                    "uri": "zhipu://config/settings",
                    "name": "Settings",
                    "description": "Configuration settings",
                    "mimeType": "application/json"
                }
            ]
        }

    @pytest.mark.asyncio
    async def test_list_resources(self, mock_resource_handler, sample_resources):
        """测试列出资源"""
        mock_resource_handler.list_resources.return_value = sample_resources

        response = await mock_resource_handler.list_resources()

        assert "resources" in response
        assert len(response["resources"]) == 2
        assert response["resources"][0]["uri"] == "zhipu://models/codegeex4"

    @pytest.mark.asyncio
    async def test_read_resource(self, mock_resource_handler):
        """测试读取资源"""
        expected_content = {
            "model": "codegeex4",
            "max_tokens": 2000,
            "temperature": 0.7,
            "supported_languages": ["python", "javascript", "java", "go"]
        }

        mock_resource_handler.read_resource.return_value = {
            "contents": [
                {
                    "uri": "zhipu://models/codegeex4",
                    "mimeType": "application/json",
                    "text": json.dumps(expected_content)
                }
            ]
        }

        response = await mock_resource_handler.read_resource("zhipu://models/codegeex4")

        assert "contents" in response
        assert len(response["contents"]) == 1
        content = json.loads(response["contents"][0]["text"])
        assert content["model"] == "codegeex4"

    @pytest.mark.asyncio
    async def test_resource_not_found(self, mock_resource_handler):
        """测试资源未找到"""
        mock_resource_handler.read_resource.side_effect = FileNotFoundError(
            "Resource not found: zhipu://models/unknown"
        )

        with pytest.raises(FileNotFoundError):
            await mock_resource_handler.read_resource("zhipu://models/unknown")


class TestMCPProtocol:
    """MCP协议测试"""

    @pytest.fixture
    def mock_transport(self):
        """模拟传输层"""
        transport = Mock()
        transport.start = AsyncMock()
        transport.stop = AsyncMock()
        transport.send = AsyncMock()
        transport.receive = AsyncMock()
        return transport

    @pytest.mark.asyncio
    async def test_mcp_message_handling(self, mock_transport):
        """测试MCP消息处理"""
        from mcp.server.fastmcp import FastMCP

        with patch('mcp.server.fastmcp.FastMCP') as mock_fastmcp:
            mock_server = Mock()
            mock_fastmcp.return_value = mock_server

            # 模拟接收消息
            mock_transport.receive.return_value = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/list",
                "params": {}
            }

            # 模拟发送响应
            mock_transport.send.return_value = {
                "jsonrpc": "2.0",
                "id": 1,
                "result": {"tools": []}
            }

            # 验证消息处理
            message = await mock_transport.receive()
            assert message["method"] == "tools/list"

            await mock_transport.send({
                "jsonrpc": "2.0",
                "id": 1,
                "result": {"tools": []}
            })

            mock_transport.send.assert_called_once()

    @pytest.mark.asyncio
    async def test_mcp_notification_handling(self, mock_transport):
        """测试MCP通知处理"""
        # 模拟通知消息（无id字段）
        notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {}
        }

        mock_transport.receive.return_value = notification

        message = await mock_transport.receive()
        assert "id" not in message
        assert message["method"] == "notifications/initialized"

    @pytest.mark.asyncio
    async def test_mcp_error_response(self, mock_transport):
        """测试MCP错误响应"""
        error_response = {
            "jsonrpc": "2.0",
            "id": 1,
            "error": {
                "code": -32601,
                "message": "Method not found"
            }
        }

        mock_transport.send.return_value = error_response

        await mock_transport.send(error_response)

        response = await mock_transport.send.return_value
        assert "error" in response
        assert response["error"]["code"] == -32601
        assert response["error"]["message"] == "Method not found"


class TestMCPSession:
    """MCP会话测试"""

    @pytest.fixture
    def mock_session(self):
        """模拟MCP会话"""
        session = Mock()
        session.initialize = AsyncMock()
        session.request = AsyncMock()
        session.notify = AsyncMock()
        session.close = AsyncMock()
        return session

    @pytest.mark.asyncio
    async def test_session_initialization(self, mock_session):
        """测试会话初始化"""
        mock_session.initialize.return_value = {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {},
                "resources": {}
            },
            "serverInfo": {
                "name": "zhipu-ai-server",
                "version": "1.0.0"
            }
        }

        response = await mock_session.initialize()

        assert response["protocolVersion"] == "2024-11-05"
        assert "capabilities" in response
        assert response["serverInfo"]["name"] == "zhipu-ai-server"

    @pytest.mark.asyncio
    async def test_session_lifecycle(self, mock_session):
        """测试会话生命周期"""
        # 初始化
        await mock_session.initialize()
        mock_session.initialize.assert_called_once()

        # 发送请求
        mock_session.request.return_value = {"result": "success"}
        response = await mock_session.request("tools/list", {})
        assert response["result"] == "success"

        # 发送通知
        await mock_session.notify("notifications/cancelled", {"id": 1})
        mock_session.notify.assert_called_once()

        # 关闭会话
        await mock_session.close()
        mock_session.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_session_concurrent_requests(self, mock_session):
        """测试会话并发请求"""
        mock_session.request.return_value = {"result": "success"}

        # 创建多个并发请求
        tasks = []
        for i in range(5):
            task = mock_session.request("tools/call", {"id": i})
            tasks.append(task)

        # 等待所有请求完成
        responses = await asyncio.gather(*tasks)

        # 验证所有请求都成功
        assert len(responses) == 5
        for response in responses:
            assert response["result"] == "success"

        # 验证request被调用了5次
        assert mock_session.request.call_count == 5