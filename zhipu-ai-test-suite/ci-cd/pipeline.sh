#!/bin/bash

# 智谱AI编码端点集成项目 - CI/CD流水线脚本
# 用于自动化构建、测试和部署

set -e  # 遇到错误时退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

# 配置变量
PYTHON_VERSION="3.11"
NODE_VERSION="18"
DOCKER_REGISTRY="your-registry.com"
IMAGE_NAME="zhipu-ai-integration"
ENVIRONMENT=${ENVIRONMENT:-development}
BRANCH_NAME=${BRANCH_NAME:-$(git rev-parse --abbrev-ref HEAD)}
COMMIT_SHA=${COMMIT_SHA:-$(git rev-parse HEAD)}
BUILD_NUMBER=${BUILD_NUMBER:-$(date +%Y%m%d%H%M%S)}

# 创建必要的目录
mkdir -p "$PROJECT_ROOT/logs"
mkdir -p "$PROJECT_ROOT/test_reports"
mkdir -p "$PROJECT_ROOT/artifacts"

# 日志文件
LOG_FILE="$PROJECT_ROOT/logs/pipeline_${BUILD_NUMBER}.log"

# 开始日志
exec > >(tee -a "$LOG_FILE")
exec 2>&1

print_info "Starting CI/CD Pipeline"
print_info "Environment: $ENVIRONMENT"
print_info "Branch: $BRANCH_NAME"
print_info "Commit: $COMMIT_SHA"
print_info "Build Number: $BUILD_NUMBER"

# 函数：检查命令是否存在
check_command() {
    if ! command -v $1 &> /dev/null; then
        print_error "$1 is not installed"
        exit 1
    fi
}

# 函数：检查端口是否可用
check_port() {
    local port=$1
    if lsof -i :$port &> /dev/null; then
        print_warning "Port $port is already in use"
        return 1
    fi
    return 0
}

# 函数：等待服务启动
wait_for_service() {
    local url=$1
    local max_attempts=30
    local attempt=1

    print_info "Waiting for service at $url"
    while [ $attempt -le $max_attempts ]; do
        if curl -s -o /dev/null -w "%{http_code}" "$url" | grep -q "200\|404"; then
            print_info "Service is ready"
            return 0
        fi
        print_info "Attempt $attempt/$max_attempts..."
        sleep 2
        ((attempt++))
    done

    print_error "Service failed to start within expected time"
    return 1
}

# 阶段1：环境准备
prepare_environment() {
    print_info "=== Preparing Environment ==="

    # 检查必要的工具
    print_info "Checking required tools..."
    check_command "python3"
    check_command "node"
    check_command "npm"
    check_command "docker"
    check_command "docker-compose"
    check_command "git"

    # 设置Python环境
    print_info "Setting up Python environment..."
    if command -v pythonenv &> /dev/null; then
        pythonenv local $PYTHON_VERSION
    fi

    # 创建虚拟环境
    if [ ! -d "venv" ]; then
        print_info "Creating Python virtual environment..."
        python3 -m venv venv
    fi

    # 激活虚拟环境
    source venv/bin/activate

    # 升级pip
    pip install --upgrade pip

    # 安装Python依赖
    print_info "Installing Python dependencies..."
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    fi

    if [ -f "requirements-dev.txt" ]; then
        pip install -r requirements-dev.txt
    fi

    # 安装测试依赖
    pip install pytest pytest-cov pytest-asyncio pytest-benchmark
    pip install selenium aiohttp docker
    pip install safety bandit semgrep
    pip install black flake8 mypy
    pip install beautifulsoup4 requests

    # 设置Node.js环境
    print_info "Setting up Node.js environment..."
    if command -v nvm &> /dev/null; then
        nvm use $NODE_VERSION
    fi

    # 安装Node.js依赖
    if [ -f "package.json" ]; then
        print_info "Installing Node.js dependencies..."
        npm ci
    fi

    # 设置环境变量
    print_info "Setting environment variables..."
    export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"
    export NODE_ENV=$ENVIRONMENT

    if [ -f ".env.$ENVIRONMENT" ]; then
        print_info "Loading environment variables from .env.$ENVIRONMENT"
        set -a
        source .env.$ENVIRONMENT
        set +a
    fi

    print_info "Environment preparation completed"
}

