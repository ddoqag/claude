"""
辅助函数

提供各种实用的辅助函数。
"""

import re
import json
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Union


def validate_model_name(model: str) -> bool:
    """验证模型名称格式"""
    if not model or not isinstance(model, str):
        return False

    # 智谱AI模型名称格式
    valid_prefixes = ["code-geex", "glm-", "chatglm-"]
    return any(model.startswith(prefix) for prefix in valid_prefixes)


def sanitize_text(text: str, max_length: Optional[int] = None) -> str:
    """清理文本"""
    if not text:
        return ""

    # 移除控制字符
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)

    # 规范化空白字符
    text = re.sub(r'\s+', ' ', text)

    # 截断到指定长度
    if max_length and len(text) > max_length:
        text = text[:max_length]
        # 避免截断Unicode字符
        if len(text.encode('utf-8')) > max_length:
            text = text.encode('utf-8', errors='ignore')[:max_length].decode('utf-8', errors='ignore')

    return text.strip()


def estimate_tokens(text: str, model: Optional[str] = None) -> int:
    """估算token数量"""
    if not text:
        return 0

    # 基础估算（中文和英文的比例不同）
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    english_chars = len(text) - chinese_chars

    # 中文通常1个字符约等于1.5个token
    # 英文通常4个字符约等于1个token
    estimated_tokens = int(chinese_chars * 1.5 + english_chars / 4)

    # 根据模型调整
    if model:
        if "gpt-4" in model:
            # GPT-4有更好的tokenizer
            estimated_tokens = int(estimated_tokens * 0.9)
        elif "gpt-3.5" in model:
            estimated_tokens = int(estimated_tokens * 0.95)

    return estimated_tokens


def format_timestamp(
    timestamp: Union[datetime, float, int],
    format: str = "%Y-%m-%d %H:%M:%S"
) -> str:
    """格式化时间戳"""
    if isinstance(timestamp, datetime):
        return timestamp.strftime(format)
    elif isinstance(timestamp, (float, int)):
        return datetime.fromtimestamp(timestamp).strftime(format)
    else:
        raise ValueError("Invalid timestamp type")


def parse_sse_line(line: str) -> Optional[Dict[str, Any]]:
    """解析SSE（Server-Sent Events）行"""
    if not line:
        return None

    # 移除前后空白
    line = line.strip()

    # 跳过注释行
    if line.startswith(":"):
        return None

    # 解析数据行
    if line.startswith("data: "):
        data = line[6:]  # 移除 "data: " 前缀

        # 检查结束标记
        if data == "[DONE]":
            return {"type": "done"}

        # 尝试解析JSON
        try:
            return {"type": "data", "data": json.loads(data)}
        except json.JSONDecodeError:
            # 如果不是JSON，返回原始数据
            return {"type": "data", "data": data}

    # 解析其他类型的行
    if ":" in line:
        field, value = line.split(":", 1)
        return {
            "type": "event",
            "field": field.strip(),
            "value": value.strip()
        }

    return None


def chunk_text(
    text: str,
    chunk_size: int,
    overlap: int = 0,
    separator: str = " "
) -> List[str]:
    """将文本分块"""
    if not text:
        return []

    if chunk_size <= 0:
        raise ValueError("Chunk size must be positive")

    if overlap >= chunk_size:
        raise ValueError("Overlap must be less than chunk size")

    chunks = []
    start = 0
    text_len = len(text)

    while start < text_len:
        end = start + chunk_size
        chunk = text[start:end]

        # 如果不是最后一块且不是在分隔符处切割，尝试在分隔符处切分
        if end < text_len and separator:
            last_sep = chunk.rfind(separator)
            if last_sep > 0:
                end = start + last_sep + len(separator)
                chunk = text[start:end]

        chunks.append(chunk)
        start = end - overlap

    return chunks


def merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """递归合并字典"""
    result = dict1.copy()

    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value

    return result


def flatten_dict(
    d: Dict[str, Any],
    parent_key: str = "",
    sep: str = "."
) -> Dict[str, Any]:
    """扁平化嵌套字典"""
    items = []

    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k

        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))

    return dict(items)


def safe_json_loads(
    json_str: str,
    default: Any = None
) -> Any:
    """安全的JSON解析"""
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return default


def truncate_string(
    s: str,
    max_length: int,
    suffix: str = "..."
) -> str:
    """截断字符串"""
    if len(s) <= max_length:
        return s

    if max_length <= len(suffix):
        return s[:max_length]

    return s[:max_length - len(suffix)] + suffix


def extract_code_blocks(text: str) -> List[Dict[str, str]]:
    """从文本中提取代码块"""
    pattern = r"```(\w+)?\n(.*?)\n```"
    matches = re.finditer(pattern, text, re.DOTALL)

    code_blocks = []
    for match in matches:
        language = match.group(1) or "text"
        code = match.group(2)
        code_blocks.append({
            "language": language,
            "code": code,
        })

    return code_blocks


def calculate_similarity(text1: str, text2: str) -> float:
    """计算两个文本的相似度（简单的Jaccard相似度）"""
    # 转换为集合
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())

    # 计算Jaccard相似度
    intersection = words1.intersection(words2)
    union = words1.union(words2)

    if not union:
        return 0.0

    return len(intersection) / len(union)


def create_hash(text: str, algorithm: str = "md5") -> str:
    """创建文本哈希"""
    import hashlib

    hash_func = getattr(hashlib, algorithm, hashlib.md5)
    return hash_func(text.encode()).hexdigest()


def format_file_size(size_bytes: int) -> str:
    """格式化文件大小"""
    if size_bytes == 0:
        return "0B"

    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0

    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024
        i += 1

    return f"{size_bytes:.2f}{size_names[i]}"


def retry_on_exception(
    exceptions: tuple,
    max_retries: int = 3,
    backoff_factor: float = 1.0
):
    """重试装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            retries = 0
            last_exception = None

            while retries <= max_retries:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if retries == max_retries:
                        break

                    wait_time = backoff_factor * (2 ** retries)
                    time.sleep(wait_time)
                    retries += 1

            raise last_exception

        return wrapper
    return decorator


class Timer:
    """计时器上下文管理器"""

    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.duration = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time

    def __str__(self):
        if self.duration is not None:
            return f"{self.duration:.3f}s"
        return "Timer not finished"


def make_batch_id() -> str:
    """生成批次ID"""
    import uuid
    import time

    timestamp = int(time.time() * 1000)
    unique_id = str(uuid.uuid4())[:8]
    return f"batch_{timestamp}_{unique_id}"


def get_system_info() -> Dict[str, Any]:
    """获取系统信息"""
    import platform
    import sys

    return {
        "python_version": sys.version,
        "platform": platform.platform(),
        "architecture": platform.architecture()[0],
        "processor": platform.processor(),
    }