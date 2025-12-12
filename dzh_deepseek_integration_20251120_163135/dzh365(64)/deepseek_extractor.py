#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DZH系统DeepSeek文件提取器
从DZH大智慧系统中提取DeepSeek相关的股票和配置信息
"""

import os
import struct
import json
from datetime import datetime
from typing import List, Dict, Any

class DZHDeepSeekExtractor:
    """DZH DeepSeek文件提取器"""

    def __init__(self, dzh_path: str = "/mnt/d/dzh365(64)"):
        self.dzh_path = dzh_path
        self.deepseek_files = {
            'config': os.path.join(dzh_path, 'cfg/deepseek.xml'),
            'block_main': os.path.join(dzh_path, 'USERDATA/block/DeepSeek概念0701303.blk'),
            'block_backup': os.path.join(dzh_path, 'USERDATA_bak/block/DeepSeek概念0701303.blk')
        }

    def extract_deepseek_config(self) -> Dict[str, Any]:
        """提取DeepSeek配置信息"""
        config_path = self.deepseek_files['config']

        if not os.path.exists(config_path):
            return {"error": f"配置文件不存在: {config_path}"}

        try:
            with open(config_path, 'r', encoding='gb2312') as f:
                content = f.read()

            # 简单解析XML配置
            config_data = {
                "file_path": config_path,
                "file_size": os.path.getsize(config_path),
                "last_modified": datetime.fromtimestamp(os.path.getmtime(config_path)).strftime('%Y-%m-%d %H:%M:%S'),
                "content_preview": content[:500] + "..." if len(content) > 500 else content,
                "contains_url": "f.dzh.com.cn" in content,
                "service_type": "AI问答服务" if "newask" in content else "未知服务"
            }

            return config_data

        except Exception as e:
            return {"error": f"读取配置文件失败: {str(e)}"}

    def parse_block_file(self, file_path: str) -> Dict[str, Any]:
        """解析DZH板块文件(.blk)"""
        if not os.path.exists(file_path):
            return {"error": f"板块文件不存在: {file_path}"}

        try:
            with open(file_path, 'rb') as f:
                data = f.read()

            # 解析板块文件头
            # DZH板块文件格式: 魔数 + 股票代码列表
            stock_codes = []

            # 读取文件头 (前4字节通常是魔数或标识)
            if len(data) >= 4:
                header = struct.unpack('<I', data[:4])[0]  # 小端序读取4字节

                # 解析股票代码 (每只股票8字节: SZ000000)
                offset = 4
                while offset + 8 <= len(data):
                    code_data = data[offset:offset+8]
                    try:
                        stock_code = code_data.decode('ascii', errors='ignore').strip('\x00')
                        if stock_code and stock_code.startswith(('SZ', 'SH')):
                            stock_codes.append(stock_code)
                        offset += 8
                    except:
                        break

            # 提取深圳股票代码
            sz_stocks = [code[2:] for code in stock_codes if code.startswith('SZ')]

            return {
                "file_path": file_path,
                "file_size": len(data),
                "header": f"0x{header:08X}" if 'header' in locals() else "N/A",
                "total_stocks": len(stock_codes),
                "stock_codes": stock_codes[:20],  # 只显示前20个
                "sz_stock_codes": sz_stocks[:20],  # 深圳股票代码
                "extracted_count": len(sz_stocks),
                "file_type": "DZH板块文件",
                "last_modified": datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S')
            }

        except Exception as e:
            return {"error": f"解析板块文件失败: {str(e)}"}

    def extract_all(self) -> Dict[str, Any]:
        """提取所有DeepSeek相关文件信息"""
        results = {
            "extraction_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "extractor_version": "v1.0",
            "dzh_path": self.dzh_path,
            "files": {}
        }

        # 提取配置文件
        print("🔧 提取DeepSeek配置文件...")
        results["files"]["config"] = self.extract_deepseek_config()

        # 提取主板块文件
        print("📊 提取DeepSeek概念板块文件...")
        results["files"]["block_main"] = self.parse_block_file(self.deepseek_files['block_main'])

        # 提取备份板块文件
        print("💾 提取DeepSeek概念板块备份文件...")
        results["files"]["block_backup"] = self.parse_block_file(self.deepseek_files['block_backup'])

        # 统计信息
        total_stocks = 0
        for block_key in ['block_main', 'block_backup']:
            block_data = results["files"].get(block_key, {})
            if 'extracted_count' in block_data:
                total_stocks = max(total_stocks, block_data['extracted_count'])

        results["summary"] = {
            "total_files_found": len([f for f in self.deepseek_files.values() if os.path.exists(f)]),
            "total_files_processed": len([k for k, v in results["files"].items() if "error" not in v]),
            "total_deepseek_stocks": total_stocks,
            "has_config": "error" not in results["files"].get("config", {}),
            "has_block_data": "error" not in results["files"].get("block_main", {})
        }

        return results

    def save_results(self, results: Dict[str, Any], output_file: str = "deepseek_extraction_results.json"):
        """保存提取结果到JSON文件"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"✅ 结果已保存到: {output_file}")
            return True
        except Exception as e:
            print(f"❌ 保存结果失败: {str(e)}")
            return False

    def print_summary(self, results: Dict[str, Any]):
        """打印提取结果摘要"""
        print("\n" + "="*60)
        print("🤖 DZH DeepSeek文件提取结果摘要")
        print("="*60)

        summary = results.get("summary", {})
        print(f"📁 文件总数: {summary.get('total_files_found', 0)}")
        print(f"✅ 处理成功: {summary.get('total_files_processed', 0)}")
        print(f"📈 DeepSeek概念股票: {summary.get('total_deepseek_stocks', 0)}只")
        print(f"⚙️ 配置文件: {'✅' if summary.get('has_config') else '❌'}")
        print(f"📊 板块数据: {'✅' if summary.get('has_block_data') else '❌'}")

        # 显示配置信息
        config = results["files"].get("config", {})
        if "error" not in config:
            print(f"\n🔧 配置文件信息:")
            print(f"   文件大小: {config.get('file_size', 0)} 字节")
            print(f"   服务类型: {config.get('service_type', '未知')}")
            print(f"   包含URL: {'是' if config.get('contains_url') else '否'}")

        #显示板块信息
        block_main = results["files"].get("block_main", {})
        if "error" not in block_main:
            print(f"\n📊 主板块文件信息:")
            print(f"   文件大小: {block_main.get('file_size', 0)} 字节")
            print(f"   股票总数: {block_main.get('total_stocks', 0)}")
            print(f"   提取股票: {block_main.get('extracted_count', 0)}只")

            # 显示前5只股票
            stock_codes = block_main.get('sz_stock_codes', [])[:5]
            if stock_codes:
                print(f"   股票示例: {', '.join(stock_codes)}")

def main():
    """主函数"""
    print("🚀 启动DZH DeepSeek文件提取器")
    print("="*50)

    # 创建提取器实例
    extractor = DZHDeepSeekExtractor()

    # 执行提取
    results = extractor.extract_all()

    # 打印摘要
    extractor.print_summary(results)

    # 保存结果
    output_file = f"/mnt/d/dzh365(64)/deepseek_extraction_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    extractor.save_results(results, output_file)

    print(f"\n🎉 提取完成！")
    print(f"📄 详细结果文件: {output_file}")

if __name__ == "__main__":
    main()