# 阶段2：代码质量检查
code_quality_checks() {
    print_info "=== Running Code Quality Checks ==="

    # Python代码格式检查
    print_info "Running Black (Python formatter)..."
    if ! black --check --diff zhipu-ai-sdk/ zhipu-ai-test-suite/; then
        print_warning "Python code formatting issues found. Running Black to fix..."
        black zhipu-ai-sdk/ zhipu-ai-test-suite/
    fi

    # Python代码风格检查
    print_info "Running Flake8 (Python linter)..."
    flake8 zhipu-ai-sdk/ zhipu-ai-test-suite/ --max-line-length=100 --ignore=E203,W503

    # Python类型检查
    print_info "Running MyPy (Python type checker)..."
    mypy zhipu-ai-sdk/ --ignore-missing-imports || true

    # JavaScript代码检查
    if [ -f "package.json" ]; then
        print_info "Running ESLint (JavaScript linter)..."
        if npm run lint; then
            print_info "ESLint checks passed"
        else
            print_warning "ESLint found issues"
        fi

        print_info "Running Prettier (JavaScript formatter)..."
        if npm run format:check; then
            print_info "Code formatting is correct"
        else
            print_warning "Running Prettier to fix formatting..."
            npm run format
        fi
    fi

    # 安全扫描
    print_info "Running Safety (Python security scanner)..."
    safety check || true

    print_info "Running Bandit (Python security linter)..."
    bandit -r zhipu-ai-sdk/ -f json -o "$PROJECT_ROOT/test_reports/bandit_report.json" || true

    print_info "Running Semgrep (static analysis)..."
    if command -v semgrep &> /dev/null; then
        semgrep --config=auto --json --output="$PROJECT_ROOT/test_reports/semgrep_report.json" zhipu-ai-sdk/ || true
    fi

    print_info "Code quality checks completed"
}

# 阶段3：单元测试
run_unit_tests() {
    print_info "=== Running Unit Tests ==="

    cd "$PROJECT_ROOT"

    # 运行Python单元测试
    print_info "Running Python unit tests with coverage..."
    python -m pytest zhipu-ai-test-suite/unit/ \
        -v \
        --cov=zhipu-ai-sdk \
        --cov-report=xml:coverage.xml \
        --cov-report=html:htmlcov \
        --cov-report=term-missing \
        --junit-xml="$PROJECT_ROOT/test_reports/unit_tests.xml"

    # 运行JavaScript单元测试（如果存在）
    if [ -f "package.json" ] && npm run test:unit &> /dev/null; then
        print_info "Running JavaScript unit tests..."
        npm run test:unit -- --coverage --ci --watchAll=false
    fi

    print_info "Unit tests completed"
}

# 阶段4：构建应用
build_application() {
    print_info "=== Building Application ==="

    # 构建Python包
    print_info "Building Python package..."
    python setup.py sdist bdist_wheel || true

    # 构建前端（如果存在）
    if [ -f "package.json" ] && npm run build &> /dev/null; then
        print_info "Building frontend application..."
        npm run build
    fi

    print_info "Application build completed"
}

# 阶段5：Docker构建
build_docker_images() {
    print_info "=== Building Docker Images ==="

    # 构建应用镜像
    print_info "Building application Docker image..."
    docker build -t $IMAGE_NAME:$BUILD_NUMBER \
                 -t $IMAGE_NAME:$BRANCH_NAME \
                 -f Dockerfile .

    # 构建测试镜像
    if [ -f "Dockerfile.test" ]; then
        print_info "Building test Docker image..."
        docker build -t $IMAGE_NAME-test:$BUILD_NUMBER \
                     -f Dockerfile.test .
    fi

    print_info "Docker images built successfully"
}

# 阶段6：集成测试
run_integration_tests() {
    print_info "=== Running Integration Tests ==="

    # 启动依赖服务（Redis, PostgreSQL等）
    print_info "Starting dependency services..."
    if [ -f "docker-compose.test.yml" ]; then
        docker-compose -f docker-compose.test.yml up -d
        sleep 10

        # 等待服务就绪
        wait_for_service http://localhost:6379  # Redis
        wait_for_service http://localhost:5432  # PostgreSQL
    fi

    # 运行集成测试
    print_info "Running Python integration tests..."
    python -m pytest zhipu-ai-test-suite/integration/ \
        -v \
        --junit-xml="$PROJECT_ROOT/test_reports/integration_tests.xml"

    print_info "Integration tests completed"
}

