"""
智谱AI客户端单元测试
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import json
import aiohttp
from zhipuai import ZhipuAI


class TestZhipuAIClient:
    """智谱AI客户端测试类"""

    @pytest.fixture
    def client_config(self):
        """客户端配置"""
        return {
            "api_key": "test_api_key_12345",
            "base_url": "https://open.bigmodel.cn/api/paas/v4",
            "model": "codegeex4",
            "timeout": 30
        }

    @pytest.mark.asyncio
    async def test_client_initialization(self, client_config):
        """测试客户端初始化"""
        with patch('zhipuai.ZhipuAI') as mock_zhipu:
            client = ZhipuAI(**client_config)
            mock_zhipu.assert_called_once_with(api_key="test_api_key_12345")
            assert client is not None

    @pytest.mark.asyncio
    async def test_code_completion_request(self, mock_zhipu_response, client_config):
        """测试代码补全请求"""
        with patch('zhipuai.ZhipuAI') as MockClient:
            # 设置Mock返回值
            mock_client_instance = Mock()
            mock_client_instance.chat.completions.create = AsyncMock(
                return_value=Mock(**mock_zhipu_response)
            )
            MockClient.return_value = mock_client_instance

            # 执行测试
            client = ZhipuAI(api_key=client_config["api_key"])
            response = await client.chat.completions.create(
                model=client_config["model"],
                messages=[
                    {"role": "user", "content": "def fibonacci(n):"}
                ],
                max_tokens=1000
            )

            # 验证结果
            assert response is not None
            mock_client_instance.chat.completions.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_streaming_response(self, test_helper):
        """测试流式响应"""
        with patch('zhipuai.ZhipuAI') as MockClient:
            mock_client_instance = Mock()

            # 模拟流式响应
            async def mock_stream():
                chunks = [
                    {"choices": [{"delta": {"content": "def "}}]},
                    {"choices": [{"delta": {"content": "hello():"}}]},
                    {"choices": [{"delta": {"content": "\n    "}}]},
                    {"choices": [{"delta": {"content": "return 'Hello'"}}]},
                    {"choices": [{"finish_reason": "stop"}]}
                ]
                for chunk in chunks:
                    yield chunk
                    await asyncio.sleep(0.01)

            mock_client_instance.chat.completions.create = AsyncMock(
                return_value=mock_stream()
            )
            MockClient.return_value = mock_client_instance

            # 执行测试
            client = ZhipuAI(api_key="test_key")

            collected_chunks = []
            async for chunk in client.chat.completions.create(
                model="codegeex4",
                messages=[{"role": "user", "content": "Write hello function"}],
                stream=True
            ):
                collected_chunks.append(chunk)

            # 验证结果
            assert len(collected_chunks) > 0
            assert any(chunk.get("choices", [{}])[0].get("finish_reason") == "stop"
                      for chunk in collected_chunks)

    @pytest.mark.asyncio
    async def test_error_handling(self, client_config):
        """测试错误处理"""
        with patch('zhipuai.ZhipuAI') as MockClient:
            mock_client_instance = Mock()

            # 模拟API错误
            mock_client_instance.chat.completions.create = AsyncMock(
                side_effect=aiohttp.ClientError("API connection failed")
            )
            MockClient.return_value = mock_client_instance

            client = ZhipuAI(api_key=client_config["api_key"])

            with pytest.raises(aiohttp.ClientError):
                await client.chat.completions.create(
                    model=client_config["model"],
                    messages=[{"role": "user", "content": "test"}]
                )

    @pytest.mark.asyncio
    async def test_request_timeout(self, client_config):
        """测试请求超时"""
        with patch('zhipuai.ZhipuAI') as MockClient:
            mock_client_instance = Mock()

            # 模拟超时
            mock_client_instance.chat.completions.create = AsyncMock(
                side_effect=asyncio.TimeoutError("Request timeout")
            )
            MockClient.return_value = mock_client_instance

            client = ZhipuAI(api_key=client_config["api_key"])

            with pytest.raises(asyncio.TimeoutError):
                await client.chat.completions.create(
                    model=client_config["model"],
                    messages=[{"role": "user", "content": "test"}]
                )

    @pytest.mark.asyncio
    async def test_rate_limiting(self, client_config):
        """测试速率限制"""
        with patch('zhipuai.ZhipuAI') as MockClient:
            mock_client_instance = Mock()

            # 模拟速率限制错误
            error_response = Mock()
            error_response.status_code = 429
            error_response.json = AsyncMock(return_value={
                "error": {"message": "Rate limit exceeded"}
            })

            mock_client_instance.chat.completions.create = AsyncMock(
                side_effect=aiohttp.ClientResponseError(
                    request_info=Mock(),
                    history=(),
                    status=429,
                    message="Rate limit exceeded"
                )
            )
            MockClient.return_value = mock_client_instance

            client = ZhipuAI(api_key=client_config["api_key"])

            with pytest.raises(aiohttp.ClientResponseError) as exc_info:
                await client.chat.completions.create(
                    model=client_config["model"],
                    messages=[{"role": "user", "content": "test"}]
                )

            assert exc_info.value.status == 429

    @pytest.mark.asyncio
    async def test_authentication_error(self, client_config):
        """测试认证错误"""
        with patch('zhipuai.ZhipuAI') as MockClient:
            mock_client_instance = Mock()

            # 模拟认证失败
            mock_client_instance.chat.completions.create = AsyncMock(
                side_effect=aiohttp.ClientResponseError(
                    request_info=Mock(),
                    history=(),
                    status=401,
                    message="Invalid API key"
                )
            )
            MockClient.return_value = mock_client_instance

            client = ZhipuAI(api_key="invalid_key")

            with pytest.raises(aiohttp.ClientResponseError) as exc_info:
                await client.chat.completions.create(
                    model=client_config["model"],
                    messages=[{"role": "user", "content": "test"}]
                )

            assert exc_info.value.status == 401

    @pytest.mark.asyncio
    async def test_token_usage_tracking(self, mock_zhipu_response, client_config):
        """测试Token使用量跟踪"""
        with patch('zhipuai.ZhipuAI') as MockClient:
            mock_response = Mock()
            mock_response.usage = Mock()
            mock_response.usage.prompt_tokens = 100
            mock_response.usage.completion_tokens = 50
            mock_response.usage.total_tokens = 150

            mock_client_instance = Mock()
            mock_client_instance.chat.completions.create = AsyncMock(
                return_value=mock_response
            )
            MockClient.return_value = mock_client_instance

            client = ZhipuAI(api_key=client_config["api_key"])
            response = await client.chat.completions.create(
                model=client_config["model"],
                messages=[{"role": "user", "content": "test"}]
            )

            # 验证Token使用量
            assert response.usage.prompt_tokens == 100
            assert response.usage.completion_tokens == 50
            assert response.usage.total_tokens == 150

    @pytest.mark.asyncio
    async def test_concurrent_requests(self, client_config):
        """测试并发请求"""
        with patch('zhipuai.ZhipuAI') as MockClient:
            mock_client_instance = Mock()
            mock_response = Mock()
            mock_response.choices = [{"message": {"content": "Generated code"}}]

            mock_client_instance.chat.completions.create = AsyncMock(
                return_value=mock_response
            )
            MockClient.return_value = mock_client_instance

            client = ZhipuAI(api_key=client_config["api_key"])

            # 创建多个并发请求
            tasks = []
            for i in range(5):
                task = client.chat.completions.create(
                    model=client_config["model"],
                    messages=[{"role": "user", "content": f"Test {i}"}]
                )
                tasks.append(task)

            # 等待所有请求完成
            responses = await asyncio.gather(*tasks)

            # 验证所有请求都成功
            assert len(responses) == 5
            for response in responses:
                assert response is not None

    @pytest.mark.asyncio
    async def test_model_parameter_validation(self, client_config):
        """测试模型参数验证"""
        with patch('zhipuai.ZhipuAI') as MockClient:
            mock_client_instance = Mock()
            mock_client_instance.chat.completions.create = AsyncMock(
                return_value=Mock()
            )
            MockClient.return_value = mock_client_instance

            client = ZhipuAI(api_key=client_config["api_key"])

            # 测试无效的temperature值
            with pytest.raises(ValueError):
                await client.chat.completions.create(
                    model=client_config["model"],
                    messages=[{"role": "user", "content": "test"}],
                    temperature=2.0  # 超出范围 [0,1]
                )

            # 测试无效的max_tokens值
            with pytest.raises(ValueError):
                await client.chat.completions.create(
                    model=client_config["model"],
                    messages=[{"role": "user", "content": "test"}],
                    max_tokens=-1  # 负数
                )


class TestZhipuCodeGeneration:
    """智谱AI代码生成功能测试"""

    @pytest.mark.asyncio
    async def test_python_code_generation(self, mock_zhipu_response):
        """测试Python代码生成"""
        with patch('zhipuai.ZhipuAI') as MockClient:
            mock_client_instance = Mock()
            mock_response = Mock()
            mock_response.choices = [{
                "message": {
                    "content": """def quick_sort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quick_sort(left) + middle + quick_sort(right)"""
                }
            }]
            mock_client_instance.chat.completions.create = AsyncMock(
                return_value=mock_response
            )
            MockClient.return_value = mock_client_instance

            client = ZhipuAI(api_key="test_key")
            response = await client.chat.completions.create(
                model="codegeex4",
                messages=[{"role": "user", "content": "Write a quick sort function in Python"}]
            )

            # 验证生成的代码包含快速排序的关键元素
            content = response.choices[0].message.content
            assert "def quick_sort" in content
            assert "pivot" in content
            assert "return" in content

    @pytest.mark.asyncio
    async def test_javascript_code_generation(self):
        """测试JavaScript代码生成"""
        with patch('zhipuai.ZhipuAI') as MockClient:
            mock_client_instance = Mock()
            mock_response = Mock()
            mock_response.choices = [{
                "message": {
                    "content": """function factorial(n) {
    if (n <= 1) return 1;
    return n * factorial(n - 1);
}

