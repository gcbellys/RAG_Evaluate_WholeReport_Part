#!/usr/bin/env python3
"""
RAG_Evaluate_WholeReport 简化启动脚本
与Rag_Evaluate完全一致的启动方式
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
    """主函数 - 简化启动入口"""
    parser = argparse.ArgumentParser(
        description="RAG_Evaluate_WholeReport - 简化启动脚本"
    )
    
    # 基本参数（与Rag_Evaluate一致）
    parser.add_argument("--start_id", type=int, help="开始报告ID")
    parser.add_argument("--end_id", type=int, help="结束报告ID")
    parser.add_argument("--max_files", type=int, help="最大处理文件数量")
    parser.add_argument("--config", default="config/config.yaml", help="配置文件路径")
    parser.add_argument("--mode", choices=['baseline', 'aggregation', 'comparison'], 
                        default='baseline', help="运行模式 (默认: baseline)")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("RAG_Evaluate_WholeReport 系统启动")
    print("=" * 60)
    
    try:
        if args.mode == 'baseline':
            print("🚀 启动基线工作流程...")
            workflow = MainWorkflow()
            workflow.initialize(args.config)
            workflow.run_baseline_workflow(
                "test_set", "results",
                args.start_id, args.end_id, args.max_files
            )
            
        elif args.mode == 'aggregation':
            print("🔄 启动聚合工作流程...")
            workflow = AggregationWorkflow()
            workflow.initialize(args.config)
            workflow.run_aggregation_workflow(
                "test_set", "results",
                args.start_id, args.end_id, args.max_files
            )
            
        elif args.mode == 'comparison':
            print("📊 启动对比工作流程...")
            workflow = ComparisonWorkflow()
            workflow.initialize(args.config)
            workflow.run_comparison(
                "test_set", "results",
                args.start_id, args.end_id, args.max_files
            )
            
        print("\n✅ 系统运行完成！")
        
    except Exception as e:
        print(f"\n❌ 系统运行失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
