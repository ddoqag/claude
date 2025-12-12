#!/bin/bash

# GLM Coding API 配置
API_KEY="13beba9abe974c7d97250b9778ca4447.8yR9f0F44Yv0YEX8"
ENDPOINT="https://open.bigmodel.cn/api/coding/paas/v4/chat/completions"
MODEL="glm-4"

# 函数：调用GLM API
call_glm_api() {
    local prompt="$1"

    curl -X POST "$ENDPOINT" \
        -H "Authorization: Bearer $API_KEY" \
        -H "Content-Type: application/json" \
        -d "{
            \"model\": \"$MODEL\",
            \"messages\": [
                {
                    \"role\": \"user\",
                    \"content\": \"$prompt\"
                }
            ]
        }"
}

# 示例1：生成Python代码
echo "=== 示例1：生成Python排序算法 ==="
call_glm_api "编写一个Python快速排序算法"

echo -e "\n\n=== 示例2：生成JavaScript函数 ==="
call_glm_api "Write a JavaScript function to validate email addresses"

echo -e "\n\n=== 示例3：代码优化建议 ==="
call_glm_api "优化以下Python代码的性能：\nfor i in range(len(arr)):\n    for j in range(len(arr)):\n        if arr[i] < arr[j]:\n            arr[i], arr[j] = arr[j], arr[i]"