// Example usage:
console.log(factorial(5)); // 120"""
                }
            }]
            mock_client_instance.chat.completions.create = AsyncMock(
                return_value=mock_response
            )
            MockClient.return_value = mock_client_instance

            client = ZhipuAI(api_key="test_key")
            response = await client.chat.completions.create(
                model="codegeex4",
                messages=[{"role": "user", "content": "Write a factorial function in JavaScript"}]
            )

            # 验证生成的JavaScript代码
            content = response.choices[0].message.content
            assert "function factorial" in content
            assert "return" in content

    @pytest.mark.asyncio
    async def test_code_completion_suggestion(self):
        """测试代码补全建议"""
        with patch('zhipuai.ZhipuAI') as MockClient:
            mock_client_instance = Mock()
            mock_response = Mock()
            mock_response.choices = [{
                "message": {
                    "content": "print(f'Hello, {name}!')"
                }
            }]
            mock_client_instance.chat.completions.create = AsyncMock(
                return_value=mock_response
            )
            MockClient.return_value = mock_client_instance

            client = ZhipuAI(api_key="test_key")
            response = await client.chat.completions.create(
                model="codegeex4",
                messages=[{"role": "user", "content": "def greet(name):\n    "}]
            )

            # 验证补全建议
            content = response.choices[0].message.content
            assert "print" in content or "return" in content

    @pytest.mark.asyncio
    async def test_code_explanation(self):
        """测试代码解释功能"""
        with patch('zhipuai.ZhipuAI') as MockClient:
            mock_client_instance = Mock()
            mock_response = Mock()
            mock_response.choices = [{
                "message": {
                    "content": """这段代码实现了二分查找算法：
1. 设置左右指针指向数组的首尾
2. 计算中间索引
3. 比较中间值与目标值
4. 根据比较结果调整搜索范围
5. 直到找到目标值或搜索范围为空

时间复杂度：O(log n)
空间复杂度：O(1)"""
                }
            }]
            mock_client_instance.chat.completions.create = AsyncMock(
                return_value=mock_response
            )
            MockClient.return_value = mock_client_instance

            client = ZhipuAI(api_key="test_key")
            response = await client.chat.completions.create(
                model="codegeex4",
                messages=[{"role": "user", "content": "解释这个二分查找代码"}]
            )

            # 验证解释内容
            content = response.choices[0].message.content
            assert "二分查找" in content or "binary search" in content
            assert "时间复杂度" in content or "time complexity" in content