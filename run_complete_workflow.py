#!/usr/bin/env python3
"""
RAG_Evaluate_WholeReport 完整工作流脚本
自动化运行整个评估流程：基线方法 → 聚合方法 → 对比分析
"""

import argparse
import sys
import time
from datetime import datetime
from pathlib import Path

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent))

from workflows.main_workflow import MainWorkflow
from workflows.aggregation_workflow import AggregationWorkflow
from workflows.comparison_workflow import ComparisonWorkflow

class CompleteWorkflowRunner:
    """完整工作流运行器"""
    
    def __init__(self):
        self.start_time = None
        self.results = {}
        
    def run_complete_workflow(self, data_path: str, output_dir: str, 
                             start_id: int = None, end_id: int = None, 
                             max_files: int = None, config: str = None):
        """运行完整的工作流"""
        self.start_time = datetime.now()
        
        print("=" * 80)
        print("🚀 RAG_Evaluate_WholeReport 完整工作流启动")
        print("=" * 80)
        print(f"开始时间: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"数据路径: {data_path}")
        print(f"输出目录: {output_dir}")
        print(f"ID范围: {start_id or '全部'} - {end_id or '全部'}")
        print(f"最大文件数: {max_files or '无限制'}")
        print(f"配置文件: {config or '默认'}")
        print("=" * 80)
        
        # 创建输出目录
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        try:
            # 步骤1: 运行基线方法
            print("\n📊 步骤1: 运行基线方法（逐个症状处理）...")
            baseline_results = self._run_baseline_method(data_path, output_path, start_id, end_id, max_files, config)
            
            # 步骤2: 运行聚合方法
            print("\n🔄 步骤2: 运行聚合方法（报告级聚合处理）...")
            aggregation_results = self._run_aggregation_method(data_path, output_path, start_id, end_id, max_files, config)
            
            # 步骤3: 运行对比分析
            print("\n📈 步骤3: 运行对比分析（基线 vs 聚合）...")
            comparison_results = self._run_comparison_method(data_path, output_path, start_id, end_id, max_files, config)
            
            # 步骤4: 生成完整报告
            print("\n📋 步骤4: 生成完整工作流报告...")
            self._generate_complete_report(output_path)
            
            # 完成
            self._workflow_completed()
            
        except Exception as e:
            print(f"\n❌ 工作流执行失败: {e}")
            self._workflow_failed(e)
            sys.exit(1)
    
    def _run_baseline_method(self, data_path: str, output_path: Path, 
                           start_id: int, end_id: int, max_files: int, config: str):
        """运行基线方法"""
        try:
            baseline_dir = output_path / "baseline_results"
            workflow = MainWorkflow()
            workflow.initialize(config)
            
            # 运行基线工作流程
            workflow.run_baseline_workflow(
                data_path, str(baseline_dir),
                start_id, end_id, max_files
            )
            
            # 收集结果
            baseline_files = list(baseline_dir.glob("*.json"))
            self.results['baseline'] = {
                'output_dir': str(baseline_dir),
                'files_count': len(baseline_files),
                'files': [f.name for f in baseline_files]
            }
            
            print(f"✅ 基线方法完成，输出 {len(baseline_files)} 个文件")
            return baseline_files
            
        except Exception as e:
            print(f"❌ 基线方法执行失败: {e}")
            raise
    
    def _run_aggregation_method(self, data_path: str, output_path: Path, 
                              start_id: int, end_id: int, max_files: int, config: str):
        """运行聚合方法"""
        try:
            aggregation_dir = output_path / "aggregation_results"
            workflow = AggregationWorkflow()
            workflow.initialize(config)
            
            # 运行聚合工作流程
            workflow.run_aggregation_workflow(
                data_path, str(aggregation_dir),
                start_id, end_id, max_files
            )
            
            # 收集结果
            aggregation_files = list(aggregation_dir.glob("*.json"))
            self.results['aggregation'] = {
                'output_dir': str(aggregation_dir),
                'files_count': len(aggregation_files),
                'files': [f.name for f in aggregation_files]
            }
            
            print(f"✅ 聚合方法完成，输出 {len(aggregation_files)} 个文件")
            return aggregation_files
            
        except Exception as e:
            print(f"❌ 聚合方法执行失败: {e}")
            raise
    
    def _run_comparison_method(self, data_path: str, output_path: Path, 
                             start_id: int, end_id: int, max_files: int, config: str):
        """运行对比分析"""
        try:
            comparison_dir = output_path / "comparison_results"
            workflow = ComparisonWorkflow()
            workflow.initialize(config)
            
            # 运行对比工作流程
            workflow.run_comparison(
                data_path, str(comparison_dir),
                start_id, end_id, max_files
            )
            
            # 收集结果
            comparison_files = list(comparison_dir.glob("*.json"))
            comparison_files.extend(list(comparison_dir.glob("*.txt")))
            self.results['comparison'] = {
                'output_dir': str(comparison_dir),
                'files_count': len(comparison_files),
                'files': [f.name for f in comparison_files]
            }
            
            print(f"✅ 对比分析完成，输出 {len(comparison_files)} 个文件")
            return comparison_files
            
        except Exception as e:
            print(f"❌ 对比分析执行失败: {e}")
            raise
    
    def _generate_complete_report(self, output_path: Path):
        """生成完整工作流报告"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = output_path / f"complete_workflow_report_{timestamp}.json"
            
            complete_report = {
                'workflow_info': {
                    'name': 'RAG_Evaluate_WholeReport 完整工作流',
                    'start_time': self.start_time.isoformat(),
                    'end_time': datetime.now().isoformat(),
                    'duration_seconds': (datetime.now() - self.start_time).total_seconds()
                },
                'results_summary': self.results,
                'total_files_generated': sum(
                    result['files_count'] for result in self.results.values()
                )
            }
            
            # 保存完整报告
            import json
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(complete_report, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 完整工作流报告已保存: {report_file}")
            
        except Exception as e:
            print(f"⚠️  生成完整报告失败: {e}")
    
    def _workflow_completed(self):
        """工作流完成"""
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        print("\n" + "=" * 80)
        print("🎉 完整工作流执行完成！")
        print("=" * 80)
        print(f"开始时间: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"结束时间: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"总耗时: {duration}")
        print(f"生成文件总数: {sum(result['files_count'] for result in self.results.values())}")
        
        print("\n📁 输出目录结构:")
        for method, result in self.results.items():
            print(f"  {method}: {result['output_dir']} ({result['files_count']} 个文件)")
        
        print("\n🚀 工作流完成！所有结果已保存到指定目录。")
        print("=" * 80)
    
    def _workflow_failed(self, error):
        """工作流失败"""
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        print("\n" + "=" * 80)
        print("❌ 完整工作流执行失败！")
        print("=" * 80)
        print(f"开始时间: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"失败时间: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"运行时长: {duration}")
        print(f"错误信息: {error}")
        print("=" * 80)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="RAG_Evaluate_WholeReport 完整工作流脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 运行完整工作流（所有报告）
  python run_complete_workflow.py --data_path test_set --output_dir results_complete

  # 运行完整工作流（指定范围）
  python run_complete_workflow.py --data_path test_set --output_dir results_complete --start_id 1 --end_id 100

  # 运行完整工作流（限制文件数量）
  python run_complete_workflow.py --data_path test_set --output_dir results_complete --max_files 50

  # 使用自定义配置
  python run_complete_workflow.py --data_path test_set --output_dir results_complete --config config/config.yaml
        """
    )
    
    # 基本参数
    parser.add_argument("--data_path", default="test_set", help="数据目录路径 (默认: test_set)")
    parser.add_argument("--output_dir", required=True, help="输出目录路径")
    parser.add_argument("--config", default="config/config.yaml", help="配置文件路径 (默认: config/config.yaml)")
    
    # 范围控制参数
    parser.add_argument("--start_id", type=int, help="开始报告ID")
    parser.add_argument("--end_id", type=int, help="结束报告ID")
    parser.add_argument("--max_files", type=int, help="最大处理文件数量")
    
    args = parser.parse_args()
    
    # 运行完整工作流
    runner = CompleteWorkflowRunner()
    runner.run_complete_workflow(
        args.data_path, args.output_dir,
        args.start_id, args.end_id, args.max_files, args.config
    )

if __name__ == "__main__":
    main()
