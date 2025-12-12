"""
端到端测试配置文件
"""

import pytest
import asyncio
import os
import json
import tempfile
import shutil
from typing import Dict, Any, List, Optional
from pathlib import Path
from unittest.mock import Mock, AsyncMock
import docker
from docker.client import DockerClient
import aiohttp
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


@pytest.fixture(scope="session")
def e2e_environment():
    """端到端测试环境配置"""
    return {
        "base_url": os.getenv("E2E_BASE_URL", "http://localhost:3000"),
        "api_base_url": os.getenv("E2E_API_BASE_URL", "http://localhost:8080"),
        "mcp_server_url": os.getenv("E2E_MCP_URL", "http://localhost:8080"),
        "zhipu_api_key": os.getenv("ZHIPU_API_KEY", "test_key"),
        "browser": os.getenv("E2E_BROWSER", "chrome"),
        "headless": os.getenv("E2E_HEADLESS", "true").lower() == "true",
        "screenshot_dir": os.getenv("E2E_SCREENSHOT_DIR", "./screenshots"),
        "video_dir": os.getenv("E2E_VIDEO_DIR", "./videos"),
        "test_data_dir": os.getenv("E2E_TEST_DATA_DIR", "./test_data")
    }


@pytest.fixture(scope="session")
def docker_compose_file():
    """Docker Compose文件路径"""
    return Path(__file__).parent / "docker-compose.yml"


@pytest.fixture(scope="session")
def docker_services(docker_compose_file):
    """Docker服务管理器"""
    try:
        docker_client = docker.from_env()
        return docker_client
    except Exception:
        pytest.skip("Docker not available")


@pytest.fixture(scope="function", autouse=True)
def screenshot_on_failure(request, driver):
    """失败时截图"""
    yield
    if request.node.rep_call.failed:
        # 保存截图
        screenshot_name = f"{request.node.name}_{int(time.time())}.png"
        screenshot_path = Path(request.config.e2e_environment["screenshot_dir"]) / screenshot_name
        driver.save_screenshot(str(screenshot_path))


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """生成测试报告钩子"""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)


class BrowserManager:
    """浏览器管理器"""

    def __init__(self, browser_type: str = "chrome", headless: bool = True):
        self.browser_type = browser_type.lower()
        self.headless = headless
        self.driver = None

    def start_driver(self):
        """启动浏览器驱动"""
        if self.browser_type == "chrome":
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--allow-running-insecure-content")

            self.driver = webdriver.Chrome(options=chrome_options)
        elif self.browser_type == "firefox":
            from selenium import webdriver
            firefox_options = webdriver.FirefoxOptions()
            if self.headless:
                firefox_options.add_argument("--headless")
            self.driver = webdriver.Firefox(options=firefox_options)
        else:
            raise ValueError(f"Unsupported browser: {self.browser_type}")

        self.driver.set_page_load_timeout(30)
        self.driver.implicitly_wait(10)

    def stop_driver(self):
        """停止浏览器驱动"""
        if self.driver:
            self.driver.quit()
            self.driver = None

    def get_driver(self):
        """获取浏览器驱动"""
        if not self.driver:
            self.start_driver()
        return self.driver


@pytest.fixture
def browser_manager(e2e_environment):
    """浏览器管理器夹具"""
    manager = BrowserManager(
        browser_type=e2e_environment["browser"],
        headless=e2e_environment["headless"]
    )
    yield manager
    manager.stop_driver()


@pytest.fixture
def driver(browser_manager):
    """浏览器驱动夹具"""
    return browser_manager.get_driver()


@pytest.fixture
def wait(driver):
    """显式等待夹具"""
    return WebDriverWait(driver, 10)


class PageObject:
    """页面对象基类"""

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def find_element(self, by: By, value: str):
        """查找元素"""
        return self.driver.find_element(by, value)

    def find_elements(self, by: By, value: str):
        """查找多个元素"""
        return self.driver.find_elements(by, value)

    def click(self, by: By, value: str):
        """点击元素"""
        element = self.wait.until(EC.element_to_be_clickable((by, value)))
        element.click()

    def type(self, by: By, value: str, text: str):
        """输入文本"""
        element = self.wait.until(EC.presence_of_element_located((by, value)))
        element.clear()
        element.send_keys(text)

    def get_text(self, by: By, value: str) -> str:
        """获取元素文本"""
        element = self.wait.until(EC.presence_of_element_located((by, value)))
        return element.text

    def wait_for_element(self, by: By, value: str):
        """等待元素出现"""
        return self.wait.until(EC.presence_of_element_located((by, value)))

    def wait_for_element_disappear(self, by: By, value: str):
        """等待元素消失"""
        return self.wait.until_not(EC.presence_of_element_located((by, value)))


@pytest.fixture
def page_factory(driver):
    """页面对象工厂夹具"""
    def create_page(page_class):
        return page_class(driver)
    return create_page


