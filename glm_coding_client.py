#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import os

class GLMCodingClient:
    def __init__(self):
        self.api_key = "13beba9abe974c7d97250b9778ca4447.8yR9f0F44Yv0YEX8"
        self.endpoint = "https://open.bigmodel.cn/api/coding/paas/v4/chat/completions"
        self.model = "glm-4"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def generate_code(self, prompt, language=None):
        """生成代码"""
        if language:
            prompt = f"用{language}编写：{prompt}"

        data = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }

        try:
            response = requests.post(self.endpoint, headers=self.headers, json=data)
            response.raise_for_status()
            result = response.json()

            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
            else:
                return "API返回异常"

        except Exception as e:
            return f"请求失败: {str(e)}"

    def explain_code(self, code):
        """解释代码"""
        prompt = f"请解释以下代码的作用：\n\n{code}"
        return self.generate_code(prompt)

    def optimize_code(self, code, language=None):
        """优化代码"""
        prompt = f"优化以下{language or ''}代码的性能和可读性：\n\n{code}"
        return self.generate_code(prompt)

# 使用示例
if __name__ == "__main__":
    client = GLMCodingClient()

    # 示例1：生成Python代码
    print("=== 生成Python排序算法 ===")
    python_code = client.generate_code("编写一个快速排序算法", "Python")
    print(python_code)

    # 示例2：生成JavaScript代码
    print("\n=== 生成JavaScript函数 ===")
    js_code = client.generate_code("创建一个防抖函数", "JavaScript")
    print(js_code)

    # 示例3：代码解释
    print("\n=== 代码解释 ===")
    code_to_explain = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
"""
    explanation = client.explain_code(code_to_explain)
    print(explanation)