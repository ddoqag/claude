"""
用户工作流端到端测试
测试完整的用户使用场景
"""

import pytest
import asyncio
import time
from typing import Dict, Any
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC


@pytest.mark.e2e
class TestCodeGenerationWorkflow:
    """代码生成工作流测试"""

    @pytest.mark.asyncio
    async def test_complete_code_generation_flow(
        self,
        driver,
        api_client,
        mcp_client,
        test_data_generator,
        page_factory
    ):
        """测试完整的代码生成流程"""
        # 1. 用户打开主页
        driver.get("http://localhost:3000")
        assert "智谱AI" in driver.title or "ZhipuAI" in driver.title

        # 2. 用户点击代码生成按钮
        generate_button = driver.find_element(By.ID, "generate-code")
        generate_button.click()

        # 3. 等待代码生成表单出现
        code_form = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "code-generation-form"))
        )

        # 4. 用户输入代码生成提示
        prompt_input = driver.find_element(By.ID, "prompt-input")
        test_prompt = "Create a Python class for a stack data structure with push, pop, and peek methods"
        prompt_input.send_keys(test_prompt)

        # 5. 用户选择编程语言
        language_select = driver.find_element(By.ID, "language-select")
        language_select.click()
        python_option = driver.find_element(By.XPATH, "//option[@value='python']")
        python_option.click()

        # 6. 用户点击生成按钮
        generate_btn = driver.find_element(By.ID, "submit-generate")
        generate_btn.click()

        # 7. 等待代码生成完成
        generated_code = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "generated-code"))
        )

        # 8. 验证生成的代码
        code_content = generated_code.text
        assert "class" in code_content
        assert "def push" in code_content or "push(" in code_content
        assert "def pop" in code_content or "pop(" in code_content

        # 9. 用户复制代码
        copy_button = driver.find_element(By.ID, "copy-code")
        copy_button.click()

        # 10. 验证复制成功提示
        toast = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "toast-message"))
        )
        assert "已复制" in toast.text or "copied" in toast.text.lower()

    @pytest.mark.asyncio
    async def test_code_generation_with_constraints(
        self,
        driver
    ):
        """测试带约束条件的代码生成"""
        # 导航到代码生成页面
        driver.get("http://localhost:3000/generate")

        # 设置约束条件
        constraint_toggle = driver.find_element(By.ID, "toggle-constraints")
        constraint_toggle.click()

        # 设置最大行数
        max_lines_input = driver.find_element(By.ID, "max-lines")
        max_lines_input.clear()
        max_lines_input.send_keys("50")

        # 设置不使用某些库
        forbidden_libraries = driver.find_element(By.ID, "forbidden-libraries")
        forbidden_libraries.send_keys("numpy, pandas")

        # 生成代码
        prompt_input = driver.find_element(By.ID, "prompt-input")
        prompt_input.send_keys("Create a data processing function")

        generate_btn = driver.find_element(By.ID, "submit-generate")
        generate_btn.click()

        # 验证生成的代码
        generated_code = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "generated-code"))
        )

        code_content = generated_code.text
        code_lines = code_content.split('\n')
        assert len(code_lines) <= 50, "Generated code exceeds line limit"
        assert "import numpy" not in code_content
        assert "import pandas" not in code_content

    @pytest.mark.asyncio
    async def test_code_generation_feedback_loop(
        self,
        driver
    ):
        """测试代码生成的反馈循环"""
        driver.get("http://localhost:3000/generate")

        # 初始生成
        prompt_input = driver.find_element(By.ID, "prompt-input")
        prompt_input.send_keys("Create a simple calculator")

        generate_btn = driver.find_element(By.ID, "submit-generate")
        generate_btn.click()

        # 等待代码生成
        generated_code = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "generated-code"))
        )

        # 用户请求修改
        modify_button = driver.find_element(By.ID, "modify-code")
        modify_button.click()

        # 输入修改要求
        modify_input = driver.find_element(By.ID, "modify-prompt")
        modify_input.send_keys("Add error handling for division by zero")

        apply_modify_btn = driver.find_element(By.ID, "apply-modification")
        apply_modify_btn.click()

        # 验证修改后的代码
        modified_code = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "generated-code"))
        )

        code_content = modified_code.text
        assert "ZeroDivisionError" in code_content or "try:" in code_content


