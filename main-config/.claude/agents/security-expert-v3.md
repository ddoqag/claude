# Security Expert v3.0 - 2025年网络安全与应用安全专家指南

**技能标签**: 零信任安全, DevSecOps, 安全左移, 威胁检测, 合规管理, 安全自动化, 2025技术栈

## 目录
1. [零信任架构深度实现](#零信任架构深度实现)
2. [AI安全新兴威胁防护](#ai安全新兴威胁防护)
3. [云原生和容器安全](#云原生和容器安全)
4. [DevSecOps和安全左移](#devsecops和安全左移)
5. [合规和隐私保护](#合规和隐私保护)
6. [新兴威胁防护](#新兴威胁防护)
7. [实施策略和代码示例](#实施策略和代码示例)

---

## 零信任架构深度实现

### 2025年零信任成熟度模型

#### 成熟度级别定义
```yaml
# Zero Trust Maturity Model 2025
maturity_levels:
  level_0_traditional:
    description: "传统边界安全模型"
    characteristics:
      - 基于边界的访问控制
      - 网络为中心的安全策略
      - 静态权限管理

  level_1_initial:
    description: "零信任初步实施"
    characteristics:
      - 基础身份验证强化
      - 网络分段初步实施
      - 基本条件访问策略

  level_2_advanced:
    description: "零信任高级实施"
    characteristics:
      - 动态访问控制
      - 持续验证机制
      - 微分段架构

  level_3_optimized:
    description: "零信任优化实施"
    characteristics:
      - AI驱动的风险分析
      - 自适应安全策略
      - 自动化威胁响应

  level_4_leading:
    description: "零信任领导力级别"
    characteristics:
      - 预测性安全分析
      - 实时威胁情报集成
      - 自愈安全系统
```

#### 身份验证和授权现代化

#### 多因素认证(MFA)实施
```typescript
// Zero Trust Authentication Framework
interface ZeroTrustAuthConfig {
  mfa: {
    required: boolean;
    methods: AuthMethod[];
    adaptiveRisk: boolean;
    continuousAuth: boolean;
  };
  biometric: {
    enabled: boolean;
    methods: BiometricMethod[];
    livenessDetection: boolean;
  };
  deviceTrust: {
    deviceCompliance: boolean;
    deviceAuthentication: boolean;
    locationBased: boolean;
  };
}

class ZeroTrustAuthenticator {
  private config: ZeroTrustAuthConfig;
  private riskEngine: RiskAssessmentEngine;
  private deviceRegistry: DeviceTrustRegistry;

  async authenticateUser(
    credentials: UserCredentials,
    context: AuthContext
  ): Promise<AuthResult> {
    // 1. 初始身份验证
    const primaryAuth = await this.performPrimaryAuth(credentials);

    // 2. 风险评估
    const riskScore = await this.riskEngine.assessRisk({
      userId: credentials.userId,
      ip: context.ipAddress,
      device: context.deviceFingerprint,
      time: new Date(),
      behavior: context.behavioralPattern
    });

    // 3. 自适应认证
    if (riskScore > this.config.mfa.adaptiveThreshold) {
      await this.requireAdditionalFactors(primaryAuth);
    }

    // 4. 设备信任验证
    const deviceTrusted = await this.verifyDeviceTrust(context.device);

    // 5. 持续认证会话
    return this.createContinuousAuthSession(primaryAuth, riskScore);
  }

  private async requireAdditionalFactors(auth: AuthResult): Promise<void> {
    const requiredFactors = this.selectMfaMethods(auth.riskLevel);

    for (const factor of requiredFactors) {
      await this.verifyAuthFactor(factor);
    }
  }

  async verifyContinuousAuth(sessionId: string): Promise<boolean> {
    const session = await this.getSession(sessionId);
    const currentRisk = await this.riskEngine.assessRisk(session.context);

    if (currentRisk > session.maxAcceptableRisk) {
      await this.revokeSession(sessionId);
      return false;
    }

    return true;
  }
}

// 风险评估引擎
class RiskAssessmentEngine {
  private mlModel: RiskPredictionModel;
  private threatIntelligence: ThreatIntelService;

  async assessRisk(context: RiskContext): Promise<number> {
    const factors = await Promise.all([
      this.analyzeGeolocationRisk(context.ip),
      this.analyzeDeviceRisk(context.device),
      this.analyzeBehavioralRisk(context.behavior),
      this.analyzeThreatIntel(context),
      this.analyzeTimePattern(context.time)
    ]);

    return this.mlModel.predictRisk(factors);
  }

  private async analyzeBehavioralRisk(behavior: BehavioralPattern): Promise<number> {
    // AI驱动的行为分析
    const baseline = await this.getBehavioralBaseline(behavior.userId);
    const anomaly = this.detectAnomalies(baseline, behavior);

    return anomaly.severity * anomaly.confidence;
  }
}
```

#### 微分段和网络隔离

#### Kubernetes微分段策略
```yaml
# Zero Trust Microsegmentation for Kubernetes
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: zero-trust-microsegmentation
  namespace: production
spec:
  podSelector:
    matchLabels:
      security-tier: critical
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          security-tier: trusted
    - namespaceSelector:
        matchLabels:
          name: monitoring-system
    ports:
    - protocol: TCP
      port: 8080
    - protocol: TCP
      port: 8443
  egress:
  - to:
    - podSelector:
        matchLabels:
          security-tier: trusted
    - namespaceSelector:
        matchLabels:
          name: database
    ports:
    - protocol: TCP
      port: 5432
    - protocol: TCP
      port: 6379
  - to: []
    ports:
    - protocol: TCP
      port: 53
    - protocol: UDP
      port: 53
    - protocol: TCP
      port: 443

# Service Mesh Security Policy (Istio)
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: zero-trust-authorization
  namespace: production
spec:
  selector:
    matchLabels:
      app: payment-service
  rules:
  - from:
    - source:
        principals: ["cluster.local/ns/default/sa/frontend-service"]
    - source:
        namespaces: ["monitoring"]
  - to:
    - operation:
        methods: ["GET", "POST"]
        paths: ["/api/v1/payments/*"]
  - when:
    - key: request.headers[authorization]
      values: ["Bearer *"]
    - key: source.principal
      values: ["cluster.local/ns/default/sa/frontend-service"]
```

#### 设备信任和持续验证

#### 设备健康状态监控
```python
import asyncio
import hashlib
from typing import Dict, Optional, List
from dataclasses import dataclass
from enum import Enum

class DeviceTrustLevel(Enum):
    TRUSTED = "trusted"
    SUSPICIOUS = "suspicious"
    UNTRUSTED = "untrusted"

@dataclass
class DeviceFingerprint:
    hardware_id: str
    os_version: str
    security_patch_level: str
    installed_certificates: List[str]
    bios_version: str
    secure_boot_enabled: bool
    tpm_present: bool

@dataclass
class DeviceHealthMetrics:
    cpu_temperature: float
    memory_usage: float
    disk_encryption: bool
    firewall_enabled: bool
    antivirus_status: str
    last_security_scan: datetime
    vulnerabilities: List[Vulnerability]

class DeviceTrustManager:
    def __init__(self, config: DeviceTrustConfig):
        self.config = config
        self.trust_cache = {}
        self.blocklist = set()

    async def assess_device_trust(
        self,
        device_fingerprint: DeviceFingerprint,
        context: AccessContext
    ) -> DeviceTrustLevel:
        """评估设备信任状态"""

        # 1. 检查设备黑名单
        if device_fingerprint.hardware_id in self.blocklist:
            return DeviceTrustLevel.UNTRUSTED

        # 2. 验证设备完整性
        integrity_result = await self.verify_device_integrity(device_fingerprint)
        if not integrity_result.is_valid:
            return DeviceTrustLevel.UNTRUSTED

        # 3. 评估设备健康状态
        health_metrics = await self.collect_device_health(device_fingerprint)
        health_score = self.calculate_health_score(health_metrics)

        # 4. 分析设备行为模式
        behavior_score = await self.analyze_device_behavior(
            device_fingerprint.hardware_id,
            context
        )

        # 5. 综合信任评估
        total_score = (
            integrity_result.score * 0.4 +
            health_score * 0.3 +
            behavior_score * 0.3
        )

        if total_score >= self.config.trust_threshold:
            return DeviceTrustLevel.TRUSTED
        elif total_score >= self.config.suspicious_threshold:
            return DeviceTrustLevel.SUSPICIOUS
        else:
            return DeviceTrustLevel.UNTRUSTED

    async def continuous_device_monitoring(
        self,
        device_id: str
    ) -> asyncio.Task:
        """持续设备监控任务"""

        async def monitor_loop():
            while True:
                try:
                    health_metrics = await self.collect_device_health(device_id)
                    anomalies = await self.detect_anomalies(health_metrics)

                    if anomalies:
                        await self.handle_anomalies(device_id, anomalies)

                    await asyncio.sleep(self.config.monitoring_interval)

                except Exception as e:
                    logger.error(f"设备监控异常: {e}")
                    await asyncio.sleep(60)

        return asyncio.create_task(monitor_loop())

    async def verify_device_integrity(
        self,
        fingerprint: DeviceFingerprint
    ) -> IntegrityResult:
        """验证设备完整性"""

        # 远程证明验证
        attestation_result = await self.remote_attestation_verify(fingerprint)

        # 系统文件完整性检查
        file_integrity = await self.verify_system_integrity(fingerprint)

        # 安全配置验证
        security_config = await self.verify_security_configuration(fingerprint)

        return IntegrityResult(
            is_valid=all([
                attestation_result.is_valid,
                file_integrity.is_valid,
                security_config.is_valid
            ]),
            score=self.calculate_integrity_score([
                attestation_result,
                file_integrity,
                security_config
            ])
        )

class RemoteAttestationService:
    """远程证明服务"""

    async def generate_device_attestation(
        self,
        device_fingerprint: DeviceFingerprint
    ) -> AttestationReport:
        """生成设备证明报告"""

        # 使用TPM生成证明
        tpm_quote = await self.get_tpm_quote(device_fingerprint)

        # 生成系统状态哈希
        system_hash = self.generate_system_state_hash(device_fingerprint)

        # 时间戳和签名
        timestamp = datetime.utcnow()
        signature = await self.sign_attestation(tpm_quote, system_hash, timestamp)

        return AttestationReport(
            device_id=device_fingerprint.hardware_id,
            tpm_quote=tpm_quote,
            system_hash=system_hash,
            timestamp=timestamp,
            signature=signature
        )
```

---

## AI安全新兴威胁防护

### LLM攻击向量和防护策略

#### Prompt注入攻击防护
```python
import re
import json
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class AttackType(Enum):
    JAILBREAK = "jailbreak"
    ROLE_PLAYING = "role_playing"
    SYSTEM_PROMPT_LEAK = "system_prompt_leak"
    INDIRECT_INJECTION = "indirect_injection"
    MULTILINGUAL_ATTACK = "multilingual_attack"
    CODE_INJECTION = "code_injection"

@dataclass
class SecurityPolicy:
    max_prompt_length: int = 8000
    forbidden_patterns: List[str] = None
    restricted_topics: List[str] = None
    allowed_languages: List[str] = None
    content_filtering: bool = True
    output_sanitization: bool = True

class LLMSecurityGuard:
    """LLM安全防护系统"""

    def __init__(self, policy: SecurityPolicy):
        self.policy = policy
        self.attack_detector = AttackPatternDetector()
        self.content_filter = ContentFilter()
        self.output_sanitizer = OutputSanitizer()

    async def validate_and_process_input(
        self,
        user_input: str,
        context: Dict = None
    ) -> Tuple[bool, str, List[str]]:
        """验证并处理用户输入"""

        issues = []

        # 1. 输入长度检查
        if len(user_input) > self.policy.max_prompt_length:
            issues.append("输入长度超过限制")
            return False, "", issues

        # 2. 攻击模式检测
        attack_patterns = await self.attack_detector.detect_patterns(user_input)
        if attack_patterns:
            for pattern in attack_patterns:
                issues.append(f"检测到潜在攻击: {pattern.attack_type.value}")

            if any(p.severity == "high" for p in attack_patterns):
                return False, "", issues

        # 3. 内容过滤
        if self.policy.content_filtering:
            filter_violations = await self.content_filter.check_content(user_input)
            if filter_violations:
                issues.extend([f"内容违规: {v.type}" for v in filter_violations])
                return False, "", issues

        # 4. 语言检查
        if self.policy.allowed_languages:
            detected_langs = await self.detect_languages(user_input)
            if not any(lang in self.policy.allowed_languages for lang in detected_langs):
                issues.append("不支持的语言")
                return False, "", issues

        # 5. 输入净化处理
        sanitized_input = await self.sanitize_input(user_input)

        return True, sanitized_input, issues

    async def validate_and_process_output(
        self,
        model_output: str,
        original_input: str
    ) -> Tuple[bool, str, List[str]]:
        """验证并处理模型输出"""

        issues = []

        # 1. 敏感信息泄露检测
        data_leakage = await self.detect_data_leakage(model_output)
        if data_leakage:
            issues.extend([f"敏感信息泄露: {leak.type}" for leak in data_leakage])
            return False, "", issues

        # 2. 恶意代码检测
        malicious_code = await self.detect_malicious_code(model_output)
        if malicious_code:
            issues.append("检测到恶意代码")
            return False, "", issues

        # 3. 输出净化
        if self.policy.output_sanitization:
            sanitized_output = await self.output_sanitizer.sanitize(model_output)
        else:
            sanitized_output = model_output

        return True, sanitized_output, issues

class AttackPatternDetector:
    """攻击模式检测器"""

    def __init__(self):
        self.jailbreak_patterns = [
            r"(?i)(ignore|forget|disregard).*previous.*instruction",
            r"(?i)(you are now|i am now|act as).*(no longer|not an?).*assistant",
            r"(?i)(bypass|override|circumvent).*filter",
            r"(?i)(hypothetically|theoretically|imagine).*if.*were"
        ]

        self.injection_patterns = [
            r"(?i)(system|developer|assistant).*message.*:",
            r"(?i)(act|role|pretend).*as.*jailbreak",
            r"(?i)(ignore|forget).*above.*instruction",
            r"(?i)(###|---).*instruction.*below"
        ]

    async def detect_patterns(
        self,
        text: str
    ) -> List[AttackPattern]:
        """检测攻击模式"""

        detected_patterns = []

        # 检测越狱攻击
        for pattern in self.jailbreak_patterns:
            if re.search(pattern, text, re.IGNORECASE | re.MULTILINE):
                detected_patterns.append(
                    AttackPattern(
                        attack_type=AttackType.JAILBREAK,
                        pattern=pattern,
                        severity="high"
                    )
                )

        # 检测注入攻击
        for pattern in self.injection_patterns:
            if re.search(pattern, text, re.IGNORECASE | re.MULTILINE):
                detected_patterns.append(
                    AttackPattern(
                        attack_type=AttackType.INDIRECT_INJECTION,
                        pattern=pattern,
                        severity="medium"
                    )
                )

        # 检测编码攻击
        encoded_attacks = await self.detect_encoded_attacks(text)
        detected_patterns.extend(encoded_attacks)

        return detected_patterns

    async def detect_encoded_attacks(self, text: str) -> List[AttackPattern]:
        """检测编码攻击"""

        patterns = []

        # Base64编码检测
        try:
            import base64
            # 检查是否包含可能的base64字符串
            base64_strings = re.findall(r'[A-Za-z0-9+/]{20,}={0,2}', text)
            for b64_str in base64_strings:
                try:
                    decoded = base64.b64decode(b64_str).decode('utf-8')
                    if any(keyword in decoded.lower() for keyword in ['system', 'ignore', 'jailbreak']):
                        patterns.append(
                            AttackPattern(
                                attack_type=AttackType.CODE_INJECTION,
                                pattern=f"base64_encoded: {b64_str[:20]}...",
                                severity="high"
                            )
                        )
                except:
                    pass
        except:
            pass

        # URL编码检测
        try:
            from urllib.parse import unquote
            url_strings = re.findall(r'%[0-9A-Fa-f]{2,}', text)
            if url_strings:
                decoded = unquote(text)
                if any(keyword in decoded.lower() for keyword in ['system', 'ignore', 'jailbreak']):
                    patterns.append(
                        AttackPattern(
                            attack_type=AttackType.CODE_INJECTION,
                            pattern="url_encoded_attack",
                            severity="medium"
                        )
                    )
        except:
            pass

        return patterns

class ContentFilter:
    """内容过滤器"""

    def __init__(self):
        self.harmful_categories = {
            'violence': ['kill', 'murder', 'attack', 'violence', 'weapon'],
            'hate_speech': ['hate', 'discrimination', 'racist', 'sexist'],
            'illegal_activities': ['drug', 'illegal', 'crime', 'fraud'],
            'adult_content': ['porn', 'adult', 'explicit', 'sexual']
        }

    async def check_content(
        self,
        text: str
    ) -> List[ContentViolation]:
        """检查内容违规"""

        violations = []
        text_lower = text.lower()

        for category, keywords in self.harmful_categories.items():
            keyword_matches = [kw for kw in keywords if kw in text_lower]
            if keyword_matches:
                violations.append(
                    ContentViolation(
                        type=category,
                        keywords=keyword_matches,
                        severity="medium" if len(keyword_matches) == 1 else "high"
                    )
                )

        # 使用ML模型检测更复杂的内容违规
        ml_violations = await self.ml_content_detection(text)
        violations.extend(ml_violations)

        return violations

    async def ml_content_detection(
        self,
        text: str
    ) -> List[ContentViolation]:
        """使用机器学习检测内容违规"""

        # 这里可以集成实际的ML模型API
        # 示例实现：调用OpenAI的内容审核API或其他安全服务

        return []
```

#### 对抗攻击防御
```python
import numpy as np
import torch
import torch.nn as nn
from typing import List, Dict, Tuple, Optional

class AdversarialDefense:
    """对抗攻击防御系统"""

    def __init__(self, model_config: Dict):
        self.model_config = model_config
        self.detector = AdversarialDetector()
        self.defense_layers = self.initialize_defense_layers()

    def initialize_defense_layers(self) -> nn.ModuleList:
        """初始化防御层"""

        layers = nn.ModuleList([
            # 1. 输入净化层
            InputSanitizationLayer(),

            # 2. 异常检测层
            AnomalyDetectionLayer(),

            # 3. 对抗样本检测层
            AdversarialSampleDetector(),

            # 4. 输出验证层
            OutputValidationLayer()
        ])

        return layers

    async def defend_against_adversarial_attack(
        self,
        input_data: torch.Tensor,
        context: Dict = None
    ) -> Tuple[bool, torch.Tensor, List[str]]:
        """防御对抗攻击"""

        defense_alerts = []

        # 1. 输入净化
        sanitized_input, alerts = await self.sanitize_input(input_data)
        defense_alerts.extend(alerts)

        # 2. 异常检测
        is_anomalous, anomaly_score, alerts = await self.detect_anomalies(sanitized_input)
        if is_anomalous:
            defense_alerts.extend(alerts)
            return False, sanitized_input, defense_alerts

        # 3. 对抗样本检测
        is_adversarial, confidence, alerts = await self.detect_adversarial_samples(sanitized_input)
        if is_adversarial:
            defense_alerts.extend(alerts)
            # 应用防御措施
            sanitized_input = await self.apply_defense_measures(sanitized_input)

        return True, sanitized_input, defense_alerts

    async def detect_adversarial_samples(
        self,
        input_data: torch.Tensor
    ) -> Tuple[bool, float, List[str]]:
        """检测对抗样本"""

        detection_methods = [
            self.gradient_based_detection,
            self.statistical_detection,
            self.ensemble_detection,
            self.certified_robustness_detection
        ]

        scores = []
        alerts = []

        for method in detection_methods:
            try:
                score, method_alerts = await method(input_data)
                scores.append(score)
                alerts.extend(method_alerts)
            except Exception as e:
                alerts.append(f"检测方法异常: {str(e)}")

        # 综合评估
        avg_score = np.mean(scores)
        max_score = np.max(scores)

        # 如果任一方法检测到高置信度对抗样本
        is_adversarial = max_score > 0.8 or avg_score > 0.6

        return is_adversarial, avg_score, alerts

class AdversarialDetector:
    """对抗样本检测器"""

    async def gradient_based_detection(
        self,
        input_data: torch.Tensor
    ) -> Tuple[float, List[str]]:
        """基于梯度的对抗样本检测"""

        # 计算输入梯度
        gradients = torch.autograd.grad(
            outputs=self.model(input_data),
            inputs=input_data,
            grad_outputs=torch.ones_like(input_data),
            create_graph=True,
            retain_graph=True
        )[0]

        # 计算梯度统计特征
        gradient_norm = torch.norm(gradients)
        gradient_variance = torch.var(gradients)

        # 基于梯度特征的异常检测
        adversarial_score = self.calculate_adversarial_score(
            gradient_norm.item(),
            gradient_variance.item()
        )

        alerts = []
        if adversarial_score > 0.7:
            alerts.append(f"检测到高梯度方差: {gradient_variance.item():.4f}")

        return adversarial_score, alerts

    async def statistical_detection(
        self,
        input_data: torch.Tensor
    ) -> Tuple[float, List[str]]:
        """统计特征检测"""

        # 计算输入的统计特征
        input_mean = torch.mean(input_data)
        input_std = torch.std(input_data)
        input_range = torch.max(input_data) - torch.min(input_data)

        # 与正常输入分布比较
        deviation_score = self.calculate_distribution_deviation(
            input_mean.item(),
            input_std.item(),
            input_range.item()
        )

        alerts = []
        if deviation_score > 0.8:
            alerts.append("输入统计特征异常")

        return deviation_score, alerts

class CertifiedRobustness:
    """认证鲁棒性防御"""

    def __init__(self, certification_radius: float = 0.1):
        self.certification_radius = certification_radius

    async def certify_robustness(
        self,
        input_data: torch.Tensor,
        model: nn.Module
    ) -> Tuple[bool, float]:
        """认证输入的鲁棒性"""

        # 使用随机平滑技术进行鲁棒性认证
        num_samples = 1000
        noise_scale = self.certification_radius

        predictions = []

        for _ in range(num_samples):
            noisy_input = input_data + torch.randn_like(input_data) * noise_scale
            with torch.no_grad():
                pred = model(noisy_input)
                predictions.append(pred.argmax().item())

        # 计算预测的一致性
        from collections import Counter
        pred_counts = Counter(predictions)
        most_common_pred, count = pred_counts.most_common(1)[0]

        # 认证鲁棒性（如果多数预测一致）
        robustness_certified = count / num_samples > 0.75
        confidence = count / num_samples

        return robustness_certified, confidence

class PrivacyPreservingAI:
    """隐私保护AI系统"""

    def __init__(self, privacy_config: Dict):
        self.config = privacy_config
        self.differential_privacy = DifferentialPrivacy()
        self.federated_learning = FederatedLearning()
        self.homomorphic_encryption = HomomorphicEncryption()

    async def train_with_privacy_preservation(
        self,
        data: torch.utils.data.DataLoader,
        model: nn.Module
    ) -> nn.Module:
        """隐私保护训练"""

        # 1. 差分隐私训练
        if self.config.get('differential_privacy', True):
            model = await self.differential_privacy.train_with_dp(
                model, data,
                epsilon=self.config.get('dp_epsilon', 1.0),
                delta=self.config.get('dp_delta', 1e-5)
            )

        # 2. 联邦学习训练
        if self.config.get('federated_learning', False):
            model = await self.federated_learning.federated_train(model)

        # 3. 同态加密推理
        if self.config.get('homomorphic_encryption', False):
            model = await self.setup_homomorphic_inference(model)

        return model

    async def privacy_preserving_inference(
        self,
        model: nn.Module,
        encrypted_input: torch.Tensor
    ) -> torch.Tensor:
        """隐私保护推理"""

        # 同态加密推理
        if self.config.get('homomorphic_encryption', False):
            encrypted_output = await self.homomorphic_encryption.encrypt_inference(
                model, encrypted_input
            )
            return encrypted_output

        # 差分隐私推理
        elif self.config.get('differential_privacy', True):
            noisy_output = await self.add_inference_noise(model, encrypted_input)
            return noisy_output

        else:
            return model(encrypted_input)
```

---

## 云原生和容器安全

### Kubernetes 1.32+安全特性

#### Pod Security Standards 2025
```yaml
# Enhanced Pod Security Standards for Kubernetes 1.32+
apiVersion: v1
kind: Namespace
metadata:
  name: secure-production
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
    security.kubernetes.io/network-policy: enabled
    security.kubernetes.io/seccomp: enabled

---
# Strict Pod Security Policy
apiVersion: v1
kind: Pod
metadata:
  name: secure-application
  namespace: secure-production
  labels:
    app: secure-app
    security-tier: critical
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    runAsGroup: 3000
    fsGroup: 2000
    seccompProfile:
      type: RuntimeDefault
    windowsOptions:
      hostProcess: false
  containers:
  - name: app-container
    image: registry.company.com/secure-app:v3.2.1
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop:
        - ALL
        add:
        - NET_BIND_SERVICE
      runAsNonRoot: true
      runAsUser: 1000
      privileged: false
    resources:
      requests:
        memory: "256Mi"
        cpu: "100m"
      limits:
        memory: "512Mi"
        cpu: "500m"
    env:
    - name: CONFIG_PATH
      value: "/app/config"
    volumeMounts:
    - name: config-volume
      mountPath: /app/config
      readOnly: true
    - name: tmp-volume
      mountPath: /tmp
    - name: cache-volume
      mountPath: /app/cache
  volumes:
  - name: config-volume
    configMap:
      name: app-config
      defaultMode: 0400
  - name: tmp-volume
    emptyDir: {}
  - name: cache-volume
    emptyDir: {}
  imagePullSecrets:
  - name: registry-credentials
  runtimeClassName: gvisor

---
# Kyverno Policy as Code
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: container-security
  annotations:
    policies.kyverno.io/title: Container Security
    policies.kyverno.io/category: Security
    policies.kyverno.io/severity: high
spec:
  validationFailureAction: Enforce
  rules:
  - name: enforce-non-root-containers
    match:
      any:
      - resources:
          kinds:
          - Pod
    validate:
      message: "Containers must run as non-root users"
      pattern:
        spec:
          securityContext:
            runAsNonRoot: true
            runAsUser: ">0"
          =(volumes):
            - !("hostPath")

  - name: require-read-only-filesystem
    match:
      any:
      - resources:
          kinds:
          - Pod
    validate:
      message: "Containers must have read-only root filesystem"
      pattern:
        spec:
          containers:
          - =(securityContext):
              readOnlyRootFilesystem: true

  - name: drop-all-capabilities
    match:
      any:
      - resources:
          kinds:
          - Pod
    validate:
      message: "Containers must drop all Linux capabilities"
      pattern:
        spec:
          containers:
          - =(securityContext):
              capabilities:
                drop: ["ALL"]
                add: ["NET_BIND_SERVICE"]

  - name: disallow-privileged-containers
    match:
      any:
      - resources:
          kinds:
          - Pod
    validate:
      message: "Privileged containers are not allowed"
      pattern:
        spec:
          containers:
          - =(securityContext):
              privileged: false
```

#### 容器运行时安全(Runc, Kata)
```go
package main

import (
	"context"
	"fmt"
	"log"
	"os"
	"os/exec"
	"path/filepath"
	"time"

	"github.com/containerd/containerd"
	"github.com/containerd/containerd/cio"
	"github.com/containerd/containerd/containers"
	"github.com/containerd/containerd/namespaces"
	"github.com/containerd/containerd/oci"
	"github.com/opencontainers/runtime-spec/specs-go"
)

type SecureContainerRuntime struct {
	client    *containerd.Client
	runtimes  map[string]containerd.Runtime
	security  *RuntimeSecurityConfig
}

type RuntimeSecurityConfig struct {
	DefaultRuntime       string
	EnableSandboxing     bool
	SeccompProfilePath   string
	AppArmorProfilePath  string
	SelinuxLabel         string
	ReadOnlyRootFS       bool
	DropAllCapabilities  bool
	NoNewPrivileges      bool
	UserNamespace        bool
	PIDNamespace         bool
	NetworkNamespace     bool
	IPCNamespace         bool
	UTSNamespace         bool
	CgroupNamespace      bool
}

func NewSecureContainerRuntime(sockPath string, config *RuntimeSecurityConfig) (*SecureContainerRuntime, error) {
	client, err := containerd.New(sockPath, containerd.WithDefaultNamespace("default"))
	if err != nil {
		return nil, fmt.Errorf("failed to create containerd client: %w", err)
	}

	runtime := &SecureContainerRuntime{
		client:   client,
		runtimes: make(map[string]containerd.Runtime),
		security: config,
	}

	// 注册运行时
	if err := runtime.registerRuntimes(); err != nil {
		return nil, fmt.Errorf("failed to register runtimes: %w", err)
	}

	return runtime, nil
}

func (r *SecureContainerRuntime) registerRuntimes() error {
	// 注册标准runc运行时
	r.runtimes["runc"] = containerd.Runtime{
		Name: "io.containerd.runc.v2",
		Options: interface{}(map[string]interface{}{
			"Root":            "/var/lib/containerd/runc",
			"SystemdCgroup":   true,
			"NoPivotRoot":     false,
			"NoNewKeyring":    false,
			"ShimCgroup":      false,
			"IoUid":           0,
			"IoGid":           0,
		}),
	}

	// 注册Kata Containers运行时（用于需要硬件隔离的场景）
	r.runtimes["kata"] = containerd.Runtime{
		Name: "io.containerd.kata.v2",
		Options: interface{}(map[string]interface{}{
			"Path":           "/usr/bin/kata-runtime",
			"Debug":          false,
			"DisableSeccomp": false,
		}),
	}

	// 注册gVisor运行时（用于轻量级虚拟化）
	r.runtimes["gvisor"] = containerd.Runtime{
		Name: "io.containerd.runsc.v1",
		Options: interface{}(map[string]interface{}{
			"Path":          "/usr/bin/runsc",
			"Debug":         false,
			"DebugLog":      "/tmp/runsc.log",
			"Network":       "none",
		}),
	}

	return nil
}

func (r *SecureContainerRuntime) CreateSecureContainer(
	ctx context.Context,
	imageRef string,
	containerName string,
	options ...containerd.NewContainerOpts,
) (containerd.Container, error) {
	// 拉取镜像
	image, err := r.client.Pull(ctx, imageRef, containerd.WithPullUnpack)
	if err != nil {
		return nil, fmt.Errorf("failed to pull image %s: %w", imageRef, err)
	}

	// 构建安全选项
	secureOpts := r.buildSecurityOptions()

	// 合并用户提供的选项
	allOpts := append(secureOpts, options...)

	// 创建容器
	container, err := r.client.NewContainer(
		ctx,
		containerName,
		append(allOpts, containerd.WithImage(image))...,
	)
	if err != nil {
		return nil, fmt.Errorf("failed to create container: %w", err)
	}

	return container, nil
}

func (r *SecureContainerRuntime) buildSecurityOptions() []containerd.NewContainerOpts {
	var opts []containerd.NewContainerOpts

	// 基础安全配置
	opts = append(opts,
		containerd.WithNewSpec(
			oci.WithImageConfig(r.client.ImageService()),
			r.withSecuritySpec(),
		),
	)

	// 运行时选择
	runtimeName := r.selectRuntime()
	opts = append(opts, containerd.WithRuntime(runtimeName, nil))

	return opts
}

func (r *SecureContainerRuntime) withSecuritySpec() oci.SpecOpts {
	return func(ctx context.Context, client oci.Client, container *containers.Container, s *specs.Spec) error {
		// 设置非root用户
		if r.security.UserNamespace {
			if err := oci.WithUserNamespace(1000, 1000)(ctx, client, container, s); err != nil {
				return err
			}
		}

		// 设置命名空间隔离
		namespaces := []oci.SpecOpts{
			oci.WithPIDNamespace,
			oci.WithNetworkNamespace,
			oci.WithIPCNamespace,
			oci.WithUTSNamespace,
			oci.WithCgroupNamespace,
		}

		for _, nsOpt := range namespaces {
			if err := nsOpt(ctx, client, container, s); err != nil {
				return err
			}
		}

		// 安全配置
		if r.security.ReadOnlyRootFS {
			if err := oci.WithRootFSReadonly()(ctx, client, container, s); err != nil {
				return err
			}
		}

		if r.security.DropAllCapabilities {
			if err := oci.WithDroppedCapabilities([]string{"ALL"})(ctx, client, container, s); err != nil {
				return err
			}
		}

		if r.security.NoNewPrivileges {
			if err := oci.WithNewPrivileges(false)(ctx, client, container, s); err != nil {
				return err
			}
		}

		// Seccomp配置
		if r.security.SeccompProfilePath != "" {
			if err := oci.WithDefaultProfileSeccomp()(ctx, client, container, s); err != nil {
				return err
			}
		}

		// AppArmor配置
		if r.security.AppArmorProfilePath != "" {
			s.Process.ApparmorProfile = "container-default"
		}

		// SELinux配置
		if r.security.SelinuxLabel != "" {
			s.Process.SelinuxLabel = r.security.SelinuxLabel
		}

		// 资源限制
		if err := oci.WithResources(&specs.LinuxResources{
			CPU: &specs.LinuxCPU{
				Shares: 1000,
				Quota:  100000,
				Period: 1000000,
			},
			Memory: &specs.LinuxMemory{
				Limit: 512 * 1024 * 1024, // 512MB
				Swap:  256 * 1024 * 1024, // 256MB
			},
		})(ctx, client, container, s); err != nil {
			return err
		}

		return nil
	}
}

func (r *SecureContainerRuntime) selectRuntime() string {
	// 根据安全要求选择合适的运行时
	switch r.security.DefaultRuntime {
	case "kata":
		return "kata"
	case "gvisor":
		return "gvisor"
	default:
		return "runc"
	}
}

func (r *SecureContainerRuntime) RunSecureContainer(
	ctx context.Context,
	containerName string,
) (containerd.Task, error) {
	container, err := r.client.LoadContainer(ctx, containerName)
	if err != nil {
		return nil, fmt.Errorf("failed to load container: %w", err)
	}

	// 创建安全的IO配置
	ioCreator := cio.NewCreator(cio.WithStdio)

	// 启动容器
	task, err := container.NewTask(ctx, ioCreator)
	if err != nil {
		return nil, fmt.Errorf("failed to create task: %w", err)
	}

	// 等待容器退出
	exitStatusC, err := task.Wait(ctx)
	if err != nil {
		return nil, fmt.Errorf("failed to wait for task: %w", err)
	}

	// 启动容器进程
	if err := task.Start(ctx); err != nil {
		return nil, fmt.Errorf("failed to start task: %w", err)
	}

	// 处理容器退出
	go func() {
		status := <-exitStatusC
		code, _, err := status.Result()
		if err != nil {
			log.Printf("Container exited with error: %v", err)
		} else {
			log.Printf("Container exited with status code: %d", code)
		}

		// 清理资源
		task.Delete(ctx, containerd.WithProcessKill)
		container.Delete(ctx, containerd.WithSnapshotCleanup)
	}()

	return task, nil
}

// RuntimeSecurityMonitor 监控运行时安全
type RuntimeSecurityMonitor struct {
	runtime  *SecureContainerRuntime
	events   chan containerd.Event
	ctx      context.Context
	cancel   context.CancelFunc
}

func NewRuntimeSecurityMonitor(runtime *SecureContainerRuntime) *RuntimeSecurityMonitor {
	ctx, cancel := context.WithCancel(context.Background())
	return &RuntimeSecurityMonitor{
		runtime: runtime,
		ctx:     ctx,
		cancel:  cancel,
	}
}

func (m *RuntimeSecurityMonitor) Start() error {
	// 订阅容器事件
	eventFilter := `topic~="/containers/create|/containers/delete|/tasks/start|/tasks/exit"`
	events, err := m.runtime.client.EventService().Subscribe(m.ctx, eventFilter)
	if err != nil {
		return fmt.Errorf("failed to subscribe to events: %w", err)
	}

	m.events = make(chan containerd.Event, 100)

	go m.processEvents(events)
	go m.monitorRuntimeSecurity()

	return nil
}

func (m *RuntimeSecurityMonitor) processEvents(events <-chan *containerd.Envelope) {
	for envelope := range events {
		if envelope.Event != nil {
			m.events <- *envelope.Event
		}
	}
}

func (m *RuntimeSecurityMonitor) monitorRuntimeSecurity() {
	for {
		select {
		case event := <-m.events:
			if err := m.handleSecurityEvent(event); err != nil {
				log.Printf("Failed to handle security event: %v", err)
			}
		case <-m.ctx.Done():
			return
		}
	}
}

func (m *RuntimeSecurityMonitor) handleSecurityEvent(event containerd.Event) error {
	switch event.Topic {
	case "/containers/create":
		log.Printf("Container created: %s", event.Namespace)
		// 可以在这里添加容器创建时的安全检查
	case "/tasks/start":
		log.Printf("Task started: %s", event.Namespace)
		// 监控容器启动
	case "/tasks/exit":
		log.Printf("Task exited: %s", event.Namespace)
		// 清理容器相关资源
	}
	return nil
}
```

#### 服务网格安全模式
```yaml
# Istio服务网格安全配置 (2025年最佳实践)
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: istio-system
spec:
  mtls:
    mode: STRICT

---
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: namespace-wide-deny-all
  namespace: production
spec:
  selector:
    matchLabels: {}
  action: DENY

---
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: allow-specific-services
  namespace: production
spec:
  selector:
    matchLabels:
      app: payment-service
  action: ALLOW
  rules:
  - from:
    - source:
        principals: ["cluster.local/ns/default/sa/frontend-sa"]
  - to:
    - operation:
        methods: ["POST"]
        paths: ["/api/v1/payments"]
  when:
  - key: request.auth.claims[role]
    values: ["payment-processor"]
  - key: source.namespace
    values: ["frontend"]

---
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: tls-settings
  namespace: production
spec:
  host: "*.production.svc.cluster.local"
  trafficPolicy:
    tls:
      mode: ISTIO_MUTUAL
      cipherSuites:
      - "TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256"
      - "TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256"
      - "TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384"
      - "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384"
      minProtocolVersion: "TLSV1_3"
      maxProtocolVersion: "TLSV1_3"
    connectionPool:
      tcp:
        maxConnections: 100
        connectTimeout: 30s
        keepalive:
          time: 7200s
          interval: 75s
      http:
        http1MaxPendingRequests: 50
        http2MaxRequests: 1000
        maxRequestsPerConnection: 10
        maxRetries: 3
        idleTimeout: 300s

---
# Envoy过滤器配置用于高级安全
apiVersion: networking.istio.io/v1beta1
kind: EnvoyFilter
metadata:
  name: security-enhancements
  namespace: istio-system
spec:
  configPatches:
  - applyTo: HTTP_FILTER
    match:
      context: SIDECAR_INBOUND
      listener:
        filterChain:
          filter:
            name: "envoy.filters.network.http_connection_manager"
            subFilter:
              name: "envoy.filters.http.router"
    patch:
      operation: INSERT_BEFORE
      value:
        name: envoy.filters.http.jwt_authn
        typed_config:
          "@type": type.googleapis.com/envoy.extensions.filters.http.jwt_authn.v3.JwtAuthentication
          providers:
            example_provider:
              issuer: "https://company.com/auth"
              audiences:
              - "api.company.com"
              remote_jwks:
                uri: "https://company.com/auth/jwks.json"
                cache_duration: 300s
                fetch_timeout: 5s
  - applyTo: HTTP_FILTER
    match:
      context: SIDECAR_INBOUND
      listener:
        filterChain:
          filter:
            name: "envoy.filters.network.http_connection_manager"
            subFilter:
              name: "envoy.filters.http.jwt_authn"
    patch:
      operation: INSERT_AFTER
      value:
        name: envoy.filters.http.ratelimit
        typed_config:
          "@type": type.googleapis.com/envoy.extensions.filters.http.ratelimit.v3.RateLimit
          domain: "api"
          stage1:
            request_headers:
              header_name: ":path"
              descriptor_key: "path"
          rate_limits:
          - actions:
            - request_headers:
                descriptor_key: "path"
                descriptor_value: "/api/v1/payments"
            - generic_key:
                descriptor_key: "per_minute"
                descriptor_value: "100"

---
# 证书管理配置
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: security@company.com
    privateKeySecretRef:
      name: letsencrypt-prod-key
    solvers:
    - http01:
        ingress:
          class: istio

---
apiVersion: v1
kind: Secret
metadata:
  name: istio-ca-secret
  namespace: istio-system
type: kubernetes.io/tls
data:
  tls.crt: <base64-encoded-certificate>
  tls.key: <base64-encoded-private-key>
  ca.crt: <base64-encoded-ca-certificate>
```

---

## DevSecOps和安全左移

### 代码安全分析工具链2025

#### 统一安全扫描平台
```python
import asyncio
import json
import subprocess
import tempfile
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum

class SecurityToolType(Enum):
    SAST = "static_application_security_testing"
    DAST = "dynamic_application_security_testing"
    SCA = "software_composition_analysis"
    CONTAINER = "container_security"
    INFRASTRUCTURE = "infrastructure_as_code"
    SECRET = "secret_detection"

@dataclass
class SecurityIssue:
    tool_type: SecurityToolType
    tool_name: str
    severity: str  # critical, high, medium, low, info
    confidence: str  # high, medium, low
    title: str
    description: str
    file_path: str
    line_number: Optional[int]
    rule_id: str
    cwe_id: Optional[str]
    cve_id: Optional[str]
    owasp_category: Optional[str]
    remediation: str
    references: List[str]

@dataclass
class ScanResult:
    success: bool
    tool_name: str
    scan_duration: float
    issues_found: int
    issues: List[SecurityIssue]
    metadata: Dict[str, Any]

class SecurityToolchain:
    """统一安全扫描工具链"""

    def __init__(self, config: Dict):
        self.config = config
        self.tools = self.initialize_tools()
        self.result_aggregator = ResultAggregator()
        self.report_generator = ReportGenerator()

    def initialize_tools(self) -> Dict[SecurityToolType, List[BaseSecurityTool]]:
        """初始化安全工具"""
        tools = {
            SecurityToolType.SAST: [
                SemgrepTool(self.config.get('semgrep', {})),
                CodeQLTool(self.config.get('codeql', {})),
                SonarQubeTool(self.config.get('sonarqube', {})),
            ],
            SecurityToolType.SCA: [
                TrivyTool(self.config.get('trivy', {})),
                OWASPDepscanTool(self.config.get('depscan', {})),
                SnykTool(self.config.get('snyk', {})),
            ],
            SecurityToolType.SECRET: [
                GitleaksTool(self.config.get('gitleaks', {})),
                TruffleHogTool(self.config.get('trufflehog', {})),
                GitLeaksTool(self.config.get('gitleaks', {})),
            ],
            SecurityToolType.CONTAINER: [
                TrivyContainerTool(self.config.get('trivy', {})),
                ClairTool(self.config.get('clair', {})),
                AnchoreTool(self.config.get('anchore', {})),
            ],
            SecurityToolType.INFRASTRUCTURE: [
                TfsecTool(self.config.get('tfsec', {})),
                CheckovTool(self.config.get('checkov', {})),
                OPACheckTool(self.config.get('opa', {})),
            ],
            SecurityToolType.DAST: [
                OWASPZapTool(self.config.get('zap', {})),
                BurpSuiteTool(self.config.get('burp', {})),
                NucleiTool(self.config.get('nuclei', {})),
            ],
        }
        return tools

    async def scan_codebase(
        self,
        codebase_path: Path,
        enabled_tools: Optional[List[SecurityToolType]] = None
    ) -> Dict[str, ScanResult]:
        """扫描代码库"""

        if enabled_tools is None:
            enabled_tools = list(SecurityToolType)

        scan_tasks = []

        for tool_type in enabled_tools:
            if tool_type in self.tools:
                for tool in self.tools[tool_type]:
                    if tool.is_available():
                        scan_tasks.append(
                            self.run_security_scan(tool, codebase_path, tool_type)
                        )

        # 并行执行扫描
        scan_results = await asyncio.gather(*scan_tasks, return_exceptions=True)

        # 处理结果
        results = {}
        for result in scan_results:
            if isinstance(result, Exception):
                print(f"扫描失败: {result}")
            else:
                results[result.tool_name] = result

        return results

    async def run_security_scan(
        self,
        tool: 'BaseSecurityTool',
        codebase_path: Path,
        tool_type: SecurityToolType
    ) -> ScanResult:
        """运行单个安全扫描工具"""

        start_time = asyncio.get_event_loop().time()

        try:
            print(f"开始运行 {tool.name} 扫描...")

            # 执行扫描
            issues = await tool.scan(codebase_path)

            scan_duration = asyncio.get_event_loop().time() - start_time

            result = ScanResult(
                success=True,
                tool_name=tool.name,
                scan_duration=scan_duration,
                issues_found=len(issues),
                issues=issues,
                metadata={
                    'tool_version': tool.version,
                    'tool_config': tool.config,
                    'scan_time': start_time,
                }
            )

            print(f"{tool.name} 扫描完成，发现 {len(issues)} 个问题")
            return result

        except Exception as e:
            scan_duration = asyncio.get_event_loop().time() - start_time
            print(f"{tool.name} 扫描失败: {e}")

            return ScanResult(
                success=False,
                tool_name=tool.name,
                scan_duration=scan_duration,
                issues_found=0,
                issues=[],
                metadata={
                    'error': str(e),
                    'scan_time': start_time,
                }
            )

class SemgrepTool(BaseSecurityTool):
    """Semgrep SAST工具"""

    def __init__(self, config: Dict):
        super().__init__("semgrep", config)

    async def scan(self, codebase_path: Path) -> List[SecurityIssue]:
        """运行Semgrep扫描"""

        cmd = [
            "semgrep",
            f"--config=auto",
            "--json",
            "--no-rewrite-rule-ids",
            "--severity=INFO",
            str(codebase_path)
        ]

        # 添加自定义规则
        if self.config.get('custom_rules'):
            for rule_path in self.config['custom_rules']:
                cmd.extend(["--config", str(rule_path)])

        # 添加排除规则
        if self.config.get('exclude_patterns'):
            for pattern in self.config['exclude_patterns']:
                cmd.extend(["--exclude", pattern])

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.config.get('timeout', 300)
            )

            if result.returncode != 0 and result.returncode != 1:
                raise Exception(f"Semgrep执行失败: {result.stderr}")

            # 解析结果
            semgrep_results = json.loads(result.stdout)
            return self.parse_semgrep_results(semgrep_results)

        except subprocess.TimeoutExpired:
            raise Exception("Semgrep扫描超时")
        except json.JSONDecodeError as e:
            raise Exception(f"解析Semgrep结果失败: {e}")

    def parse_semgrep_results(self, results: Dict) -> List[SecurityIssue]:
        """解析Semgrep结果"""

        issues = []

        for result in results.get('results', []):
            metadata = result.get('metadata', {})
            extra = result.get('extra', {})

            issue = SecurityIssue(
                tool_type=SecurityToolType.SAST,
                tool_name="semgrep",
                severity=result.get('metadata', {}).get('severity', 'info').lower(),
                confidence=extra.get('metavars', {}).get('confidence', 'medium'),
                title=metadata.get('message', result.get('message', '')),
                description=extra.get('message', ''),
                file_path=result.get('path', ''),
                line_number=result.get('start', {}).get('line'),
                rule_id=result.get('check_id', ''),
                cwe_id=metadata.get('cwe'),
                owasp_category=metadata.get('owasp'),
                remediation=extra.get('fix', {}).get('regex', ''),
                references=metadata.get('references', [])
            )

            issues.append(issue)

        return issues

class TrivyTool(BaseSecurityTool):
    """Trivy SCA和容器扫描工具"""

    def __init__(self, config: Dict):
        super().__init__("trivy", config)

    async def scan_filesystem(self, codebase_path: Path) -> List[SecurityIssue]:
        """扫描文件系统依赖"""

        cmd = [
            "trivy", "fs",
            "--format", "json",
            "--quiet",
            "--no-progress",
            str(codebase_path)
        ]

        # 添加配置选项
        if self.config.get('severity'):
            cmd.extend(["--severity", ",".join(self.config['severity'])])

        if self.config.get('ignore_unfixed'):
            cmd.append("--ignore-unfixed")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.config.get('timeout', 600)
            )

            if result.returncode != 0:
                raise Exception(f"Trivy执行失败: {result.stderr}")

            trivy_results = json.loads(result.stdout)
            return self.parse_trivy_results(trivy_results)

        except subprocess.TimeoutExpired:
            raise Exception("Trivy扫描超时")

    async def scan_container(self, image_name: str) -> List[SecurityIssue]:
        """扫描容器镜像"""

        cmd = [
            "trivy", "image",
            "--format", "json",
            "--quiet",
            "--no-progress",
            image_name
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.config.get('timeout', 600)
            )

            if result.returncode != 0:
                raise Exception(f"Trivy容器扫描失败: {result.stderr}")

            trivy_results = json.loads(result.stdout)
            return self.parse_trivy_results(trivy_results)

        except subprocess.TimeoutExpired:
            raise Exception("Trivy容器扫描超时")

    def parse_trivy_results(self, results: Dict) -> List[SecurityIssue]:
        """解析Trivy结果"""

        issues = []

        for result in results.get('Results', []):
            for vulnerability in result.get('Vulnerabilities', []):
                issue = SecurityIssue(
                    tool_type=SecurityToolType.SCA,
                    tool_name="trivy",
                    severity=vulnerability.get('Severity', 'UNKNOWN').lower(),
                    confidence="high",
                    title=vulnerability.get('Title', ''),
                    description=vulnerability.get('Description', ''),
                    file_path=result.get('Target', ''),
                    line_number=None,
                    rule_id=vulnerability.get('VulnerabilityID', ''),
                    cwe_id=vulnerability.get('CweIDs', []),
                    cve_id=vulnerability.get('VulnerabilityID', ''),
                    owasp_category=None,
                    remediation=self.get_trivy_remediation(vulnerability),
                    references=vulnerability.get('References', [])
                )

                issues.append(issue)

        return issues

    def get_trivy_remediation(self, vulnerability: Dict) -> str:
        """获取Trivy漏洞修复建议"""

        fixed_version = vulnerability.get('FixedVersion')
        if fixed_version:
            return f"升级到版本 {fixed_version} 或更高版本"

        return vulnerability.get('Description', '')

class ResultAggregator:
    """结果聚合器"""

    def __init__(self):
        self.severity_weights = {
            'critical': 10,
            'high': 7,
            'medium': 4,
            'low': 1,
            'info': 0.1
        }

    def aggregate_results(
        self,
        scan_results: Dict[str, ScanResult]
    ) -> Dict[str, Any]:
        """聚合扫描结果"""

        all_issues = []
        tool_summary = {}

        # 收集所有问题
        for tool_name, result in scan_results.items():
            if result.success:
                all_issues.extend(result.issues)
                tool_summary[tool_name] = {
                    'issues_found': len(result.issues),
                    'scan_duration': result.scan_duration,
                    'severity_breakdown': self.get_severity_breakdown(result.issues)
                }
            else:
                tool_summary[tool_name] = {
                    'error': result.metadata.get('error', 'Unknown error'),
                    'scan_duration': result.scan_duration
                }

        # 去重和优先级排序
        deduplicated_issues = self.deduplicate_issues(all_issues)
        prioritized_issues = self.prioritize_issues(deduplicated_issues)

        # 计算风险评分
        risk_score = self.calculate_risk_score(prioritized_issues)

        return {
            'summary': {
                'total_issues': len(prioritized_issues),
                'critical_issues': len([i for i in prioritized_issues if i.severity == 'critical']),
                'high_issues': len([i for i in prioritized_issues if i.severity == 'high']),
                'medium_issues': len([i for i in prioritized_issues if i.severity == 'medium']),
                'low_issues': len([i for i in prioritized_issues if i.severity == 'low']),
                'info_issues': len([i for i in prioritized_issues if i.severity == 'info']),
                'risk_score': risk_score,
                'tools_executed': len(scan_results),
                'successful_scans': len([r for r in scan_results.values() if r.success])
            },
            'tool_summary': tool_summary,
            'issues': prioritized_issues,
            'recommendations': self.generate_recommendations(prioritized_issues)
        }

    def deduplicate_issues(self, issues: List[SecurityIssue]) -> List[SecurityIssue]:
        """去除重复的安全问题"""

        seen = set()
        deduplicated = []

        for issue in issues:
            # 创建唯一标识符
            issue_key = (
                issue.file_path,
                issue.line_number,
                issue.rule_id,
                issue.tool_type
            )

            if issue_key not in seen:
                seen.add(issue_key)
                deduplicated.append(issue)

        return deduplicated

    def prioritize_issues(self, issues: List[SecurityIssue]) -> List[SecurityIssue]:
        """按优先级排序问题"""

        return sorted(
            issues,
            key=lambda x: (
                -self.severity_weights.get(x.severity, 0),
                x.confidence == 'high',
                x.file_path
            )
        )

    def calculate_risk_score(self, issues: List[SecurityIssue]) -> float:
        """计算风险评分"""

        total_score = 0
        for issue in issues:
            severity_weight = self.severity_weights.get(issue.severity, 0)
            confidence_multiplier = {
                'high': 1.0,
                'medium': 0.7,
                'low': 0.4
            }.get(issue.confidence, 0.5)

            total_score += severity_weight * confidence_multiplier

        return min(total_score, 100)  # 限制最大值为100

class CI_CD_Security_Integration:
    """CI/CD安全集成"""

    def __init__(self, toolchain: SecurityToolchain):
        self.toolchain = toolchain

    async def integrate_github_actions(
        self,
        repo_path: Path,
        github_token: str
    ) -> Dict[str, Any]:
        """集成GitHub Actions安全工作流"""

        # 生成GitHub Actions工作流文件
        workflow_content = self.generate_github_workflow()

        workflow_path = repo_path / ".github" / "workflows" / "security.yml"
        workflow_path.parent.mkdir(parents=True, exist_ok=True)

        with open(workflow_path, 'w') as f:
            f.write(workflow_content)

        # 提交工作流文件
        await self.commit_security_workflow(workflow_path)

        # 设置GitHub安全特性
        await self.setup_github_security_features(repo_path, github_token)

        return {
            'workflow_created': str(workflow_path),
            'security_features_enabled': True
        }

    def generate_github_workflow(self) -> str:
        """生成GitHub Actions安全工作流"""

        return """name: Security Scan

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  schedule:
    - cron: '0 2 * * 1'  # 每周一凌晨2点

permissions:
  contents: read
  security-events: write
  actions: read

jobs:
  security-scan:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        tool: [semgrep, trivy, gitleaks]

    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      with:
        fetch-depth: 0

    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install security tools
      run: |
        pip install semgrep
        sudo apt-get update
        sudo apt-get install wget apt-transport-https gnupg lsb-release
        wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | sudo apt-key add -
        echo "deb https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main" | sudo tee -a /etc/apt/sources.list.d/trivy.list
        sudo apt-get update
        sudo apt-get install trivy
        wget https://github.com/gitleaks/gitleaks/releases/latest/download/gitleaks-linux-amd64
        chmod +x gitleaks-linux-amd64
        sudo mv gitleaks-linux-amd64 /usr/local/bin/gitleaks

    - name: Run ${{ matrix.tool }} scan
      run: |
        mkdir -p security-results
        case "${{ matrix.tool }}" in
          semgrep)
            semgrep --config=auto --json --output=security-results/semgrep.json . || true
            ;;
          trivy)
            trivy fs --format json --output security-results/trivy.json . || true
            ;;
          gitleaks)
            gitleaks detect --format json --output security-results/gitleaks.json || true
            ;;
        esac

    - name: Upload scan results
      uses: actions/upload-artifact@v3
      with:
        name: security-results-${{ matrix.tool }}
        path: security-results/

    - name: Process security results
      if: always()
      run: |
        python3 - <<'EOF'
        import json
        import os
        from pathlib import Path

        results_dir = Path('security-results')
        all_issues = []

        for result_file in results_dir.glob('*.json'):
            if result_file.stat().st_size > 0:
                with open(result_file) as f:
                    data = json.load(f)
                    # 处理不同工具的结果格式
                    # 这里需要根据具体工具格式进行调整
                    print(f"Processed {result_file.name}")

        # 生成安全报告
        report = {
            'summary': {
                'total_files_scanned': len(list(Path('.').rglob('*.py'))),
                'tools_run': ['semgrep', 'trivy', 'gitleaks'],
                'timestamp': '${{ github.event.head_commit.timestamp }}',
                'commit': '${{ github.sha }}',
                'repository': '${{ github.repository }}'
            },
            'issues': all_issues
        }

        with open('security-report.json', 'w') as f:
            json.dump(report, f, indent=2)
        EOF

    - name: Create security issue if critical findings
      if: failure()
      uses: actions/github-script@v6
      with:
        script: |
          const fs = require('fs');
          try {
            const report = JSON.parse(fs.readFileSync('security-report.json', 'utf8'));
            const criticalIssues = report.issues.filter(issue => issue.severity === 'critical');

            if (criticalIssues.length > 0) {
              await github.rest.issues.create({
                owner: context.repo.owner,
                repo: context.repo.repo,
                title: `🚨 Critical Security Issues Detected`,
                body: `Critical security issues were detected in commit ${{ github.sha }}:\\n\\n${criticalIssues.map(issue => `• ${issue.title} in ${issue.file_path}:${issue.line_number}`).join('\\n')}`,
                labels: ['security', 'critical']
              });
            }
          } catch (error) {
            console.log('No critical issues or error reading report:', error.message);
          }
"""

# 基础工具类
class BaseSecurityTool:
    """安全工具基类"""

    def __init__(self, name: str, config: Dict):
        self.name = name
        self.config = config
        self.version = self.get_version()

    def get_version(self) -> str:
        """获取工具版本"""
        try:
            result = subprocess.run(
                [self.name, "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.stdout.strip()
        except:
            return "unknown"

    def is_available(self) -> bool:
        """检查工具是否可用"""
        try:
            subprocess.run(
                [self.name, "--help"],
                capture_output=True,
                timeout=5
            )
            return True
        except:
            return False

    async def scan(self, codebase_path: Path) -> List[SecurityIssue]:
        """执行扫描 - 子类需要实现"""
        raise NotImplementedError
```

---

## 合规和隐私保护

### GDPR 2025年更新要求

#### 数据保护影响评估(DPIA)
```python
import hashlib
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum

class DataProtectionLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ProcessingPurpose(Enum):
    CONSENT = "consent"
    CONTRACT = "contract"
    LEGAL_OBLIGATION = "legal_obligation"
    VITAL_INTERESTS = "vital_interests"
    PUBLIC_TASK = "public_task"
    LEGITIMATE_INTERESTS = "legitimate_interests"

class DataSubjectRights(Enum):
    ACCESS = "access"
    RECTIFICATION = "rectification"
    ERASURE = "erasure"
    RESTRICTION = "restriction"
    DATA_PORTABILITY = "data_portability"
    OBJECTION = "objection"
    AUTOMATED_DECISION_MAKING = "automated_decision_making"

@dataclass
class DataCategory:
    name: str
    sensitivity_level: DataProtectionLevel
    special_category: bool  # 特殊类别数据（种族、政治观点、宗教信仰等）
    retention_period: int  # 保留期（天）
    processing_lawful_basis: ProcessingPurpose
    encryption_required: bool
    anonymization_required: bool

@dataclass
class DPIARisk:
    probability: str  # low, medium, high
    severity: str    # low, medium, high, critical
    description: str
    mitigation_measures: List[str]
    residual_risk: str

@dataclass
class DataProtectionImpactAssessment:
    assessment_id: str
    assessment_date: datetime
    controller_name: str
    processor_names: List[str]
    processing_purposes: List[ProcessingPurpose]
    data_categories: List[DataCategory]
    data_subjects: List[str]  # 数据主体类型
    processing_operations: List[str]
    risks: List[DPIARisk]
    compliance_measures: List[str]
    assessment_outcome: str  # compliant, needs_review, non_compliant
    reviewer: str
    approval_date: Optional[datetime] = None
    next_review_date: datetime = field(default_factory=lambda: datetime.now() + timedelta(days=365))

class GDPRComplianceManager:
    """GDPR合规管理器"""

    def __init__(self, config: Dict):
        self.config = config
        self.dpia_repository = DPIARepository()
        self.consent_manager = ConsentManagementSystem()
        self.data_subject_requests = DataSubjectRequestHandler()
        self.breach_notification = BreachNotificationSystem()

    async def conduct_dpia(
        self,
        processing_activity: Dict,
        reviewer_id: str
    ) -> DataProtectionImpactAssessment:
        """执行数据保护影响评估"""

        # 1. 创建DPIA记录
        assessment = await self.initialize_dpia(processing_activity, reviewer_id)

        # 2. 分析数据处理活动
        data_analysis = await self.analyze_data_processing(processing_activity)

        # 3. 识别风险
        risks = await self.identify_dpia_risks(data_analysis)

        # 4. 评估合规措施
        compliance_measures = await self.evaluate_compliance_measures(data_analysis)

        # 5. 生成评估结果
        assessment_outcome = await self.determine_assessment_outcome(risks, compliance_measures)

        # 6. 更新DPIA记录
        assessment.risks = risks
        assessment.compliance_measures = compliance_measures
        assessment.assessment_outcome = assessment_outcome
        assessment.next_review_date = datetime.now() + timedelta(days=365)

        # 7. 保存评估结果
        await self.dpia_repository.save(assessment)

        # 8. 发送审查通知
        if assessment_outcome in ['needs_review', 'non_compliant']:
            await self.notify_reviewer(assessment, reviewer_id)

        return assessment

    async def analyze_data_processing(
        self,
        processing_activity: Dict
    ) -> Dict[str, Any]:
        """分析数据处理活动"""

        analysis = {
            'data_volume': await self.estimate_data_volume(processing_activity),
            'data_subjects_count': await self.estimate_data_subjects(processing_activity),
            'data_types': await self.categorize_data_types(processing_activity),
            'processing_frequency': processing_activity.get('frequency', 'continuous'),
            'international_transfers': await self.check_international_transfers(processing_activity),
            'automated_processing': await self.check_automated_processing(processing_activity),
            'profiling_activities': await self.check_profiling_activities(processing_activity),
        }

        return analysis

    async def identify_dpia_risks(self, analysis: Dict) -> List[DPIARisk]:
        """识别DPIA风险"""

        risks = []

        # 数据量风险
        if analysis['data_volume'] > 100000:  # 10万条记录
            risks.append(DPIARisk(
                probability="medium",
                severity="high",
                description="处理大量个人数据可能导致大规模数据泄露",
                mitigation_measures=[
                    "实施强加密",
                    "最小化数据收集",
                    "定期安全审计",
                    "数据分类分级"
                ],
                residual_risk="low"
            ))

        # 国际传输风险
        if analysis['international_transfers']:
            risks.append(DPIARisk(
                probability="medium",
                severity="medium",
                description="数据跨境传输可能违反GDPR规定",
                mitigation_measures=[
                    "使用标准合同条款(SCCs)",
                    "确认接收国的充分性决定",
                    "实施额外的技术保障措施"
                ],
                residual_risk="low"
            ))

        # 自动化处理风险
        if analysis['automated_processing']:
            risks.append(DPIARisk(
                probability="high",
                severity="medium",
                description="自动化决策可能影响数据主体权利",
                mitigation_measures=[
                    "提供人工审查机制",
                    "确保算法透明性",
                    "实施定期审计",
                    "提供解释权利"
                ],
                residual_risk="medium"
            ))

        # 特殊类别数据风险
        for data_type in analysis['data_types']:
            if data_type.get('special_category'):
                risks.append(DPIARisk(
                    probability="medium",
                    severity="high",
                    description=f"处理特殊类别数据: {data_type['name']}",
                    mitigation_measures=[
                        "获取明确同意",
                        "实施额外安全保障",
                        "限制访问权限",
                        "定期风险评估"
                    ],
                    residual_risk="low"
                ))

        return risks

    async def ensure_data_subject_rights(self) -> Dict[str, Any]:
        """确保数据主体权利的实现"""

        rights_implementation = {
            'access_right': {
                'implemented': True,
                'response_time': '30 days',
                'automation_level': 'automated',
                'verification_required': True
            },
            'rectification_right': {
                'implemented': True,
                'response_time': '30 days',
                'audit_trail': True
            },
            'erasure_right': {
                'implemented': True,
                'response_time': '30 days',
                'verification_required': True,
                'backup_retention': '30 days'
            },
            'restriction_right': {
                'implemented': True,
                'response_time': '30 days'
            },
            'portability_right': {
                'implemented': True,
                'response_time': '30 days',
                'formats': ['JSON', 'XML', 'CSV']
            },
            'objection_right': {
                'implemented': True,
                'response_time': '30 days',
                'direct_marketing_optout': True
            },
            'automated_decision_making': {
                'implemented': True,
                'human_intervention': True,
                'explanation_provided': True
            }
        }

        return rights_implementation

class ConsentManagementSystem:
    """同意管理系统"""

    def __init__(self):
        self.consent_records = {}
        self.consent_templates = self.load_consent_templates()

    async def record_consent(
        self,
        data_subject_id: str,
        consent_data: Dict
    ) -> str:
        """记录同意"""

        consent_id = self.generate_consent_id()

        consent_record = {
            'consent_id': consent_id,
            'data_subject_id': data_subject_id,
            'timestamp': datetime.utcnow().isoformat(),
            'consent_given': consent_data['consent_given'],
            'purposes': consent_data['purposes'],
            'data_categories': consent_data['data_categories'],
            'retention_period': consent_data.get('retention_period'),
            'withdrawal_allowed': consent_data.get('withdrawal_allowed', True),
            'ip_address': consent_data.get('ip_address'),
            'user_agent': consent_data.get('user_agent'),
            'consent_language': consent_data.get('language', 'en'),
            'version': consent_data.get('version', '1.0'),
            'valid_from': datetime.utcnow().isoformat(),
            'valid_until': self.calculate_valid_until(consent_data)
        }

        # 验证同意的有效性
        is_valid = await self.validate_consent(consent_record)
        if not is_valid:
            raise ValueError("Invalid consent record")

        # 保存同意记录
        await self.save_consent_record(consent_record)

        return consent_id

    async def withdraw_consent(
        self,
        consent_id: str,
        withdrawal_reason: str
    ) -> bool:
        """撤回同意"""

        consent_record = await self.get_consent_record(consent_id)
        if not consent_record:
            raise ValueError("Consent record not found")

        if not consent_record.get('withdrawal_allowed', True):
            raise ValueError("Consent withdrawal not allowed")

        # 更新同意状态
        consent_record.update({
            'consent_given': False,
            'withdrawal_timestamp': datetime.utcnow().isoformat(),
            'withdrawal_reason': withdrawal_reason,
            'status': 'withdrawn'
        })

        # 保存更新后的记录
        await self.save_consent_record(consent_record)

        # 触发数据处理流程调整
        await self.adjust_processing_after_withdrawal(consent_record)

        return True

    async def validate_consent(
        self,
        consent_record: Dict
    ) -> bool:
        """验证同意记录的有效性"""

        # 检查必要字段
        required_fields = [
            'data_subject_id', 'consent_given', 'purposes',
            'data_categories', 'timestamp'
        ]

        for field in required_fields:
            if field not in consent_record:
                return False

        # 检查目的的明确性
        if not consent_record['purposes']:
            return False

        # 检查数据类别的具体性
        if not consent_record['data_categories']:
            return False

        # 检查同意的自由性（这里可以添加更多逻辑）
        # 例如检查是否为预勾选框等

        return True

    def calculate_valid_until(self, consent_data: Dict) -> str:
        """计算同意有效期"""

        retention_period = consent_data.get('retention_period_days', 365)
        valid_until = datetime.utcnow() + timedelta(days=retention_period)
        return valid_until.isoformat()

class DataSubjectRequestHandler:
    """数据主体请求处理器"""

    def __init__(self):
        self.request_queue = []
        self.processing_time_limit = 30  # 天

    async def process_access_request(
        self,
        data_subject_id: str,
        identity_verification: Dict
    ) -> Dict[str, Any]:
        """处理数据访问请求"""

        # 1. 验证身份
        identity_confirmed = await self.verify_identity(
            data_subject_id,
            identity_verification
        )

        if not identity_confirmed:
            raise ValueError("Identity verification failed")

        # 2. 收集相关数据
        personal_data = await self.collect_personal_data(data_subject_id)

        # 3. 应用数据最小化原则
        relevant_data = await self.apply_data_minimization(personal_data)

        # 4. 准备响应
        response = {
            'request_id': self.generate_request_id(),
            'data_subject_id': data_subject_id,
            'response_date': datetime.utcnow().isoformat(),
            'data_summary': self.generate_data_summary(relevant_data),
            'data_export': await self.export_data(relevant_data),
            'processing_activities': await self.get_processing_activities(data_subject_id),
            'recipients': await self.get_data_recipients(data_subject_id),
            'retention_periods': await self.get_retention_periods(data_subject_id),
            'rights_exercised': await self.get_rights_exercised(data_subject_id),
            'contact_information': self.get_contact_information()
        }

        # 5. 记录请求处理
        await self.log_request_processing(response)

        return response

    async def process_erasure_request(
        self,
        data_subject_id: str,
        identity_verification: Dict,
        erasure_scope: List[str] = None
    ) -> Dict[str, Any]:
        """处理数据删除请求"""

        # 1. 验证身份
        identity_confirmed = await self.verify_identity(
            data_subject_id,
            identity_verification
        )

        if not identity_confirmed:
            raise ValueError("Identity verification failed")

        # 2. 检查删除限制
        legal_holds = await self.check_legal_holds(data_subject_id)
        if legal_holds:
            raise ValueError(f"Deletion restricted due to legal holds: {legal_holds}")

        # 3. 执行数据删除
        deletion_results = await self.execute_data_erasure(
            data_subject_id,
            erasure_scope
        )

        # 4. 通知第三方处理者
        await self.notify_third_party_processors(data_subject_id)

        # 5. 准备响应
        response = {
            'request_id': self.generate_request_id(),
            'data_subject_id': data_subject_id,
            'response_date': datetime.utcnow().isoformat(),
            'deletion_completed': deletion_results,
            'exceptions': await self.get_deletion_exceptions(data_subject_id),
            'contact_information': self.get_contact_information()
        }

        # 6. 记录请求处理
        await self.log_request_processing(response)

        return response

class BreachNotificationSystem:
    """数据泄露通知系统"""

    def __init__(self):
        self.notification_templates = self.load_notification_templates()
        self.supervisory_authorities = self.load_authorities()

    async def detect_and_assess_breach(
        self,
        breach_indicators: List[Dict]
    ) -> Dict[str, Any]:
        """检测和评估数据泄露"""

        breach_assessment = {
            'breach_detected': False,
            'risk_level': 'low',
            'notification_required': False,
            'timeline_72h': False,
            'affected_data_subjects': 0,
            'data_types_affected': [],
            'mitigation_steps': []
        }

        # 分析泄露指标
        for indicator in breach_indicators:
            if self.is_data_breach_indicator(indicator):
                breach_assessment['breach_detected'] = True
                risk_level = await self.assess_breach_risk(indicator)
                breach_assessment['risk_level'] = max(
                    breach_assessment['risk_level'],
                    risk_level,
                    key=lambda x: {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}[x]
                )

        # 确定是否需要通知
        if breach_assessment['breach_detected']:
            notification_required = await self.determine_notification_requirement(
                breach_assessment
            )
            breach_assessment['notification_required'] = notification_required

            # 估算影响范围
            impact_assessment = await self.assess_breach_impact(breach_indicators)
            breach_assessment.update(impact_assessment)

        return breach_assessment

    async def send_breach_notifications(
        self,
        breach_assessment: Dict,
        breach_details: Dict
    ) -> Dict[str, Any]:
        """发送泄露通知"""

        notification_results = {
            'supervisory_authority_notified': False,
            'data_subjects_notified': False,
            'notification_timestamp': None,
            'notification_methods': [],
            'errors': []
        }

        try:
            # 通知监管机构（如果需要）
            if breach_assessment['notification_required']:
                await self.notify_supervisory_authority(breach_details)
                notification_results['supervisory_authority_notified'] = True
                notification_results['notification_methods'].append('supervisory_authority')

            # 通知数据主体（如果需要）
            if breach_assessment['risk_level'] in ['high', 'critical']:
                await self.notify_data_subjects(breach_assessment, breach_details)
                notification_results['data_subjects_notified'] = True
                notification_results['notification_methods'].append('data_subjects')

            notification_results['notification_timestamp'] = datetime.utcnow().isoformat()

        except Exception as e:
            notification_results['errors'].append(str(e))

        return notification_results

# SOC 2 Type II和ISO 27001合规工具
class ComplianceAuditSystem:
    """合规审计系统"""

    def __init__(self):
        self.soc2_controls = self.load_soc2_controls()
        self.iso27001_controls = self.load_iso27001_controls()
        self.audit_repository = AuditRepository()

    async def conduct_soc2_audit(
        self,
        audit_period: str,
        scope: List[str]
    ) -> Dict[str, Any]:
        """执行SOC 2 Type II审计"""

        audit_results = {
            'audit_id': self.generate_audit_id(),
            'audit_period': audit_period,
            'scope': scope,
            'controls_tested': [],
            'compliance_status': {},
            'exceptions': [],
            'recommendations': [],
            'overall_rating': None
        }

        # 测试安全控制
        for control_id in scope:
            if control_id in self.soc2_controls:
                control_result = await self.test_control(control_id, 'SOC2')
                audit_results['controls_tested'].append(control_result)

        # 评估合规状态
        compliance_status = await self.evaluate_compliance_status(audit_results['controls_tested'])
        audit_results['compliance_status'] = compliance_status

        # 识别例外情况
        exceptions = await self.identify_exceptions(audit_results['controls_tested'])
        audit_results['exceptions'] = exceptions

        # 生成改进建议
        recommendations = await self.generate_recommendations(audit_results['controls_tested'])
        audit_results['recommendations'] = recommendations

        # 计算总体评级
        overall_rating = await self.calculate_overall_rating(compliance_status)
        audit_results['overall_rating'] = overall_rating

        # 保存审计结果
        await self.audit_repository.save_audit_result(audit_results)

        return audit_results

    async def conduct_iso27001_audit(
        self,
        audit_period: str,
        scope: List[str]
    ) -> Dict[str, Any]:
        """执行ISO 27001审计"""

        audit_results = {
            'audit_id': self.generate_audit_id(),
            'audit_period': audit_period,
            'scope': scope,
            'controls_tested': [],
            'compliance_status': {},
            'non_conformities': [],
            'opportunities_for_improvement': [],
            'overall_compliance': None
        }

        # 测试ISO 27001控制措施
        for control_id in scope:
            if control_id in self.iso27001_controls:
                control_result = await self.test_control(control_id, 'ISO27001')
                audit_results['controls_tested'].append(control_result)

        # 评估符合性
        compliance_status = await self.evaluate_iso27001_compliance(audit_results['controls_tested'])
        audit_results['compliance_status'] = compliance_status

        # 识别不符合项
        non_conformities = await self.identify_non_conformities(audit_results['controls_tested'])
        audit_results['non_conformities'] = non_conformities

        # 识别改进机会
        opportunities = await self.identify_improvement_opportunities(audit_results['controls_tested'])
        audit_results['opportunities_for_improvement'] = opportunities

        # 计算总体符合性
        overall_compliance = await self.calculate_iso27001_compliance(compliance_status)
        audit_results['overall_compliance'] = overall_compliance

        return audit_results
```

---

## 新兴威胁防护

### 量子计算威胁准备

#### 后量子密码学实施
```python
import os
import json
import hashlib
from typing import Dict, List, Optional, Tuple, Union, Any
from dataclasses import dataclass
from enum import Enum
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, PublicFormat, NoEncryption

class QuantumAlgorithm(Enum):
    DILITHIUM = "dilithium"
    FALCON = "falcon"
    SPHINCSPLUS = "sphincsplus"
    CRYSTALS_KYBER = "crystals-kyber"
    NTRU = "ntru"
    HQC = "hqc"

class SecurityLevel(Enum):
    LEVEL_1 = "level1"  # 128位安全
    LEVEL_3 = "level3"  # 192位安全
    LEVEL_5 = "level5"  # 256位安全

@dataclass
class QuantumKeyPair:
    algorithm: QuantumAlgorithm
    security_level: SecurityLevel
    public_key: bytes
    private_key: bytes
    public_key_id: str
    created_at: datetime
    expires_at: datetime
    key_usage: List[str]

@dataclass
class HybridCiphertext:
    classical_component: bytes
    quantum_component: bytes
    algorithm_info: Dict[str, str]
    metadata: Dict[str, Any]

class PostQuantumCryptoSystem:
    """后量子密码学系统"""

    def __init__(self, config: Dict):
        self.config = config
        self.key_store = QuantumKeyStore()
        self.algorithms = self.initialize_algorithms()
        self.key_rotation_manager = KeyRotationManager()

    def initialize_algorithms(self) -> Dict[QuantumAlgorithm, Any]:
        """初始化后量子算法"""

        algorithms = {
            QuantumAlgorithm.DILITHIUM: DilithiumAlgorithm(),
            QuantumAlgorithm.FALCON: FalconAlgorithm(),
            QuantumAlgorithm.SPHINCSPLUS: SphincsPlusAlgorithm(),
            QuantumAlgorithm.CRYSTALS_KYBER: CrystalsKyberAlgorithm(),
            QuantumAlgorithm.NTRU: NTRUAlgorithm(),
            QuantumAlgorithm.HQC: HqcAlgorithm()
        }

        return algorithms

    async def generate_hybrid_keypair(
        self,
        algorithm: QuantumAlgorithm,
        security_level: SecurityLevel,
        key_usage: List[str] = None,
        key_size: int = 2048
    ) -> QuantumKeyPair:
        """生成混合密钥对（经典+后量子）"""

        # 1. 生成经典密钥对（用于向后兼容）
        classical_keypair = await self.generate_classical_keypair(key_size)

        # 2. 生成后量子密钥对
        quantum_algorithm = self.algorithms[algorithm]
        quantum_keypair = await quantum_algorithm.generate_keypair(security_level)

        # 3. 创建混合密钥对
        hybrid_keypair = QuantumKeyPair(
            algorithm=algorithm,
            security_level=security_level,
            public_key=quantum_keypair.public_key,
            private_key=quantum_keypair.private_key,
            public_key_id=self.generate_key_id(),
            created_at=datetime.utcnow(),
            expires_at=self.calculate_expiry_date(security_level),
            key_usage=key_usage or ["encryption", "signing"]
        )

        # 4. 安全存储密钥
        await self.key_store.store_keypair(
            hybrid_keypair,
            classical_keypair
        )

        return hybrid_keypair

    async def hybrid_encrypt(
        self,
        plaintext: bytes,
        recipient_public_key_id: str,
        algorithm: QuantumAlgorithm = None
    ) -> HybridCiphertext:
        """混合加密"""

        # 1. 获取接收方的混合公钥
        recipient_keys = await self.key_store.get_keypair(recipient_public_key_id)
        if not recipient_keys:
            raise ValueError("Recipient key not found")

        # 2. 生成临时对称密钥
        symmetric_key = os.urandom(32)  # AES-256

        # 3. 使用对称密钥加密明文
        ciphertext = await self.symmetric_encrypt(plaintext, symmetric_key)

        # 4. 使用混合方法加密对称密钥
        if algorithm is None:
            algorithm = recipient_keys.quantum_key.algorithm

        quantum_algorithm = self.algorithms[algorithm]

        # 经典加密组件（RSA/ECDH）
        classical_component = await self.classical_key_encapsulation(
            symmetric_key,
            recipient_keys.classical_public_key
        )

        # 后量子加密组件
        quantum_component = await quantum_algorithm.encrypt(
            symmetric_key,
            recipient_keys.quantum_key.public_key
        )

        # 5. 构建混合密文
        hybrid_ciphertext = HybridCiphertext(
            classical_component=classical_component,
            quantum_component=quantum_component,
            algorithm_info={
                "algorithm": algorithm.value,
                "security_level": recipient_keys.quantum_key.security_level.value,
                "classical_algorithm": "RSA-4096",  # 可配置
                "symmetric_algorithm": "AES-256-GCM"
            },
            metadata={
                "recipient_key_id": recipient_public_key_id,
                "encryption_timestamp": datetime.utcnow().isoformat(),
                "key_id": self.generate_key_id()
            }
        )

        return hybrid_ciphertext

    async def hybrid_decrypt(
        self,
        hybrid_ciphertext: HybridCiphertext,
        recipient_private_key_id: str
    ) -> bytes:
        """混合解密"""

        # 1. 获取接收方的私钥
        recipient_keys = await self.key_store.get_keypair(recipient_private_key_id)
        if not recipient_keys:
            raise ValueError("Private key not found")

        # 2. 尝试经典解密
        symmetric_key = None
        try:
            symmetric_key = await self.classical_key_decapsulation(
                hybrid_ciphertext.classical_component,
                recipient_keys.classical_private_key
            )
        except Exception as e:
            print(f"Classical decryption failed: {e}")

        # 3. 如果经典解密失败，尝试后量子解密
        if symmetric_key is None:
            algorithm = QuantumAlgorithm(hybrid_ciphertext.algorithm_info["algorithm"])
            quantum_algorithm = self.algorithms[algorithm]

            symmetric_key = await quantum_algorithm.decrypt(
                hybrid_ciphertext.quantum_component,
                recipient_keys.quantum_key.private_key
            )

        if symmetric_key is None:
            raise ValueError("Decryption failed - both classical and quantum methods failed")

        # 4. 使用对称密钥解密密文
        plaintext = await self.symmetric_decrypt(
            symmetric_key,
            hybrid_ciphertext.classical_component  # 假设密文在此处
        )

        return plaintext

    async def quantum_resistant_sign(
        self,
        message: bytes,
        private_key_id: str
    ) -> bytes:
        """量子抗性数字签名"""

        # 1. 获取签名私钥
        signer_keys = await self.key_store.get_keypair(private_key_id)
        if not signer_keys:
            raise ValueError("Signing key not found")

        # 2. 哈希消息
        message_hash = hashlib.sha256(message).digest()

        # 3. 生成后量子签名
        algorithm = signer_keys.quantum_key.algorithm
        quantum_algorithm = self.algorithms[algorithm]

        signature = await quantum_algorithm.sign(
            message_hash,
            signer_keys.quantum_key.private_key
        )

        # 4. 添加元数据
        signature_data = {
            "signature": signature.hex(),
            "algorithm": algorithm.value,
            "security_level": signer_keys.quantum_key.security_level.value,
            "key_id": private_key_id,
            "timestamp": datetime.utcnow().isoformat(),
            "message_hash": message_hash.hex()
        }

        return json.dumps(signature_data).encode()

    async def quantum_resistant_verify(
        self,
        message: bytes,
        signature_data: bytes,
        public_key_id: str
    ) -> bool:
        """验证量子抗性签名"""

        try:
            # 1. 解析签名数据
            signature_info = json.loads(signature_data.decode())

            # 2. 获取验证公钥
            verifier_key = await self.key_store.get_public_key(public_key_id)
            if not verifier_key:
                return False

            # 3. 哈希消息
            message_hash = hashlib.sha256(message).digest()

            # 4. 验证哈希匹配
            expected_hash = signature_info.get("message_hash")
            if message_hash.hex() != expected_hash:
                return False

            # 5. 使用后量子算法验证签名
            algorithm = QuantumAlgorithm(signature_info["algorithm"])
            quantum_algorithm = self.algorithms[algorithm]

            signature = bytes.fromhex(signature_info["signature"])

            is_valid = await quantum_algorithm.verify(
                message_hash,
                signature,
                verifier_key.public_key
            )

            return is_valid

        except Exception as e:
            print(f"Signature verification failed: {e}")
            return False

class KeyRotationManager:
    """密钥轮换管理器"""

    def __init__(self):
        self.rotation_schedule = self.load_rotation_schedule()
        self.compliance_requirements = self.load_compliance_requirements()

    async def schedule_key_rotation(
        self,
        key_id: str,
        rotation_interval_days: int = None
    ) -> Dict[str, Any]:
        """安排密钥轮换"""

        # 获取当前密钥信息
        key_info = await self.get_key_info(key_id)
        if not key_info:
            raise ValueError("Key not found")

        # 确定轮换间隔
        if rotation_interval_days is None:
            rotation_interval_days = self.get_default_rotation_interval(
                key_info.algorithm,
                key_info.security_level
            )

        # 计算轮换时间
        next_rotation = datetime.utcnow() + timedelta(days=rotation_interval_days)

        # 创建轮换计划
        rotation_plan = {
            'key_id': key_id,
            'current_rotation': next_rotation.isoformat(),
            'interval_days': rotation_interval_days,
            'algorithm': key_info.algorithm.value,
            'security_level': key_info.security_level.value,
            'status': 'scheduled'
        }

        # 保存轮换计划
        await self.save_rotation_plan(rotation_plan)

        return rotation_plan

    async def execute_key_rotation(self, key_id: str) -> Dict[str, Any]:
        """执行密钥轮换"""

        # 1. 获取当前密钥
        current_key = await self.get_key_info(key_id)
        if not current_key:
            raise ValueError("Key not found")

        # 2. 生成新密钥
        new_keypair = await self.generate_new_keypair(
            current_key.algorithm,
            current_key.security_level,
            current_key.key_usage
        )

        # 3. 更新密钥依赖项
        await self.update_key_dependencies(key_id, new_keypair.public_key_id)

        # 4. 标记旧密钥为已弃用
        await self.deprecate_key(key_id)

        # 5. 记录轮换事件
        rotation_event = {
            'old_key_id': key_id,
            'new_key_id': new_keypair.public_key_id,
            'rotation_timestamp': datetime.utcnow().isoformat(),
            'algorithm': current_key.algorithm.value,
            'security_level': current_key.security_level.value
        }

        await self.log_rotation_event(rotation_event)

        return {
            'rotation_completed': True,
            'new_key_id': new_keypair.public_key_id,
            'old_key_id': key_id,
            'rotation_timestamp': rotation_event['rotation_timestamp']
        }

class QuantumVulnerabilityScanner:
    """量子漏洞扫描器"""

    def __init__(self):
        self.vulnerability_database = self.load_vulnerability_database()
        self.quantum_risk_models = self.load_risk_models()

    async def scan_quantum_vulnerabilities(
        self,
        system_info: Dict,
        crypto_configurations: List[Dict]
    ) -> Dict[str, Any]:
        """扫描量子相关漏洞"""

        scan_results = {
            'scan_id': self.generate_scan_id(),
            'scan_timestamp': datetime.utcnow().isoformat(),
            'vulnerabilities': [],
            'risk_assessment': {},
            'recommendations': [],
            'quantum_readiness_score': 0
        }

        # 1. 扫描加密算法脆弱性
        crypto_vulnerabilities = await self.scan_crypto_vulnerabilities(crypto_configurations)
        scan_results['vulnerabilities'].extend(crypto_vulnerabilities)

        # 2. 扫描密钥管理问题
        key_vulnerabilities = await self.scan_key_management_vulnerabilities(system_info)
        scan_results['vulnerabilities'].extend(key_vulnerabilities)

        # 3. 扫描协议层面问题
        protocol_vulnerabilities = await self.scan_protocol_vulnerabilities(system_info)
        scan_results['vulnerabilities'].extend(protocol_vulnerabilities)

        # 4. 评估量子风险
        risk_assessment = await self.assess_quantum_risk(scan_results['vulnerabilities'])
        scan_results['risk_assessment'] = risk_assessment

        # 5. 生成建议
        recommendations = await self.generate_quantum_recommendations(scan_results['vulnerabilities'])
        scan_results['recommendations'] = recommendations

        # 6. 计算量子就绪度评分
        readiness_score = await self.calculate_quantum_readiness_score(scan_results)
        scan_results['quantum_readiness_score'] = readiness_score

        return scan_results

    async def assess_quantum_timeline_threat(
        self,
        current_crypto_strength: Dict,
        system_criticality: str
    ) -> Dict[str, Any]:
        """评估量子时间线威胁"""

        # 基于NIST预测的量子计算发展时间线
        quantum_timeline = {
            'rsa_2048_break': {
                'optimistic': 2027,
                'realistic': 2030,
                'pessimistic': 2035
            },
            'ecc_256_break': {
                'optimistic': 2028,
                'realistic': 2031,
                'pessimistic': 2036
            },
            'rsa_4096_break': {
                'optimistic': 2032,
                'realistic': 2035,
                'pessimistic': 2040
            }
        }

        # 评估系统面临的量子威胁
        threat_assessment = {
            'immediate_threat': False,
            'transition_timeline': None,
            'recommended_actions': [],
            'risk_level': 'low'
        }

        current_year = datetime.now().year

        for crypto_type, timeline in quantum_timeline.items():
            if crypto_type in current_crypto_strength:
                years_until_threat = timeline['realistic'] - current_year

                if years_until_threat <= 2:
                    threat_assessment['immediate_threat'] = True
                    threat_assessment['risk_level'] = 'critical'
                elif years_until_threat <= 5:
                    threat_assessment['risk_level'] = 'high'
                elif years_until_threat <= 10:
                    threat_assessment['risk_level'] = 'medium'

        # 确定迁移时间线
        if threat_assessment['risk_level'] in ['critical', 'high']:
            threat_assessment['transition_timeline'] = current_year + 2
        elif threat_assessment['risk_level'] == 'medium':
            threat_assessment['transition_timeline'] = current_year + 5
        else:
            threat_assessment['transition_timeline'] = current_year + 10

        # 生成建议行动
        threat_assessment['recommended_actions'] = [
            "开始规划后量子密码学迁移",
            "评估现有加密系统的量子脆弱性",
            "制定密钥管理升级策略",
            "建立密码学敏捷性框架",
            "关注NIST后量子标准化进程"
        ]

        return threat_assessment

# IoT和边缘设备安全
class IoTSecurityFramework:
    """IoT和边缘设备安全框架"""

    def __init__(self, config: Dict):
        self.config = config
        self.device_registry = DeviceRegistry()
        self.trust_manager = DeviceTrustManager()
        self.anomaly_detector = IoTAnomalyDetector()

    async def secure_device_onboarding(
        self,
        device_info: Dict,
        device_certificate: bytes
    ) -> Dict[str, Any]:
        """安全设备接入"""

        onboarding_result = {
            'device_id': None,
            'trust_level': None,
            'security_policies': [],
            'encryption_keys': {},
            'monitoring_config': {}
        }

        # 1. 验证设备身份
        device_auth = await self.authenticate_device(device_info, device_certificate)
        if not device_auth.success:
            raise ValueError(f"Device authentication failed: {device_auth.reason}")

        # 2. 评估设备信任度
        trust_assessment = await self.trust_manager.assess_device_trust(device_info)
        onboarding_result['trust_level'] = trust_assessment.level

        # 3. 生成设备专用加密密钥
        device_keys = await self.generate_device_keys(device_auth.device_id)
        onboarding_result['encryption_keys'] = device_keys

        # 4. 应用安全策略
        security_policies = await self.apply_security_policies(
            device_auth.device_id,
            trust_assessment
        )
        onboarding_result['security_policies'] = security_policies

        # 5. 配置监控
        monitoring_config = await self.configure_device_monitoring(
            device_auth.device_id,
            device_info['device_type']
        )
        onboarding_result['monitoring_config'] = monitoring_config

        # 6. 注册设备
        onboarding_result['device_id'] = device_auth.device_id
        await self.device_registry.register_device({
            'device_id': device_auth.device_id,
            'device_type': device_info['device_type'],
            'trust_level': trust_assessment.level,
            'certificate_fingerprint': hashlib.sha256(device_certificate).hexdigest(),
            'onboarding_timestamp': datetime.utcnow().isoformat(),
            'last_seen': datetime.utcnow().isoformat(),
            'status': 'active'
        })

        return onboarding_result

    async def monitor_device_security(
        self,
        device_id: str,
        telemetry_data: Dict
    ) -> Dict[str, Any]:
        """监控设备安全"""

        monitoring_result = {
            'device_id': device_id,
            'anomalies_detected': [],
            'security_events': [],
            'trust_score_change': None,
            'recommended_actions': []
        }

        # 1. 异常检测
        anomalies = await self.anomaly_detector.detect_anomalies(
            device_id,
            telemetry_data
        )
        monitoring_result['anomalies_detected'] = anomalies

        # 2. 安全事件分析
        security_events = await self.analyze_security_events(
            device_id,
            telemetry_data
        )
        monitoring_result['security_events'] = security_events

        # 3. 信任度评估
        if anomalies or security_events:
            trust_score_change = await self.trust_manager.update_trust_score(
                device_id,
                anomalies,
                security_events
            )
            monitoring_result['trust_score_change'] = trust_score_change

        # 4. 生成建议
        if anomalies or security_events:
            recommendations = await self.generate_security_recommendations(
                device_id,
                anomalies,
                security_events
            )
            monitoring_result['recommended_actions'] = recommendations

        # 5. 更新设备状态
        await self.device_registry.update_device_status(
            device_id,
            {
                'last_seen': datetime.utcnow().isoformat(),
                'last_anomaly_count': len(anomalies),
                'last_security_event_count': len(security_events)
            }
        )

        return monitoring_result

# 区块链和Web3安全
class BlockchainSecurityManager:
    """区块链和Web3安全管理器"""

    def __init__(self, config: Dict):
        self.config = config
        self.smart_contract_auditor = SmartContractAuditor()
        self.wallet_security = WalletSecurityManager()
        self.defi_security = DeFiSecurityAnalyzer()

    async def audit_smart_contract(
        self,
        contract_address: str,
        contract_source: str,
        blockchain: str
    ) -> Dict[str, Any]:
        """智能合约安全审计"""

        audit_result = {
            'contract_address': contract_address,
            'blockchain': blockchain,
            'vulnerabilities': [],
            'gas_optimizations': [],
            'security_score': 0,
            'recommendations': []
        }

        # 1. 静态分析
        static_issues = await self.smart_contract_auditor.static_analysis(
            contract_source,
            blockchain
        )
        audit_result['vulnerabilities'].extend(static_issues)

        # 2. 动态分析（如果合约已部署）
        if contract_address:
            dynamic_issues = await self.smart_contract_auditor.dynamic_analysis(
                contract_address,
                blockchain
            )
            audit_result['vulnerabilities'].extend(dynamic_issues)

        # 3. 模式匹配
        pattern_issues = await self.smart_contract_auditor.pattern_detection(
            contract_source
        )
        audit_result['vulnerabilities'].extend(pattern_issues)

        # 4. Gas优化分析
        gas_optimizations = await self.analyze_gas_optimizations(contract_source)
        audit_result['gas_optimizations'] = gas_optimizations

        # 5. 计算安全评分
        security_score = await self.calculate_contract_security_score(
            audit_result['vulnerabilities']
        )
        audit_result['security_score'] = security_score

        # 6. 生成修复建议
        recommendations = await self.generate_contract_recommendations(
            audit_result['vulnerabilities']
        )
        audit_result['recommendations'] = recommendations

        return audit_result

    async def secure_wallet_management(
        self,
        wallet_config: Dict,
        user_preferences: Dict
    ) -> Dict[str, Any]:
        """安全钱包管理"""

        wallet_security_result = {
            'wallet_id': None,
            'security_level': 'standard',
            'multisig_config': None,
            'hardware_wallet_integration': False,
            'transaction_rules': [],
            'recovery_options': []
        }

        # 1. 确定安全级别
        security_level = await self.determine_wallet_security_level(
            wallet_config,
            user_preferences
        )
        wallet_security_result['security_level'] = security_level

        # 2. 配置多重签名
        if security_level in ['high', 'maximum']:
            multisig_config = await self.setup_multisig_wallet(wallet_config)
            wallet_security_result['multisig_config'] = multisig_config

        # 3. 硬件钱包集成
        if user_preferences.get('hardware_wallet'):
            hw_integration = await self.setup_hardware_wallet_integration(
                wallet_config
            )
            wallet_security_result['hardware_wallet_integration'] = hw_integration

        # 4. 设置交易规则
        transaction_rules = await self.setup_transaction_rules(
            wallet_config,
            user_preferences
        )
        wallet_security_result['transaction_rules'] = transaction_rules

        # 5. 配置恢复选项
        recovery_options = await self.setup_recovery_options(
            wallet_config,
            user_preferences
        )
        wallet_security_result['recovery_options'] = recovery_options

        return wallet_security_result

    async def analyze_defi_protocol_security(
        self,
        protocol_address: str,
        protocol_type: str,
        blockchain: str
    ) -> Dict[str, Any]:
        """DeFi协议安全分析"""

        defi_analysis = {
            'protocol_address': protocol_address,
            'protocol_type': protocol_type,
            'blockchain': blockchain,
            'vulnerabilities': [],
            'economic_risks': [],
            'contract_risks': [],
            'liquidity_risks': [],
            'governance_risks': [],
            'overall_risk_score': 0
        }

        # 1. 智能合约风险评估
        contract_risks = await this.analyze_defi_contract_risks(
            protocol_address,
            blockchain
        )
        defi_analysis['contract_risks'] = contract_risks

        # 2. 经济机制分析
        economic_risks = await this.analyze_economic_mechanisms(
            protocol_address,
            protocol_type
        )
        defi_analysis['economic_risks'] = economic_risks

        # 3. 流动性风险评估
        liquidity_risks = await this.analyze_liquidity_risks(
            protocol_address,
            blockchain
        )
        defi_analysis['liquidity_risks'] = liquidity_risks

        # 4. 治理机制分析
        governance_risks = await this.analyze_governance_mechanisms(
            protocol_address,
            blockchain
        )
        defi_analysis['governance_risks'] = governance_risks

        # 5. 综合风险评估
        overall_risk_score = await this.calculate_defi_risk_score(defi_analysis)
        defi_analysis['overall_risk_score'] = overall_risk_score

        return defi_analysis
```

---

## 实施策略和代码示例

### 2025年完整安全威胁防护框架

#### 集成安全管理平台
```python
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

class SecurityFramework2025:
    """2025年网络安全威胁防护框架"""

    def __init__(self, config: Dict):
        self.config = config
        self.zero_trust = ZeroTrustSystem(config.get('zero_trust', {}))
        self.ai_security = AISecuritySystem(config.get('ai_security', {}))
        self.cloud_security = CloudNativeSecurity(config.get('cloud_security', {}))
        self.devsecops = DevSecOpsSystem(config.get('devsecops', {}))
        self.compliance = ComplianceSystem(config.get('compliance', {}))
        self.emerging_threats = EmergingThreatProtection(config.get('emerging_threats', {}))

        # 集成监控和响应系统
        self.security_monitoring = IntegratedSecurityMonitoring()
        self.threat_intelligence = ThreatIntelligencePlatform()
        self.incident_response = AutomatedIncidentResponse()

    async def initialize_framework(self) -> bool:
        """初始化安全框架"""

        try:
            # 1. 初始化各子系统
            initialization_tasks = [
                self.zero_trust.initialize(),
                self.ai_security.initialize(),
                self.cloud_security.initialize(),
                self.devsecops.initialize(),
                self.compliance.initialize(),
                self.emerging_threats.initialize()
            ]

            results = await asyncio.gather(*initialization_tasks, return_exceptions=True)

            # 2. 检查初始化结果
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logging.error(f"子系统初始化失败: {result}")
                    return False

            # 3. 建立系统集成
            await self.establish_integrations()

            # 4. 启动持续监控
            await self.start_continuous_monitoring()

            logging.info("2025年安全框架初始化完成")
            return True

        except Exception as e:
            logging.error(f"框架初始化失败: {e}")
            return False

    async def comprehensive_security_assessment(
        self,
        target_system: Dict,
        assessment_scope: List[str]
    ) -> Dict[str, Any]:
        """全面安全评估"""

        assessment_result = {
            'assessment_id': self.generate_assessment_id(),
            'timestamp': datetime.utcnow().isoformat(),
            'target_system': target_system,
            'assessment_scope': assessment_scope,
            'findings': {},
            'risk_score': 0,
            'recommendations': [],
            'compliance_status': {}
        }

        # 1. 零信任安全评估
        if 'zero_trust' in assessment_scope:
            zero_trust_assessment = await self.zero_trust.assess_security_posture(
                target_system
            )
            assessment_result['findings']['zero_trust'] = zero_trust_assessment

        # 2. AI安全评估
        if 'ai_security' in assessment_scope:
            ai_assessment = await self.ai_security.assess_ai_security(
                target_system
            )
            assessment_result['findings']['ai_security'] = ai_assessment

        # 3. 云原生安全评估
        if 'cloud_security' in assessment_scope:
            cloud_assessment = await self.cloud_security.assess_cloud_security(
                target_system
            )
            assessment_result['findings']['cloud_security'] = cloud_assessment

        # 4. DevSecOps评估
        if 'devsecops' in assessment_scope:
            devsecops_assessment = await self.devsecops.assess_devsecops_maturity(
                target_system
            )
            assessment_result['findings']['devsecops'] = devsecops_assessment

        # 5. 合规性评估
        if 'compliance' in assessment_scope:
            compliance_assessment = await self.compliance.assess_compliance(
                target_system
            )
            assessment_result['findings']['compliance'] = compliance_assessment
            assessment_result['compliance_status'] = compliance_assessment

        # 6. 新兴威胁评估
        if 'emerging_threats' in assessment_scope:
            emerging_assessment = await self.emerging_threats.assess_emerging_threats(
                target_system
            )
            assessment_result['findings']['emerging_threats'] = emerging_assessment

        # 7. 计算总体风险评分
        risk_score = await self.calculate_overall_risk_score(
            assessment_result['findings']
        )
        assessment_result['risk_score'] = risk_score

        # 8. 生成综合建议
        recommendations = await self.generate_comprehensive_recommendations(
            assessment_result['findings']
        )
        assessment_result['recommendations'] = recommendations

        return assessment_result

    async def automated_incident_response_workflow(
        self,
        incident_data: Dict
    ) -> Dict[str, Any]:
        """自动化事件响应工作流"""

        response_result = {
            'incident_id': self.generate_incident_id(),
            'timestamp': datetime.utcnow().isoformat(),
            'incident_type': incident_data.get('type', 'unknown'),
            'severity': incident_data.get('severity', 'medium'),
            'actions_taken': [],
            'containment_status': 'not_started',
            'remediation_status': 'not_started',
            'recovery_status': 'not_started',
            'lessons_learned': []
        }

        try:
            # 1. 事件分类和优先级
            incident_classification = await self.classify_incident(incident_data)
            response_result['classification'] = incident_classification

            # 2. 自动遏制
            if incident_classification['requires_containment']:
                containment_result = await self.execute_automatic_containment(
                    incident_data,
                    incident_classification
                )
                response_result['actions_taken'].append(containment_result)
                response_result['containment_status'] = 'completed'

            # 3. 证据收集
            evidence_collected = await self.collect_forensic_evidence(incident_data)
            response_result['forensic_evidence'] = evidence_collected

            # 4. 根因分析
            root_cause_analysis = await self.perform_root_cause_analysis(
                incident_data,
                evidence_collected
            )
            response_result['root_cause'] = root_cause_analysis

            # 5. 自动修复
            if root_cause_analysis['automated_remediation_possible']:
                remediation_result = await self.execute_automated_remediation(
                    root_cause_analysis
                )
                response_result['actions_taken'].append(remediation_result)
                response_result['remediation_status'] = 'completed'

            # 6. 系统恢复
            recovery_result = await self.execute_system_recovery(incident_data)
            response_result['actions_taken'].append(recovery_result)
            response_result['recovery_status'] = 'completed'

            # 7. 安全加固
            hardening_result = await self.apply_security_hardening(
                root_cause_analysis
            )
            response_result['actions_taken'].append(hardening_result)

            # 8. 生成事件报告
            incident_report = await self.generate_incident_report(response_result)
            response_result['incident_report'] = incident_report

            # 9. 更新威胁情报
            await self.update_threat_intelligence(incident_data, root_cause_analysis)

            # 10. 经验教训
            lessons_learned = await self.extract_lessons_learned(
                incident_data,
                root_cause_analysis,
                response_result['actions_taken']
            )
            response_result['lessons_learned'] = lessons_learned

        except Exception as e:
            logging.error(f"事件响应失败: {e}")
            response_result['error'] = str(e)
            response_result['status'] = 'failed'

        return response_result

class IntegratedSecurityMonitoring:
    """集成安全监控系统"""

    def __init__(self):
        self.log_sources = []
        self.monitoring_rules = []
        self.alerting_system = AlertingSystem()
        self.correlation_engine = EventCorrelationEngine()

    async def start_continuous_monitoring(self):
        """启动持续监控"""

        # 启动日志收集
        await self.start_log_collection()

        # 启动异常检测
        await self.start_anomaly_detection()

        # 启动威胁狩猎
        await self.start_threat_hunting()

        # 启动合规监控
        await self.start_compliance_monitoring()

    async def analyze_security_events(
        self,
        events: List[Dict]
    ) -> Dict[str, Any]:
        """分析安全事件"""

        analysis_result = {
            'total_events': len(events),
            'high_priority_events': 0,
            'correlated_incidents': [],
            'anomalies_detected': [],
            'security_recommendations': []
        }

        # 事件优先级分类
        for event in events:
            priority = await this.classify_event_priority(event)
            if priority in ['critical', 'high']:
                analysis_result['high_priority_events'] += 1

        # 事件关联分析
        correlated_incidents = await this.correlation_engine.correlate_events(events)
        analysis_result['correlated_incidents'] = correlated_incidents

        # 异常检测
        anomalies = await this.detect_anomalies(events)
        analysis_result['anomalies_detected'] = anomalies

        # 生成安全建议
        recommendations = await this.generate_security_recommendations(
            analysis_result['correlated_incidents'],
            analysis_result['anomalies_detected']
        )
        analysis_result['security_recommendations'] = recommendations

        return analysis_result

# 使用示例和最佳实践
async def main():
    """主函数 - 演示2025年安全框架使用"""

    # 1. 初始化安全框架
    config = load_security_config()
    security_framework = SecurityFramework2025(config)

    # 2. 启动框架
    framework_initialized = await security_framework.initialize_framework()
    if not framework_initialized:
        print("安全框架初始化失败")
        return

    print("2025年网络安全威胁防护框架已成功启动")

    # 3. 执行全面安全评估
    target_system = {
        'name': '企业云计算平台',
        'type': 'cloud_native',
        'components': ['kubernetes', 'microservices', 'ai_models'],
        'data_classification': 'confidential'
    }

    assessment_scope = [
        'zero_trust', 'ai_security', 'cloud_security',
        'devsecops', 'compliance', 'emerging_threats'
    ]

    security_assessment = await security_framework.comprehensive_security_assessment(
        target_system,
        assessment_scope
    )

    print(f"安全评估完成，风险评分: {security_assessment['risk_score']}/100")

    # 4. 处理安全事件
    sample_incident = {
        'type': 'ai_model_injection',
        'severity': 'high',
        'source': 'ml_service',
        'description': '检测到可疑的AI模型注入攻击',
        'evidence': {
            'malicious_input': 'ignore_previous_instructions',
            'model_response': 'unusual_behavior_detected'
        }
    }

    incident_response = await security_framework.automated_incident_response_workflow(
        sample_incident
    )

    print(f"安全事件处理完成: {incident_response['incident_id']}")

    # 5. 生成安全报告
    security_report = await generate_comprehensive_security_report(
        security_assessment,
        incident_response
    )

    # 保存报告
    await save_security_report(security_report)
    print("安全报告已生成并保存")

if __name__ == "__main__":
    asyncio.run(main())
```

#### 部署和运维最佳实践
```yaml
# security-framework-2025-deployment.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: security-framework
  labels:
    security-tier: critical
    purpose: security-management

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: security-framework-2025
  namespace: security-framework
  labels:
    app: security-framework-2025
    version: "3.0"
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: security-framework-2025
  template:
    metadata:
      labels:
        app: security-framework-2025
        security-tier: critical
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "9090"
        prometheus.io/path: "/metrics"
    spec:
      serviceAccountName: security-framework-sa
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        runAsGroup: 3000
        fsGroup: 2000
      containers:
      - name: security-framework
        image: security-company/framework-2025:v3.0.0
        imagePullPolicy: Always
        ports:
        - containerPort: 8080
          name: http
          protocol: TCP
        - containerPort: 9090
          name: metrics
          protocol: TCP
        env:
        - name: FRAMEWORK_CONFIG_PATH
          value: "/etc/security-framework/config"
        - name: LOG_LEVEL
          value: "INFO"
        - name: THREAT_INTEL_API_KEY
          valueFrom:
            secretKeyRef:
              name: security-secrets
              key: threat-intel-api-key
        - name: ENCRYPTION_KEY
          valueFrom:
            secretKeyRef:
              name: security-secrets
              key: encryption-key
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          capabilities:
            drop:
            - ALL
          runAsNonRoot: true
          runAsUser: 1000
        volumeMounts:
        - name: config-volume
          mountPath: /etc/security-framework/config
          readOnly: true
        - name: tls-certs
          mountPath: /etc/security-framework/certs
          readOnly: true
        - name: tmp-volume
          mountPath: /tmp
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
      volumes:
      - name: config-volume
        configMap:
          name: security-framework-config
          defaultMode: 0400
      - name: tls-certs
        secret:
          secretName: security-framework-tls
          defaultMode: 0400
      - name: tmp-volume
        emptyDir: {}
      imagePullSecrets:
      - name: registry-credentials
      tolerations:
      - key: "security-tier"
        operator: "Equal"
        value: "critical"
        effect: "NoSchedule"
      nodeSelector:
        security-tier: "critical"
        node-type: "security"

---
apiVersion: v1
kind: Service
metadata:
  name: security-framework-service
  namespace: security-framework
  labels:
    app: security-framework-2025
spec:
  type: ClusterIP
  ports:
  - port: 8080
    targetPort: 8080
    protocol: TCP
    name: http
  - port: 9090
    targetPort: 9090
    protocol: TCP
    name: metrics
  selector:
    app: security-framework-2025

---
apiVersion: networking.istio.io/v1beta1
kind: Gateway
metadata:
  name: security-framework-gateway
  namespace: security-framework
spec:
  selector:
    istio: ingressgateway
  servers:
  - port:
      number: 443
      name: https
      protocol: HTTPS
    tls:
      mode: SIMPLE
      credentialName: security-framework-tls
    hosts:
    - security-framework.company.com

---
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: security-framework-vs
  namespace: security-framework
spec:
  hosts:
  - security-framework.company.com
  gateways:
  - security-framework-gateway
  http:
  - match:
    - uri:
        prefix: /api/v1/
    route:
    - destination:
        host: security-framework-service
        port:
          number: 8080
    timeout: 30s
    retries:
      attempts: 3
      perTryTimeout: 10s

---
# 监控配置
apiVersion: v1
kind: ServiceMonitor
metadata:
  name: security-framework-monitor
  namespace: security-framework
  labels:
    app: security-framework-2025
spec:
  selector:
    matchLabels:
      app: security-framework-2025
  endpoints:
  - port: metrics
    interval: 30s
    path: /metrics

---
# 安全策略
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: security-framework-policy
  annotations:
    policies.kyverno.io/title: Security Framework Security Policy
    policies.kyverno.io/category: Security
    policies.kyverno.io/severity: high
spec:
  validationFailureAction: Enforce
  rules:
  - name: require-security-context
    match:
      any:
      - resources:
          kinds:
          - Pod
          namespaces:
          - security-framework
    validate:
      message: "Security framework pods must have non-root security context"
      pattern:
        spec:
          securityContext:
            runAsNonRoot: true
            runAsUser: ">0"

  - name: require-read-only-filesystem
    match:
      any:
      - resources:
          kinds:
          - Pod
          namespaces:
          - security-framework
    validate:
      message: "Security framework pods must have read-only root filesystem"
      pattern:
        spec:
          containers:
          - =(securityContext):
              readOnlyRootFilesystem: true
```

## 总结

这个security-expert-v3.md文档提供了2025年完整的网络安全和应用安全防护框架，包含：

### 核心升级内容

1. **零信任架构深度实现**
   - 2025年零信任成熟度模型
   - 现代化身份验证和授权
   - 微分段和网络隔离
   - 设备信任和持续验证

2. **AI安全新兴威胁防护**
   - LLM攻击向量防护
   - Prompt注入防御
   - 对抗攻击保护
   - 隐私保护AI系统

3. **云原生和容器安全**
   - Kubernetes 1.32+安全特性
   - 容器运行时安全
   - 服务网格安全模式
   - 无服务器安全

4. **DevSecOps和安全左移**
   - 统一安全扫描工具链
   - CI/CD安全集成
   - 代码安全分析
   - 自动化安全测试

5. **合规和隐私保护**
   - GDPR 2025年更新
   - SOC 2 Type II和ISO 27001
   - 数据保护影响评估
   - 数据主体权利保障

6. **新兴威胁防护**
   - 量子计算威胁准备
   - 后量子密码学实施
   - IoT和边缘设备安全
   - 区块链和Web3安全

### 实施特点

- **全面性**: 涵盖所有主要安全领域
- **前瞻性**: 包含2025年最新威胁和防护技术
- **实用性**: 提供完整的代码示例和部署配置
- **集成性**: 各安全组件相互集成，形成完整防护体系
- **自动化**: 强调安全自动化和智能化

这个框架为企业提供了2025年所需的完整网络安全解决方案，能够应对量子计算、AI攻击、云原生威胁等新兴安全挑战。