class TestDataGenerator:
    """测试数据生成器"""

    @staticmethod
    def generate_code_snippet(language: str = "python") -> Dict[str, Any]:
        """生成代码片段"""
        snippets = {
            "python": {
                "code": """def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# 测试
for i in range(10):
    print(f"F({i}) = {fibonacci(i)}")""",
                "description": "斐波那契数列实现",
                "expected_output": "F(0) = 0\nF(1) = 1\n..."
            },
            "javascript": {
                "code": """function quickSort(arr) {
    if (arr.length <= 1) {
        return arr;
    }
    const pivot = arr[Math.floor(arr.length / 2)];
    const left = arr.filter(x => x < pivot);
    const middle = arr.filter(x => x === pivot);
    const right = arr.filter(x => x > pivot);
    return [...quickSort(left), ...middle, ...quickSort(right)];
}

// 测试
const numbers = [3, 6, 8, 10, 1, 2, 1];
console.log(quickSort(numbers));""",
                "description": "快速排序算法",
                "expected_output": "[1, 1, 2, 3, 6, 8, 10]"
            },
            "java": {
                "code": """public class Calculator {
    public static int add(int a, int b) {
        return a + b;
    }

    public static int multiply(int a, int b) {
        return a * b;
    }

    public static void main(String[] args) {
        System.out.println("5 + 3 = " + add(5, 3));
        System.out.println("5 * 3 = " + multiply(5, 3));
    }
}""",
                "description": "简单计算器类",
                "expected_output": "5 + 3 = 8\n5 * 3 = 15"
            }
        }
        return snippets.get(language, snippets["python"])

    @staticmethod
    def generate_test_scenarios() -> List[Dict[str, Any]]:
        """生成测试场景"""
        return [
            {
                "name": "代码生成场景",
                "steps": [
                    {"action": "open_page", "url": "/"},
                    {"action": "click", "selector": "button[id='generate-code']"},
                    {"action": "type", "selector": "textarea[id='prompt']", "text": "Write a hello world function"},
                    {"action": "select", "selector": "select[id='language']", "value": "python"},
                    {"action": "click", "selector": "button[id='submit']"},
                    {"action": "wait", "selector": "pre[id='generated-code']", "timeout": 10},
                    {"action": "verify", "selector": "pre[id='generated-code']", "contains": "def hello"}
                ]
            },
            {
                "name": "代码解释场景",
                "steps": [
                    {"action": "open_page", "url": "/"},
                    {"action": "click", "selector": "button[id='explain-code']"},
                    {"action": "type", "selector": "textarea[id='code']", "text": "def add(a, b): return a + b"},
                    {"action": "click", "selector": "button[id='explain']"},
                    {"action": "wait", "selector": "div[id='explanation']", "timeout": 10},
                    {"action": "verify", "selector": "div[id='explanation']", "contains": "addition"}
                ]
            },
            {
                "name": "代码优化场景",
                "steps": [
                    {"action": "open_page", "url": "/"},
                    {"action": "click", "selector": "button[id='optimize-code']"},
                    {"action": "type", "selector": "textarea[id='code']", "text": "for i in range(len(arr)): for j in range(i): # O(n^2)"},
                    {"action": "click", "selector": "button[id='optimize']"},
                    {"action": "wait", "selector": "div[id='optimized-code']", "timeout": 15},
                    {"action": "verify", "selector": "div[id='optimized-code']", "contains": "O(n)"}
                ]
            }
        ]

    @staticmethod
    def create_temp_project(project_type: str = "python") -> str:
        """创建临时项目"""
        temp_dir = tempfile.mkdtemp(prefix=f"test_project_{project_type}_")

        if project_type == "python":
            # Python项目结构
            files = {
                "main.py": "print('Hello, World!')",
                "requirements.txt": "requests==2.31.0\nnumpy==1.24.3",
                "README.md": "# Test Python Project\n\nThis is a test project.",
                "tests/test_main.py": "def test_main():\n    assert True"
            }
        elif project_type == "javascript":
            # JavaScript项目结构
            files = {
                "index.js": "console.log('Hello, World!');",
                "package.json": '{"name": "test-project", "version": "1.0.0"}',
                "README.md": "# Test JavaScript Project\n\nThis is a test project.",
                "test/index.test.js": "test('example', () => { expect(1).toBe(1); });"
            }
        else:
            files = {"README.md": f"# Test {project_type.title()} Project"}

        # 创建文件
        for file_path, content in files.items():
            full_path = Path(temp_dir) / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            with open(full_path, 'w') as f:
                f.write(content)

        return temp_dir


@pytest.fixture
def test_data_generator():
    """测试数据生成器夹具"""
    return TestDataGenerator()


