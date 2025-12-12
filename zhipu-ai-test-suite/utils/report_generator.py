"""
测试报告和质量指标生成器
"""

import os
import json
import time
import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from collections import defaultdict
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from jinja2 import Template, Environment, FileSystemLoader
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots


@dataclass
class QualityMetrics:
    """质量指标数据类"""
    test_coverage: float
    code_quality_score: float
    security_score: float
    performance_score: float
    reliability_score: float
    maintainability_index: float
    technical_debt_ratio: float
    bug_density: float
    test_pass_rate: float
    build_success_rate: float


@dataclass
class TrendData:
    """趋势数据"""
    date: str
    value: float
    metric_name: str


class QualityMetricsCalculator:
    """质量指标计算器"""

    def __init__(self):
        self.metrics_history: Dict[str, List[TrendData]] = defaultdict(list)

    def calculate_code_quality_score(self, test_results: Dict[str, Any]) -> float:
        """计算代码质量分数 (0-100)"""
        scores = []

        # 测试覆盖率 (30%)
        coverage = test_results.get("coverage", {}).get("unit", 0)
        coverage_score = min(coverage, 100)
        scores.append(("coverage", coverage_score, 0.3))

        # 代码风格合规性 (20%)
        lint_issues = test_results.get("lint_issues", 0)
        lint_score = max(0, 100 - lint_issues * 2)
        scores.append(("lint", lint_score, 0.2))

        # 类型检查合规性 (15%)
        type_issues = test_results.get("type_issues", 0)
        type_score = max(0, 100 - type_issues * 5)
        scores.append(("type", type_score, 0.15))

        # 复杂度 (15%)
        complexity_score = self._calculate_complexity_score(test_results)
        scores.append(("complexity", complexity_score, 0.15))

        # 重复率 (20%)
        duplication_score = self._calculate_duplication_score(test_results)
        scores.append(("duplication", duplication_score, 0.2))

        # 加权平均
        weighted_score = sum(score * weight for _, score, weight in scores)
        return round(weighted_score, 2)

    def calculate_security_score(self, security_results: Dict[str, Any]) -> float:
        """计算安全分数 (0-100)"""
        scores = []

        # 漏洞严重性评分
        vulnerabilities = security_results.get("vulnerabilities", {})
        critical_count = vulnerabilities.get("critical", 0)
        high_count = vulnerabilities.get("high", 0)
        medium_count = vulnerabilities.get("medium", 0)
        low_count = vulnerabilities.get("low", 0)

        # 基础分数100，根据漏洞扣分
        vulnerability_score = 100
        vulnerability_score -= critical_count * 25
        vulnerability_score -= high_count * 15
        vulnerability_score -= medium_count * 5
        vulnerability_score -= low_count * 1
        scores.append(("vulnerabilities", max(0, vulnerability_score), 0.4))

        # 依赖安全扫描 (30%)
        dependency_issues = security_results.get("dependency_issues", 0)
        dependency_score = max(0, 100 - dependency_issues * 10)
        scores.append(("dependencies", dependency_score, 0.3))

        # 安全测试通过率 (30%)
        security_tests_passed = security_results.get("tests_passed", 0)
        security_tests_total = security_results.get("tests_total", 1)
        test_score = (security_tests_passed / security_tests_total) * 100
        scores.append(("security_tests", test_score, 0.3))

        weighted_score = sum(score * weight for _, score, weight in scores)
        return round(weighted_score, 2)

    def calculate_performance_score(self, performance_results: Dict[str, Any]) -> float:
        """计算性能分数 (0-100)"""
        scores = []

        # 响应时间分数 (40%)
        avg_response_time = performance_results.get("avg_response_time", 1.0)
        # 期望响应时间小于200ms
        response_time_score = max(0, 100 - (avg_response_time - 0.2) * 100)
        scores.append(("response_time", response_time_score, 0.4))

        # 吞吐量分数 (30%)
        throughput = performance_results.get("throughput", 100)
        # 期望吞吐量大于1000 req/s
        throughput_score = min(100, throughput / 10)
        scores.append(("throughput", throughput_score, 0.3))

        # 资源利用率分数 (20%)
        cpu_usage = performance_results.get("cpu_usage", 50)
        memory_usage = performance_results.get("memory_usage", 50)
        resource_score = 100 - abs(cpu_usage - 50) - abs(memory_usage - 50)
        scores.append(("resources", max(0, resource_score), 0.2))

        # 错误率分数 (10%)
        error_rate = performance_results.get("error_rate", 0)
        error_score = max(0, 100 - error_rate * 1000)
        scores.append(("errors", error_score, 0.1))

        weighted_score = sum(score * weight for _, score, weight in scores)
        return round(weighted_score, 2)

    def calculate_reliability_score(self, test_results: Dict[str, Any]) -> float:
        """计算可靠性分数 (0-100)"""
        scores = []

        # 测试通过率 (40%)
        total_tests = test_results.get("total_tests", 1)
        passed_tests = test_results.get("passed_tests", 0)
        pass_rate = (passed_tests / total_tests) * 100
        scores.append(("pass_rate", pass_rate, 0.4))

        # 平均故障间隔时间 (MTBF) (30%)
        mtbf = test_results.get("mtbf_hours", 24)
        mtbf_score = min(100, mtbf)
        scores.append(("mtbf", mtbf_score, 0.3))

        # 平均修复时间 (MTTR) (30%)
        mttr = test_results.get("mttr_hours", 1)
        mttr_score = max(0, 100 - mttr * 10)
        scores.append(("mttr", mttr_score, 0.3))

        weighted_score = sum(score * weight for _, score, weight in scores)
        return round(weighted_score, 2)

    def calculate_maintainability_index(self, code_metrics: Dict[str, Any]) -> float:
        """计算可维护性指数 (0-100)"""
        # 使用微软的可维护性指数公式
        # MI = MAX(0, (171 - 5.2 * ln(Halstead Volume) - 0.23 * (Cyclomatic Complexity) - 16.2 * ln(Lines of Code)) * 100 / 171)

        loc = code_metrics.get("lines_of_code", 1000)
        complexity = code_metrics.get("cyclomatic_complexity", 10)
        volume = code_metrics.get("halstead_volume", 1000)

        import math
        if loc > 0 and volume > 0:
            mi = max(0, (171 - 5.2 * math.log(volume) - 0.23 * complexity - 16.2 * math.log(loc)))
            mi_score = (mi / 171) * 100
        else:
            mi_score = 0

        return round(mi_score, 2)

    def calculate_technical_debt_ratio(self, code_metrics: Dict[str, Any]) -> float:
        """计算技术债务比率 (%)"""
        # 技术债务比率 = (代码债务时间 / 开发新功能时间) * 100
        debt_hours = code_metrics.get("technical_debt_hours", 8)
        development_hours = code_metrics.get("development_hours", 40)

        if development_hours > 0:
            debt_ratio = (debt_hours / development_hours) * 100
        else:
            debt_ratio = 0

        return round(debt_ratio, 2)

    def calculate_bug_density(self, test_results: Dict[str, Any], code_metrics: Dict[str, Any]) -> float:
        """计算缺陷密度 (defects per KLOC)"""
        total_bugs = test_results.get("total_bugs", 0)
        kloc = code_metrics.get("lines_of_code", 1000) / 1000

        if kloc > 0:
            bug_density = total_bugs / kloc
        else:
            bug_density = 0

        return round(bug_density, 2)

    def _calculate_complexity_score(self, test_results: Dict[str, Any]) -> float:
        """计算复杂度分数"""
        complexity_metrics = test_results.get("complexity", {})
        avg_complexity = complexity_metrics.get("average", 10)
        max_complexity = complexity_metrics.get("maximum", 20)

        # 期望平均复杂度小于5，最大复杂度小于15
        avg_score = max(0, 100 - (avg_complexity - 5) * 10)
        max_score = max(0, 100 - (max_complexity - 15) * 5)

        return (avg_score + max_score) / 2

    def _calculate_duplication_score(self, test_results: Dict[str, Any]) -> float:
        """计算代码重复分数"""
        duplication_ratio = test_results.get("duplication_ratio", 0.05)
        # 期望重复率小于5%
        return max(0, 100 - duplication_ratio * 1000)

    def update_metrics_history(self, date: str, metrics: QualityMetrics):
        """更新指标历史记录"""
        metrics_dict = asdict(metrics)
        for metric_name, value in metrics_dict.items():
            if isinstance(value, (int, float)):
                self.metrics_history[metric_name].append(
                    TrendData(date, value, metric_name)
                )

    def get_trend_analysis(self, metric_name: str, days: int = 30) -> Dict[str, Any]:
        """获取趋势分析"""
        if metric_name not in self.metrics_history:
            return {"trend": "no_data"}

        recent_data = self.metrics_history[metric_name][-days:]
        if len(recent_data) < 2:
            return {"trend": "insufficient_data"}

        values = [d.value for d in recent_data]
        # 计算趋势
        x = np.arange(len(values))
        slope, _ = np.polyfit(x, values, 1)

        # 确定趋势方向
        if abs(slope) < 0.01:
            trend = "stable"
        elif slope > 0:
            trend = "improving"
        else:
            trend = "degrading"

        # 计算变化率
        if len(values) >= 2:
            change_rate = ((values[-1] - values[0]) / values[0]) * 100
        else:
            change_rate = 0

        return {
            "trend": trend,
            "slope": slope,
            "change_rate": change_rate,
            "current_value": values[-1],
            "previous_value": values[-2] if len(values) > 1 else values[-1]
        }


