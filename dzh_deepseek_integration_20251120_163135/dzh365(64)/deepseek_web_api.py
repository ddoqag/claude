#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DZH DeepSeek股票预测Web API服务
基于DZH配置的RESTful API接口，支持股票预测查询
"""

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import asyncio
import json
from datetime import datetime
import os
import sys

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from deepseek_stock_prediction_integration import DeepSeekStockAPI

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 全局API实例
api_service = None
loop = None

# HTML模板
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DZH DeepSeek股票预测系统</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { text-align: center; margin-bottom: 30px; padding-bottom: 20px; border-bottom: 2px solid #007bff; }
        .header h1 { color: #007bff; margin: 0; }
        .header p { color: #666; margin: 10px 0 0 0; }
        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; margin-bottom: 5px; font-weight: bold; color: #333; }
        .form-group input, .form-group textarea { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
        .form-group textarea { height: 100px; resize: vertical; }
        .btn { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; margin: 5px; }
        .btn:hover { background: #0056b3; }
        .btn-secondary { background: #6c757d; }
        .btn-secondary:hover { background: #545b62; }
        .result { margin-top: 20px; padding: 15px; background: #f8f9fa; border-radius: 4px; border-left: 4px solid #007bff; }
        .prediction-item { margin: 10px 0; padding: 10px; background: white; border-radius: 4px; border: 1px solid #e9ecef; }
        .prediction-buy { border-left: 4px solid #28a745; }
        .prediction-sell { border-left: 4px solid #dc3545; }
        .prediction-hold { border-left: 4px solid #ffc107; }
        .stats { display: flex; justify-content: space-around; margin: 20px 0; }
        .stat-item { text-align: center; padding: 10px; }
        .stat-number { font-size: 24px; font-weight: bold; color: #007bff; }
        .stat-label { color: #666; font-size: 14px; }
        .loading { text-align: center; padding: 20px; color: #666; }
        .error { color: #dc3545; background: #f8d7da; padding: 10px; border-radius: 4px; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 DZH DeepSeek股票预测系统</h1>
            <p>基于大智慧DeepSeek配置的AI股票价格预测服务</p>
        </div>

        <div class="form-group">
            <label>单股预测:</label>
            <div style="display: flex; gap: 10px;">
                <input type="text" id="singleStock" placeholder="输入股票代码 (如: 000001)" value="000001">
                <button class="btn" onclick="predictSingle()">预测</button>
            </div>
        </div>

        <div class="form-group">
            <label>批量预测:</label>
            <textarea id="batchStocks" placeholder="输入股票代码，每行一个&#10;000001&#10;000002&#10;000032">000001
000002
000032</textarea>
            <div style="margin-top: 10px;">
                <button class="btn" onclick="predictBatch()">批量预测</button>
                <button class="btn btn-secondary" onclick="clearResults()">清空结果</button>
            </div>
        </div>

        <div id="results"></div>

        <div class="stats" id="stats" style="display: none;">
            <div class="stat-item">
                <div class="stat-number" id="totalCount">0</div>
                <div class="stat-label">分析总数</div>
            </div>
            <div class="stat-item">
                <div class="stat-number" id="buyCount">0</div>
                <div class="stat-label">买入推荐</div>
            </div>
            <div class="stat-item">
                <div class="stat-number" id="sellCount">0</div>
                <div class="stat-label">卖出推荐</div>
            </div>
            <div class="stat-item">
                <div class="stat-number" id="holdCount">0</div>
                <div class="stat-label">持有推荐</div>
            </div>
        </div>
    </div>

    <script>
        function showLoading() {
            document.getElementById('results').innerHTML = '<div class="loading">🔄 正在分析中，请稍候...</div>';
        }

        function showError(message) {
            document.getElementById('results').innerHTML = `<div class="error">❌ ${message}</div>`;
        }

        function showSingleResult(data) {
            const prediction = data.data;
            const predictionClass = prediction.prediction === '买入' ? 'prediction-buy' :
                                   prediction.prediction === '卖出' ? 'prediction-sell' : 'prediction-hold';

            const html = `
                <div class="result">
                    <h3>📊 ${prediction.stock_code} 预测结果</h3>
                    <div class="prediction-item ${predictionClass}">
                        <strong>预测建议:</strong> ${prediction.prediction}<br>
                        <strong>置信度:</strong> ${(prediction.confidence * 100).toFixed(0)}%<br>
                        <strong>目标价格:</strong> ¥${prediction.price_target}<br>
                        <strong>分析因素:</strong> ${prediction.factors.join(', ')}<br>
                        <strong>预测时间:</strong> ${prediction.timestamp}
                    </div>
                </div>
            `;
            document.getElementById('results').innerHTML = html;
            document.getElementById('stats').style.display = 'none';
        }

        function showBatchResult(data) {
            let html = '<div class="result"><h3>📊 批量预测结果</h3>';

            const predictions = data.data || [];
            let buyCount = 0, sellCount = 0, holdCount = 0;

            predictions.forEach(pred => {
                const predictionClass = pred.prediction === '买入' ? 'prediction-buy' :
                                       pred.prediction === '卖出' ? 'prediction-sell' : 'prediction-hold';

                if (pred.prediction === '买入') buyCount++;
                else if (pred.prediction === '卖出') sellCount++;
                else holdCount++;

                html += `
                    <div class="prediction-item ${predictionClass}">
                        <strong>${pred.stock_code}</strong> - ${pred.prediction}
                        (置信度: ${(pred.confidence * 100).toFixed(0)}%, 目标价: ¥${pred.price_target})
                        <br><small>因素: ${pred.factors.join(', ')}</small>
                    </div>
                `;
            });

            html += '</div>';
            document.getElementById('results').innerHTML = html;

            // 更新统计
            document.getElementById('totalCount').textContent = predictions.length;
            document.getElementById('buyCount').textContent = buyCount;
            document.getElementById('sellCount').textContent = sellCount;
            document.getElementById('holdCount').textContent = holdCount;
            document.getElementById('stats').style.display = 'flex';
        }

        async function predictSingle() {
            const stockCode = document.getElementById('singleStock').value.trim();
            if (!stockCode) {
                showError('请输入股票代码');
                return;
            }

            showLoading();
            try {
                const response = await fetch(`/predict/${stockCode}`);
                const data = await response.json();

                if (data.success) {
                    showSingleResult(data);
                } else {
                    showError(data.error || '预测失败');
                }
            } catch (error) {
                showError('网络错误: ' + error.message);
            }
        }

        async function predictBatch() {
            const stocksText = document.getElementById('batchStocks').value.trim();
            if (!stocksText) {
                showError('请输入股票代码');
                return;
            }

            const stocks = stocksText.split('\n').filter(s => s.trim()).map(s => s.trim());
            if (stocks.length === 0) {
                showError('请输入有效的股票代码');
                return;
            }

            showLoading();
            try {
                const response = await fetch('/predict/batch', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ stocks: stocks })
                });

                const data = await response.json();

                if (data.success) {
                    showBatchResult(data);
                } else {
                    showError(data.error || '批量预测失败');
                }
            } catch (error) {
                showError('网络错误: ' + error.message);
            }
        }

        function clearResults() {
            document.getElementById('results').innerHTML = '';
            document.getElementById('stats').style.display = 'none';
        }
    </script>
</body>
</html>
"""

