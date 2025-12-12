#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DZH DeepSeek自然语言对话接口
支持真正的自然语言交流，基于DZH配置的DeepSeek API
"""

import os
import sys
import json
import asyncio
import aiohttp
from datetime import datetime
from typing import Dict, List, Optional, Any
import xml.etree.ElementTree as ET

# 添加DZH系统集成
sys.path.append('/mnt/d/dzh365(64)')
from deepseek_stock_prediction_integration import DZHDeepSeekIntegrator

class DZHDeepSeekChatInterface:
    """DZH DeepSeek自然语言对话接口"""

    def __init__(self):
        self.config_path = "/mnt/d/dzh365(64)/cfg/deepseek.xml"
        self.integrator = DZHDeepSeekIntegrator()
        self.session = None
        self.conversation_history = []

        # 预设的对话场景
        self.chat_scenes = {
            "股票分析": "分析股票走势、技术指标、投资建议",
            "市场预测": "预测市场整体走势和板块表现",
            "财经新闻": "解读财经新闻和市场事件",
            "投资策略": "制定个人投资策略和资产配置",
            "风险评估": "分析投资风险和给出风险提示",
            "公司分析": "深入分析公司基本面和财务状况"
        }

    async def initialize(self, auth_token: Optional[str] = None) -> bool:
        """初始化对话接口"""
        try:
            print("🤖 初始化DZH DeepSeek自然语言对话接口...")

            # 加载配置
            if not self.integrator.load_config():
                print("❌ 配置加载失败")
                return False

            # 设置认证Token
            if auth_token:
                self.integrator.set_auth_token(auth_token)
            else:
                # 尝试从环境变量获取
                env_token = os.getenv('DEEPSEEK_CURRENT_TOKEN')
                if env_token:
                    self.integrator.set_auth_token(env_token)
                    print(f"✅ 使用环境变量Token: {env_token[:10]}...")
                else:
                    print("⚠️ 未设置Token，将使用模拟模式")

            # 创建HTTP会话
            self.session = aiohttp.ClientSession()

            print("✅ 自然语言对话接口初始化完成")
            return True

        except Exception as e:
            print(f"❌ 初始化失败: {str(e)}")
            return False

    async def send_message(self, message: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """发送自然语言消息并获得AI回复"""
        try:
            # 添加到对话历史
            self.conversation_history.append({
                "role": "user",
                "message": message,
                "timestamp": datetime.now().isoformat()
            })

            # 构建完整的对话上下文
            full_context = self._build_conversation_context(message, context)

            # 调用DeepSeek API
            response = await self._call_deepseek_chat(full_context)

            if response:
                # 添加AI回复到历史
                self.conversation_history.append({
                    "role": "assistant",
                    "message": response,
                    "timestamp": datetime.now().isoformat()
                })

                return {
                    "success": True,
                    "response": response,
                    "context": full_context,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": "AI回复获取失败",
                    "timestamp": datetime.now().isoformat()
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"发送消息失败: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }

    def _build_conversation_context(self, current_message: str, additional_context: Optional[Dict] = None) -> str:
        """构建对话上下文"""
        context_parts = []

        # 添加系统提示
        system_prompt = """你是DZH DeepSeek AI助手，专业的金融投资顾问。请基于以下原则回答用户问题：

1. 专业准确：提供准确、专业的金融分析和投资建议
2. 风险提示：始终包含适当的风险提示
3. 个性化：根据用户的具体情况提供个性化建议
4. 实时性：基于最新的市场信息和数据进行分析
5. 可操作性：提供具体的、可操作的投资建议