class Visualizer:
    """可视化工具"""

    @staticmethod
    def create_quality_gauge(score: float, title: str) -> go.Figure:
        """创建质量仪表盘图"""
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': title},
            delta = {'reference': 80},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 80], 'color': "gray"},
                    {'range': [80, 100], 'color': "green"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        return fig

    @staticmethod
    def create_trend_chart(trend_data: List[TrendData], title: str) -> go.Figure:
        """创建趋势图"""
        dates = [d.date for d in trend_data]
        values = [d.value for d in trend_data]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates,
            y=values,
            mode='lines+markers',
            name=title,
            line=dict(color='blue', width=2),
            marker=dict(size=6)
        ))

        fig.update_layout(
            title=title,
            xaxis_title="Date",
            yaxis_title="Value",
            hovermode='x unified',
            showlegend=False
        )
        return fig

    @staticmethod
    def create_test_results_pie_chart(test_results: Dict[str, int]) -> go.Figure:
        """创建测试结果饼图"""
        labels = ['Passed', 'Failed', 'Skipped', 'Errors']
        values = [
            test_results.get('passed', 0),
            test_results.get('failed', 0),
            test_results.get('skipped', 0),
            test_results.get('errors', 0)
        ]
        colors = ['#2E8B57', '#DC143C', '#FFD700', '#FF6347']

        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.3,
            marker_colors=colors
        )])
        fig.update_layout(title="Test Results Distribution")
        return fig

    @staticmethod
    def create_coverage_bar_chart(coverage_data: Dict[str, float]) -> go.Figure:
        """创建覆盖率条形图"""
        modules = list(coverage_data.keys())
        coverage = list(coverage_data.values())

        colors = ['green' if c >= 80 else 'yellow' if c >= 60 else 'red' for c in coverage]

        fig = go.Figure(data=[
            go.Bar(
                x=modules,
                y=coverage,
                marker_color=colors,
                text=[f"{c:.1f}%" for c in coverage],
                textposition='auto'
            )
        ])
        fig.update_layout(
            title="Test Coverage by Module",
            xaxis_title="Modules",
            yaxis_title="Coverage (%)",
            yaxis=dict(range=[0, 100])
        )
        return fig

    @staticmethod
    def create_performance_comparison_chart(performance_data: Dict[str, Dict[str, float]]) -> go.Figure:
        """创建性能对比图"""
        metrics = list(performance_data.keys())
        current_values = [performance_data[m].get('current', 0) for m in metrics]
        baseline_values = [performance_data[m].get('baseline', 0) for m in metrics]

        fig = go.Figure()
        fig.add_trace(go.Bar(
            name='Current',
            x=metrics,
            y=current_values,
            marker_color='blue'
        ))
        fig.add_trace(go.Bar(
            name='Baseline',
            x=metrics,
            y=baseline_values,
            marker_color='gray'
        ))

        fig.update_layout(
            title="Performance Metrics Comparison",
            xaxis_title="Metrics",
            yaxis_title="Value",
            barmode='group'
        )
        return fig

    @staticmethod
    def create_security_heatmap(security_data: Dict[str, Dict[str, int]]) -> go.Figure:
        """创建安全热力图"""
        categories = list(security_data.keys())
        severities = ['critical', 'high', 'medium', 'low']

        z = []
        for category in categories:
            row = []
            for severity in severities:
                row.append(security_data[category].get(severity, 0))
            z.append(row)

        fig = go.Figure(data=go.Heatmap(
            z=z,
            x=severities,
            y=categories,
            colorscale='Reds',
            showscale=True
        ))
        fig.update_layout(title="Security Vulnerabilities Heatmap")
        return fig


