# DZH DeepSeek 自然语言对话系统使用指南

## 🎯 系统概述

基于DZH（大智慧）配置的DeepSeek自然语言对话接口，支持与AI进行真正的自然语言交流，专注于金融投资分析和股票咨询。

## 🚀 快速开始

### 1. 基本命令

```bash
# 使用完整路径
/home/ddo/.local/bin/deepseek-chat "你的问题"

# 交互式对话模式
/home/ddo/.local/bin/deepseek-chat --interactive

# 股票分析
/home/ddo/.local/bin/deepseek-chat --analyze 000001

# 市场整体分析
/home/ddo/.local/bin/deepseek-chat --market
```

### 2. 别名命令（需要重新加载bashrc）

重新加载配置后可以使用以下别名：
```bash
# 重新加载配置
source ~/.bashrc

# 然后可以使用这些别名
ds-chat "分析今天市场走势"
deepseek-chat --interactive
dsc --analyze 000001
ds-stock 000002
ds-market
```

## 💬 对话功能

### 单次消息模式
```bash
deepseek-chat "今天深圳市场走势如何？"
deepseek-chat "新能源汽车板块值得投资吗？"
deepseek-chat "给我一些具体的投资建议"
deepseek-chat "分析一下平安银行的投资价值"
```

### 交互式对话模式
```bash
deepseek-chat --interactive
# 或
deepseek-chat -i
```

在交互式模式中，可以使用以下命令：
- `help` 或 `帮助`: 显示帮助信息
- `history` 或 `历史`: 查看对话历史
- `clear` 或 `清空`: 清空对话历史
- `scenes` 或 `场景`: 查看对话场景
- `analyze <股票代码>`: 分析指定股票
- `market` 或 `市场`: 市场整体分析
- `quit` 或 `exit` 或 `退出`: 退出系统

## 📊 专门功能

### 股票分析
```bash
deepseek-chat --analyze 000001  # 分析平安银行
deepseek-chat --analyze 000002  # 分析万科A
deepseek-chat --analyze 600519  # 分析贵州茅台
```

### 市场分析
```bash
deepseek-chat --market          # 市场整体分析
deepseek-chat "今天市场热点板块有哪些？"
deepseek-chat "A股短期走势如何？"
```

## 🎭 对话场景

系统支持以下专业对话场景：

1. **股票分析**: 分析股票走势、技术指标、投资建议
2. **市场预测**: 预测市场整体走势和板块表现
3. **财经新闻**: 解读财经新闻和市场事件
4. **投资策略**: 制定个人投资策略和资产配置
5. **风险评估**: 分析投资风险和给出风险提示
6. **公司分析**: 深入分析公司基本面和财务状况

## 💡 示例对话

### 股票咨询示例
```bash
deepseek-chat "分析一下比亚迪的投资价值，包括技术面和基本面"
```

### 市场分析示例
```bash
deepseek-chat "今天A股市场表现如何？科技板块有什么新的投资机会？"
```

### 投资策略示例
```bash
deepseek-chat "我是保守型投资者，应该如何配置我的投资组合？"
```

### 风险评估示例
```bash
deepseek-chat "当前市场的主要风险是什么？应该如何防范？"
```

## ⚙️ 系统配置

### Token设置
系统会自动尝试使用环境变量中的Token：
```bash
# 查看当前Token
echo $DEEPSEEK_CURRENT_TOKEN

# 设置Token
export DEEPSEEK_CURRENT_TOKEN="your_token_here"
```

### 配置文件路径
- 主配置文件: `/mnt/d/dzh365(64)/cfg/deepseek.xml`
- 聊天工具: `/home/ddo/.config/claude-tools/dzh_deepseek_chat.py`
- 命令行工具: `/home/ddo/.local/bin/deepseek-chat`

## 🔧 技术特性

### 核心功能
- ✅ 自然语言理解与对话
- ✅ DZH配置集成
- ✅ 实时股票分析
- ✅ 市场走势预测
- ✅ 对话历史记录
- ✅ 个性化投资建议

### 安全特性
- ✅ 编码处理（GB2312->UTF-8）
- ✅ 错误恢复机制
- ✅ 默认配置兜底
- ✅ 异步HTTP请求

### 集成特性
- ✅ 与现有DZH系统无缝集成
- ✅ 支持多种对话场景
- ✅ 可扩展的消息处理
- ✅ 灵活的上下文管理

## 📋 状态说明

### 当前状态
- ✅ XML解析问题已修复
- ✅ 自然语言对话功能正常
- ✅ 股票分析功能正常
- ✅ 市场分析功能正常
- ⚠️ Token需要真实API才能获得完整功能

### 运行模式
- **模拟模式**: 使用预设回复进行演示
- **真实模式**: 连接DZH DeepSeek API获得真实AI分析

## 🎯 下一步计划

1. **Token集成**: 集成真实的DZH Token管理
2. **实时数据**: 接入实时股票数据源
3. **多模态**: 支持图表分析和数据可视化
4. **个性化**: 用户偏好学习和个性化推荐
5. **API扩展**: 提供RESTful API供其他系统调用

## 📞 使用建议

### 最佳实践
1. **明确问题**: 提出具体、明确的问题
2. **上下文**: 在交互式模式中保持对话连贯性
3. **风险评估**: 始终关注AI提供的风险提示
4. **交叉验证**: 重要决策建议多方验证

### 注意事项
1. AI分析仅供参考，不构成投资建议
2. 投资有风险，入市需谨慎
3. 关注市场变化，及时调整策略
4. 保护个人信息和账户安全

---

**版本**: v1.0.0
**更新时间**: 2025-11-20
**维护者**: DZH DeepSeek集成团队