当前时间是：""" + datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        context_parts.append(system_prompt)

        # 添加额外上下文
        if additional_context:
            if "current_stock" in additional_context:
                context_parts.append(f"当前关注股票: {additional_context['current_stock']}")
            if "market_data" in additional_context:
                context_parts.append(f"市场数据: {additional_context['market_data']}")
            if "user_preference" in additional_context:
                context_parts.append(f"用户偏好: {additional_context['user_preference']}")

        # 添加对话历史（最近3轮）
        if len(self.conversation_history) > 0:
            context_parts.append("\n最近的对话历史:")
            for msg in self.conversation_history[-6:]:  # 最近3轮对话
                role = "用户" if msg["role"] == "user" else "助手"
                context_parts.append(f"{role}: {msg['message']}")

        # 添加当前消息
        context_parts.append(f"\n用户当前问题: {current_message}")

        return "\n".join(context_parts)

    async def _call_deepseek_chat(self, context: str) -> Optional[str]:
        """调用DeepSeek聊天API"""
        try:
            if not self.integrator.auth_token or self.integrator.auth_token == "#V3TOKEN#":
                return self._get_mock_chat_response(context)

            # 构建API请求URL
            base_url = "https://f.dzh.com.cn/zswd/newask"
            params = {
                "tun": self.integrator.tunnel,
                "token": self.integrator.auth_token,
                "version": self.integrator.version,
                "scene": "chat",
                "sceneName": "自然语言对话",
                "sceneCode": "CHAT001",
                "sceneDesc": "智能投资顾问对话"
            }

            query_string = "&".join([f"{k}={v}" for k, v in params.items()])
            url = f"{base_url}?{query_string}"

            # 发送聊天请求
            chat_data = {
                "message": context,
                "type": "text",
                "timestamp": datetime.now().isoformat()
            }

            async with self.session.post(url, json=chat_data, timeout=30) as response:
                if response.status == 200:
                    result = await response.text()

                    # 尝试解析JSON响应
                    try:
                        json_result = json.loads(result)
                        if "response" in json_result:
                            return json_result["response"]
                        elif "answer" in json_result:
                            return json_result["answer"]
                        elif "data" in json_result:
                            return json_result["data"]
                        else:
                            return result
                    except json.JSONDecodeError:
                        return result
                else:
                    print(f"❌ API请求失败: HTTP {response.status}")
                    return self._get_mock_chat_response(context)

        except Exception as e:
            print(f"❌ 调用DeepSeek聊天API失败: {str(e)}")
            return self._get_mock_chat_response(context)

    def _get_mock_chat_response(self, context: str) -> str:
        """生成模拟聊天回复"""
        # 简单的关键词匹配生成回复
        if any(word in context for word in ["股票", "投资", "买入"]):
            return """基于当前市场情况，我为您提供以下投资建议：

📈 市场分析：
- 当前A股市场处于震荡上行阶段
- 科技板块表现活跃，新能源、半导体板块领涨
- 成交量温和放大，市场情绪相对乐观

💡 投资建议：
1. 短期可关注热点板块的轮动机会
2. 中线建议配置核心资产，关注业绩优良的白马股
3. 控制仓位在7成左右，保留灵活资金

⚠️ 风险提示：
- 注意外围市场波动影响
- 谨慎追高，注意止盈止损
- 关注政策面变化

如需分析具体股票，请告诉我股票代码，我将为您提供详细分析。"""

        elif any(word in context for word in ["市场", "走势", "预测"]):
            return """📊 市场走势分析：

🔥 热点板块：
1. 新能源汽车：政策支持力度大，行业景气度高
2. 半导体芯片：国产替代加速，技术突破明显
3. 人工智能：应用场景丰富，成长空间巨大

📈 技术面分析：
- 大盘指数在关键支撑位获得支撑
- 成交量配合良好，上涨趋势有望延续
- MACD指标金叉向上，短期趋势偏强

🎯 操作策略：
- 短线：关注热点板块回调机会
- 中线：布局成长性好的优质股票
- 长线：重点关注科技创新和消费升级

您有什么具体问题需要咨询吗？"""

        else:
            return """您好！我是DZH DeepSeek AI投资助手，很高兴为您服务！

我可以为您提供以下专业的金融服务：
📈 股票分析和投资建议
📊 市场走势预测和解读
💼 个股深度分析和风险评估
📰 财经新闻解读和市场分析
🎯 个性化投资策略制定

