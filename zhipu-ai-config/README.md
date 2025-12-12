# 智谱AI编码端点配置系统

这是一个完整、安全、可扩展的配置管理系统，专为智谱AI编码端点设计。

## 🚀 特性

- **多环境支持**: 开发、测试、预生产、生产环境
- **安全配置**: 加密存储、密钥管理、审计日志
- **配置验证**: 全面的验证规则和错误处理
- **灵活加载**: 环境变量、配置文件、动态覆盖
- **类型安全**: 完整的类型提示和验证

## 📁 项目结构

```
zhipu-ai-config/
├── config/
│   ├── settings.py         # 核心配置管理
│   ├── env_loader.py       # 环境变量加载
│   ├── environment.py      # 多环境管理
│   ├── security.py         # 安全配置和加密
│   └── validator.py        # 配置验证
├── scripts/
│   ├── setup.py           # 环境初始化脚本
│   ├── generate_keys.py   # 密钥生成工具
│   └── test_config.py     # 配置测试工具
├── development.json       # 开发环境配置
├── testing.json          # 测试环境配置
├── production.json       # 生产环境配置
└── .env.example          # 环境变量模板
```

## 🛠️ 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 初始化环境

```bash
# 交互式设置开发环境
python scripts/setup.py development --interactive

# 设置生产环境（使用默认值）
python scripts/setup.py production

# 创建环境变量文件
python scripts/setup.py development --create-env
```

### 3. 配置环境变量

复制 `.env.example` 为 `.env` 并填写实际值：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
ENVIRONMENT=development
ZHIPU_AI_API_KEY=your_actual_api_key_here
DB_PASSWORD=your_database_password
```

### 4. 测试配置

```bash
# 测试当前环境配置
python scripts/test_config.py

# 测试特定环境
python scripts/test_config.py --env production

# 跳过数据库和缓存测试
python scripts/test_config.py --skip-db --skip-cache
```

## 📖 详细使用指南

### 配置管理

```python
from config import get_config, init_config

# 初始化配置
config = init_config("development")

# 或者获取配置实例
config = get_config("production")

# 访问配置
api_key = config.zhipu_ai.api_key
db_url = config.get_database_url()
```

### 环境切换

```python
from config.environment import EnvironmentManager

env_manager = EnvironmentManager()

# 切换环境
env_manager.switch_environment("production")

# 比较环境差异
differences = env_manager.compare_environments("development", "production")
```

### 安全功能

```python
from config.security import SecureConfig

secure = SecureConfig()

# 加密数据
encrypted = secure.encrypt("sensitive_data")
decrypted = secure.decrypt(encrypted)

# 哈希密码
hash_val, salt = secure.hash_password("my_password")
verified = secure.verify_password("my_password", hash_val, salt)
```

### 配置验证

```python
from config.validator import ConfigValidator

validator = ConfigValidator()
result = validator.validate(config_dict, schema)

if not result.is_valid:
    for error in result.errors:
        print(f"Error: {error.message}")
```

## 🔧 配置项说明

### 智谱AI配置

- `api_key`: API密钥（必需）
- `endpoint_url`: API端点URL
- `model_name`: 模型名称（默认：glm-4.6）
- `max_retries`: 最大重试次数
- `timeout`: 请求超时时间（秒）
- `rate_limit`: 速率限制（每分钟）

### 安全配置

- `encryption_key`: 加密密钥
- `jwt_secret`: JWT密钥
- `allowed_origins`: 允许的来源列表
- `allowed_ips`: 允许的IP地址列表
- `session_timeout`: 会话超时时间
- `enable_audit_log`: 是否启用审计日志

### 数据库配置

- `host`: 数据库主机
- `port`: 端口号
- `name`: 数据库名
- `username`: 用户名
- `password`: 密码
- `ssl_mode`: SSL模式
- `pool_size`: 连接池大小
- `max_overflow`: 最大溢出连接数

### 缓存配置

- `host`: 缓存主机
- `port`: 端口号
- `db`: 数据库索引
- `password`: 密码（可选）
- `ttl`: 缓存过期时间

## 🔐 安全最佳实践

1. **密钥管理**
   - 使用 `generate_keys.py` 生成安全的密钥
   - 定期轮换加密密钥
   - 不要在代码中硬编码密钥

2. **环境隔离**
   - 不同环境使用不同的API密钥
   - 生产环境使用专用的数据库和缓存实例
   - 限制生产环境的访问权限

3. **审计日志**
   - 启用配置访问审计
   - 定期检查审计日志
   - 监控异常访问模式

## 📋 工具说明

### setup.py - 环境初始化

```bash
# 交互式设置
python scripts/setup.py <环境名> --interactive

# 使用默认值设置
python scripts/setup.py <环境名>

# 创建环境变量文件
python scripts/setup.py <环境名> --create-env
```

### generate_keys.py - 密钥生成

```bash
# 生成所有类型的密钥
python scripts/generate_keys.py

# 生成特定类型
python scripts/generate_keys.py --type fernet
python scripts/generate_keys.py --type jwt

# 生成密码哈希
python scripts/generate_keys.py --type password --password mypass

# 保存到文件
python scripts/generate_keys.py --save
```

### test_config.py - 配置测试

```bash
# 测试默认环境
python scripts/test_config.py

# 测试特定环境
python scripts/test_config.py --env production

# 详细输出
python scripts/test_config.py --verbose

# 跳过某些测试
python scripts/test_config.py --skip-db --skip-cache
```

## 🚨 注意事项

1. **敏感信息处理**
   - 所有敏感配置项都应该使用环境变量
   - 不要提交包含真实密钥的配置文件到版本控制
   - 生产环境的密钥应该使用专门的密钥管理服务

2. **环境隔离**
   - 确保不同环境使用不同的配置文件
   - 测试环境不应使用生产环境的API密钥
   - 定期检查环境配置是否正确

3. **定期维护**
   - 定期更新依赖库
   - 定期轮换密钥
   - 定期检查和更新配置验证规则

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 📄 许可证

MIT License

## 🆘 故障排除

### 常见问题

1. **配置加载失败**
   - 检查环境变量 `ENVIRONMENT` 是否设置
   - 确认配置文件存在且格式正确
   - 查看错误日志获取详细信息

2. **API密钥错误**
   - 确认API密钥是否有效
   - 检查是否有足够的权限
   - 确认请求频率是否超限

3. **数据库连接失败**
   - 检查数据库服务是否运行
   - 确认连接参数是否正确
   - 检查网络连接和防火墙设置

### 获取帮助

1. 查看文档和注释
2. 运行测试脚本诊断问题
3. 检查日志文件
4. 提交Issue并提供详细错误信息

## 📝 更新日志

### v1.0.0 (2025-12-10)
- 初始版本发布
- 完整的多环境支持
- 安全配置和加密功能
- 配置验证和错误处理
- 管理工具和脚本

---

⭐ 如果这个项目对您有帮助，请给我们一个星标！