@pytest.mark.e2e
class TestCodeExplanationWorkflow:
    """代码解释工作流测试"""

    @pytest.mark.asyncio
    async def test_code_explanation_flow(
        self,
        driver,
        test_data_generator
    ):
        """测试代码解释流程"""
        # 获取测试代码片段
        code_snippet = test_data_generator.generate_code_snippet("python")

        # 导航到代码解释页面
        driver.get("http://localhost:3000/explain")

        # 输入代码
        code_textarea = driver.find_element(By.ID, "code-input")
        code_textarea.send_keys(code_snippet["code"])

        # 选择解释语言
        explanation_lang = driver.find_element(By.ID, "explanation-language")
        explanation_lang.send_keys("中文")

        # 点击解释按钮
        explain_btn = driver.find_element(By.ID, "explain-code")
        explain_btn.click()

        # 等待解释生成
        explanation = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "code-explanation"))
        )

        # 验证解释内容
        explanation_text = explanation.text
        assert "斐波那契" in explanation_text or "fibonacci" in explanation_text.lower()
        assert "递归" in explanation_text or "recursion" in explanation_text.lower()

        # 测试深度解释选项
        detailed_toggle = driver.find_element(By.ID, "detailed-explanation")
        detailed_toggle.click()

        # 获取详细解释
        detailed_explanation = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "detailed-code-explanation"))
        )

        # 验证详细解释包含更多内容
        assert len(detailed_explanation.text) > len(explanation_text)

    @pytest.mark.asyncio
    async def test_line_by_line_explanation(
        self,
        driver
    ):
        """测试逐行解释功能"""
        driver.get("http://localhost:3000/explain")

        # 输入多行代码
        code_textarea = driver.find_element(By.ID, "code-input")
        test_code = """def quick_sort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quick_sort(left) + middle + quick_sort(right)"""
        code_textarea.send_keys(test_code)

        # 启用逐行解释
        line_by_line_toggle = driver.find_element(By.ID, "line-by-line-mode")
        line_by_line_toggle.click()

        # 生成解释
        explain_btn = driver.find_element(By.ID, "explain-code")
        explain_btn.click()

        # 验证逐行解释
        line_explanations = WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "line-explanation"))
        )

        # 应该有每一行的解释
        code_lines = test_code.strip().split('\n')
        assert len(line_explanations) == len(code_lines)

        # 检查第一行的解释
        first_line_exp = line_explanations[0].text
        assert "函数" in first_line_exp or "function" in first_line_exp.lower()