请告诉我您想了解什么，我将为您提供专业的分析和建议。比如：
- "分析一下贵州茅台的投资价值"
- "当前市场走势如何？"
- "新能源汽车板块值得投资吗？"
- "帮我分析一下我的持仓组合" """

    def get_conversation_history(self) -> List[Dict]:
        """获取对话历史"""
        return self.conversation_history

    def clear_conversation_history(self):
        """清空对话历史"""
        self.conversation_history.clear()
        print("🗑️ 对话历史已清空")

    def get_chat_scenes(self) -> Dict[str, str]:
        """获取可用的对话场景"""
        return self.chat_scenes

    async def analyze_stock(self, stock_code: str) -> Dict[str, Any]:
        """专门的股票分析功能"""
        message = f"请详细分析股票{stock_code}的投资价值，包括基本面分析、技术分析、风险评估和投资建议"
        return await self.send_message(message, {"current_stock": stock_code})

    async def market_analysis(self) -> Dict[str, Any]:
        """专门的市场分析功能"""
        message = "请分析当前A股市场的整体走势，包括主要指数表现、热点板块、资金流向和短期展望"
        return await self.send_message(message, {"analysis_type": "market_overview"})

    async def close(self):
        """关闭对话接口"""
        if self.session:
            await self.session.close()
        print("🔚 DZH DeepSeek对话接口已关闭")

# 命令行接口
async def main():
    """命令行交互界面"""
    print("🤖 DZH DeepSeek自然语言对话系统")
    print("=" * 50)
    print("输入 'help' 查看可用命令")
    print("输入 'quit' 或 'exit' 退出")
    print("=" * 50)

    # 创建对话接口
    chat_interface = DZHDeepSeekChatInterface()

    try:
        # 初始化
        if not await chat_interface.initialize():
            print("❌ 初始化失败，退出")
            return

        print("\n✅ 系统已就绪，请输入您的问题...")

        while True:
            try:
                # 获取用户输入
                user_input = input("\n👤 您: ").strip()

                if not user_input:
                    continue

                # 处理命令
                if user_input.lower() in ['quit', 'exit', '退出']:
                    print("👋 再见！")
                    break

                elif user_input.lower() in ['help', '帮助']:
                    print("""
📋 可用命令:
- help/帮助: 显示帮助信息
- history/历史: 查看对话历史
- clear/清空: 清空对话历史
- scenes/场景: 查看对话场景
- analyze <股票代码>: 分析指定股票
- market/市场: 市场整体分析
- quit/exit/退出: 退出系统

💡 示例问题:
- "分析一下贵州茅台"
- "今天市场怎么样？"
- "新能源汽车值得投资吗？"
- "给我一些投资建议" """)

                elif user_input.lower() in ['history', '历史']:
                    history = chat_interface.get_conversation_history()
                    if history:
                        print(f"\n📜 对话历史 (共 {len(history)} 条):")
                        for i, msg in enumerate(history[-10:], 1):  # 显示最近10条
                            role = "👤 用户" if msg["role"] == "user" else "🤖 助手"
                            print(f"{i}. {role}: {msg['message'][:100]}...")
                    else:
                        print("📭 暂无对话历史")

                elif user_input.lower() in ['clear', '清空']:
                    chat_interface.clear_conversation_history()

                elif user_input.lower() in ['scenes', '场景']:
                    scenes = chat_interface.get_chat_scenes()
                    print("\n🎭 可用对话场景:")
                    for scene, desc in scenes.items():
                        print(f"- {scene}: {desc}")

                elif user_input.lower().startswith('analyze '):
                    stock_code = user_input[8:].strip()
                    if stock_code:
                        print(f"\n🔍 正在分析股票 {stock_code}...")
                        result = await chat_interface.analyze_stock(stock_code)
                        if result["success"]:
                            print(f"\n🤖 DeepSeek: {result['response']}")
                        else:
                            print(f"❌ 分析失败: {result['error']}")
                    else:
                        print("💡 请输入股票代码，例如: analyze 000001")

                elif user_input.lower() in ['market', '市场']:
                    print(f"\n📊 正在进行市场分析...")
                    result = await chat_interface.market_analysis()
                    if result["success"]:
                        print(f"\n🤖 DeepSeek: {result['response']}")
                    else:
                        print(f"❌ 分析失败: {result['error']}")

                else:
                    # 普通对话
                    print(f"\n🔄 正在处理您的问题...")
                    result = await chat_interface.send_message(user_input)

                    if result["success"]:
                        print(f"\n🤖 DeepSeek: {result['response']}")
                    else:
                        print(f"❌ 处理失败: {result['error']}")
                        print("💡 您可以尝试重新提问或检查网络连接")

            except KeyboardInterrupt:
                print("\n\n👋 再见！")
                break
            except Exception as e:
                print(f"\n❌ 处理请求时出错: {str(e)}")
                continue

    finally:
        await chat_interface.close()

if __name__ == "__main__":
    # 运行命令行界面
    asyncio.run(main())