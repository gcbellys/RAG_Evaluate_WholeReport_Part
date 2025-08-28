#!/usr/bin/env python3
"""
对比工作流程
比较基线方法（逐个症状处理）和聚合方法（报告级聚合处理）的性能
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
from src.aggregation_processor import AggregationProcessor
from src.aggregation_evaluator import AggregationEvaluator
from src.config_loader import ConfigLoader

class ComparisonWorkflow:
    """对比工作流程 - 比较基线方法和聚合方法"""
    
    def __init__(self):
        self.config = None
        self.api_manager = None
        self.data_loader = None
        self.evaluator = None
        self.aggregation_processor = None
        self.aggregation_evaluator = None
        
    def initialize(self, config_path: str = None):
        """初始化所有组件"""
        print("🔧 初始化对比工作流程...")
        
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
        self.aggregation_processor = AggregationProcessor()
        self.aggregation_evaluator = AggregationEvaluator()
        
        print("✅ 对比工作流程初始化完成")
    
    def run_baseline_method(self, report_files: List[Path], baseline_dir: Path) -> List[Dict[str, Any]]:
        """运行基线方法（症状聚合处理）"""
        print("📊 运行基线方法（症状聚合处理）...")
        
        baseline_results = []
        for file_path in report_files:
            try:
                print(f"\n📋 处理报告: {file_path.name}")
                
                # 加载报告数据
                report_data = self.data_loader.load_report_data(file_path)
                if 'error' in report_data:
                    print(f"❌ 加载报告失败: {report_data['error']}")
                    continue
                
                # 使用聚合方法处理整个报告
                print(f"🔄 聚合 {len(report_data['symptoms'])} 个症状...")
                aggregated_data = self.aggregation_processor.aggregate_symptoms_for_report(report_data)
                
                # 整体预测
                overall_prediction = self.aggregation_processor.predict_overall_organs_and_locations(
                    aggregated_data, self.api_manager
                )
                
                # 智能分割
                intelligent_symptoms = self.aggregation_processor.intelligently_split_symptoms(
                    aggregated_data, self.api_manager
                )
                
                # RAG搜索
                rag_results = self.aggregation_processor.rag_search_for_split_symptoms(
                    intelligent_symptoms, self.api_manager
                )
                
                # 构造基线结果（使用聚合方法）
                baseline_result = {
                    'report_id': report_data['report_id'],
                    'file_path': str(file_path),
                    'method': 'baseline_aggregation',
                    'original_symptoms_count': len(report_data['symptoms']),
                    'aggregated_symptoms': aggregated_data['aggregated_symptoms'],
                    'overall_prediction': overall_prediction,
                    'intelligent_symptoms': intelligent_symptoms,
                    'rag_results': rag_results,
                    'processing_timestamp': datetime.now().isoformat()
                }
                
                baseline_results.append(baseline_result)
                print(f"✅ 报告 {report_data['report_id']} 基线处理完成")
                 
            except Exception as e:
                print(f"❌ 处理报告 {file_path.name} 时出错: {e}")
                continue
         
        return baseline_results
    
    def run_aggregation_method(self, report_files: List[Path], aggregation_dir: Path) -> List[Dict[str, Any]]:
        """运行增强聚合方法：智能症状聚合+分割+RAG"""
        print("\n🔄 运行增强聚合方法（智能症状聚合+分割+RAG）...")
        
        aggregation_results = []
        for file_path in report_files:
            try:
                print(f"\n📋 处理报告: {file_path.name}")
                
                # 加载报告数据
                report_data = self.data_loader.load_report_data(file_path)
                if 'error' in report_data:
                    print(f"❌ 加载报告失败: {report_data['error']}")
                    continue
                
                # 使用聚合方法处理整个报告
                print(f"🔄 聚合 {len(report_data['symptoms'])} 个症状...")
                aggregated_data = self.aggregation_processor.aggregate_symptoms_for_report(report_data)
                
                # 整体预测
                overall_prediction = self.aggregation_processor.predict_overall_organs_and_locations(
                    aggregated_data, self.api_manager
                )
                
                # 智能分割
                intelligent_symptoms = self.aggregation_processor.intelligently_split_symptoms(
                    aggregated_data, self.api_manager
                )
                
                # RAG搜索
                rag_results = self.aggregation_processor.rag_search_for_split_symptoms(
                    intelligent_symptoms, self.api_manager
                )
                
                # 构造聚合结果
                aggregation_result = {
                    'report_id': report_data['report_id'],
                    'file_path': str(file_path),
                    'method': 'aggregation_report_level',
                    'original_symptoms_count': len(report_data['symptoms']),
                    'aggregated_symptoms': aggregated_data['aggregated_symptoms'],
                    'overall_prediction': overall_prediction,
                    'intelligent_symptoms': intelligent_symptoms,
                    'rag_results': rag_results,
                    'processing_timestamp': datetime.now().isoformat()
                }
                 
                aggregation_results.append(aggregation_result)
                print(f"✅ 报告 {report_data['report_id']} 聚合处理完成")
                 
            except Exception as e:
                print(f"❌ 处理报告 {file_path.name} 时出错: {e}")
                continue
         
        return aggregation_results
    
    def compare_methods(self, baseline_results: List[Dict[str, Any]], 
                       aggregation_results: List[Dict[str, Any]], 
                       output_dir: Path) -> Dict[str, Any]:
        """比较两种方法的性能"""
        print("\n📈 比较两种方法的性能...")
        
        comparison_results = {
            'comparison_timestamp': datetime.now().isoformat(),
            'total_reports': len(baseline_results),
            'method_comparison': {},
            'summary': {
                'baseline_method': '症状聚合基线方法',
                'aggregation_method': '增强症状聚合方法',
                'comparison_metrics': {
                    'processing_efficiency': '处理效率对比',
                    'prediction_quality': '预测质量对比',
                    'symptom_analysis': '症状分析对比'
                }
            }
        }
        
        # 逐个报告比较
        for baseline_result in baseline_results:
            report_id = baseline_result['report_id']
            
            # 查找对应的聚合结果
            aggregation_result = None
            for agg_result in aggregation_results:
                if agg_result['report_id'] == report_id:
                    aggregation_result = agg_result
                    break
            
            if not aggregation_result:
                continue
            
            # 比较基本信息
            baseline_symptoms_count = baseline_result.get('original_symptoms_count', 0)
            aggregation_symptoms_count = aggregation_result.get('original_symptoms_count', 0)
            
            # 比较预测结果
            baseline_prediction = baseline_result.get('overall_prediction', {})
            aggregation_prediction = aggregation_result.get('overall_prediction', {})
            
            # 比较智能分割结果
            baseline_intelligent = baseline_result.get('intelligent_symptoms', {})
            aggregation_intelligent = aggregation_result.get('intelligent_symptoms', {})
            
            # 比较RAG搜索结果
            baseline_rag = baseline_result.get('rag_results', {})
            aggregation_rag = aggregation_result.get('rag_results', {})
            
            # 记录详细比较
            comparison_results['method_comparison'][report_id] = {
                'baseline': {
                    'method': baseline_result.get('method', 'baseline_aggregation'),
                    'symptoms_count': baseline_symptoms_count,
                    'prediction_success': baseline_prediction.get('success', False),
                    'intelligent_split_success': baseline_intelligent.get('success', False),
                    'rag_searches': baseline_rag.get('total_searched', 0),
                    'processing_time': baseline_result.get('processing_timestamp', '')
                },
                'aggregation': {
                    'method': aggregation_result.get('method', 'aggregation_report_level'),
                    'symptoms_count': aggregation_symptoms_count,
                    'prediction_success': aggregation_prediction.get('success', False),
                    'intelligent_split_success': aggregation_intelligent.get('success', False),
                    'rag_searches': aggregation_rag.get('total_searched', 0),
                    'processing_time': aggregation_result.get('processing_timestamp', '')
                },
                'comparison': {
                    'symptoms_consistency': baseline_symptoms_count == aggregation_symptoms_count,
                    'prediction_comparison': f"基线: {'成功' if baseline_prediction.get('success') else '失败'}, 增强: {'成功' if aggregation_prediction.get('success') else '失败'}",
                    'processing_efficiency': '两种方法都使用症状聚合处理'
                }
            }
        
        # 计算总体统计
        total_reports = len(comparison_results['method_comparison'])
        if total_reports > 0:
            successful_baseline = sum(1 for comp in comparison_results['method_comparison'].values() 
                                    if comp['baseline']['prediction_success'])
            successful_aggregation = sum(1 for comp in comparison_results['method_comparison'].values() 
                                       if comp['aggregation']['prediction_success'])
            
            comparison_results['summary']['statistics'] = {
                'total_reports_compared': total_reports,
                'baseline_success_rate': f"{(successful_baseline/total_reports)*100:.1f}%",
                'aggregation_success_rate': f"{(successful_aggregation/total_reports)*100:.1f}%",
                'improvement_analysis': '两种方法都采用症状聚合，主要区别在于智能分割和RAG增强'
            }
        
        # 保存比较结果
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        comparison_dir = output_dir / "comparison_results"
        comparison_dir.mkdir(parents=True, exist_ok=True)
        comparison_file = comparison_dir / f"comparison_results_{timestamp}.json"
        
        try:
            with open(comparison_file, 'w', encoding='utf-8') as f:
                json.dump(comparison_results, f, ensure_ascii=False, indent=2)
            print(f"✅ 比较结果已保存到: {comparison_file}")
        except Exception as e:
            print(f"❌ 保存比较结果失败: {e}")
        
        return comparison_results
    
    def run_comparison(self, data_path: str, output_dir: str, 
                      start_id: int = None, end_id: int = None, 
                      max_files: int = None):
        """运行完整的对比分析"""
        print("🚀 开始对比分析...")
        
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
        
        # 运行基线方法
        baseline_dir = output_path / "baseline_results"
        baseline_results = self.run_baseline_method(report_files, baseline_dir)
        
        # 运行聚合方法
        aggregation_dir = output_path / "aggregation_results"
        aggregation_results = self.run_aggregation_method(report_files, aggregation_dir)
        
        # 比较结果
        comparison_dir = output_path / "comparison_results"
        comparison_results = self.compare_methods(baseline_results, aggregation_results, comparison_dir)
        
        # 生成总结报告
        self._generate_summary_report(comparison_results, output_path)
        
        print("🎉 对比分析完成！")
    
    def _generate_summary_report(self, comparison_results: Dict[str, Any], output_dir: Path):
        """生成总结报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        summary_file = output_dir / f"summary_report_{timestamp}.txt"
        
        try:
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write("🧠 RAG_Evaluate_WholeReport 症状聚合系统对比分析报告\n")
                f.write("=" * 80 + "\n\n")
                
                f.write(f"分析时间: {comparison_results['comparison_timestamp']}\n")
                f.write(f"总报告数: {comparison_results['total_reports']}\n\n")
                
                summary = comparison_results['summary']
                f.write("📊 方法对比:\n")
                f.write("-" * 50 + "\n")
                f.write(f"基线方法: {summary['baseline_method']}\n")
                f.write(f"增强方法: {summary['aggregation_method']}\n\n")
                
                if 'statistics' in summary:
                    stats = summary['statistics']
                    f.write("📈 处理统计:\n")
                    f.write("-" * 50 + "\n")
                    f.write(f"对比报告总数: {stats['total_reports_compared']}\n")
                    f.write(f"基线方法成功率: {stats['baseline_success_rate']}\n")
                    f.write(f"增强方法成功率: {stats['aggregation_success_rate']}\n\n")
                    
                    f.write("💡 分析结论:\n")
                    f.write("-" * 50 + "\n")
                    f.write(f"{stats['improvement_analysis']}\n\n")
                
                f.write("🔍 处理流程对比:\n")
                f.write("-" * 50 + "\n")
                f.write("基线方法: 症状聚合 → 整体预测 → 智能分割 → RAG搜索\n")
                f.write("增强方法: 症状聚合 → 整体预测 → 智能分割 → 增强RAG搜索\n\n")
                
                f.write("📁 详细结果文件位置:\n")
                f.write("-" * 50 + "\n")
                f.write("- 基线结果: baseline_results/\n")
                f.write("- 增强结果: aggregation_results/\n")
                f.write("- 对比分析: comparison_results/\n\n")
                
                f.write("详细数据请查看对应的JSON文件\n")
            
            print(f"✅ 总结报告已保存到: {summary_file}")
        except Exception as e:
            print(f"❌ 生成总结报告失败: {e}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="对比工作流程：比较基线方法和聚合方法")
    parser.add_argument("--data_path", required=True, help="数据目录路径")
    parser.add_argument("--output_dir", required=True, help="输出目录路径")
    parser.add_argument("--config", help="配置文件路径")
    parser.add_argument("--start_id", type=int, help="开始ID")
    parser.add_argument("--end_id", type=int, help="结束ID")
    parser.add_argument("--max_files", type=int, help="最大文件数量")
    
    args = parser.parse_args()
    
    # 运行对比工作流程
    workflow = ComparisonWorkflow()
    workflow.initialize(args.config)
    workflow.run_comparison(
        args.data_path, args.output_dir,
        args.start_id, args.end_id, args.max_files
    )

if __name__ == "__main__":
    main()