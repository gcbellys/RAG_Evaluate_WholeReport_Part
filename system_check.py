#!/usr/bin/env python3
"""
系统验证脚本
检查系统是否配置正确，可以正常运行
"""

import sys
import os
from pathlib import Path

def check_system():
    """检查系统配置"""
    print("🔍 系统验证检查...")
    
    # 检查文件结构
    required_files = [
        'start.py',
        'start_evaluation.py',
        'api_clients',
        'src/api_manager.py',
        'src/evaluator.py',
        'src/data_loader.py',
        'src/config_loader.py',
        'src/aggregation_processor.py',
        'src/aggregation_evaluator.py',
        'workflows/main_workflow.py',
        'workflows/aggregation_workflow.py',
        'workflows/comparison_workflow.py',
        'config/config.yaml',
        'requirements.txt'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ 缺失文件:")
        for f in missing_files:
            print(f"   - {f}")
        return False
    
    print("✅ 文件结构完整")
    
    # 检查Python环境
    try:
        import json
        import datetime
        from pathlib import Path
        print("✅ Python基础库正常")
    except ImportError as e:
        print(f"❌ Python库缺失: {e}")
        return False
    
    # 检查API客户端
    try:
        sys.path.append(str(Path(__file__).parent))
        from api_clients.openai_client import OpenAIClient
        from api_clients.anthropic_client import AnthropicClient
        print("✅ API客户端模块正常")
    except ImportError as e:
        print(f"❌ API客户端导入失败: {e}")
        return False
    
    # 检查核心组件
    try:
        from src.api_manager import APIManager
        from src.evaluator import Evaluator
        from src.data_loader import DataLoader
        from src.config_loader import ConfigLoader
        from src.aggregation_processor import AggregationProcessor
        from src.aggregation_evaluator import AggregationEvaluator
        print("✅ 核心组件正常")
    except ImportError as e:
        print(f"❌ 核心组件导入失败: {e}")
        return False
    
    # 检查工作流程
    try:
        from workflows.main_workflow import MainWorkflow
        from workflows.aggregation_workflow import AggregationWorkflow
        from workflows.comparison_workflow import ComparisonWorkflow
        print("✅ 工作流程正常")
    except ImportError as e:
        print(f"❌ 工作流程导入失败: {e}")
        return False
    
    # 检查配置文件
    config_path = Path("config/config.yaml")
    if config_path.exists():
        print("✅ 配置文件存在")
    else:
        print("⚠️  配置文件不存在，将使用默认配置")
    
    # 检查测试数据
    test_path = Path("test_set")
    if test_path.exists() and any(test_path.glob("*.json")):
        print("✅ 测试数据存在")
    else:
        print("⚠️  测试数据目录为空或不存在")
    
    print("\n🎉 系统验证完成！")
    print("\n使用指南:")
    print("1. 激活环境: conda activate rag5090")
    print("2. 运行系统: python start.py")
    print("3. 查看帮助: python start.py --help")
    
    return True

if __name__ == "__main__":
    check_system()
