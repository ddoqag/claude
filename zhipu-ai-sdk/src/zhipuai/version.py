"""版本信息"""

from typing import Tuple

# 版本号
VERSION = (1, 0, 0)

# 版本字符串
__version__ = ".".join(map(str, VERSION))

# 完整版本（包含构建信息）
FULL_VERSION = f"{__version__}.0"

# API版本
API_VERSION = "v1"

# 支持的Python版本
SUPPORTED_PYTHON_VERSIONS = ("3.11", "3.12", "3.13")

# 项目元数据
PROJECT_NAME = "zhipu-ai-sdk"
PROJECT_DESCRIPTION = "智谱AI编码端点集成 SDK"
PROJECT_URL = "https://github.com/zhipu-ai/zhipu-ai-sdk"
AUTHOR = "Zhipu AI SDK Team"
AUTHOR_EMAIL = "sdk@zhipu.ai"