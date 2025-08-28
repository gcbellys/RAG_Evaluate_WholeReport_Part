#!/usr/bin/env python3
"""
主工作流程
运行基线方法：逐个症状处理
"""

import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

# 添加项目根目录到路径
import sys
sys.path.append(str(Path(__file__).parent.parent))

from src.api_manager import APIManager
from src.data_loader import DataLoader
from src.evaluator import Evaluator
from src.config_loader import ConfigLoader

class MainWorkflow:
    """主工作流程 - 运行基线方法（逐个症状处理）"""
    
    def __init__(self):
        self.config = None
        self.api_manager = None
        self.data_loader = None
        self.evaluator = None
        
    def initialize(self, config_path: str = None):
        """初始化所有组件"""
        print("🔧 初始化主工作流程...")
        
        # 加载配置
        self.config_loader = ConfigLoader(config_path) if config_path else ConfigLoader()
        self.config = self.config_loader.config
        
        # 初始化API管理器
        self.api_manager = APIManager()
        if not self.api_manager.initialize_clients(self.config):
            raise ValueError("API客户端初始化失败")
        
        # 测试API连通性
        if not self.api_manager.test_connectivity():
            print("⚠️  API连通性测试失败，但继续执行")
        
        # 初始化其他组件
        self.data_loader = DataLoader()
        self.evaluator = Evaluator()
        
        print("✅ 主工作流程初始化完成")
    
    def process_single_report(self, file_path: Path) -> Dict[str, Any]:
        """处理单个报告文件"""
        try:
            print(f"\n📋 处理报告: {file_path.name}")
            
            # 加载报告数据
            report_data = self.data_loader.load_report_data(file_path)
            if 'error' in report_data:
                print(f"❌ 加载报告失败: {report_data['error']}")
                return None
            
            # 逐个处理症状
            # 加载系统提示词
            system_prompt_path = Path("prompt/system_prompt.txt")
            if system_prompt_path.exists():
                with open(system_prompt_path, 'r', encoding='utf-8') as f:
                    system_prompt = f.read().strip()
            else:
                system_prompt = "你是一个医学专家，请根据症状识别相关的器官和解剖位置。"
            
            report_results = self.api_manager.process_report_symptoms(report_data, system_prompt)
            
            # 评估结果
            report_evaluation = self.evaluator.evaluate_report_responses(report_results)
            
            return {
                'report_id': report_data['report_id'],
                'file_path': str(file_path),
                'report_results': report_results,
                'report_evaluation': report_evaluation
            }
            
        except Exception as e:
            print(f"❌ 处理报告 {file_path.name} 时出错: {e}")
            return None
    
    def run_baseline_workflow(self, data_path: str, output_dir: str, 
                            start_id: int = None, end_id: int = None, 
                            max_files: int = None):
        """运行基线工作流程"""
        print("🚀 开始基线工作流程（逐个症状处理）...")
        
        # 创建输出目录
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 获取报告文件
        data_path = Path(data_path)
        report_files = self.data_loader.get_reports_by_id_range(
            data_path, start_id, end_id, max_files
        )
        
        if not report_files:
            print("❌ 没有找到符合条件的报告文件")
            return
        
        print(f"📁 找到 {len(report_files)} 个报告文件")
        
        # 处理每个报告
        processed_reports = []
        
        for i, file_path in enumerate(report_files, 1):
            print(f"\n进度: {i}/{len(report_files)}")
            
            result = self.process_single_report(file_path)
            if result:
                processed_reports.append(result)
                
                # 保存单个报告结果
                saved_file = self.evaluator.save_report_results(
                    result['report_results'], 
                    result['report_evaluation'], 
                    output_path
                )
                
                print(f"✅ 报告 {result['report_id']} 处理完成，结果已保存")
        
        # 生成汇总报告
        if processed_reports:
            self._generate_summary_report(processed_reports, output_path)
        
        print(f"\n🎉 基线工作流程完成！成功处理 {len(processed_reports)} 个报告")
    
    def _generate_summary_report(self, processed_reports: List[Dict[str, Any]], output_dir: Path):
        """生成汇总报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        summary_file = output_dir / f"baseline_summary_report_{timestamp}.json"
        
        summary = {
            'workflow_type': 'baseline_individual_symptoms',
            'timestamp': datetime.now().isoformat(),
            'total_reports': len(processed_reports),
            'reports': [],
            'overall_statistics': {
                'total_symptoms': 0,
                'valid_symptoms': 0,
                'total_api_calls': 0,
                'successful_api_calls': 0,
                'failed_api_calls': 0,
                'average_overall_score': 0.0,
                'average_precision': 0.0,
                'average_recall': 0.0
            }
        }
        
        total_scores = []
        total_precision = []
        total_recall = []
        
        for report in processed_reports:
            report_data = report['report_results']
            evaluation = report['report_evaluation']
            
            # 记录报告信息
            summary['reports'].append({
                'report_id': report['report_id'],
                'file_path': report['file_path'],
                'total_symptoms': report_data['total_symptoms'],
                'valid_symptoms': report_data['valid_symptoms'],
                'api_clients': list(report_data['symptoms'][0]['api_responses'].keys()) if report_data['symptoms'] else []
            })
            
            # 累计统计
            summary['overall_statistics']['total_symptoms'] += report_data['total_symptoms']
            summary['overall_statistics']['valid_symptoms'] += report_data['valid_symptoms']
            summary['overall_statistics']['total_api_calls'] += evaluation['summary']['total_api_calls']
            summary['overall_statistics']['successful_api_calls'] += evaluation['summary']['successful_api_calls']
            summary['overall_statistics']['failed_api_calls'] += evaluation['summary']['failed_api_calls']
            
            # 累计分数
            if evaluation['summary']['average_overall_score'] > 0:
                total_scores.append(evaluation['summary']['average_overall_score'])
                total_precision.append(evaluation['summary']['average_precision'])
                total_recall.append(evaluation['summary']['average_recall'])
        
        # 计算平均分数
        if total_scores:
            summary['overall_statistics']['average_overall_score'] = round(sum(total_scores) / len(total_scores), 1)
            summary['overall_statistics']['average_precision'] = round(sum(total_precision) / len(total_precision), 1)
            summary['overall_statistics']['average_recall'] = round(sum(total_recall) / len(total_recall), 1)
        
        # 保存汇总报告
        try:
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)
            print(f"✅ 汇总报告已保存到: {summary_file}")
        except Exception as e:
            print(f"❌ 保存汇总报告失败: {e}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="主工作流程：运行基线方法（逐个症状处理）")
    parser.add_argument("--data_path", required=True, help="数据目录路径")
    parser.add_argument("--output_dir", required=True, help="输出目录路径")
    parser.add_argument("--config", help="配置文件路径")
    parser.add_argument("--start_id", type=int, help="开始ID")
    parser.add_argument("--end_id", type=int, help="结束ID")
    parser.add_argument("--max_files", type=int, help="最大文件数量")
    
    args = parser.parse_args()
    
    # 运行主工作流程
    workflow = MainWorkflow()
    workflow.initialize(args.config)
    workflow.run_baseline_workflow(
        args.data_path, args.output_dir,
        args.start_id, args.end_id, args.max_files
    )

if __name__ == "__main__":
    main()
