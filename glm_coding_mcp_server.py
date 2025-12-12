#!/usr/bin/env python3
"""
GLM Coding API MCP服务器
为Claude Code提供GLM-4编程模型集成
"""

import json
import sys
import requests
from typing import Dict, Any, List
import os

class GLMCodingMCPServer:
    def __init__(self):
        self.api_key = os.getenv("GLM_API_KEY", "13beba9abe974c7d97250b9778ca4447.8yR9f0F44Yv0YEX8")
        self.base_url = os.getenv("GLM_API_ENDPOINT", "https://open.bigmodel.cn/api/coding/paas/v4/chat/completions")
        self.model = os.getenv("GLM_MODEL", "glm-4")
        self.timeout = int(os.getenv("GLM_API_TIMEOUT", "120"))

    def chat_completion(self, messages: List[Dict], **kwargs) -> Dict[str, Any]:
        """调用GLM Coding API进行对话补全"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": self.model,
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", 65536),
            "temperature": kwargs.get("temperature", 0.1),
            "top_p": kwargs.get("top_p", 0.9)
        }

        try:
            response = requests.post(
                self.base_url,
                headers=headers,
                json=data,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"API请求失败: {str(e)}"}
        except Exception as e:
            return {"error": f"未知错误: {str(e)}"}

    def generate_code(self, prompt: str, language: str = None) -> str:
        """生成代码"""
        if language:
            prompt = f"用{language}编写：{prompt}"

        messages = [{"role": "user", "content": prompt}]
        result = self.chat_completion(messages)

        if "error" in result:
            return f"API错误: {result['error']}"

        if "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0]["message"]["content"]

        return "生成失败，未收到有效响应"

    def explain_code(self, code: str) -> str:
        """解释代码"""
        prompt = f"请解释以下代码的作用：\n\n{code}"
        return self.generate_code(prompt)

    def debug_code(self, code: str, error_info: str = None) -> str:
        """调试代码"""
        prompt = f"请帮我调试以下代码"
        if error_info:
            prompt += f"，错误信息：{error_info}"
        prompt += f"：\n\n{code}"
        return self.generate_code(prompt)

    def optimize_code(self, code: str) -> str:
        """优化代码"""
        prompt = f"请优化以下代码的性能和可读性：\n\n{code}"
        return self.generate_code(prompt)

def main():
    server = GLMCodingMCPServer()

    # 处理MCP协议消息
    for line in sys.stdin:
        try:
            message = json.loads(line.strip())

            if message.get("method") == "initialize":
                response = {
                    "jsonrpc": "2.0",
                    "id": message.get("id"),
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {}
                        },
                        "serverInfo": {
                            "name": "glm-coding-mcp-server",
                            "version": "1.0.0"
                        }
                    }
                }
            elif message.get("method") == "tools/list":
                response = {
                    "jsonrpc": "2.0",
                    "id": message.get("id"),
                    "result": {
                        "tools": [
                            {
                                "name": "glm_generate_code",
                                "description": "使用GLM-4生成代码",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "prompt": {
                                            "type": "string",
                                            "description": "代码生成提示"
                                        },
                                        "language": {
                                            "type": "string",
                                            "description": "编程语言（可选）"
                                        }
                                    },
                                    "required": ["prompt"]
                                }
                            },
                            {
                                "name": "glm_explain_code",
                                "description": "使用GLM-4解释代码",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "code": {
                                            "type": "string",
                                            "description": "要解释的代码"
                                        }
                                    },
                                    "required": ["code"]
                                }
                            },
                            {
                                "name": "glm_debug_code",
                                "description": "使用GLM-4调试代码",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "code": {
                                            "type": "string",
                                            "description": "要调试的代码"
                                        },
                                        "error": {
                                            "type": "string",
                                            "description": "错误信息（可选）"
                                        }
                                    },
                                    "required": ["code"]
                                }
                            },
                            {
                                "name": "glm_optimize_code",
                                "description": "使用GLM-4优化代码",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "code": {
                                            "type": "string",
                                            "description": "要优化的代码"
                                        }
                                    },
                                    "required": ["code"]
                                }
                            }
                        ]
                    }
                }
            elif message.get("method") == "tools/call":
                params = message.get("params", {})
                tool_name = params.get("name")
                arguments = params.get("arguments", {})

                if tool_name == "glm_generate_code":
                    result = server.generate_code(
                        arguments.get("prompt", ""),
                        arguments.get("language")
                    )
                elif tool_name == "glm_explain_code":
                    result = server.explain_code(arguments.get("code", ""))
                elif tool_name == "glm_debug_code":
                    result = server.debug_code(
                        arguments.get("code", ""),
                        arguments.get("error")
                    )
                elif tool_name == "glm_optimize_code":
                    result = server.optimize_code(arguments.get("code", ""))
                else:
                    result = f"未知工具: {tool_name}"

                response = {
                    "jsonrpc": "2.0",
                    "id": message.get("id"),
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": result
                            }
                        ]
                    }
                }
            else:
                response = {
                    "jsonrpc": "2.0",
                    "id": message.get("id"),
                    "error": {
                        "code": -32601,
                        "message": "方法未找到"
                    }
                }

            print(json.dumps(response, ensure_ascii=False))
            sys.stdout.flush()

        except json.JSONDecodeError:
            continue
        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": message.get("id") if 'message' in locals() else None,
                "error": {
                    "code": -32603,
                    "message": f"内部错误: {str(e)}"
                }
            }
            print(json.dumps(error_response, ensure_ascii=False))
            sys.stdout.flush()

if __name__ == "__main__":
    main()