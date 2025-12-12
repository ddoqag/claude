#!/bin/bash

# 快速模型切换器 - 优化版本
# 使用预复制到全局目录的配置文件，提升加载速度

FAST_TOKEN_MANAGER="/home/ddo/.config/claude-tools/fast_token_manager.py"

# 快速获取Token
get_fast_token() {
    local token_name="$1"

    if [[ -n "$token_name" ]]; then
        python3 "$FAST_TOKEN_MANAGER" get "$token_name" 2>/dev/null
    else
        python3 "$FAST_TOKEN_MANAGER" best 2>/dev/null
    fi
}

# 快速列出Token
list_fast_tokens() {
    python3 "$FAST_TOKEN_MANAGER" list 2>/dev/null
}

# 快速切换到DeepSeek
switch_to_deepseek_fast() {
    local token_name="$1"

    if [[ -z "$token_name" ]]; then
        echo "🔑 选择Token:"
        list_fast_tokens
        echo ""
        read -p "请输入Token名称 (回车自动选择最佳): " token_name

        if [[ -z "$token_name" ]]; then
            # 自动选择最佳Token
            token_result=$(get_fast_token)
            if [[ -n "$token_result" ]]; then
                token_name="auto_selected"
                token="$token_result"
            else
                echo "❌ 无可用Token"
                return 1
            fi
        else
            token=$(get_fast_token "$token_name")
        fi
    else
        token=$(get_fast_token "$token_name")
    fi

    if [[ -z "$token" ]]; then
        echo "❌ Token获取失败: $token_name"
        return 1
    fi

    # 快速设置环境变量
    export ANTHROPIC_BASE_URL="https://f.dzh.com.cn/zswd/newask"
    export CLAUDE_CODE_DEFAULT_MODEL="deepseek-coder"
    export CLAUDE_CODE_DEFAULT_MAX_TOKENS="32768"
    export DEEPSEEK_CURRENT_TOKEN="$token"
    export DEEPSEEK_TOKEN_NAME="$token_name"
    export DEEPSEEK_TUNNEL_ID="dzhsp846"

    # 构建完整URL
    local full_url="${ANTHROPIC_BASE_URL}?tun=${DEEPSEEK_TUNNEL_ID}&token=${token}&version=2.0.45&scene=gg"
    export DEEPSEEK_FULL_URL="$full_url"

    echo "✅ 快速切换到 DeepSeek"
    echo "   Token: $token_name (${token:0:20}...)"
}

# 快速切换到Claude
switch_to_claude_fast() {
    export ANTHROPIC_BASE_URL="https://api.anthropic.com"
    export CLAUDE_CODE_DEFAULT_MODEL="claude-3.5-sonnet"
    export CLAUDE_CODE_DEFAULT_MAX_TOKENS="200000"

    # 清除DeepSeek相关变量
    unset DEEPSEEK_CURRENT_TOKEN
    unset DEEPSEEK_TOKEN_NAME
    unset DEEPSEEK_FULL_URL

    echo "✅ 快速切换到 Claude 3.5 Sonnet"
}

# 快速切换到GLM4
switch_to_glm4_fast() {
    export ANTHROPIC_BASE_URL="https://open.bigmodel.cn/api/anthropic"
    export CLAUDE_CODE_DEFAULT_MODEL="glm-4.6"
    export CLAUDE_CODE_DEFAULT_MAX_TOKENS="65536"

    # GLM4特定配置
    export GLM_MODEL_DEFAULT="glm-4.6"
    export GLM_MODEL_CODING="glm-4.6-code"
    export GLM_MAX_TOKENS="65536"
    export GLM_TEMPERATURE="0.1"
    export GLM_TOP_P="0.9"

    # 清除DeepSeek相关变量
    unset DEEPSEEK_CURRENT_TOKEN
    unset DEEPSEEK_TOKEN_NAME
    unset DEEPSEEK_FULL_URL

    echo "✅ 快速切换到 GLM-4.6"
}

# 显示当前状态
show_status_fast() {
    echo "📊 当前模型状态:"
    echo "  API端点: ${ANTHROPIC_BASE_URL:-未设置}"
    echo "  默认模型: ${CLAUDE_CODE_DEFAULT_MODEL:-未设置}"
    echo "  最大Tokens: ${CLAUDE_CODE_DEFAULT_MAX_TOKENS:-未设置}"

    if [[ "$ANTHROPIC_BASE_URL" == *"dzh.com"* ]]; then
        echo "  Token名称: ${DEEPSEEK_TOKEN_NAME:-未设置}"
        echo "  Token状态: ${DEEPSEEK_CURRENT_TOKEN:+已设置}"
    fi

    # Claude CLI版本
    if command -v claude &> /dev/null; then
        echo "  Claude CLI: $(claude --version 2>/dev/null || echo '获取失败')"
    fi
}

# 主程序
case "${1:-}" in
    "claude"|"sonnet")
        switch_to_claude_fast
        ;;
    "glm4"|"glm")
        switch_to_glm4_fast
        ;;
    "deepseek"|"ds")
        switch_to_deepseek_fast "$2"
        ;;
    "tokens"|"list")
        echo "🔑 可用的Token:"
        list_fast_tokens
        ;;
    "status"|"current")
        show_status_fast
        ;;
    *)
        echo "🚀 快速模型切换器 v2.0"
        echo ""
        echo "用法: $0 <command> [token_name]"
        echo ""
        echo "命令:"
        echo "  claude         - 切换到 Claude 3.5 Sonnet"
        echo "  glm4           - 切换到 GLM-4.6"
        echo "  deepseek [name] - 切换到 DeepSeek (可选指定Token名)"
        echo "  tokens         - 列出可用Token"
        echo "  status         - 显示当前状态"
        echo ""
        echo "示例:"
        echo "  $0 deepseek production_api  # 指定Token切换"
        echo "  $0 deepseek                 # 自动选择最佳Token"
        echo "  $0 status                    # 查看当前状态"
        exit 1
        ;;
esac