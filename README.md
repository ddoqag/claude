# Claude Code MCP 配置中心

## 📋 项目概述

这是 Claude Code 和 MCP (Model Context Protocol) 服务器的配置备份仓库。

## 🗂️ 最新备份

- **备份日期**: 2025-12-14 08:52:31
- **备份内容**: Claude Code MCP 完整配置
- **备份位置**: `claude-code-mcp-backup-20251214-085231/`

## ✅ 当前 MCP 服务器状态 (5个在线)

1. **web-search-prime** ✅ - 网页搜索服务
   - URL: https://open.bigmodel.cn/api/mcp/web_search_prime/mcp

2. **web-reader** ✅ - 网页内容读取
   - URL: https://open.bigmodel.cn/api/mcp/web_reader/mcp

3. **context7** ✅ - 技术文档获取
   - URL: https://mcp.context7.com/mcp

4. **ida-pro-mcp** ✅ - IDA Pro 逆向工程
   - 命令: Python 服务器

5. **chrome-devtools** ✅ - Chrome 开发者工具
   - 命令: chrome-devtools-mcp v0.12.1

## 🚀 快速恢复

如需恢复配置，请查看对应备份目录中的 `BACKUP_LOG.md` 和 `BACKUP_COMPLETE.md` 文件。

## 📝 重要文件

- `BACKUP_LOG.md` - 详细备份日志
- `BACKUP_COMPLETE.md` - 备份完成通知
- `mcp_servers_status.txt` - MCP 服务器实时状态
- `npm_global_packages.txt` - NPM 全局包列表

## 🔧 配置特性

- **GLM-4.6 模型集成**: 完整配置
- **5个在线MCP服务器**: 高效协作
- **Chrome DevTools**: 浏览器自动化
- **智能插件系统**: 7个已启用插件
- **技能系统**: 完整技能生态

## 💾 备份策略

建议每周执行一次完整备份：
```bash
# 创建新的备份
mkdir claude-code-mcp-backup-$(date +%Y%m%d-%H%M%S)
cp -r ~/.claude/* claude-code-mcp-backup-$(date +%Y%m%d-%H%M%S)/
```

---
*最后更新: 2025-12-14*
*Claude Code 自动备份系统*