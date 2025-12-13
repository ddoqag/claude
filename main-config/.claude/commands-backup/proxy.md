# 代理管理

智能代理开关控制，支持全球网络访问和包管理器使用。

## 代理配置
- **HTTP代理**: `http://127.0.0.1:33210`
- **HTTPS代理**: `http://127.0.0.1:33210`
- **SOCKS5代理**: `socks5://127.0.0.1:33211`

## 使用方法

### 启用代理
```bash
export https_proxy=http://127.0.0.1:33210
export http_proxy=http://127.0.0.1:33210
export all_proxy=socks5://127.0.0.1:33211
```

### 停用代理
```bash
unset https_proxy http_proxy all_proxy
```

### 检查状态
```bash
env | grep -i proxy
```

## 使用场景

### 📦 包管理器安装
```bash
# 启用代理后安装国际包
/proxy on
npm install -g @types/node
pip install tensorflow
go get github.com/example/package
```

### 🌐 GitHub操作
```bash
# 启用代理后进行GitHub操作
/proxy on
git clone https://github.com/international-repo.git
gh repo create new-repo --public
```

### 📡 API调用
```bash
# 启用代理后访问国际API
/proxy on
curl https://api.openai.com/v1/models
curl https://api.github.com/users
```

## 自动化脚本示例

### 安装包时自动管理代理
```bash
#!/bin/bash
# 智能包安装脚本

install_with_proxy() {
    echo "🔧 启用代理..."
    /proxy on

    echo "📦 安装包..."
    npm install "$@"

    echo "🔧 停用代理..."
    /proxy off

    echo "✅ 安装完成！"
}

# 使用示例
install_with_proxy @types/node react lodash
```

### GitHub操作自动代理
```bash
#!/bin/bash
# GitHub操作脚本

github_operation() {
    echo "🔧 启用代理访问GitHub..."
    /proxy on

    echo "📡 执行GitHub操作..."
    git clone "$1"

    echo "🔧 停用代理..."
    /proxy off

    echo "✅ GitHub操作完成！"
}

# 使用示例
github_operation https://github.com/user/repo.git
```

## 代理检测和诊断

### 连接测试
```bash
# 测试代理连接
/proxy test

# 手动测试
curl -I --proxy socks5://127.0.0.1:33211 https://www.google.com
curl -I --proxy http://127.0.0.1:33210 https://www.github.com
```

### 故障排除
```bash
# 检查代理服务状态
netstat -an | grep :33210
netstat -an | grep :33211

# 查代理日志
journalctl -u proxy-service -f

# 重启代理服务
sudo systemctl restart proxy-service
```

## 应用程序配置

### Git代理配置
```bash
# Git HTTP/HTTPS代理
git config --global http.proxy http://127.0.0.1:33210
git config --global https.proxy http://127.0.0.1:33210

# 查看Git代理配置
git config --global --get http.proxy
git config --global --get https.proxy

# 取消Git代理
git config --global --unset http.proxy
git config --global --unset https.proxy
```

### npm代理配置
```bash
# npm代理配置
npm config set proxy http://127.0.0.1:33210
npm config set https-proxy http://127.0.0.1:33210

# 查看npm代理配置
npm config get proxy
npm config get https-proxy

# 取消npm代理
npm config delete proxy
npm config delete https-proxy
```

### Docker代理配置
```bash
# Docker代理配置
sudo mkdir -p /etc/systemd/system/docker.service.d
sudo tee /etc/systemd/system/docker.service.d/proxy.conf > /dev/null <<EOF
[Service]
Environment="HTTP_PROXY=http://127.0.0.1:33210"
Environment="HTTPS_PROXY=http://127.0.0.1:33210"
Environment="NO_PROXY=localhost,127.0.0.1"
EOF

# 重启Docker
sudo systemctl daemon-reload
sudo systemctl restart docker
```

## 性能优化

### 代理绕过规则
```bash
# 设置本地网络绕过代理
export no_proxy="localhost,127.0.0.1,*.local,*.lan"

# 添加企业内网绕过
export no_proxy="$no_proxy,*.company.com,192.168.*"
```

### 并发连接优化
```bash
# 增加并发连接数
export npm_config_maxsockets=10
export npm_config_maxsockets_half_open=5
```

## 安全注意事项

### 🔒 安全最佳实践
- **仅使用可信代理**: 确保代理服务器安全可靠
- **敏感数据保护**: 避免通过代理传输敏感信息
- **定期检查**: 定期验证代理配置和连接状态
- **日志监控**: 监控代理使用情况和异常连接

### 🚫 禁止场景
- 不要在生产环境中随意使用代理
- 不要通过代理访问未知的敏感网站
- 不要在不安全的网络环境下使用代理

## 状态指示
- **代理启用**: 🌐 代理已启用 (可访问国际网络)
- **代理停用**: 🏠 代理已停用 (仅访问本地网络)
- **连接正常**: ✅ 代理连接正常
- **连接异常**: ❌ 代理连接失败

使用 `/proxy` 命令可以轻松管理网络代理，确保在需要时访问国际网络资源！