# 阶段7：性能测试
run_performance_tests() {
    print_info "=== Running Performance Tests ==="

    # 启动应用（如果尚未运行）
    print_info "Starting application for performance testing..."
    docker run -d \
        --name zhipu-ai-perf-test \
        -p 8080:8080 \
        -e ZHIPU_API_KEY=$ZHIPU_API_KEY \
        $IMAGE_NAME:$BUILD_NUMBER

    # 等待应用启动
    wait_for_service http://localhost:8080

    # 运行性能测试
    print_info "Running performance benchmarks..."
    python -m pytest zhipu-ai-test-suite/performance/ \
        -v \
        --benchmark-json="$PROJECT_ROOT/test_reports/performance_benchmarks.json"

    # 运行负载测试
    if command -v artillery &> /dev/null; then
        print_info "Running artillery load tests..."
        artillery run load-test-config.yml \
            --target http://localhost:8080 \
            --output "$PROJECT_ROOT/test_reports/load_test_results.json"
    fi

    # 清理
    docker stop zhipu-ai-perf-test
    docker rm zhipu-ai-perf-test

    print_info "Performance tests completed"
}

# 阶段8：安全测试
run_security_tests() {
    print_info "=== Running Security Tests ==="

    # 启动应用
    print_info "Starting application for security testing..."
    docker run -d \
        --name zhipu-ai-security-test \
        -p 8080:8080 \
        $IMAGE_NAME:$BUILD_NUMBER

    # 等待应用启动
    wait_for_service http://localhost:8080

    # 运行安全测试
    print_info "Running security tests..."
    python -m pytest zhipu-ai-test-suite/security/ \
        -v \
        --junit-xml="$PROJECT_ROOT/test_reports/security_tests.xml"

    # 运行Docker安全扫描
    if command -v trivy &> /dev/null; then
        print_info "Running Trivy vulnerability scanner..."
        trivy image --format json \
            --output "$PROJECT_ROOT/test_reports/docker_vulnerabilities.json" \
            $IMAGE_NAME:$BUILD_NUMBER
    fi

    # 清理
    docker stop zhipu-ai-security-test
    docker rm zhipu-ai-security-test

    print_info "Security tests completed"
}

# 阶段9：端到端测试
run_e2e_tests() {
    print_info "=== Running End-to-End Tests ==="

    # 启动完整环境
    print_info "Starting full application stack..."
    if [ -f "docker-compose.yml" ]; then
        docker-compose up -d
        sleep 30

        # 等待所有服务就绪
        wait_for_service http://localhost:3000  # Frontend
        wait_for_service http://localhost:8080  # Backend
    fi

    # 运行E2E测试
    print_info "Running end-to-end tests..."
    python -m pytest zhipu-ai-test-suite/e2e/ \
        -v \
        --html="$PROJECT_ROOT/test_reports/e2e_report.html" \
        --self-contained-html \
        --junit-xml="$PROJECT_ROOT/test_reports/e2e_tests.xml"

    print_info "End-to-end tests completed"
}