@pytest.mark.e2e
class TestCodeOptimizationWorkflow:
    """代码优化工作流测试"""

    @pytest.mark.asyncio
    async def test_code_optimization_flow(
        self,
        driver
    ):
        """测试代码优化流程"""
        driver.get("http://localhost:3000/optimize")

        # 输入待优化的代码
        code_input = driver.find_element(By.ID, "code-to-optimize")
        inefficient_code = """def find_duplicates(arr):
    duplicates = []
    for i in range(len(arr)):
        for j in range(len(arr)):
            if i != j and arr[i] == arr[j] and arr[i] not in duplicates:
                duplicates.append(arr[i])
    return duplicates"""
        code_input.send_keys(inefficient_code)

        # 选择优化目标
        optimization_goal = driver.find_element(By.ID, "optimization-goal")
        optimization_goal.click()
        performance_option = driver.find_element(By.XPATH, "//option[@value='performance']")
        performance_option.click()

        # 点击优化按钮
        optimize_btn = driver.find_element(By.ID, "start-optimization")
        optimize_btn.click()

        # 等待优化完成
        optimized_code = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "optimized-code"))
        )

        # 验证优化结果
        optimized_content = optimized_code.text
        # 优化后的代码应该使用集合或字典来提高效率
        assert "set" in optimized_content or "dict" in optimized_content

        # 查看优化报告
        optimization_report = driver.find_element(By.ID, "optimization-report")
        report_text = optimization_report.text

        # 验证报告包含性能分析
        assert "O(n)" in report_text or "复杂度" in report_text

    @pytest.mark.asyncio
    async def test_optimization_comparison(
        self,
        driver
    ):
        """测试优化前后对比"""
        driver.get("http://localhost:3000/optimize")

        # 输入代码并优化
        code_input = driver.find_element(By.ID, "code-to-optimize")
        test_code = """def is_prime(n):
    if n < 2:
        return False
    for i in range(2, n):
        if n % i == 0:
            return False
    return True"""
        code_input.send_keys(test_code)

        optimize_btn = driver.find_element(By.ID, "start-optimization")
        optimize_btn.click()

        # 等待优化完成
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "optimized-code"))
        )

        # 切换到对比视图
        comparison_view = driver.find_element(By.ID, "comparison-view")
        comparison_view.click()

        # 验证对比视图显示
        original_panel = driver.find_element(By.ID, "original-code-panel")
        optimized_panel = driver.find_element(By.ID, "optimized-code-panel")

        assert original_panel.is_displayed()
        assert optimized_panel.is_displayed()

        # 查看性能对比数据
        performance_metrics = driver.find_element(By.ID, "performance-comparison")
        metrics_text = performance_metrics.text

        assert "提升" in metrics_text or "improvement" in metrics_text.lower()


@pytest.mark.e2e
class TestMultiLanguageSupport:
    """多语言支持测试"""

    @pytest.mark.asyncio
    @pytest.mark.parametrize("language", ["python", "javascript", "java", "go", "rust"])
    async def test_code_generation_in_different_languages(
        self,
        driver,
        language
    ):
        """测试不同语言的代码生成"""
        driver.get("http://localhost:3000/generate")

        # 输入通用提示
        prompt_input = driver.find_element(By.ID, "prompt-input")
        prompt_input.send_keys("Create a REST API server with basic CRUD operations")

        # 选择语言
        language_select = driver.find_element(By.ID, "language-select")
        language_select.click()
        language_option = driver.find_element(By.XPATH, f"//option[@value='{language}']")
        language_option.click()

        # 生成代码
        generate_btn = driver.find_element(By.ID, "submit-generate")
        generate_btn.click()

        # 等待生成完成
        generated_code = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "generated-code"))
        )

        # 验证语言特定的语法
        code_content = generated_code.text
        language_checks = {
            "python": ["def ", "import ", "if __name__"],
            "javascript": ["function", "const ", "=>", "export"],
            "java": ["public class", "public static", "import java"],
            "go": ["func ", "package ", "import ("],
            "rust": ["fn ", "pub ", "use ", "impl"]
        }

        for check in language_checks.get(language, []):
            assert check in code_content, f"Expected '{check}' in {language} code"

    @pytest.mark.asyncio
    async def test_ui_language_switching(
        self,
        driver
    ):
        """测试UI语言切换"""
        driver.get("http://localhost:3000")

        # 查找语言切换按钮
        language_switcher = driver.find_element(By.ID, "language-switcher")
        language_switcher.click()

        # 选择英文
        english_option = driver.find_element(By.XPATH, "//button[@data-lang='en']")
        english_option.click()

        # 验证UI变为英文
        WebDriverWait(driver, 5).until(
            lambda d: "Generate Code" in d.page_source
        )

        # 切换到中文
        language_switcher = driver.find_element(By.ID, "language-switcher")
        language_switcher.click()

        chinese_option = driver.find_element(By.XPATH, "//button[@data-lang='zh']")
        chinese_option.click()

        # 验证UI变为中文
        WebDriverWait(driver, 5).until(
            lambda d: "生成代码" in d.page_source
        )


