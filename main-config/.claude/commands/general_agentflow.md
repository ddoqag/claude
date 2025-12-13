# AgentFlow 四模块智能协作系统

召唤🔗 **AgentFlow四模块系统**，使用Planner→Executor→Verifier→Generator的智能协作流程处理复杂任务。

## 系统架构

### 🧠 Planner (规划器)
- **任务分解**: 将复杂任务拆分为可执行的子任务
- **步骤规划**: 制定详细的执行计划和顺序
- **资源分配**: 智能分配专业Agent到各个子任务
- **依赖分析**: 识别任务间的依赖关系

### ⚙️ Executor (执行器)
- **专业执行**: 调用最适合的专业Agent执行任务
- **Agent协调**: 协调多个专业Agent的协作
- **进度跟踪**: 实时监控任务执行进度
- **异常处理**: 处理执行过程中的问题和异常

### ✅ Verifier (验证器)
- **质量检查**: 验证每个子任务的完成质量
- **结果验证**: 确保结果符合预期要求
- **标准检查**: 检查代码质量、安全性、性能
- **反馈机制**: 提供改进建议和修正方案

### 📝 Generator (生成器)
- **最终输出**: 整合所有结果生成最终响应
- **格式优化**: 优化输出格式和可读性
- **文档生成**: 自动生成相关文档和说明
- **总结报告**: 提供完整的任务执行总结

## 使用方式

### 基础命令
```bash
/general                    # 显示AgentFlow状态和Logo
/general help              # 查看完整帮助信息
/general status            # 查看四模块详细状态
```

### 任务管理命令
```bash
/general tasks             # 任务管理概览
/general tasks active      # 查看进行中任务 (Planner处理)
/general tasks list        # 列出所有任务 (Executor管理)
/general tasks completed   # 查看已完成任务 (Verifier验证)
/general projects         # 项目管理 (Generator文档化)
```

### 系统状态命令
```bash
/general modules          # 四模块状态检查
/general modules planner  # 查看Planner任务队列
/general modules executor # 查看Executor执行状态
/general modules verifier # 查看Verifier验证结果
/general modules generator# 查看Generator输出统计
```

### 智能开发支持

除了命令，AgentFlow四模块还能智能识别和处理开发需求：

#### 自动任务分解和执行
```bash
用户: 开发一个完整的量化交易系统
AgentFlow响应:
🧠 Planner: 分解为数据采集、策略开发、回测、部署等4个子任务
⚙️ Executor: 调用data-engineer、ml-engineer、backend-architect
✅ Verifier: 验证每个模块的质量和集成
📝 Generator: 生成完整的系统和文档

任务ID: agentflow_task_$(date +%s)
🔗 四模块协作已启动，开始智能生产...
```

#### 复杂项目管理
```bash
用户: 创建一个高可用的微服务架构
AgentFlow响应:
🧠 Planner: 分解为服务拆分、数据存储、负载均衡、监控等
⚙️ Executor: 调用cloud-architect、database-expert、devops-expert
✅ Verifier: 验证架构的扩展性和可靠性
📝 Generator: 生成架构图和实施计划
```

## 适用场景

### 🎯 最适合AgentFlow的任务
- **多步骤复杂项目**: 需要多个专业领域协作
- **系统集成**: 涉及多个组件的集成开发
- **架构设计**: 需要多角度考虑的复杂架构
- **质量要求高**: 需要严格验证的关键项目
- **大型开发**: 需要系统化管理的开发任务

### 💡 典型应用场景
1. **企业级应用开发** - 从需求到部署的完整流程
2. **数据科学项目** - 数据处理、分析、建模全流程
3. **云原生架构** - 容器化、微服务、DevOps集成
4. **AI系统集成** - 从数据处理到模型部署
5. **安全审计** - 全面的安全检查和修复

## 系统优势

### 🔄 系统化处理
- **完整工作流程**: 从分析到生成的完整链路
- **模块化设计**: 每个步骤都有专门模块负责
- **质量控制**: 内置验证和质量保证机制

### 🎯 专业化执行
- **智能Agent选择**: 根据任务特点选择最适合的Agent
- **多Agent协作**: 复杂任务的多Agent协调执行
- **专业深度**: 每个领域都有专业Agent深度处理

### ✅ 质量保证
- **多层验证**: 每个子任务都经过质量检查
- **标准检查**: 代码质量、安全性、性能全面检查
- **持续改进**: 基于反馈的持续优化机制

### 📊 可追溯性
- **完整记录**: 每个步骤都有详细记录
- **进度跟踪**: 实时任务进度和状态监控
- **结果分析**: 完整的任务执行分析和总结

## 模式对比

| 特性 | Flow Mode总监 | AgentFlow四模块 |
|------|---------------|-----------------|
| **处理方式** | 单一总监协调 | 四模块协作 |
| **任务分解** | 简单任务识别 | 系统化分解 |
| **质量保证** | 基础验证 | 四层质量检查 |
| **复杂度支持** | 中等 | 高复杂度 |
| **可追溯性** | 基础记录 | 完整追踪 |
| **专业深度** | 单一领域 | 多领域协作 |

## 技术架构

### 核心组件
- **FlowAgent**: 四模块主控制器 (`.claude/agentflow-core/flow_agent.py`)
- **Planner**: 任务规划模块 (`.claude/agentflow-core/planner.py`)
- **Executor**: 执行协调模块 (`.claude/agentflow-core/executor.py`)
- **Verifier**: 质量验证模块 (`.claude/agentflow-core/verifier.py`)
- **Generator**: 结果生成模块 (`.claude/agentflow-core/generator.py`)

### 集成方式
- **命令集成**: 保持`/general`命令接口兼容性
- **模块调用**: 后端完全替换为AgentFlow四模块
- **状态管理**: 统一的任务状态和进度管理
- **Agent生态**: 兼容现有的88个专业Agent

---

**🔗 AgentFlow四模块系统 - 复杂任务的智能协作解决方案**

**立即开始**: 输入 `/general` 启动四模块智能协作！

*版本: v2.0.0 | 架构: 四模块协作 | 响应时间: <1秒 | 质量: 四层保证*