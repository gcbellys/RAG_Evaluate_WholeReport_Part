#!/usr/bin/env python3
"""
RAG_Evaluate_WholeReport 智能工作流脚本
智能检查baseline信息，避免重复运行，提高效率
"""

import argparse
import sys
import json
from datetime import datetime
from pathlib import Path

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent))

from workflows.main_workflow import MainWorkflow
from workflows.aggregation_workflow import AggregationWorkflow
from workflows.comparison_workflow import ComparisonWorkflow

class SmartWorkflowRunner:
    """智能工作流运行器"""
    
    def __init__(self):
        self.start_time = None
        self.results = {}
        self.baseline_existing = False
        self.aggregation_existing = False
        
    def check_existing_results(self, output_dir: str):
        """检查是否已存在结果文件"""
        output_path = Path(output_dir)
        
        print("🔍 检查现有结果...")
        
        # 检查baseline结果
        baseline_dir = output_path / "baseline_results"
        if baseline_dir.exists():
            baseline_files = list(baseline_dir.glob("*.json"))
            if baseline_files:
                print(f"✅ 发现现有baseline结果: {len(baseline_files)} 个文件")
                self.baseline_existing = True
                self.results['baseline'] = {
                    'output_dir': str(baseline_dir),
                    'files_count': len(baseline_files),
                    'status': 'existing'
                }
        
        # 检查aggregation结果
        aggregation_dir = output_path / "aggregation_results"
        if aggregation_dir.exists():
            aggregation_files = list(aggregation_dir.glob("*.json"))
            if aggregation_files:
                print(f"✅ 发现现有aggregation结果: {len(aggregation_files)} 个文件")
                self.aggregation_existing = True
                self.results['aggregation'] = {
                    'output_dir': str(aggregation_dir),
                    'files_count': len(aggregation_files),
                    'status': 'existing'
                }
        
        return self.baseline_existing and self.aggregation_existing
    
    def run_smart_workflow(self, data_path: str, output_dir: str, 
                          start_id: int = None, end_id: int = None, 
                          max_files: int = None, config: str = None,
                          force_rerun: bool = False):
        """运行智能工作流"""
        self.start_time = datetime.now()
        
        print("=" * 80)
        print("🧠 RAG_Evaluate_WholeReport 智能症状聚合工作流启动")
        print("=" * 80)
        print(f"开始时间: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"数据路径: {data_path}")
        print(f"输出目录: {output_dir}")
        print(f"ID范围: {start_id or '全部'} - {end_id or '全部'}")
        print(f"最大文件数: {max_files or '无限制'}")
        print(f"配置文件: {config or '默认'}")
        print(f"强制重运行: {'是' if force_rerun else '否'}")
        print("=" * 80)
        
        # 创建输出目录
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        try:
            # 如果不是强制重运行，先检查现有结果
            if not force_rerun:
                all_existing = self.check_existing_results(output_dir)
                if all_existing:
                    print("\n🎯 所有结果已存在，跳过重新运行，直接进行对比分析...")
                else:
                    print("\n🔄 部分结果缺失，需要补充运行...")
            else:
                print("\n🔄 强制重运行模式，忽略现有结果...")
                all_existing = False
            
            # 步骤1: 运行或使用baseline方法
            if not self.baseline_existing or force_rerun:
                print("\n📊 步骤1: 运行症状聚合基线方法...")
                self._run_baseline_method(data_path, output_path, start_id, end_id, max_files, config)
            else:
                print("\n📊 步骤1: 使用现有症状聚合基线结果...")
            
            # 步骤2: 运行或使用aggregation方法
            if not self.aggregation_existing or force_rerun:
                print("\n🔄 步骤2: 运行增强症状聚合方法...")
                self._run_aggregation_method(data_path, output_path, start_id, end_id, max_files, config)
            else:
                print("\n🔄 步骤2: 使用现有增强症状聚合结果...")
            
            # 步骤3: 运行对比分析
            print("\n📈 步骤3: 运行对比分析...")
            self._run_comparison_method(data_path, output_path, start_id, end_id, max_files, config)
            
            # 完成
            self._workflow_completed()
            
        except Exception as e:
            print(f"\n❌ 智能工作流执行失败: {e}")
            sys.exit(1)
    
    def _run_baseline_method(self, data_path: str, output_path: Path, 
                           start_id: int, end_id: int, max_files: int, config: str):
        """运行基线方法"""
        try:
            baseline_dir = output_path / "baseline_results"
            workflow = MainWorkflow()
            workflow.initialize(config)
            workflow.run_baseline_workflow(data_path, str(baseline_dir), start_id, end_id, max_files)
            print("✅ 基线方法完成")
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
            workflow.run_aggregation_workflow(data_path, str(aggregation_dir), start_id, end_id, max_files)
            print("✅ 聚合方法完成")
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
            workflow.run_comparison(data_path, str(comparison_dir), start_id, end_id, max_files)
            print("✅ 对比分析完成")
        except Exception as e:
            print(f"❌ 对比分析执行失败: {e}")
            raise
    
    def _workflow_completed(self):
        """工作流完成"""
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        print("\n" + "=" * 80)
        print("🎉 智能工作流执行完成！")
        print("=" * 80)
        print(f"开始时间: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"结束时间: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"总耗时: {duration}")
        
        print(f"\n📊 效率分析:")
        print(f"  Baseline重用: {'是' if self.baseline_existing else '否'}")
        print(f"  Aggregation重用: {'是' if self.aggregation_existing else '否'}")
        
        print("\n🚀 智能工作流完成！")
        print("=" * 80)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="RAG_Evaluate_WholeReport 智能工作流脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 智能工作流（自动检查现有结果）
  python run_smart_workflow.py --data_path test_set --output_dir results_smart

  # 智能工作流（指定范围）
  python run_smart_workflow.py --data_path test_set --output_dir results_smart --start_id 1 --end_id 100

  # 强制重运行（忽略现有结果）
  python run_smart_workflow.py --data_path test_set --output_dir results_smart --force_rerun

  # 智能工作流（限制文件数量）
  python run_smart_workflow.py --data_path test_set --output_dir results_smart --max_files 50

  # 使用自定义配置
  python run_smart_workflow.py --data_path test_set --output_dir results_smart --config config/config.yaml
        """
    )
    
    # 基本参数
    parser.add_argument("--data_path", default="test_set", help="数据目录路径 (默认: test_set)")
    parser.add_argument("--output_dir", required=True, help="输出目录路径")
    parser.add_argument("--config", default="config/config_cn.yaml", help="配置文件路径 (默认: config/config_cn.yaml)")
    
    # 范围控制参数
    parser.add_argument("--start_id", type=int, help="开始报告ID")
    parser.add_argument("--end_id", type=int, help="结束报告ID")
    parser.add_argument("--max_files", type=int, help="最大处理文件数量")
    
    # 智能模式参数
    parser.add_argument("--force_rerun", action="store_true", help="强制重运行，忽略现有结果")
    
    args = parser.parse_args()
    
    # 运行智能工作流
    runner = SmartWorkflowRunner()
    runner.run_smart_workflow(
        args.data_path, args.output_dir,
        args.start_id, args.end_id, args.max_files, args.config,
        args.force_rerun
    )

if __name__ == "__main__":
    main()
