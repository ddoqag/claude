"""
自动化测试运行器
用于执行所有类型的测试并生成报告
"""

import os
import sys
import time
import json
import subprocess
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import asyncio
import aiohttp
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart


@dataclass
class TestResult:
    """测试结果数据类"""
    name: str
    type: str  # unit, integration, performance, security, e2e
    status: str  # passed, failed, skipped, error
    duration: float
    passed: int
    failed: int
    skipped: int
    errors: int
    coverage: Optional[float] = None
    details: Dict[str, Any] = None


@dataclass
class TestReport:
    """测试报告数据类"""
    timestamp: str
    total_duration: float
    total_passed: int
    total_failed: int
    total_skipped: int
    total_errors: int
    overall_status: str
    test_results: List[TestResult]
    coverage_summary: Dict[str, float]
    performance_summary: Dict[str, float]
    security_summary: Dict[str, Any]


class TestRunner:
    """测试运行器"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.test_suite_dir = project_root / "zhipu-ai-test-suite"
        self.results: List[TestResult] = []
        self.start_time = None
        self.end_time = None

    def run_unit_tests(self) -> TestResult:
        """运行单元测试"""
        print("\n" + "="*50)
        print("Running Unit Tests")
        print("="*50)

        unit_test_dir = self.test_suite_dir / "unit"
        cmd = [
            sys.executable, "-m", "pytest",
            str(unit_test_dir),
            "-v",
            "--tb=short",
            "--cov-report=json",
            "--cov-report=term-missing",
            "--cov=zhipu-ai-sdk"
        ]

        start_time = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)
        duration = time.time() - start_time

        # 解析测试结果
        output_lines = result.stdout.split('\n')
        passed = failed = skipped = errors = 0

        for line in output_lines:
            if " passed in " in line:
                parts = line.split()
                passed = int(parts[0])
            if " failed in " in line:
                parts = line.split()
                failed = int(parts[0])
            if " skipped in " in line:
                parts = line.split()
                skipped = int(parts[0])
            if " error in " in line:
                parts = line.split()
                errors = int(parts[0])

        # 读取覆盖率报告
        coverage = None
        coverage_file = Path("coverage.json")
        if coverage_file.exists():
            with open(coverage_file) as f:
                coverage_data = json.load(f)
                coverage = coverage_data.get("totals", {}).get("percent_covered", 0)

        test_result = TestResult(
            name="Unit Tests",
            type="unit",
            status="passed" if result.returncode == 0 else "failed",
            duration=duration,
            passed=passed,
            failed=failed,
            skipped=skipped,
            errors=errors,
            coverage=coverage
        )

        self.results.append(test_result)
        return test_result

    def run_integration_tests(self) -> TestResult:
        """运行集成测试"""
        print("\n" + "="*50)
        print("Running Integration Tests")
        print("="*50)

        integration_test_dir = self.test_suite_dir / "integration"
        cmd = [
            sys.executable, "-m", "pytest",
            str(integration_test_dir),
            "-v",
            "--tb=short",
            "-m", "integration"
        ]

        start_time = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)
        duration = time.time() - start_time

        # 解析测试结果
        output_lines = result.stdout.split('\n')
        passed = failed = skipped = errors = 0

        for line in output_lines:
            if " passed in " in line:
                parts = line.split()
                passed = int(parts[0])
            if " failed in " in line:
                parts = line.split()
                failed = int(parts[0])
            if " skipped in " in line:
                parts = line.split()
                skipped = int(parts[0])
            if " error in " in line:
                parts = line.split()
                errors = int(parts[0])

        test_result = TestResult(
            name="Integration Tests",
            type="integration",
            status="passed" if result.returncode == 0 else "failed",
            duration=duration,
            passed=passed,
            failed=failed,
            skipped=skipped,
            errors=errors
        )

        self.results.append(test_result)
        return test_result

    def run_performance_tests(self) -> TestResult:
        """运行性能测试"""
        print("\n" + "="*50)
        print("Running Performance Tests")
        print("="*50)

        performance_test_dir = self.test_suite_dir / "performance"
        cmd = [
            sys.executable, "-m", "pytest",
            str(performance_test_dir),
            "-v",
            "--tb=short",
            "-m", "performance",
            "--benchmark-json=benchmark_results.json"
        ]

        start_time = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)
        duration = time.time() - start_time

        # 解析测试结果
        output_lines = result.stdout.split('\n')
        passed = failed = skipped = errors = 0

        for line in output_lines:
            if " passed in " in line:
                parts = line.split()
                passed = int(parts[0])
            if " failed in " in line:
                parts = line.split()
                failed = int(parts[0])
            if " skipped in " in line:
                parts = line.split()
                skipped = int(parts[0])
            if " error in " in line:
                parts = line.split()
                errors = int(parts[0])

        # 读取性能基准结果
        performance_data = {}
        benchmark_file = Path("benchmark_results.json")
        if benchmark_file.exists():
            with open(benchmark_file) as f:
                performance_data = json.load(f)

        test_result = TestResult(
            name="Performance Tests",
            type="performance",
            status="passed" if result.returncode == 0 else "failed",
            duration=duration,
            passed=passed,
            failed=failed,
            skipped=skipped,
            errors=errors,
            details={"benchmarks": performance_data}
        )

        self.results.append(test_result)
        return test_result

    def run_security_tests(self) -> TestResult:
        """运行安全测试"""
        print("\n" + "="*50)
        print("Running Security Tests")
        print("="*50)

        security_test_dir = self.test_suite_dir / "security"
        cmd = [
            sys.executable, "-m", "pytest",
            str(security_test_dir),
            "-v",
            "--tb=short",
            "-m", "security"
        ]

        start_time = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)
        duration = time.time() - start_time

        # 解析测试结果
        output_lines = result.stdout.split('\n')
        passed = failed = skipped = errors = 0

        for line in output_lines:
            if " passed in " in line:
                parts = line.split()
                passed = int(parts[0])
            if " failed in " in line:
                parts = line.split()
                failed = int(parts[0])
            if " skipped in " in line:
                parts = line.split()
                skipped = int(parts[0])
            if " error in " in line:
                parts = line.split()
                errors = int(parts[0])

        test_result = TestResult(
            name="Security Tests",
            type="security",
            status="passed" if result.returncode == 0 else "failed",
            duration=duration,
            passed=passed,
            failed=failed,
            skipped=skipped,
            errors=errors
        )

        self.results.append(test_result)
        return test_result

    def run_e2e_tests(self) -> TestResult:
        """运行端到端测试"""
        print("\n" + "="*50)
        print("Running End-to-End Tests")
        print("="*50)

        e2e_test_dir = self.test_suite_dir / "e2e"
        cmd = [
            sys.executable, "-m", "pytest",
            str(e2e_test_dir),
            "-v",
            "--tb=short",
            "-m", "e2e",
            "--html=e2e_report.html",
            "--self-contained-html"
        ]

        start_time = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)
        duration = time.time() - start_time

        # 解析测试结果
        output_lines = result.stdout.split('\n')
        passed = failed = skipped = errors = 0

        for line in output_lines:
            if " passed in " in line:
                parts = line.split()
                passed = int(parts[0])
            if " failed in " in line:
                parts = line.split()
                failed = int(parts[0])
            if " skipped in " in line:
                parts = line.split()
                skipped = int(parts[0])
            if " error in " in line:
                parts = line.split()
                errors = int(parts[0])

        test_result = TestResult(
            name="End-to-End Tests",
            type="e2e",
            status="passed" if result.returncode == 0 else "failed",
            duration=duration,
            passed=passed,
            failed=failed,
            skipped=skipped,
            errors=errors
        )

        self.results.append(test_result)
        return test_result

    def generate_report(self) -> TestReport:
        """生成测试报告"""
        total_passed = sum(r.passed for r in self.results)
        total_failed = sum(r.failed for r in self.results)
        total_skipped = sum(r.skipped for r in self.results)
        total_errors = sum(r.errors for r in self.results)

        overall_status = "passed"
        if total_failed > 0 or total_errors > 0:
            overall_status = "failed"
        elif total_skipped > 0:
            overall_status = "partial"

        # 覆盖率摘要
        coverage_summary = {}
        for result in self.results:
            if result.coverage is not None:
                coverage_summary[result.type] = result.coverage

        # 性能摘要
        performance_summary = {}
        perf_result = next((r for r in self.results if r.type == "performance"), None)
        if perf_result and perf_result.details and "benchmarks" in perf_result.details:
            benchmarks = perf_result.details["benchmarks"]
            if "benchmarks" in benchmarks:
                for benchmark in benchmarks["benchmarks"]:
                    performance_summary[benchmark["name"]] = benchmark["stats"]["mean"]

        # 安全摘要
        security_summary = {}
        sec_result = next((r for r in self.results if r.type == "security"), None)
        if sec_result:
            security_summary = {
                "status": sec_result.status,
                "vulnerabilities_found": sec_result.failed
            }

        report = TestReport(
            timestamp=datetime.now().isoformat(),
            total_duration=self.end_time - self.start_time if self.end_time and self.start_time else 0,
            total_passed=total_passed,
            total_failed=total_failed,
            total_skipped=total_skipped,
            total_errors=total_errors,
            overall_status=overall_status,
            test_results=self.results,
            coverage_summary=coverage_summary,
            performance_summary=performance_summary,
            security_summary=security_summary
        )

        return report

    def save_report(self, report: TestReport, output_dir: Path):
        """保存测试报告"""
        output_dir.mkdir(parents=True, exist_ok=True)

        # 保存JSON报告
        json_file = output_dir / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(json_file, 'w') as f:
            json.dump(asdict(report), f, indent=2, ensure_ascii=False)

        # 保存HTML报告
        html_file = output_dir / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        self._generate_html_report(report, html_file)

        # 保存简化的摘要
        summary_file = output_dir / "latest_test_summary.json"
        with open(summary_file, 'w') as f:
            summary = {
                "timestamp": report.timestamp,
                "status": report.overall_status,
                "total_tests": report.total_passed + report.total_failed + report.total_skipped + report.total_errors,
                "passed": report.total_passed,
                "failed": report.total_failed,
                "skipped": report.total_skipped,
                "errors": report.total_errors,
                "coverage": report.coverage_summary.get("unit", 0),
                "duration": report.total_duration
            }
            json.dump(summary, f, indent=2)

        print(f"\nTest reports saved to:")
        print(f"- JSON: {json_file}")
        print(f"- HTML: {html_file}")
        print(f"- Summary: {summary_file}")

    def _generate_html_report(self, report: TestReport, output_file: Path):
        """生成HTML报告"""
        html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Test Report - {timestamp}</title>
    <meta charset="utf-8">
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            border-bottom: 2px solid #4CAF50;
            padding-bottom: 10px;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .summary-card {{
            background-color: #f9f9f9;
            padding: 15px;
            border-radius: 5px;
            text-align: center;
        }}
        .status-passed {{ background-color: #d4edda; color: #155724; }}
        .status-failed {{ background-color: #f8d7da; color: #721c24; }}
        .status-partial {{ background-color: #fff3cd; color: #856404; }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #4CAF50;
            color: white;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .progress-bar {{
            width: 100%;
            height: 20px;
            background-color: #e0e0e0;
            border-radius: 10px;
            overflow: hidden;
        }}
        .progress-fill {{
            height: 100%;
            transition: width 0.3s ease;
        }}
        .progress-passed {{ background-color: #4CAF50; }}
        .progress-failed {{ background-color: #f44336; }}
        .progress-skipped {{ background-color: #ff9800; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Test Report</h1>
        <p><strong>Timestamp:</strong> {timestamp}</p>
        <p><strong>Total Duration:</strong> {total_duration:.2f} seconds</p>

        <div class="summary">
            <div class="summary-card status-{status_lower}">
                <h3>Overall Status</h3>
                <p style="font-size: 24px; font-weight: bold;">{overall_status}</p>
            </div>
            <div class="summary-card">
                <h3>Total Tests</h3>
                <p style="font-size: 24px; font-weight: bold;">{total_tests}</p>
            </div>
            <div class="summary-card">
                <h3>Passed</h3>
                <p style="font-size: 24px; font-weight: bold; color: #4CAF50;">{total_passed}</p>
            </div>
            <div class="summary-card">
                <h3>Failed</h3>
                <p style="font-size: 24px; font-weight: bold; color: #f44336;">{total_failed}</p>
            </div>
        </div>

        <h2>Test Results by Type</h2>
        <table>
            <thead>
                <tr>
                    <th>Test Type</th>
                    <th>Status</th>
                    <th>Duration</th>
                    <th>Passed</th>
                    <th>Failed</th>
                    <th>Skipped</th>
                    <th>Coverage</th>
                    <th>Progress</th>
                </tr>
            </thead>
            <tbody>
                {test_rows}
            </tbody>
        </table>

        {coverage_section}
        {performance_section}
        {security_section}
    </div>
</body>
</html>
        """

        # 生成测试结果行
        test_rows = ""
        for result in report.test_results:
            total = result.passed + result.failed + result.skipped + result.errors
            passed_percent = (result.passed / total * 100) if total > 0 else 0

            test_rows += f"""
            <tr>
                <td>{result.name}</td>
                <td><span class="status-{result.status}">{result.status}</span></td>
                <td>{result.duration:.2f}s</td>
                <td>{result.passed}</td>
                <td>{result.failed}</td>
                <td>{result.skipped}</td>
                <td>{result.coverage or 'N/A'}%</td>
                <td>
                    <div class="progress-bar">
                        <div class="progress-fill progress-passed" style="width: {passed_percent}%"></div>
                    </div>
                </td>
            </tr>
            """

        # 覆盖率部分
        coverage_section = ""
        if report.coverage_summary:
            coverage_rows = ""
            for test_type, coverage in report.coverage_summary.items():
                coverage_rows += f"""
                <tr>
                    <td>{test_type.title()}</td>
                    <td>{coverage:.2f}%</td>
                    <td>
                        <div class="progress-bar">
                            <div class="progress-fill progress-passed" style="width: {coverage}%"></div>
                        </div>
                    </td>
                </tr>
                """

            coverage_section = f"""
            <h2>Coverage Summary</h2>
            <table>
                <thead>
                    <tr>
                        <th>Test Type</th>
                        <th>Coverage</th>
                        <th>Visual</th>
                    </tr>
                </thead>
                <tbody>
                    {coverage_rows}
                </tbody>
            </table>
            """

        # 性能部分
        performance_section = ""
        if report.performance_summary:
            perf_rows = ""
            for benchmark, value in report.performance_summary.items():
                perf_rows += f"""
                <tr>
                    <td>{benchmark}</td>
                    <td>{value:.4f}s</td>
                </tr>
                """

            performance_section = f"""
            <h2>Performance Summary</h2>
            <table>
                <thead>
                    <tr>
                        <th>Benchmark</th>
                        <th>Average Time</th>
                    </tr>
                </thead>
                <tbody>
                    {perf_rows}
                </tbody>
            </table>
            """

        # 安全部分
        security_section = ""
        if report.security_summary:
            security_section = f"""
            <h2>Security Summary</h2>
            <table>
                <thead>
                    <tr>
                        <th>Status</th>
                        <th>Vulnerabilities Found</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>{report.security_summary['status']}</td>
                        <td>{report.security_summary['vulnerabilities_found']}</td>
                    </tr>
                </tbody>
            </table>
            """

        # 替换模板变量
        html_content = html_template.format(
            timestamp=report.timestamp,
            total_duration=report.total_duration,
            status_lower=report.overall_status,
            overall_status=report.overall_status.upper(),
            total_tests=report.total_passed + report.total_failed + report.total_skipped + report.total_errors,
            total_passed=report.total_passed,
            total_failed=report.total_failed,
            test_rows=test_rows,
            coverage_section=coverage_section,
            performance_section=performance_section,
            security_section=security_section
        )

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

    async def notify_results(self, report: TestReport, config: Dict[str, Any]):
        """发送测试结果通知"""
        if not config.get("notifications", {}).get("enabled", False):
            return

        # Slack通知
        slack_config = config.get("notifications", {}).get("slack", {})
        if slack_config.get("webhook_url"):
            await self._send_slack_notification(report, slack_config)

        # 邮件通知
        email_config = config.get("notifications", {}).get("email", {})
        if email_config.get("smtp_server"):
            self._send_email_notification(report, email_config)

    async def _send_slack_notification(self, report: TestReport, config: Dict[str, Any]):
        """发送Slack通知"""
        webhook_url = config["webhook_url"]
        channel = config.get("channel", "#test-results")

        color = "good" if report.overall_status == "passed" else "danger"

        payload = {
            "channel": channel,
            "attachments": [{
                "color": color,
                "title": f"Test Results - {report.overall_status.upper()}",
                "fields": [
                    {"title": "Total Tests", "value": report.total_passed + report.total_failed + report.total_skipped + report.total_errors},
                    {"title": "Passed", "value": report.total_passed, "short": True},
                    {"title": "Failed", "value": report.total_failed, "short": True},
                    {"title": "Coverage", "value": f"{report.coverage_summary.get('unit', 0):.1f}%", "short": True}
                ],
                "footer": "ZhipuAI Test Runner",
                "ts": datetime.now().timestamp()
            }]
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(webhook_url, json=payload) as response:
                if response.status != 200:
                    print(f"Failed to send Slack notification: {response.status}")

    def _send_email_notification(self, report: TestReport, config: Dict[str, Any]):
        """发送邮件通知"""
        smtp_server = config["smtp_server"]
        smtp_port = config.get("smtp_port", 587)
        username = config["username"]
        password = config["password"]
        recipients = config["recipients"]

        # 创建邮件内容
        msg = MimeMultipart()
        msg['From'] = username
        msg['To'] = ", ".join(recipients)
        msg['Subject'] = f"Test Results - {report.overall_status.upper()}"

        body = f"""
Test execution completed at {report.timestamp}

Overall Status: {report.overall_status.upper()}

Summary:
- Total Tests: {report.total_passed + report.total_failed + report.total_skipped + report.total_errors}
- Passed: {report.total_passed}
- Failed: {report.total_failed}
- Skipped: {report.total_skipped}
- Errors: {report.total_errors}
- Duration: {report.total_duration:.2f} seconds
- Coverage: {report.coverage_summary.get('unit', 0):.1f}%

For detailed results, check the test reports.
        """

        msg.attach(MimeText(body, 'plain'))

        # 发送邮件
        try:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(username, password)
            server.send_message(msg)
            server.quit()
            print("Email notification sent successfully")
        except Exception as e:
            print(f"Failed to send email notification: {e}")

    def run_all_tests(self, test_types: List[str] = None) -> TestReport:
        """运行所有测试"""
        if test_types is None:
            test_types = ["unit", "integration", "performance", "security", "e2e"]

        self.start_time = time.time()

        # 按顺序运行测试
        if "unit" in test_types:
            self.run_unit_tests()

        if "integration" in test_types:
            self.run_integration_tests()

        if "performance" in test_types:
            self.run_performance_tests()

        if "security" in test_types:
            self.run_security_tests()

        if "e2e" in test_types:
            self.run_e2e_tests()

        self.end_time = time.time()

        # 生成报告
        report = self.generate_report()
        return report


def load_config(config_file: Path) -> Dict[str, Any]:
    """加载配置文件"""
    if config_file.exists():
        with open(config_file) as f:
            return json.load(f)
    return {}


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="ZhipuAI Test Runner")
    parser.add_argument("--config", type=Path, default=Path("test_config.json"),
                       help="Test configuration file")
    parser.add_argument("--output", type=Path, default=Path("test_reports"),
                       help="Output directory for test reports")
    parser.add_argument("--types", nargs="+",
                       choices=["unit", "integration", "performance", "security", "e2e"],
                       help="Test types to run")
    parser.add_argument("--notify", action="store_true",
                       help="Send notifications after test completion")

    args = parser.parse_args()

    # 获取项目根目录
    project_root = Path(__file__).parent.parent.parent

    # 加载配置
    config = load_config(args.config)

    # 创建测试运行器
    runner = TestRunner(project_root)

    # 运行测试
    print(f"Starting test execution at {datetime.now()}")
    report = runner.run_all_tests(args.types)

    # 保存报告
    runner.save_report(report, args.output)

    # 发送通知
    if args.notify:
        asyncio.run(runner.notify_results(report, config))

    # 返回适当的退出码
    sys.exit(0 if report.overall_status == "passed" else 1)


if __name__ == "__main__":
    main()