#!/usr/bin/env python3
"""
测试参数解析
"""

import argparse

def main():
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
    parser.add_argument("--config", default="config/config.yaml", help="配置文件路径 (默认: config/config.yaml)")
    
    # 范围控制参数
    parser.add_argument("--start_id", type=int, help="开始报告ID")
    parser.add_argument("--end_id", type=int, help="结束报告ID")
    parser.add_argument("--max_files", type=int, help="最大处理文件数量")
    
    # 智能模式参数
    parser.add_argument("--force_rerun", action="store_true", help="强制重运行，忽略现有结果")
    
    args = parser.parse_args()
    
    print("参数解析成功！")
    print(f"data_path: {args.data_path}")
    print(f"output_dir: {args.output_dir}")
    print(f"config: {args.config}")
    print(f"start_id: {args.start_id}")
    print(f"end_id: {args.end_id}")
    print(f"max_files: {args.max_files}")
    print(f"force_rerun: {args.force_rerun}")

if __name__ == "__main__":
    main()