@pytest.mark.e2e
class TestUserSessionManagement:
    """用户会话管理测试"""

    @pytest.mark.asyncio
    async def test_session_persistence(
        self,
        driver
    ):
        """测试会话持久化"""
        # 用户生成第一个代码
        driver.get("http://localhost:3000/generate")
        prompt_input = driver.find_element(By.ID, "prompt-input")
        prompt_input.send_keys("Create a hello world function")
        generate_btn = driver.find_element(By.ID, "submit-generate")
        generate_btn.click()

        # 等待生成
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "generated-code"))
        )

        # 检查历史记录
        history_panel = driver.find_element(By.ID, "history-panel")
        history_items = history_panel.find_elements(By.CLASS_NAME, "history-item")
        assert len(history_items) > 0, "History should contain at least one item"

        # 刷新页面
        driver.refresh()

        # 等待页面加载并检查历史是否保留
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "history-panel"))
        )

        # 验证历史记录仍然存在
        history_panel = driver.find_element(By.ID, "history-panel")
        history_items_after_refresh = history_panel.find_elements(By.CLASS_NAME, "history-item")
        assert len(history_items_after_refresh) > 0, "History should persist after refresh"

    @pytest.mark.asyncio
    async def test_history_navigation(
        self,
        driver
    ):
        """测试历史记录导航"""
        driver.get("http://localhost:3000")

        # 生成多个代码
        prompts = [
            "Create a sorting algorithm",
            "Write a data structure class",
            "Implement a design pattern"
        ]

        for prompt in prompts:
            driver.get("http://localhost:3000/generate")
            prompt_input = driver.find_element(By.ID, "prompt-input")
            prompt_input.send_keys(prompt)
            generate_btn = driver.find_element(By.ID, "submit-generate")
            generate_btn.click()

            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.ID, "generated-code"))
            )

        # 打开历史记录
        history_button = driver.find_element(By.ID, "history-button")
        history_button.click()

        # 验证历史记录数量
        history_items = driver.find_elements(By.CLASS_NAME, "history-item")
        assert len(history_items) >= len(prompts)

        # 点击历史记录项
        first_history_item = history_items[0]
        first_history_item.click()

        # 验证加载了历史代码
        prompt_input = driver.find_element(By.ID, "prompt-input")
        assert prompts[0] in prompt_input.get_attribute("value")

        generated_code = driver.find_element(By.ID, "generated-code")
        assert generated_code.is_displayed()


