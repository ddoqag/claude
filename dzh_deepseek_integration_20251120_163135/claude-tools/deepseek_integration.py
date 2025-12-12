#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DeepSeek集成器 - 直接API调用
绕过Web界面，直接调用DeepSeek后端API
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional

class DeepSeekIntegration:
    """DeepSeek直接集成器"""

    def __init__(self):
        self.base_url = "https://f.dzh.com.cn/zswd/newask"
        self.token_manager_path = "/home/ddo/.config/claude-tools/fast_token_manager.py"

    def get_active_token(self) -> Optional[str]:
        """获取活跃的Token"""
        try:
            import subprocess
            result = subprocess.run([
                'python3', self.token_manager_path, 'best'
            ], capture_output=True, text=True, timeout=10)

            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
            return None
        except Exception as e:
            print(f"❌ 获取Token失败: {e}")
            return None

    def build_api_url(self, token: str, scene_code: str = "399001",
                      scene_name: str = "深圳成指", scene_desc: str = None) -> str:
        """构建API URL"""
        params = {
            'tun': 'dzhsp846',
            'token': token,
            'version': '2.0.45',
            'scene': 'gg',
            'sceneName': scene_name,
            'sceneCode': scene_code,
            'sceneDesc': scene_desc or f"分析{scene_name}的实时走势和技术指标"
        }

        param_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        return f"{self.base_url}?{param_string}"

    def direct_api_call(self, query: str, scene_code: str = "399001",
                        scene_name: str = "深圳成指") -> Dict[str, Any]:
        """直接API调用，返回JSON响应"""
        token = self.get_active_token()
        if not token:
            return {
                "success": False,
                "error": "无法获取有效Token",
                "timestamp": datetime.now().isoformat()
            }

        # 构建请求数据
        data = {
            "question": query,
            "scene": "gg",
            "sceneName": scene_name,
            "sceneCode": scene_code,
            "token": token,
            "tunnel": "dzhsp846",
            "version": "2.0.45",
            "timestamp": int(time.time())
        }

        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'DeepSeek-Client/1.0',
            'Accept': 'application/json'
        }

        try:
            # 尝试不同的API端点
            endpoints = [
                "https://f.dzh.com.cn/zswd/api/ask",
                "https://f.dzh.com.cn/api/deepseek/ask",
                "https://api.dzh.com.cn/deepseek/ask"
            ]

            for endpoint in endpoints:
                try:
                    response = requests.post(
                        endpoint,
                        json=data,
                        headers=headers,
                        timeout=30
                    )

                    if response.status_code == 200:
                        try:
                            result = response.json()
                            return {
                                "success": True,
                                "data": result,
                                "endpoint": endpoint,
                                "timestamp": datetime.now().isoformat()
                            }
                        except json.JSONDecodeError:
                            return {
                                "success": False,
                                "error": f"返回非JSON格式: {response.text[:200]}",
                                "endpoint": endpoint,
                                "timestamp": datetime.now().isoformat()
                            }

                except requests.exceptions.RequestException as e:
                    continue  # 尝试下一个端点

            return {
                "success": False,
                "error": "所有API端点都无法访问",
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"API调用失败: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }

    def analyze_shenzhen_market(self) -> Dict[str, Any]:
        """分析深圳市场"""
        query = """
        请详细分析今天深圳市场的以下方面：
        1. 深圳成指(399001)的实时走势
        2. 成交量和市场活跃度
        3. 热点板块表现
        4. 技术指标分析(MACD, KDJ, RSI)
        5. 市场情绪和资金流向
        6. 短期走势预测和投资建议
        请提供具体的数值和分析结论。
        """

        return self.direct_api_call(query, "399001", "深圳成指")

    def get_market_summary(self) -> str:
        """获取市场摘要"""
        result = self.analyze_shenzhen_market()

        if result["success"]:
            return f"""
🎯 深圳市场分析报告
===================

📊 分析时间: {result['timestamp']}
🔗 API端点: {result.get('endpoint', '未知')}

📈 分析结果:
{json.dumps(result['data'], ensure_ascii=False, indent=2)}

⚠️  风险提示:
- AI分析仅供参考，不构成投资建议
- 投资有风险，入市需谨慎
- 请结合自身风险承受能力做决策
            """
        else:
            return f"""
❌ DeepSeek分析失败
==================

错误信息: {result['error']}
时间戳: {result['timestamp']}

🔧 建议解决方案:
1. 检查Token有效性
2. 验证网络连接
3. 确认API服务状态
            """

# 命令行接口
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1]

        ds = DeepSeekIntegration()

        if command == "analyze" or command == "shenzhen":
            print("🔍 正在分析深圳市场...")
            result = ds.get_market_summary()
            print(result)

        elif command == "token":
            token = ds.get_active_token()
            if token:
                print(f"✅ 当前Token: {token[:30]}...")
            else:
                print("❌ 无法获取Token")

        elif command == "test":
            print("🧪 测试DeepSeek集成...")
            result = ds.direct_api_call("测试连接", "000001", "平安银行")
            print(json.dumps(result, ensure_ascii=False, indent=2))

        else:
            print(f"未知命令: {command}")
            print("可用命令: analyze, token, test")
    else:
        print("DeepSeek集成器 v1.0")
        print("用法: python3 deepseek_integration.py <command>")
        print("命令: analyze, token, test")