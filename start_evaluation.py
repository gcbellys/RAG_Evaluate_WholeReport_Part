#!/usr/bin/env python3
"""
RAG_Evaluate_WholeReport 统一启动脚本
一个命令启动整个系统，支持基线、聚合和对比三种模式
"""

import argparse
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent))

from workflows.main_workflow import MainWorkflow
from workflows.aggregation_workflow import AggregationWorkflow
from workflows.comparison_workflow import ComparisonWorkflow

def main():
    """主函数 - 统一启动入口"""
    parser = argparse.ArgumentParser(
        description="RAG_Evaluate_WholeReport - 统一启动脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 运行基线方法（逐个症状处理）
  python start_evaluation.py --mode baseline --data_path test_set --output_dir results_baseline

  # 运行聚合方法（报告级聚合处理）
  python start_evaluation.py --mode aggregation --data_path test_set --output_dir results_aggregation

  # 运行对比分析（同时运行两种方法）
  python start_evaluation.py --mode comparison --data_path test_set --output_dir results_comparison

  # 处理指定范围的报告
  python start_evaluation.py --mode baseline --data_path test_set --output_dir results --start_id 1 --end_id 10 --max_files 5
        """
    )
    
    # 基本参数
    parser.add_argument("--mode", required=True, choices=['baseline', 'aggregation', 'comparison'],
                        help="运行模式: baseline(基线), aggregation(聚合), comparison(对比)")
    parser.add_argument("--data_path", default="test_set", help="数据目录路径 (默认: test_set)")
    parser.add_argument("--output_dir", required=True, help="输出目录路径")
    parser.add_argument("--config", default="config/config.yaml", help="配置文件路径 (默认: config/config.yaml)")
    
    # 范围控制参数
    parser.add_argument("--start_id", type=int, help="开始报告ID")
    parser.add_argument("--end_id", type=int, help="结束报告ID")
    parser.add_argument("--max_files", type=int, help="最大处理文件数量")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("RAG_Evaluate_WholeReport 系统启动")
    print("=" * 60)
    print(f"运行模式: {args.mode}")
    print(f"数据路径: {args.data_path}")
    print(f"输出目录: {args.output_dir}")
    print(f"配置文件: {args.config}")
    
    try:
        if args.mode == 'baseline':
            print("\n🚀 启动基线工作流程（逐个症状处理）...")
            workflow = MainWorkflow()
            workflow.initialize(args.config)
            workflow.run_baseline_workflow(
                args.data_path, args.output_dir,
                args.start_id, args.end_id, args.max_files
            )
            
        elif args.mode == 'aggregation':
            print("\n🔄 启动聚合工作流程（报告级聚合处理）...")
            workflow = AggregationWorkflow()
            workflow.initialize(args.config)
            workflow.run_aggregation_workflow(
                args.data_path, args.output_dir,
                args.start_id, args.end_id, args.max_files
            )
            
        elif args.mode == 'comparison':
            print("\n📊 启动对比工作流程（基线 vs 聚合）...")
            workflow = ComparisonWorkflow()
            workflow.initialize(args.config)
            workflow.run_comparison(
                args.data_path, args.output_dir,
                args.start_id, args.end_id, args.max_files
            )
            
        print("\n✅ 系统运行完成！")
        
    except Exception as e:
        print(f"\n❌ 系统运行失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
