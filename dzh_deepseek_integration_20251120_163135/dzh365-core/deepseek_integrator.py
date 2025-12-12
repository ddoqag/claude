#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DZH DeepSeek股票预测集成器
基于DZH配置文件的DeepSeek AI服务集成，实现股票价格预测功能
"""

import os
import json
import time
import asyncio
import aiohttp
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import xml.etree.ElementTree as ET
import hashlib
import base64

from .data_models import (
    StockData, PredictionResult, BatchPredictionResult,
    MarketSentiment, PredictionReport, PredictionType, TimeHorizon, MarketType
)


class DZHDeepSeekIntegrator:
    """DZH DeepSeek集成器 - 核心预测引擎"""

    def __init__(self, config_path: str = "/mnt/d/dzh365(64)/cfg/deepseek.xml"):
        """
        初始化DeepSeek集成器

        Args:
            config_path: DZH配置文件路径
        """
        self.config_path = config_path
        self.base_url = "https://f.dzh.com.cn/zswd/newask"
        self.auth_token = None
        self.tunnel = "dzhsp846"
        self.version = "1.0"
        self.session = None

        # 支持的分析周期类型
        self.supported_periods = {
            1: "分时", 2: "分笔", 3: "1分钟k线", 4: "5分钟k线",
            5: "15分钟k线", 6: "30分钟k线", 7: "60分钟k线", 8: "日线",
            9: "周线", 10: "月线", 11: "多周期线", 12: "年线", 14: "半年线"
        }

        # 股票名称映射（可扩展）
        self.stock_names = {
            "000001": "平安银行", "000002": "万科A", "000032": "深桑达A",
            "000066": "中国长城", "000513": "粤宏远A", "000555": "神州信息",
            "000710": "贝瑞基因", "000785": "居然之家", "000948": "京山轻机",
            "000997": "新大陆", "002010": "传化智联", "002152": "广电运通",
            "002230": "科大讯飞", "002415": "海康威视", "000858": "五粮液",
            "000858": "五粮液", "600519": "贵州茅台", "600036": "招商银行"
        }

    def load_config(self) -> bool:
        """
        加载DZH配置文件

        Returns:
            bool: 加载是否成功
        """
        try:
            if not os.path.exists(self.config_path):
                print(f"❌ 配置文件不存在: {self.config_path}")
                return False

            # 解析XML配置
            tree = ET.parse(self.config_path)
            root = tree.getroot()

            # 提取URL配置
            url_elem = root.find(".//url")
            if url_elem is not None:
                url_text = url_elem.text
                print(f"📋 解析到配置URL: {url_text[:100]}...")

                # 从URL中提取参数
                if "tun=" in url_text:
                    self.tunnel = url_text.split("tun=")[1].split("&")[0]
                if "version=" in url_text:
                    self.version = url_text.split("version=")[1].split("&")[0]

                return True
            else:
                print("❌ 配置文件中未找到URL配置")
                return False

        except Exception as e:
            print(f"❌ 加载配置文件失败: {str(e)}")
            return False

    def set_auth_token(self, token: str):
        """
        设置认证令牌

        Args:
            token: 认证令牌
        """
        self.auth_token = token
        print(f"🔑 设置认证令牌: {token[:10]}...")

    def generate_token(self, user_id: str, api_key: str) -> str:
        """
        生成认证令牌（示例实现）

        Args:
            user_id: 用户ID
            api_key: API密钥

        Returns:
            str: 生成的令牌
        """
        timestamp = str(int(time.time()))
        raw_string = f"{user_id}:{api_key}:{timestamp}"
        token_hash = hashlib.md5(raw_string.encode()).hexdigest()
        return base64.b64encode(f"{timestamp}:{token_hash}".encode()).decode()

    def build_request_url(self, stock: StockData, period: int = 8) -> str:
        """
        构建DeepSeek API请求URL

        Args:
            stock: 股票数据
            period: 分析周期

        Returns:
            str: 请求URL
        """
        params = {
            "tun": self.tunnel,
            "token": self.auth_token or "#V3TOKEN#",
            "version": self.version,
            "scene": "gg",
            "sceneName": stock.name,
            "sceneCode": f"{stock.market.value}{stock.code}",
            "sceneDesc": f"{self.supported_periods.get(period, '日线')}分析"
        }

        # 构建查询字符串
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        popup_param = "#DZHPOPUP(600,700)#"

        return f"{self.base_url}?{query_string}{popup_param}"

    def get_market_data(self, stock_code: str) -> Optional[StockData]:
        """
        获取市场数据（生产环境应接入真实数据源）

        Args:
            stock_code: 股票代码

        Returns:
            Optional[StockData]: 股票数据
        """
        try:
            # 这里可以接入真实的数据源
            # 目前使用模拟数据进行演示
            import random

            # 基于股票代码生成一致的模拟数据
            random.seed(hash(stock_code) % 10000)

            base_price = random.uniform(10, 100)
            change = random.uniform(-5, 5)
            change_percent = (change / base_price) * 100

            # 确定市场类型
            if stock_code.startswith('6'):
                market = MarketType.SH
            elif stock_code.startswith(('0', '3')):
                market = MarketType.SZ
            elif stock_code.startswith(('8', '4')):
                market = MarketType.BJ
            else:
                market = MarketType.SZ

            stock_data = StockData(
                code=stock_code,
                name=self.stock_names.get(stock_code, f"股票{stock_code}"),
                current_price=round(base_price, 2),
                change_amount=round(change, 2),
                change_percent=round(change_percent, 2),
                volume=random.randint(100000, 10000000),
                market=market,
                timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            )

            return stock_data

        except Exception as e:
            print(f"❌ 获取股票 {stock_code} 数据失败: {str(e)}")
            return None

    async def call_deepseek_api(self, stock: StockData, query: str) -> Optional[str]:
        """
        调用DeepSeek API

        Args:
            stock: 股票数据
            query: 查询内容

        Returns:
            Optional[str]: AI响应结果
        """
        if not self.auth_token or self.auth_token == "#V3TOKEN#":
            print("⚠️ 使用模拟API响应（需要真实Token）")
            return self._get_mock_response(stock, query)

        try:
            # 构建请求URL
            url = self.build_request_url(stock)

            # 创建异步HTTP会话
            if self.session is None:
                self.session = aiohttp.ClientSession()

            # 发送请求
            async with self.session.post(url, json={"query": query}) as response:
                if response.status == 200:
                    result = await response.text()
                    return result
                else:
                    print(f"❌ API请求失败: HTTP {response.status}")
                    return None

        except Exception as e:
            print(f"❌ 调用DeepSeek API失败: {str(e)}")
            return self._get_mock_response(stock, query)

    def _get_mock_response(self, stock: StockData, query: str) -> str:
        """
        生成模拟API响应

        Args:
            stock: 股票数据
            query: 查询内容

        Returns:
            str: 模拟响应
        """
        import random

        # 基于股票数据生成智能响应
        responses = [
            f"基于{stock.name}({stock.code})的技术分析，当前价格为¥{stock.current_price}，"
            f"建议关注支撑位{stock.current_price * 0.95:.2f}元和阻力位{stock.current_price * 1.05:.2f}元。"
            f"今日{stock.change_percent:+.2f}%的涨跌显示市场情绪相对{'积极' if stock.change_percent > 0 else '谨慎'}。",

            f"{stock.name}当前处于相对强势状态，技术指标显示{self._get_trend_description()}趋势。"
            f"考虑到成交量为{stock.volume:,}手，市场参与度{'较高' if stock.volume > 5000000 else '一般'}，"
            f"建议投资者{'可考虑逢低买入' if stock.change_percent < -2 else '保持谨慎乐观'}。",

            f"综合技术面分析，{stock.name}的均线系统呈{'多头排列' if stock.change_percent > 0 else '空头排列'}，"
            f"RSI指标位于{'超买区间' if stock.change_percent > 3 else '正常区间'}，"
            f"预计短期内可能继续{self._get_prediction()}，目标价位{stock.current_price * (1.05 if stock.change_percent > 0 else 0.95):.2f}元。"
        ]

        return random.choice(responses)

    def _get_trend_description(self) -> str:
        """获取趋势描述"""
        import random
        trends = ["上升", "震荡上行", "横盘整理", "震荡下行", "调整", "反弹"]
        return random.choice(trends)

    def _get_prediction(self) -> str:
        """获取预测结果"""
        import random
        predictions = ["上涨", "调整", "盘整", "反弹", "回调"]
        return random.choice(predictions)

    def analyze_ai_response(self, stock: StockData, ai_response: str) -> PredictionResult:
        """
        分析AI响应并生成预测结果

        Args:
            stock: 股票数据
            ai_response: AI响应内容

        Returns:
            PredictionResult: 预测结果
        """
        # 增强的情感分析
        positive_keywords = ["上涨", "买入", "看涨", "支撑", "反弹", "机会", "强势", "积极", "多头"]
        negative_keywords = ["下跌", "卖出", "看跌", "阻力", "风险", "谨慎", "弱势", "消极", "空头"]
        neutral_keywords = ["持有", "观望", "盘整", "震荡", "等待", "横盘", "平稳"]

        positive_score = sum(1 for word in positive_keywords if word in ai_response)
        negative_score = sum(1 for word in negative_keywords if word in ai_response)
        neutral_score = sum(1 for word in neutral_keywords if word in ai_response)

        # 确定预测方向和置信度
        if positive_score > negative_score and positive_score > neutral_score:
            prediction_type = PredictionType.BUY
            confidence = min(0.95, 0.5 + positive_score * 0.08)
            price_target = stock.current_price * (1.05 + positive_score * 0.01)
            time_horizon = TimeHorizon.SHORT_TERM
            risk_level = "中等"
        elif negative_score > positive_score and negative_score > neutral_score:
            prediction_type = PredictionType.SELL
            confidence = min(0.95, 0.5 + negative_score * 0.08)
            price_target = stock.current_price * (0.95 - negative_score * 0.01)
            time_horizon = TimeHorizon.SHORT_TERM
            risk_level = "较高"
        else:
            prediction_type = PredictionType.HOLD
            confidence = 0.6 + neutral_score * 0.05
            price_target = stock.current_price
            time_horizon = TimeHorizon.MEDIUM_TERM
            risk_level = "较低"

        # 提取影响因素
        factors = []
        if "技术" in ai_response or "指标" in ai_response:
            factors.append("技术面分析")
        if "市场" in ai_response or "情绪" in ai_response:
            factors.append("市场情绪")
        if "支撑" in ai_response or "阻力" in ai_response:
            factors.append("关键价位")
        if "成交量" in ai_response or "参与度" in ai_response:
            factors.append("资金流向")
        if "均线" in ai_response:
            factors.append("趋势指标")
        if "RSI" in ai_response or "超买" in ai_response or "超卖" in ai_response:
            factors.append("动量指标")

        if not factors:
            factors = ["综合分析"]

        return PredictionResult(
            stock_code=stock.code,
            stock_name=stock.name,
            prediction=prediction_type,
            confidence=round(confidence, 2),
            price_target=round(price_target, 2),
            time_horizon=time_horizon,
            factors=factors,
            risk_level=risk_level,
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )

    async def predict_stock(self, stock_code: str) -> Optional[PredictionResult]:
        """
        预测单只股票

        Args:
            stock_code: 股票代码

        Returns:
            Optional[PredictionResult]: 预测结果
        """
        print(f"🔍 开始分析股票: {stock_code}")

        # 获取股票数据
        stock = self.get_market_data(stock_code)
        if not stock:
            print(f"❌ 无法获取股票 {stock_code} 的市场数据")
            return None

        print(f"📊 {stock.name}({stock.code}) - 当前价格: ¥{stock.current_price}")

        # 构建分析查询
        query = f"""
        请分析{stock.name}({stock.code})的股票走势，包括：
        1. 当前技术指标分析（均线、RSI、MACD等）
        2. 短期价格趋势预测（1-3个交易日）
        3. 关键支撑位和阻力位分析
        4. 投资建议（买入/卖出/持有）及理由
        5. 风险评估和操作策略

        当前市场数据：
        - 价格: ¥{stock.current_price}
        - 涨跌: {stock.change_amount:+.2f} ({stock.change_percent:+.2f}%)
        - 成交量: {stock.volume:,}手
        - 市场: {stock.market.value}
        """

        # 调用DeepSeek AI
        ai_response = await self.call_deepseek_api(stock, query)

        if ai_response:
            print(f"🤖 AI分析完成，生成预测结果...")

            # 分析AI响应
            prediction = self.analyze_ai_response(stock, ai_response)

            print(f"📈 预测结果: {prediction.prediction.value} (置信度: {prediction.confidence:.0%})")
            print(f"🎯 目标价格: ¥{prediction.price_target}")
            print(f"⏰ 预测周期: {prediction.time_horizon.value}")
            print(f"🔍 影响因素: {', '.join(prediction.factors)}")

            return prediction
        else:
            print("❌ AI分析失败")
            return None

    async def predict_multiple_stocks(self, stock_codes: List[str]) -> BatchPredictionResult:
        """
        批量预测多只股票

        Args:
            stock_codes: 股票代码列表

        Returns:
            BatchPredictionResult: 批量预测结果
        """
        print(f"🚀 开始批量分析 {len(stock_codes)} 只股票...")
        start_time = time.time()

        results = []
        error_messages = []

        for stock_code in stock_codes:
            try:
                prediction = await self.predict_stock(stock_code)
                if prediction:
                    results.append(prediction)

                # 避免请求过于频繁
                await asyncio.sleep(0.5)

            except Exception as e:
                error_msg = f"分析股票 {stock_code} 失败: {str(e)}"
                print(f"❌ {error_msg}")
                error_messages.append(error_msg)
                continue

        execution_time = time.time() - start_time

        batch_result = BatchPredictionResult(
            total_analyzed=len(stock_codes),
            successful_predictions=len(results),
            predictions=results,
            execution_time=execution_time,
            error_messages=error_messages
        )

        print(f"✅ 批量分析完成: {len(results)}/{len(stock_codes)} 成功，耗时 {execution_time:.2f}秒")
        return batch_result

    async def close(self):
        """关闭会话"""
        if self.session:
            await self.session.close()


class DeepSeekStockAPI:
    """DeepSeek股票预测API服务"""

    def __init__(self):
        """初始化API服务"""
        self.integrator = DZHDeepSeekIntegrator()

    async def initialize(self, auth_token: Optional[str] = None) -> bool:
        """
        初始化服务

        Args:
            auth_token: 认证令牌

        Returns:
            bool: 初始化是否成功
        """
        print("🚀 初始化DeepSeek股票预测服务...")

        # 加载配置
        if not self.integrator.load_config():
            print("❌ 配置加载失败")
            return False

        # 设置认证
        if auth_token:
            self.integrator.set_auth_token(auth_token)
        else:
            # 生成演示Token
            demo_token = self.integrator.generate_token("demo_user", "demo_key")
            self.integrator.set_auth_token(demo_token)
            print("🔑 使用演示Token")

        print("✅ 服务初始化完成")
        return True

    async def predict_single(self, stock_code: str) -> Dict[str, Any]:
        """
        单股预测API

        Args:
            stock_code: 股票代码

        Returns:
            Dict[str, Any]: 预测结果
        """
        prediction = await self.integrator.predict_stock(stock_code)

        if prediction:
            return {
                "success": True,
                "data": prediction.to_dict()
            }
        else:
            return {
                "success": False,
                "error": "预测失败",
                "stock_code": stock_code
            }

    async def predict_batch(self, stock_codes: List[str]) -> Dict[str, Any]:
        """
        批量预测API

        Args:
            stock_codes: 股票代码列表

        Returns:
            Dict[str, Any]: 批量预测结果
        """
        batch_result = await self.integrator.predict_multiple_stocks(stock_codes)
        return batch_result.to_dict()

    async def get_report(self, stock_codes: List[str], report_title: str = "AI股票预测分析报告") -> Dict[str, Any]:
        """
        生成分析报告

        Args:
            stock_codes: 股票代码列表
            report_title: 报告标题

        Returns:
            Dict[str, Any]: 分析报告
        """
        print(f"📋 生成{report_title}...")

        # 获取批量预测结果
        batch_result = await self.integrator.predict_multiple_stocks(stock_codes)

        # 分析市场情绪
        buy_count = sum(1 for p in batch_result.predictions if p.prediction == PredictionType.BUY)
        sell_count = sum(1 for p in batch_result.predictions if p.prediction == PredictionType.SELL)
        hold_count = sum(1 for p in batch_result.predictions if p.prediction == PredictionType.HOLD)

        # 确定市场情绪
        if buy_count > sell_count and buy_count > hold_count:
            market_sentiment_text = "乐观"
            sentiment_score = 0.6 + buy_count / len(batch_result.predictions) * 0.4
        elif sell_count > buy_count and sell_count > hold_count:
            market_sentiment_text = "悲观"
            sentiment_score = 0.4 - sell_count / len(batch_result.predictions) * 0.3
        else:
            market_sentiment_text = "中性"
            sentiment_score = 0.5

        market_sentiment = MarketSentiment(
            market_sentiment=market_sentiment_text,
            sentiment_score=round(sentiment_score, 2),
            bullish_count=buy_count,
            bearish_count=sell_count,
            neutral_count=hold_count,
            volatility_index=0.3,  # 可以基于实际波动率计算
            market_momentum="上涨" if buy_count > sell_count else "下跌" if sell_count > buy_count else "平稳"
        )

        # 生成关键发现和建议
        high_confidence_stocks = [p for p in batch_result.predictions if p.is_high_confidence()]

        key_findings = [
            f"本次分析覆盖{len(stock_codes)}只股票，成功预测{len(batch_result.predictions)}只",
            f"市场整体情绪倾向{market_sentiment_text}，看涨股票{buy_count}只，看跌股票{sell_count}只",
            f"高置信度推荐{len(high_confidence_stocks)}只股票，平均置信度{batch_result.get_average_confidence():.0%}",
        ]

        recommendations = [
            "建议重点关注高置信度的买入推荐股票",
            "注意控制风险，分散投资降低集中度",
            "定期跟踪预测结果，及时调整投资策略"
        ]

        if buy_count > sell_count * 1.5:
            recommendations.append("市场情绪偏暖，可考虑适当增加仓位")
        elif sell_count > buy_count * 1.5:
            recommendations.append("市场情绪偏冷，建议谨慎操作，控制风险")

        # 创建报告
        report = PredictionReport(
            report_title=report_title,
            generation_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            market_sentiment=market_sentiment,
            batch_result=batch_result,
            analysis_summary=f"基于AI技术分析的股票预测报告，涵盖技术指标、市场情绪和投资建议等多个维度。",
            key_findings=key_findings,
            recommendations=recommendations
        )

        return report.to_dict()