class ReportGenerator:
    """报告生成器"""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.calculator = QualityMetricsCalculator()
        self.visualizer = Visualizer()

    def generate_comprehensive_report(
        self,
        test_results: Dict[str, Any],
        code_metrics: Dict[str, Any],
        build_info: Dict[str, Any]
    ) -> str:
        """生成综合报告"""
        # 计算质量指标
        metrics = self._calculate_all_metrics(test_results, code_metrics)

        # 更新历史记录
        today = datetime.date.today().isoformat()
        self.calculator.update_metrics_history(today, metrics)

        # 生成可视化
        self._generate_visualizations(metrics, test_results)

        # 生成HTML报告
        report_path = self._generate_html_report(metrics, test_results, code_metrics, build_info)

        # 生成JSON报告
        self._generate_json_report(metrics, test_results, code_metrics, build_info)

        # 生成PDF报告
        self._generate_pdf_report(report_path)

        return report_path

    def _calculate_all_metrics(
        self,
        test_results: Dict[str, Any],
        code_metrics: Dict[str, Any]
    ) -> QualityMetrics:
        """计算所有质量指标"""
        return QualityMetrics(
            test_coverage=test_results.get("coverage", {}).get("unit", 0),
            code_quality_score=self.calculator.calculate_code_quality_score(test_results),
            security_score=self.calculator.calculate_security_score(
                test_results.get("security", {})
            ),
            performance_score=self.calculator.calculate_performance_score(
                test_results.get("performance", {})
            ),
            reliability_score=self.calculator.calculate_reliability_score(test_results),
            maintainability_index=self.calculator.calculate_maintainability_index(code_metrics),
            technical_debt_ratio=self.calculator.calculate_technical_debt_ratio(code_metrics),
            bug_density=self.calculator.calculate_bug_density(test_results, code_metrics),
            test_pass_rate=self._calculate_pass_rate(test_results),
            build_success_rate=self._calculate_build_success_rate(test_results)
        )

    def _generate_visualizations(self, metrics: QualityMetrics, test_results: Dict[str, Any]):
        """生成可视化图表"""
        visualizations_dir = self.output_dir / "visualizations"
        visualizations_dir.mkdir(exist_ok=True)

        # 质量仪表盘
        quality_gauge = self.visualizer.create_quality_gauge(
            metrics.code_quality_score,
            "Code Quality Score"
        )
        quality_gauge.write_html(str(visualizations_dir / "quality_gauge.html"))

        # 测试结果饼图
        test_summary = {
            'passed': test_results.get('passed_tests', 0),
            'failed': test_results.get('failed_tests', 0),
            'skipped': test_results.get('skipped_tests', 0),
            'errors': test_results.get('error_tests', 0)
        }
        pie_chart = self.visualizer.create_test_results_pie_chart(test_summary)
        pie_chart.write_html(str(visualizations_dir / "test_results_pie.html"))

        # 覆盖率条形图
        coverage_data = test_results.get("coverage", {})
        if coverage_data:
            coverage_chart = self.visualizer.create_coverage_bar_chart(coverage_data)
            coverage_chart.write_html(str(visualizations_dir / "coverage_bar.html"))

        # 生成趋势图（如果有历史数据）
        for metric_name in ["test_coverage", "code_quality_score", "security_score"]:
            if metric_name in self.calculator.metrics_history:
                trend_data = self.calculator.metrics_history[metric_name]
                trend_chart = self.visualizer.create_trend_chart(
                    trend_data,
                    metric_name.replace("_", " ").title()
                )
                trend_chart.write_html(str(visualizations_dir / f"{metric_name}_trend.html"))

    def _generate_html_report(
        self,
        metrics: QualityMetrics,
        test_results: Dict[str, Any],
        code_metrics: Dict[str, Any],
        build_info: Dict[str, Any]
    ) -> str:
        """生成HTML报告"""
        # 设置Jinja2环境
        env = Environment(
            loader=FileSystemLoader(Path(__file__).parent / "templates")
        )
        template = env.get_template("report_template.html")

        # 准备模板数据
        template_data = {
            "report_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "build_info": build_info,
            "metrics": asdict(metrics),
            "test_results": test_results,
            "code_metrics": code_metrics,
            "trend_analysis": self._get_trend_summary(),
            "recommendations": self._generate_recommendations(metrics, test_results)
        }

        # 渲染报告
        html_content = template.render(**template_data)

        # 保存报告
        report_path = self.output_dir / f"report_{datetime.date.today()}.html"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return str(report_path)

    def _generate_json_report(
        self,
        metrics: QualityMetrics,
        test_results: Dict[str, Any],
        code_metrics: Dict[str, Any],
        build_info: Dict[str, Any]
    ):
        """生成JSON报告"""
        report_data = {
            "metadata": {
                "report_date": datetime.datetime.now().isoformat(),
                "report_version": "1.0",
                "generator": "ZhipuAI Test Suite"
            },
            "build_info": build_info,
            "quality_metrics": asdict(metrics),
            "test_results": test_results,
            "code_metrics": code_metrics,
            "trend_analysis": {
                metric: self.calculator.get_trend_analysis(metric)
                for metric in asdict(metrics).keys()
                if metric in self.calculator.metrics_history
            }
        }

        report_path = self.output_dir / f"report_{datetime.date.today()}.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)

    def _generate_pdf_report(self, html_report_path: str):
        """生成PDF报告"""
        try:
            import pdfkit
            pdf_path = html_report_path.replace('.html', '.pdf')
            pdfkit.from_file(html_report_path, pdf_path)
        except ImportError:
            print("pdfkit not installed, skipping PDF generation")

    def _get_trend_summary(self) -> Dict[str, Any]:
        """获取趋势摘要"""
        trends = {}
        for metric_name in ["test_coverage", "code_quality_score", "security_score"]:
            if metric_name in self.calculator.metrics_history:
                trends[metric_name] = self.calculator.get_trend_analysis(metric_name)
        return trends

    def _generate_recommendations(
        self,
        metrics: QualityMetrics,
        test_results: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """生成改进建议"""
        recommendations = []

        # 测试覆盖率建议
        if metrics.test_coverage < 80:
            recommendations.append({
                "category": "Test Coverage",
                "priority": "high" if metrics.test_coverage < 60 else "medium",
                "description": f"Test coverage is {metrics.test_coverage:.1f}%, consider adding more unit tests",
                "action_items": [
                    "Add unit tests for uncovered code paths",
                    "Consider using test-driven development (TDD)",
                    "Set up coverage gates in CI/CD pipeline"
                ]
            })

        # 代码质量建议
        if metrics.code_quality_score < 80:
            recommendations.append({
                "category": "Code Quality",
                "priority": "high" if metrics.code_quality_score < 60 else "medium",
                "description": f"Code quality score is {metrics.code_quality_score:.1f}, improvements needed",
                "action_items": [
                    "Address linting warnings",
                    "Reduce code complexity",
                    "Remove code duplication"
                ]
            })

        # 安全建议
        if metrics.security_score < 90:
            recommendations.append({
                "category": "Security",
                "priority": "high" if metrics.security_score < 70 else "medium",
                "description": f"Security score is {metrics.security_score:.1f}, address security issues",
                "action_items": [
                    "Fix high-priority security vulnerabilities",
                    "Update dependencies with known vulnerabilities",
                    "Implement security headers and best practices"
                ]
            })

        # 性能建议
        if metrics.performance_score < 80:
            recommendations.append({
                "category": "Performance",
                "priority": "medium",
                "description": f"Performance score is {metrics.performance_score:.1f}, optimization needed",
                "action_items": [
                    "Profile slow endpoints",
                    "Optimize database queries",
                    "Implement caching strategies"
                ]
            })

        # 技术债务建议
        if metrics.technical_debt_ratio > 20:
            recommendations.append({
                "category": "Technical Debt",
                "priority": "high" if metrics.technical_debt_ratio > 40 else "medium",
                "description": f"Technical debt ratio is {metrics.technical_debt_ratio:.1f}%, allocate time for refactoring",
                "action_items": [
                    "Schedule regular refactoring sprints",
                    "Create a technical debt backlog",
                    "Automate code quality checks"
                ]
            })

        return recommendations

    def _calculate_pass_rate(self, test_results: Dict[str, Any]) -> float:
        """计算测试通过率"""
        total = test_results.get('total_tests', 1)
        passed = test_results.get('passed_tests', 0)
        return round((passed / total) * 100, 2)

    def _calculate_build_success_rate(self, test_results: Dict[str, Any]) -> float:
        """计算构建成功率"""
        total_builds = test_results.get('total_builds', 1)
        successful_builds = test_results.get('successful_builds', 0)
        return round((successful_builds / total_builds) * 100, 2)

    def generate_daily_summary(self) -> str:
        """生成每日质量摘要"""
        today = datetime.date.today().isoformat()

        # 收集今天的测试结果
        test_results_path = self.output_dir / "latest_test_summary.json"
        if not test_results_path.exists():
            return "No test results available for today"

        with open(test_results_path) as f:
            test_results = json.load(f)

        # 生成摘要
        summary = f"""
# Daily Quality Report - {today}

## Test Results
- Total Tests: {test_results.get('total_tests', 0)}
- Passed: {test_results.get('passed', 0)} ({test_results.get('pass_rate', 0):.1f}%)
- Failed: {test_results.get('failed', 0)}
- Coverage: {test_results.get('coverage', 0):.1f}%
- Duration: {test_results.get('duration', 0):.2f}s

## Quality Metrics
- Overall Status: {test_results.get('status', 'unknown').upper()}

## Recommendations
{self._get_daily_recommendations(test_results)}
        """

        # 保存摘要
        summary_path = self.output_dir / f"daily_summary_{today}.md"
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(summary)

        return str(summary_path)

    def _get_daily_recommendations(self, test_results: Dict[str, Any]) -> str:
        """获取每日建议"""
        recommendations = []

        if test_results.get('failed', 0) > 0:
            recommendations.append("- Fix failing tests")

        if test_results.get('coverage', 0) < 80:
            recommendations.append("- Improve test coverage")

        if test_results.get('status') == 'failed':
            recommendations.append("- Investigate build failures")

        return '\n'.join(recommendations) if recommendations else "- All quality gates passed!"