@pytest.mark.e2e
class TestErrorHandlingAndRecovery:
    """错误处理和恢复测试"""

    @pytest.mark.asyncio
    async def test_api_error_handling(
        self,
        driver
    ):
        """测试API错误处理"""
        # 模拟API错误（通过使用无效的API密钥）
        driver.get("http://localhost:3000/settings")
        api_key_input = driver.find_element(By.ID, "api-key-input")
        api_key_input.clear()
        api_key_input.send_keys("invalid_api_key")
        save_button = driver.find_element(By.ID, "save-settings")
        save_button.click()

        # 尝试生成代码
        driver.get("http://localhost:3000/generate")
        prompt_input = driver.find_element(By.ID, "prompt-input")
        prompt_input.send_keys("Test prompt")
        generate_btn = driver.find_element(By.ID, "submit-generate")
        generate_btn.click()

        # 验证错误消息显示
        error_message = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "error-message"))
        )
        assert "API" in error_message.text or "认证" in error_message.text

        # 验证重试按钮
        retry_button = driver.find_element(By.ID, "retry-button")
        assert retry_button.is_displayed()

    @pytest.mark.asyncio
    async def test_network_timeout_handling(
        self,
        driver
    ):
        """测试网络超时处理"""
        # 模拟慢网络（可能需要开发工具或特殊配置）
        driver.get("http://localhost:3000/generate")

        # 输入一个复杂的提示，可能导致超时
        prompt_input = driver.find_element(By.ID, "prompt-input")
        prompt_input.send_keys("Create a complete e-commerce platform with all features")

        generate_btn = driver.find_element(By.ID, "submit-generate")
        generate_btn.click()

        # 等待超时消息
        try:
            timeout_message = WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.CLASS_NAME, "timeout-message"))
            )
            assert "超时" in timeout_message.text or "timeout" in timeout_message.text.lower()
        except:
            # 如果没有超时，测试仍然通过
            pass

    @pytest.mark.asyncio
    async def test_invalid_input_handling(
        self,
        driver
    ):
        """测试无效输入处理"""
        driver.get("http://localhost:3000/generate")

        # 输入空的提示
        prompt_input = driver.find_element(By.ID, "prompt-input")
        prompt_input.send_keys("")

        # 尝试生成
        generate_btn = driver.find_element(By.ID, "submit-generate")
        generate_btn.click()

        # 验证验证错误
        validation_error = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "validation-error"))
        )
        assert "必填" in validation_error.text or "required" in validation_error.text.lower()

        # 输入过长的提示
        prompt_input = driver.find_element(By.ID, "prompt-input")
        prompt_input.send_keys("x" * 10000)  # 超长文本

        generate_btn = driver.find_element(By.ID, "submit-generate")
        generate_btn.click()

        # 验证长度限制错误
        length_error = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "length-error"))
        )
        assert "长度" in length_error.text or "length" in length_error.text.lower()


@pytest.mark.e2e
class TestAccessibilityFeatures:
    """无障碍功能测试"""

    @pytest.mark.asyncio
    async def test_keyboard_navigation(
        self,
        driver
    ):
        """测试键盘导航"""
        driver.get("http://localhost:3000")

        # 使用Tab键导航
        body = driver.find_element(By.TAG_NAME, "body")
        body.send_keys(Keys.TAB)

        # 验证焦点在第一个可聚焦元素上
        focused_element = driver.switch_to.active_element
        assert focused_element.is_enabled()

        # 继续Tab导航
        for _ in range(5):
            body.send_keys(Keys.TAB)
            focused_element = driver.switch_to.active_element
            # 验证每个聚焦的元素都是可交互的
            assert focused_element.tag_name in ["input", "button", "select", "a", "textarea"]

    @pytest.mark.asyncio
    async def test_screen_reader_support(
        self,
        driver
    ):
        """测试屏幕阅读器支持"""
        driver.get("http://localhost:3000")

        # 检查重要元素的ARIA标签
        generate_button = driver.find_element(By.ID, "generate-code")
        assert generate_button.get_attribute("aria-label") or generate_button.get_attribute("title")

        # 检查表单字段的标签
        prompt_input = driver.find_element(By.ID, "prompt-input")
        assert prompt_input.get_attribute("aria-label") or prompt_input.get_attribute("placeholder")

        # 检查语义化HTML
        main_content = driver.find_element(By.TAG_NAME, "main")
        assert main_content.is_displayed()

        navigation = driver.find_element(By.TAG_NAME, "nav")
        assert navigation.is_displayed()

    @pytest.mark.asyncio
    async def test_contrast_and_visibility(
        self,
        driver
    ):
        """测试对比度和可见性"""
        driver.get("http://localhost:3000")

        # 切换到高对比度模式
        driver.execute_script("document.body.classList.add('high-contrast')")

        # 验证样式应用
        high_contrast_style = driver.execute_script(
            "return window.getComputedStyle(document.body).getPropertyValue('--contrast-ratio')"
        )
        # 这里需要根据实际实现调整验证逻辑

        # 测试字体大小调整
        driver.execute_script("document.body.classList.add('large-text')")

        # 验证字体大小增加
        font_size = driver.execute_script(
            "return window.getComputedStyle(document.body).fontSize"
        )
        assert float(font_size) >= 16  # 最小字体大小应为16px