def run_async(coro):
    """在新的事件循环中运行异步函数"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    return loop.run_until_complete(coro)

@app.route('/')
def index():
    """主页"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/health')
def health():
    """健康检查"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "DZH DeepSeek Stock Prediction API",
        "version": "1.0.0"
    })

@app.route('/predict/<stock_code>')
def predict_single(stock_code):
    """单股预测API"""
    try:
        # 在线程池中运行异步函数
        future = run_async(api_service.predict_single(stock_code))
        return jsonify(future)
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/predict/batch', methods=['POST'])
def predict_batch():
    """批量预测API"""
    try:
        data = request.get_json()
        stocks = data.get('stocks', [])

        if not stocks:
            return jsonify({
                "success": False,
                "error": "股票代码列表不能为空"
            }), 400

        # 在线程池中运行异步函数
        future = run_async(api_service.predict_batch(stocks))
        return jsonify(future)
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/config')
def get_config():
    """获取配置信息"""
    try:
        config_path = "/mnt/d/dzh365(64)/cfg/deepseek.xml"
        if os.path.exists(config_path):
            return jsonify({
                "success": True,
                "config_path": config_path,
                "file_size": os.path.getsize(config_path),
                "last_modified": datetime.fromtimestamp(os.path.getmtime(config_path)).isoformat()
            })
        else:
            return jsonify({
                "success": False,
                "error": "配置文件不存在"
            }), 404
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

def init_api_service():
    """初始化API服务"""
    global api_service

    try:
        api_service = DeepSeekStockAPI()
        print("🚀 初始化DeepSeek股票预测API服务...")

        # 使用异步方式初始化
        success = run_async(api_service.initialize())

        if success:
            print("✅ API服务初始化成功")
            return True
        else:
            print("❌ API服务初始化失败")
            return False

    except Exception as e:
        print(f"❌ 初始化API服务失败: {str(e)}")
        return False

if __name__ == '__main__':
    print("🌐 启动DZH DeepSeek股票预测Web API服务")
    print("="*60)

    # 初始化API服务
    if not init_api_service():
        print("❌ API服务初始化失败，退出")
        sys.exit(1)

    print("🚀 Web API服务启动中...")
    print("📋 可用端点:")
    print("   GET  / - Web界面")
    print("   GET  /health - 健康检查")
    print("   GET  /predict/<stock_code> - 单股预测")
    print("   POST /predict/batch - 批量预测")
    print("   GET  /config - 配置信息")

    try:
        # 启动Flask应用
        app.run(
            host='0.0.0.0',
            port=8093,  # 使用8093端口避免冲突
            debug=False,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n🛑 收到停止信号，关闭Web API服务...")
    except Exception as e:
        print(f"❌ Web API服务启动失败: {str(e)}")

    print("🎯 Web API服务已停止")