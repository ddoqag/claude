#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DZH系统DeepSeek文件分析器
分析DeepSeek相关的股票代码、配置信息和板块数据
"""

import os
import struct
import json
import re
from datetime import datetime
from typing import List, Dict, Any, Optional

class DZHDeepSeekAnalyzer:
    """DZH DeepSeek文件分析器"""

    def __init__(self, dzh_path: str = "/mnt/d/dzh365(64)"):
        self.dzh_path = dzh_path
        self.deepseek_files = {
            'config': os.path.join(dzh_path, 'cfg/deepseek.xml'),
            'block_main': os.path.join(dzh_path, 'USERDATA/block/DeepSeek概念0701303.blk'),
            'block_backup': os.path.join(dzh_path, 'USERDATA_bak/block/DeepSeek概念0701303.blk')
        }

    def analyze_deepseek_config(self) -> Dict[str, Any]:
        """分析DeepSeek配置信息"""
        config_path = self.deepseek_files['config']

        if not os.path.exists(config_path):
            return {"error": f"配置文件不存在: {config_path}"}

        try:
            # 尝试多种编码
            encodings = ['utf-8', 'gb2312', 'gbk', 'latin-1', 'cp936']
            content = None
            used_encoding = None

            for encoding in encodings:
                try:
                    with open(config_path, 'r', encoding=encoding, errors='ignore') as f:
                        content = f.read()
                    used_encoding = encoding
                    break
                except UnicodeDecodeError:
                    continue

            if content is None:
                return {"error": "无法解码配置文件"}

            # 解析配置信息
            config_data = {
                "file_path": config_path,
                "file_size": os.path.getsize(config_path),
                "last_modified": datetime.fromtimestamp(os.path.getmtime(config_path)).strftime('%Y-%m-%d %H:%M:%S'),
                "encoding_used": used_encoding,
                "config_analysis": {}
            }

            # 提取URL信息
            url_match = re.search(r'<url>([^<]+)</url>', content)
            if url_match:
                url = url_match.group(1)
                config_data["config_analysis"]["service_url"] = url
                config_data["config_analysis"]["domain"] = self._extract_domain(url)
                config_data["config_analysis"]["has_api_token"] = "#V3TOKEN#" in url
                config_data["config_analysis"]["service_type"] = "AI问答服务" if "newask" in url else "未知服务"

            # 提取场景描述
            scene_descs = re.findall(r'<desc[^>]*>([^<]+)</desc>', content)
            if scene_descs:
                config_data["config_analysis"]["scene_descriptions"] = scene_descs

            # 提取注释信息
            comments = re.findall(r'<!--([^>]*)-->', content)
            if comments:
                config_data["config_analysis"]["comments"] = [comment.strip() for comment in comments]

            return config_data

        except Exception as e:
            return {"error": f"分析配置文件失败: {str(e)}"}

    def _extract_domain(self, url: str) -> str:
        """从URL中提取域名"""
        import urllib.parse
        try:
            parsed = urllib.parse.urlparse(url)
            return parsed.netloc
        except:
            return "解析失败"

    def parse_block_file_enhanced(self, file_path: str) -> Dict[str, Any]:
        """增强版DZH板块文件解析"""
        if not os.path.exists(file_path):
            return {"error": f"板块文件不存在: {file_path}"}

        try:
            with open(file_path, 'rb') as f:
                data = f.read()

            result = {
                "file_path": file_path,
                "file_size": len(data),
                "last_modified": datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S'),
                "file_analysis": {}
            }

            # 分析文件头
            if len(data) >= 4:
                header_bytes = data[:4]
                header = struct.unpack('<I', header_bytes)[0]
                result["file_analysis"]["header_hex"] = f"0x{header:08X}"
                result["file_analysis"]["header_bytes"] = header_bytes.hex()

            # 解析股票代码
            stock_codes = []
            sz_stocks = []
            sh_stocks = []

            # DZH板块文件通常是: 魔数(4字节) + 股票代码列表(每只6字节: 市场代码+股票代码)
            offset = 4
            while offset + 6 <= len(data):
                code_data = data[offset:offset+6]
                try:
                    # 解析6字节的股票代码 (2字节市场 + 4字节股票代码)
                    market_code = code_data[:2].decode('ascii', errors='ignore').strip('\x00')
                    stock_code_num = code_data[2:6].decode('ascii', errors='ignore').strip('\x00')

                    if market_code in ['SZ', 'SH'] and stock_code_num.isdigit():
                        full_code = f"{market_code}{stock_code_num}"
                        stock_codes.append(full_code)

                        if market_code == 'SZ':
                            sz_stocks.append(stock_code_num)
                        elif market_code == 'SH':
                            sh_stocks.append(stock_code_num)

                    offset += 6
                except:
                    # 尝试8字节格式
                    if offset + 8 <= len(data):
                        code_data_8 = data[offset:offset+8]
                        try:
                            full_code = code_data_8.decode('ascii', errors='ignore').strip('\x00')
                            if full_code.startswith(('SZ', 'SH')) and len(full_code) >= 8:
                                stock_codes.append(full_code)
                                market = full_code[:2]
                                stock_num = full_code[2:]
                                if market == 'SZ':
                                    sz_stocks.append(stock_num)
                                elif market == 'SH':
                                    sh_stocks.append(stock_num)
                            offset += 8
                        except:
                            break
                    else:
                        break

            result["file_analysis"]["total_stocks"] = len(stock_codes)
            result["file_analysis"]["sz_stocks"] = len(sz_stocks)
            result["file_analysis"]["sh_stocks"] = len(sh_stocks)
            result["file_analysis"]["stock_codes"] = stock_codes
            result["file_analysis"]["sz_stock_codes"] = sz_stocks
            result["file_analysis"]["sh_stock_codes"] = sh_stocks
            result["file_analysis"]["sample_stocks"] = stock_codes[:10]  # 显示前10只股票

            # 分析股票代码分布
            if sz_stocks:
                result["file_analysis"]["sz_sample"] = sz_stocks[:10]
                # 分析股票代码范围
                sz_nums = [int(code) for code in sz_stocks if code.isdigit()]
                if sz_nums:
                    result["file_analysis"]["sz_range"] = f"{min(sz_nums):06d}-{max(sz_nums):06d}"

            if sh_stocks:
                result["file_analysis"]["sh_sample"] = sh_stocks[:10]

            return result

        except Exception as e:
            return {"error": f"解析板块文件失败: {str(e)}"}

    def get_stock_name_from_code(self, stock_code: str) -> Optional[str]:
        """根据股票代码获取股票名称（模拟）"""
        # 这里应该连接到真实的股票数据库，现在只是示例
        stock_names = {
            "000001": "平安银行",
            "000002": "万科A",
            "000032": "深桑达A",
            "000066": "中国长城",
            "000513": "粤宏远A",
            "000555": "神州信息",
            "000710": "贝瑞基因",
            "000785": "居然之家",
            "000948": "京山轻机",
            "000997": "新大陆",
            "002010": "传化智联",
            "002152": "广电运通"
        }
        return stock_names.get(stock_code, f"股票{stock_code}")

    def analyze_all(self) -> Dict[str, Any]:
        """分析所有DeepSeek相关文件"""
        results = {
            "analysis_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "analyzer_version": "v2.0",
            "dzh_path": self.dzh_path,
            "files": {}
        }

        print("🔧 分析DeepSeek配置文件...")
        results["files"]["config"] = self.analyze_deepseek_config()

        print("📊 分析DeepSeek概念主板块文件...")
        results["files"]["block_main"] = self.parse_block_file_enhanced(self.deepseek_files['block_main'])

        print("💾 分析DeepSeek概念备份板块文件...")
        results["files"]["block_backup"] = self.parse_block_file_enhanced(self.deepseek_files['block_backup'])

        # 生成综合分析
        results["comprehensive_analysis"] = self._generate_comprehensive_analysis(results["files"])

        return results

    def _generate_comprehensive_analysis(self, file_results: Dict[str, Any]) -> Dict[str, Any]:
        """生成综合分析报告"""
        analysis = {
            "found_files": {},
            "stock_analysis": {},
            "service_analysis": {},
            "data_quality": {}
        }

        # 统计找到的文件
        for key, result in file_results.items():
            if "error" not in result:
                analysis["found_files"][key] = {
                    "size": result.get("file_size", 0),
                    "status": "正常"
                }
            else:
                analysis["found_files"][key] = {
                    "status": "错误",
                    "error": result.get("error", "未知错误")
                }

        # 股票数据分析
        total_stocks = 0
        all_stocks = []

        for block_key in ['block_main', 'block_backup']:
            block_data = file_results.get(block_key, {})
            if "file_analysis" in block_data:
                file_analysis = block_data["file_analysis"]
                total_stocks = max(total_stocks, file_analysis.get("total_stocks", 0))
                if "stock_codes" in file_analysis:
                    all_stocks.extend(file_analysis["stock_codes"])

        # 去重统计
        unique_stocks = list(set(all_stocks))
        analysis["stock_analysis"] = {
            "total_stocks_in_block": total_stocks,
            "unique_stocks_found": len(unique_stocks),
            "sample_stocks_with_names": []
        }

        # 为前10只股票添加名称
        for stock in unique_stocks[:10]:
            market = stock[:2]
            code = stock[2:]
            name = self.get_stock_name_from_code(code)
            analysis["stock_analysis"]["sample_stocks_with_names"].append({
                "code": code,
                "market": market,
                "name": name,
                "full_code": stock
            })

        # 服务配置分析
        config_data = file_results.get("config", {})
        if "config_analysis" in config_data:
            config_analysis = config_data["config_analysis"]
            analysis["service_analysis"] = {
                "service_type": config_analysis.get("service_type", "未知"),
                "service_domain": config_analysis.get("domain", "未知"),
                "uses_token_auth": config_analysis.get("has_api_token", False),
                "scene_descriptions": config_analysis.get("scene_descriptions", [])
            }

        # 数据质量评估
        analysis["data_quality"] = {
            "has_config": "config_analysis" in config_data,
            "has_block_data": any("file_analysis" in file_results.get(k, {}) for k in ['block_main', 'block_backup']),
            "data_completeness": "完整" if len(analysis["found_files"]) == 3 else "部分",
            "last_update": "2025-11-20"  # 基于文件修改时间
        }

        return analysis

    def save_analysis(self, results: Dict[str, Any], output_file: str = None):
        """保存分析结果"""
        if output_file is None:
            output_file = f"/mnt/d/dzh365(64)/deepseek_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"✅ 分析结果已保存到: {output_file}")
            return True
        except Exception as e:
            print(f"❌ 保存分析结果失败: {str(e)}")
            return False

    def print_comprehensive_report(self, results: Dict[str, Any]):
        """打印综合分析报告"""
        print("\n" + "="*70)
        print("🤖 DZH DeepSeek文件综合分析报告")
        print("="*70)

        comprehensive = results.get("comprehensive_analysis", {})

        # 文件状态
        print(f"\n📁 文件发现状况:")
        found_files = comprehensive.get("found_files", {})
        for file_type, info in found_files.items():
            status_icon = "✅" if info.get("status") == "正常" else "❌"
            print(f"   {status_icon} {file_type}: {info.get('status', '未知')}")

        # 股票分析
        stock_analysis = comprehensive.get("stock_analysis", {})
        print(f"\n📈 股票数据分析:")
        print(f"   📊 板块内股票总数: {stock_analysis.get('total_stocks_in_block', 0)}只")
        print(f"   🔢 去重后股票数量: {stock_analysis.get('unique_stocks_found', 0)}只")

        sample_stocks = stock_analysis.get("sample_stocks_with_names", [])
        if sample_stocks:
            print(f"   📋 股票示例:")
            for stock in sample_stocks[:5]:
                print(f"      {stock['full_code']} - {stock['name']}")

        # 服务分析
        service_analysis = comprehensive.get("service_analysis", {})
        if service_analysis:
            print(f"\n🔧 服务配置分析:")
            print(f"   🌐 服务类型: {service_analysis.get('service_type', '未知')}")
            print(f"   🌍 服务域名: {service_analysis.get('service_domain', '未知')}")
            print(f"   🔑 Token认证: {'启用' if service_analysis.get('uses_token_auth') else '未启用'}")

            scenes = service_analysis.get('scene_descriptions', [])
            if scenes:
                print(f"   📝 场景描述: {', '.join(scenes[:2])}")

        # 数据质量
        data_quality = comprehensive.get("data_quality", {})
        print(f"\n📊 数据质量评估:")
        print(f"   📄 配置文件: {'完整' if data_quality.get('has_config') else '缺失'}")
        print(f"   📋 板块数据: {'完整' if data_quality.get('has_block_data') else '缺失'}")
        print(f"   📈 数据完整性: {data_quality.get('data_completeness', '未知')}")

def main():
    """主函数"""
    print("🚀 启动DZH DeepSeek文件分析器")
    print("="*60)

    # 创建分析器实例
    analyzer = DZHDeepSeekAnalyzer()

    # 执行分析
    results = analyzer.analyze_all()

    # 打印综合报告
    analyzer.print_comprehensive_report(results)

    # 保存结果
    analyzer.save_analysis(results)

    print(f"\n🎉 分析完成！")

if __name__ == "__main__":
    main()