class APIClient:
    """API客户端"""

    def __init__(self, base_url: str, api_key: str = None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers={"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def get(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """GET请求"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        async with self.session.get(url, **kwargs) as response:
            return {
                "status": response.status,
                "data": await response.json() if response.content_type == "application/json" else await response.text()
            }

    async def post(self, endpoint: str, data: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        """POST请求"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        json_data = kwargs.pop('json', data)
        async with self.session.post(url, json=json_data, **kwargs) as response:
            return {
                "status": response.status,
                "data": await response.json() if response.content_type == "application/json" else await response.text()
            }

    async def put(self, endpoint: str, data: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        """PUT请求"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        async with self.session.put(url, json=data, **kwargs) as response:
            return {
                "status": response.status,
                "data": await response.json() if response.content_type == "application/json" else await response.text()
            }

    async def delete(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """DELETE请求"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        async with self.session.delete(url, **kwargs) as response:
            return {
                "status": response.status,
                "data": await response.json() if response.content_type == "application/json" else await response.text()
            }


@pytest.fixture
async def api_client(e2e_environment):
    """API客户端夹具"""
    client = APIClient(
        base_url=e2e_environment["api_base_url"],
        api_key=e2e_environment["zhipu_api_key"]
    )
    async with client:
        yield client


class MCPClient:
    """MCP客户端"""

    def __init__(self, server_url: str):
        self.server_url = server_url.rstrip('/')
        self.session = None
        self.request_id = 0

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """调用MCP工具"""
        self.request_id += 1
        url = f"{self.server_url}/mcp/tools/call"
        payload = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }

        async with self.session.post(url, json=payload) as response:
            return await response.json()

    async def list_tools(self) -> Dict[str, Any]:
        """列出MCP工具"""
        url = f"{self.server_url}/mcp/tools/list"
        async with self.session.post(url, json={}) as response:
            return await response.json()

    async def read_resource(self, uri: str) -> Dict[str, Any]:
        """读取MCP资源"""
        url = f"{self.server_url}/mcp/resources/read"
        payload = {"uri": uri}
        async with self.session.post(url, json=payload) as response:
            return await response.json()


@pytest.fixture
async def mcp_client(e2e_environment):
    """MCP客户端夹具"""
    client = MCPClient(e2e_environment["mcp_server_url"])
    async with client:
        yield client


class TestScenario:
    """测试场景基类"""

    def __init__(self, name: str, steps: List[Dict[str, Any]]):
        self.name = name
        self.steps = steps
        self.results = []

    async def execute(self, driver: Optional[webdriver.Chrome] = None,
                     api_client: Optional[APIClient] = None,
                     mcp_client: Optional[MCPClient] = None):
        """执行测试场景"""
        for step in self.steps:
            try:
                result = await self._execute_step(step, driver, api_client, mcp_client)
                self.results.append({
                    "step": step,
                    "success": True,
                    "result": result
                })
            except Exception as e:
                self.results.append({
                    "step": step,
                    "success": False,
                    "error": str(e)
                })
                raise

    async def _execute_step(self, step: Dict[str, Any],
                          driver: Optional[webdriver.Chrome] = None,
                          api_client: Optional[APIClient] = None,
                          mcp_client: Optional[MCPClient] = None):
        """执行单个步骤"""
        action = step["action"]

        if action == "open_page" and driver:
            driver.get(f"{driver.current_url.split('/')[0]}//{driver.current_url.split('/')[2]}{step['url']}")
            return {"status": "opened", "url": step["url"]}

        elif action == "click" and driver:
            element = driver.find_element(By.CSS_SELECTOR, step["selector"])
            element.click()
            return {"status": "clicked", "element": step["selector"]}

        elif action == "type" and driver:
            element = driver.find_element(By.CSS_SELECTOR, step["selector"])
            element.clear()
            element.send_keys(step["text"])
            return {"status": "typed", "element": step["selector"], "text": step["text"]}

        elif action == "wait" and driver:
            wait = WebDriverWait(driver, step.get("timeout", 10))
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, step["selector"])))
            return {"status": "waited", "element": step["selector"]}

        elif action == "verify" and driver:
            element = driver.find_element(By.CSS_SELECTOR, step["selector"])
            text = element.text
            assert step["contains"] in text, f"Expected '{step['contains']}' in '{text}'"
            return {"status": "verified", "element": step["selector"], "contains": step["contains"]}

        elif action == "api_call" and api_client:
            method = step.get("method", "get").lower()
            endpoint = step["endpoint"]
            data = step.get("data")

            if method == "get":
                result = await api_client.get(endpoint)
            elif method == "post":
                result = await api_client.post(endpoint, data)
            elif method == "put":
                result = await api_client.put(endpoint, data)
            elif method == "delete":
                result = await api_client.delete(endpoint)

            return result

        elif action == "mcp_call" and mcp_client:
            tool = step["tool"]
            arguments = step["arguments"]
            result = await mcp_client.call_tool(tool, arguments)
            return result

        else:
            raise ValueError(f"Unsupported action: {action}")

    def get_results(self) -> List[Dict[str, Any]]:
        """获取测试结果"""
        return self.results

    def is_successful(self) -> bool:
        """检查场景是否成功"""
        return all(r["success"] for r in self.results)


@pytest.fixture
def test_scenario():
    """测试场景夹具"""
    def create_scenario(name: str, steps: List[Dict[str, Any]]):
        return TestScenario(name, steps)
    return create_scenario