# 阶段10：生成测试报告
generate_reports() {
    print_info "=== Generating Test Reports ==="

    # 使用Python测试运行器生成综合报告
    python "$SCRIPT_DIR/test_runner.py" \
        --output "$PROJECT_ROOT/test_reports" \
        --notify

    # 合并所有XML报告
    if command -v junitparser &> /dev/null; then
        print_info "Merging test reports..."
        junitparser merge "$PROJECT_ROOT/test_reports"/*.xml \
            -o "$PROJECT_ROOT/test_reports/combined_tests.xml"
    fi

    # 生成测试覆盖率徽章
    if [ -f "coverage.xml" ]; then
        print_info "Generating coverage badge..."
        # 这里可以集成第三方徽章生成服务
    fi

    print_info "Test reports generated"
}

# 阶段11：打包和发布
package_and_release() {
    print_info "=== Packaging and Release ==="

    # 仅在master/main分支执行发布
    if [[ "$BRANCH_NAME" == "master" || "$BRANCH_NAME" == "main" ]]; then
        print_info "Creating release artifacts..."

        # 创建发布目录
        RELEASE_DIR="$PROJECT_ROOT/artifacts/release_$BUILD_NUMBER"
        mkdir -p "$RELEASE_DIR"

        # 复制构建产物
        cp dist/* "$RELEASE_DIR/" 2>/dev/null || true
        cp -r frontend/dist "$RELEASE_DIR/frontend" 2>/dev/null || true

        # 创建版本信息文件
        cat > "$RELEASE_DIR/version.json" << EOF
{
    "version": "$BUILD_NUMBER",
    "commit": "$COMMIT_SHA",
    "branch": "$BRANCH_NAME",
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "environment": "$ENVIRONMENT"
}
EOF

        # 压缩发布包
        cd "$PROJECT_ROOT/artifacts"
        tar -czf "zhipu-ai-integration-$BUILD_NUMBER.tar.gz" "release_$BUILD_NUMBER"

        # 推送Docker镜像到注册表（仅生产环境）
        if [ "$ENVIRONMENT" = "production" ]; then
            print_info "Pushing Docker images to registry..."
            docker tag $IMAGE_NAME:$BUILD_NUMBER $DOCKER_REGISTRY/$IMAGE_NAME:$BUILD_NUMBER
            docker tag $IMAGE_NAME:$BUILD_NUMBER $DOCKER_REGISTRY/$IMAGE_NAME:latest
            docker push $DOCKER_REGISTRY/$IMAGE_NAME:$BUILD_NUMBER
            docker push $DOCKER_REGISTRY/$IMAGE_NAME:latest
        fi

        print_info "Release artifacts created"
    else
        print_info "Skipping release on non-master branch"
    fi
}

# 阶段12：部署
deploy_application() {
    print_info "=== Deploying Application ==="

    # 仅在特定环境部署
    if [[ "$ENVIRONMENT" == "staging" || "$ENVIRONMENT" == "production" ]]; then
        print_info "Deploying to $ENVIRONMENT environment..."

        # 使用Helm或Kubectl部署
        if command -v helm &> /dev/null && [ -d "helm-chart" ]; then
            print_info "Deploying with Helm..."
            cd helm-chart
            helm upgrade --install zhipu-ai . \
                --set image.tag=$BUILD_NUMBER \
                --set environment=$ENVIRONMENT \
                --namespace $ENVIRONMENT
        elif [ -f "docker-compose.prod.yml" ]; then
            print_info "Deploying with Docker Compose..."
            docker-compose -f docker-compose.prod.yml up -d
        else
            print_warning "No deployment configuration found"
        fi

        print_info "Deployment completed"
    else
        print_info "Skipping deployment for $ENVIRONMENT environment"
    fi
}

# 清理函数
cleanup() {
    print_info "=== Cleaning Up ==="

    # 停止并移除测试容器
    if [ -f "docker-compose.test.yml" ]; then
        docker-compose -f docker-compose.test.yml down -v
    fi

    if [ -f "docker-compose.yml" ]; then
        docker-compose down
    fi

    # 清理Docker镜像（可选）
    if [ "$CLEANUP_DOCKER" = "true" ]; then
        docker system prune -f
    fi

    print_info "Cleanup completed"
}

# 错误处理
handle_error() {
    print_error "Pipeline failed at stage: $1"
    print_error "Check logs at: $LOG_FILE"

    # 发送失败通知
    if [ -f "$SCRIPT_DIR/notify.sh" ]; then
        "$SCRIPT_DIR/notify.sh" failure "$1"
    fi

    cleanup
    exit 1
}

# 设置错误处理
trap 'handle_error "${BASH_COMMAND}"' ERR

# 主流程
main() {
    # 解析命令行参数
    case "${1:-all}" in
        "prepare")
            prepare_environment
            ;;
        "quality")
            code_quality_checks
            ;;
        "unit")
            run_unit_tests
            ;;
        "build")
            build_application
            build_docker_images
            ;;
        "integration")
            run_integration_tests
            ;;
        "performance")
            run_performance_tests
            ;;
        "security")
            run_security_tests
            ;;
        "e2e")
            run_e2e_tests
            ;;
        "test")
            code_quality_checks
            run_unit_tests
            run_integration_tests
            run_performance_tests
            run_security_tests
            run_e2e_tests
            ;;
        "package")
            build_application
            build_docker_images
            package_and_release
            ;;
        "deploy")
            deploy_application
            ;;
        "all")
            prepare_environment
            code_quality_checks
            run_unit_tests
            build_application
            build_docker_images
            run_integration_tests
            run_performance_tests
            run_security_tests
            run_e2e_tests
            generate_reports
            package_and_release
            deploy_application
            ;;
        *)
            echo "Usage: $0 {prepare|quality|unit|build|integration|performance|security|e2e|test|package|deploy|all}"
            exit 1
            ;;
    esac

    cleanup
    print_info "Pipeline completed successfully!"
}

# 执行主函数
main "$@"