#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
运行报告级症状聚合处理的脚本
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from workflows.report_level_workflow import ReportLevelWorkflow

def main():
    """主函数"""
    # 创建并运行报告级工作流程
    workflow = ReportLevelWorkflow()
    
    # 可以在这里设置参数
    workflow.run_workflow(
        start_id=None,  # 设置为具体值来限制范围，如 1
        end_id=None,    # 设置为具体值来限制范围，如 10
        max_files=5     # 设置为具体值来限制文件数量
    )

if __name__ == "__main__":
    main()