#!/bin/bash

# DZH DeepSeek集成系统恢复脚本
# 备份时间: 2025-11-20 16:31:35
# 版本: v1.0.0

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_DIR="$SCRIPT_DIR"

log_info "DZH DeepSeek集成系统恢复开始"
log_info "备份目录: $BACKUP_DIR"
echo "================================"

# 检查备份目录
if [[ ! -d "$BACKUP_DIR" ]]; then
    log_error "备份目录不存在: $BACKUP_DIR"
    exit 1
fi

# 检查关键文件
required_files=(
    "$BACKUP_DIR/claude-tools/dzh_deepseek_chat.py"
    "$BACKUP_DIR/local-bin/deepseek-chat"
    "$BACKUP_DIR/dzh365(64)/cfg/deepseek.xml"
)

for file in "${required_files[@]}"; do
    if [[ ! -f "$file" ]]; then
        log_error "关键备份文件缺失: $(basename $file)"
        exit 1
    fi
done

log_success "备份文件完整性检查通过"

# 创建目标目录（如果不存在）
log_info "检查目标目录..."
mkdir -p /home/ddo/.config/claude-tools
mkdir -p /home/ddo/.local/bin
mkdir -p /mnt/d/dzh365\(64\)

# 恢复Claude工具
log_info "恢复Claude工具..."
if cp -r "$BACKUP_DIR/claude-tools/"* /home/ddo/.config/claude-tools/; then
    chmod +x /home/ddo/.config/claude-tools/*.py
    chown -R ddo:ddo /home/ddo/.config/claude-tools/
    log_success "Claude工具恢复完成"
else
    log_error "Claude工具恢复失败"
    exit 1
fi

# 恢复可执行工具
log_info "恢复可执行工具..."
if cp -r "$BACKUP_DIR/local-bin/"* /home/ddo/.local/bin/; then
    chmod +x /home/ddo/.local/bin/*
    chown -R ddo:ddo /home/ddo/.local/bin/
    log_success "可执行工具恢复完成"
else
    log_error "可执行工具恢复失败"
    exit 1
fi

# 恢复DZH核心文件
log_info "恢复DZH核心文件..."
if cp -r "$BACKUP_DIR/dzh365(64)"/cfg /mnt/d/dzh365\(64\)/; then
    log_success "DZH配置文件恢复完成"
else
    log_error "DZH配置文件恢复失败"
    exit 1
fi

# 复制其他DZH文件
log_info "复制DZH Python文件..."
if [[ -f "$BACKUP_DIR/dzh365(64)/token_config.py" ]]; then
    cp "$BACKUP_DIR/dzh365(64)/token_config.py" /mnt/d/dzh365\(64\)/
    log_success "Token配置文件恢复完成"
fi

for py_file in "$BACKUP_DIR/dzh365(64)"/deepseek*.py; do
    if [[ -f "$py_file" ]]; then
        cp "$py_file" /mnt/d/dzh365\(64\)/
        log_success "恢复: $(basename $py_file)"
    fi
done

# 恢复系统集成文件（如果存在）
if [[ -d "$BACKUP_DIR/dzh365-core" ]]; then
    log_info "恢复系统集成文件..."
    mkdir -p /mnt/d/1d/dzh_system/prediction/
    mkdir -p /mnt/d/1d/llm_engines/

    # 复制集成器文件
    if [[ -f "$BACKUP_DIR/dzh365-core/deepseek_integrator.py" ]]; then
        cp "$BACKUP_DIR/dzh365-core/deepseek_integrator.py" /mnt/d/1d/dzh_system/prediction/
        log_success "系统集成器恢复完成"
    fi

    # 复制LLM引擎文件
    if [[ -f "$BACKUP_DIR/dzh365-core/deepseek.py" ]]; then
        cp "$BACKUP_DIR/dzh365-core/deepseek.py" /mnt/d/1d/llm_engines/
        log_success "LLM引擎恢复完成"
    fi
fi

# 恢复文档
log_info "恢复文档..."
if [[ -f "$BACKUP_DIR/docs/DZH_DEEPSEEK_CHAT_GUIDE.md" ]]; then
    cp "$BACKUP_DIR/docs/DZH_DEEPSEEK_CHAT_GUIDE.md" /home/ddo/.config/claude-tools/
    log_success "使用指南恢复完成"
fi

# 备份并更新bashrc
log_info "更新bashrc配置..."
if [[ -f /home/ddo/.bashrc ]]; then
    # 创建备份
    cp /home/ddo/.bashrc /home/ddo/.bashrc.backup.$(date +%Y%m%d_%H%M%S)
    log_warning "原有bashrc已备份"

    # 检查是否已包含DeepSeek别名
    if ! grep -q "ds-chat=" /home/ddo/.bashrc; then
        # 添加DeepSeek别名到bashrc
        cat >> /home/ddo/.bashrc << 'EOF'

# DZH DeepSeek自然语言对话别名 (自动添加)
if [[ -f /home/ddo/.local/bin/deepseek-chat ]]; then
    alias ds-chat="/home/ddo/.local/bin/deepseek-chat"
    alias deepseek-chat="/home/ddo/.local/bin/deepseek-chat"
    alias dsc="/home/ddo/.local/bin/deepseek-chat"
    alias ds-i="/home/ddo/.local/bin/deepseek-chat --interactive"
    alias ds-stock="/home/ddo/.local/bin/deepseek-chat --analyze"
    alias ds-market="/home/ddo/.local/bin/deepseek-chat --market"
fi
EOF
        log_success "bashrc配置更新完成"
    else
        log_warning "bashrc中已包含DeepSeek别名，跳过更新"
    fi
fi

# 设置权限
log_info "设置文件权限..."
chown -R ddo:ddo /home/ddo/.config/claude-tools/
chown -R ddo:ddo /home/ddo/.local/bin/
chmod +x /home/ddo/.local/bin/deepseek*

log_success "文件权限设置完成"

# 验证恢复
log_info "验证恢复结果..."
echo "================================"

# 检查核心文件
check_files=(
    "/home/ddo/.config/claude-tools/dzh_deepseek_chat.py"
    "/home/ddo/.local/bin/deepseek-chat"
    "/mnt/d/dzh365(64)/cfg/deepseek.xml"
)

all_good=true
for file in "${check_files[@]}"; do
    if [[ -f "$file" ]]; then
        log_success "✓ $(basename $file)"
    else
        log_error "✗ $(basename $file) - 恢复失败!"
        all_good=false
    fi
done

# 功能测试
log_info "功能测试..."
echo "================================"

# 测试Python导入
if python3 -c "import sys; sys.path.append('/home/ddo/.config/claude-tools'); import dzh_deepseek_chat" 2>/dev/null; then
    log_success "✓ Python模块导入测试通过"
else
    log_warning "⚠ Python模块导入测试失败，可能需要安装依赖"
fi

# 测试命令执行
if /home/ddo/.local/bin/deepseek-chat --help &>/dev/null; then
    log_success "✓ 命令行工具测试通过"
else
    log_warning "⚠ 命令行工具测试失败"
fi

# 完成
echo "================================"
if $all_good; then
    log_success "🎉 DZH DeepSeek集成系统恢复完成!"
    echo ""
    log_info "下一步操作:"
    echo "1. 重新加载shell配置: source ~/.bashrc"
    echo "2. 测试系统: deepseek-chat '你好'"
    echo "3. 查看帮助: deepseek-chat --help"
    echo ""
    log_info "主要命令:"
    echo "- ds-chat '你的问题'     - 自然语言对话"
    echo "- deepseek-chat --interactive - 交互式模式"
    echo "- deepseek-chat --analyze 000001 - 股票分析"
    echo "- deepseek-chat --market - 市场分析"
else
    log_error "❌ 恢复过程中发现问题，请检查上述错误信息"
    exit 1
fi

log_info "恢复完成时间: $(date)"
log_info "备份位置: $BACKUP_DIR"