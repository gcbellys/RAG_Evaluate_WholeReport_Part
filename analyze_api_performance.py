#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API性能分析脚本
分析4050-4080范围内各个API的性能表现
"""

import json
import os
import glob
from typing import Dict, List, Tuple
import statistics
from collections import defaultdict

def load_json_file(file_path: str) -> dict:
    """加载JSON文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"加载文件失败 {file_path}: {e}")
        return {}

def extract_api_performance(file_path: str) -> Dict[str, List[Dict]]:
    """从文件中提取API性能数据"""
    data = load_json_file(file_path)
    if not data:
        return {}
    
    api_performance = defaultdict(list)
    
    for report in data:
        if 'method' not in report:
            continue
            
        method = report['method']
        method_type = 'baseline' if 'baseline' in method else 'rag_enhanced'
        
        # 提取API评估分数
        for api_response in report.get('api_responses', []):
            if 'api_eva' in api_response and api_response['api_eva']:
                eva = api_response['api_eva']
                api_name = api_response.get('api_name', 'unknown')
                
                performance_data = {
                    'method_type': method_type,
                    'overall_score': eva.get('overall_score', 0),
                    'precision': eva.get('precision', 0),
                    'recall': eva.get('recall', 0),
                    'penalty': eva.get('overgeneration_penalty', 0),
                    'report_id': report.get('report_number', 'unknown')
                }
                
                api_performance[api_name].append(performance_data)
    
    return dict(api_performance)

def analyze_api_performance(api_performance: Dict[str, List[Dict]]) -> Dict[str, Dict]:
    """分析各个API的性能"""
    analysis = {}
    
    for api_name, performances in api_performance.items():
        # 分离基线方法和增强方法的数据
        baseline_data = [p for p in performances if p['method_type'] == 'baseline']
        enhanced_data = [p for p in performances if p['method_type'] == 'rag_enhanced']
        
        analysis[api_name] = {
            'baseline': analyze_method_performance(baseline_data),
            'enhanced': analyze_method_performance(enhanced_data),
            'total_calls': len(performances),
            'baseline_calls': len(baseline_data),
            'enhanced_calls': len(enhanced_data)
        }
    
    return analysis

def analyze_method_performance(performances: List[Dict]) -> Dict:
    """分析单个方法的性能"""
    if not performances:
        return {
            'count': 0,
            'overall': {'mean': 0, 'median': 0, 'min': 0, 'max': 0, 'std': 0},
            'precision': {'mean': 0, 'median': 0, 'min': 0, 'max': 0, 'std': 0},
            'recall': {'mean': 0, 'median': 0, 'min': 0, 'max': 0, 'std': 0},
            'penalty': {'mean': 0, 'median': 0, 'min': 0, 'max': 0, 'std': 0}
        }
    
    # 提取各项指标
    overall_scores = [p['overall_score'] for p in performances]
    precision_scores = [p['precision'] for p in performances]
    recall_scores = [p['recall'] for p in performances]
    penalty_scores = [p['penalty'] for p in performances]
    
    return {
        'count': len(performances),
        'overall': calculate_stats(overall_scores),
        'precision': calculate_stats(precision_scores),
        'recall': calculate_stats(recall_scores),
        'penalty': calculate_stats(penalty_scores)
    }

def calculate_stats(values: List[float]) -> Dict:
    """计算统计信息"""
    if not values:
        return {'mean': 0, 'median': 0, 'min': 0, 'max': 0, 'std': 0}
    
    return {
        'mean': round(statistics.mean(values), 2),
        'median': round(statistics.median(values), 2),
        'min': round(min(values), 2),
        'max': round(max(values), 2),
        'std': round(statistics.stdev(values), 2) if len(values) > 1 else 0
    }

def generate_api_analysis_report(analysis: Dict[str, Dict]) -> str:
    """生成API分析报告"""
    report = []
    report.append("=" * 80)
    report.append("🔌 各API性能分析报告")
    report.append("=" * 80)
    report.append("")
    
    # 总体统计
    total_apis = len(analysis)
    report.append(f"📊 总体统计:")
    report.append(f"  参与评估的API数量: {total_apis}")
    report.append(f"  评估方法: 基线方法 + 增强方法")
    report.append("")
    
    # 各API详细分析
    for api_name, api_data in analysis.items():
        report.append(f"🔌 {api_name.upper()} API 性能分析:")
        report.append("-" * 60)
        
        # 调用统计
        report.append(f"  调用统计:")
        report.append(f"    总调用次数: {api_data['total_calls']}")
        report.append(f"    基线方法调用: {api_data['baseline_calls']}")
        report.append(f"    增强方法调用: {api_data['enhanced_calls']}")
        report.append("")
        
        # 基线方法性能
        baseline = api_data['baseline']
        if baseline['count'] > 0:
            report.append(f"  基线方法性能:")
            report.append(f"    整体评分: {baseline['overall']['mean']} (范围: {baseline['overall']['min']}-{baseline['overall']['max']})")
            report.append(f"    精确率: {baseline['precision']['mean']}% (范围: {baseline['precision']['min']}-{baseline['precision']['max']}%)")
            report.append(f"    召回率: {baseline['recall']['mean']}% (范围: {baseline['recall']['min']}-{baseline['recall']['max']}%)")
            report.append(f"    过度生成惩罚: {baseline['penalty']['mean']}%")
            report.append("")
        
        # 增强方法性能
        enhanced = api_data['enhanced']
        if enhanced['count'] > 0:
            report.append(f"  增强方法性能:")
            report.append(f"    整体评分: {enhanced['overall']['mean']} (范围: {enhanced['overall']['min']}-{enhanced['overall']['max']})")
            report.append(f"    精确率: {enhanced['precision']['mean']}% (范围: {enhanced['precision']['min']}-{enhanced['precision']['max']}%)")
            report.append(f"    召回率: {enhanced['recall']['mean']}% (范围: {enhanced['recall']['min']}-{enhanced['recall']['max']}%)")
            report.append(f"    过度生成惩罚: {enhanced['penalty']['mean']}%")
            report.append("")
        
        # 方法对比
        if baseline['count'] > 0 and enhanced['count'] > 0:
            report.append(f"  方法对比:")
            overall_diff = enhanced['overall']['mean'] - baseline['overall']['mean']
            precision_diff = enhanced['precision']['mean'] - baseline['precision']['mean']
            recall_diff = enhanced['recall']['mean'] - baseline['recall']['mean']
            
            report.append(f"    整体评分差异: {overall_diff:+.2f} ({overall_diff/baseline['overall']['mean']*100:+.1f}%)")
            report.append(f"    精确率差异: {precision_diff:+.2f}% ({precision_diff/baseline['precision']['mean']*100:+.1f}%)")
            report.append(f"    召回率差异: {recall_diff:+.2f}% ({recall_diff/baseline['recall']['mean']*100:+.1f}%)")
            
            if overall_diff > 0:
                report.append(f"    🟢 增强方法在整体评分上优于基线方法")
            elif overall_diff < 0:
                report.append(f"    🔴 基线方法在整体评分上优于增强方法")
            else:
                report.append(f"    🟡 两种方法在整体评分上表现相当")
            report.append("")
        
        report.append("")
    
    # API排名
    report.append("🏆 API性能排名:")
    report.append("-" * 60)
    
    # 按基线方法整体评分排名
    baseline_rankings = []
    for api_name, api_data in analysis.items():
        if api_data['baseline']['count'] > 0:
            baseline_rankings.append((api_name, api_data['baseline']['overall']['mean']))
    
    baseline_rankings.sort(key=lambda x: x[1], reverse=True)
    
    report.append("  基线方法排名 (按整体评分):")
    for i, (api_name, score) in enumerate(baseline_rankings, 1):
        report.append(f"    {i}. {api_name.upper()}: {score}分")
    report.append("")
    
    # 按增强方法整体评分排名
    enhanced_rankings = []
    for api_name, api_data in analysis.items():
        if api_data['enhanced']['count'] > 0:
            enhanced_rankings.append((api_name, api_data['enhanced']['overall']['mean']))
    
    enhanced_rankings.sort(key=lambda x: x[1], reverse=True)
    
    report.append("  增强方法排名 (按整体评分):")
    for i, (api_name, score) in enumerate(enhanced_rankings, 1):
        report.append(f"    {i}. {api_name.upper()}: {score}分")
    report.append("")
    
    # 改进建议
    report.append("💡 API优化建议:")
    report.append("-" * 60)
    
    # 找出表现最好的API
    if baseline_rankings:
        best_baseline_api = baseline_rankings[0]
        report.append(f"  最佳基线方法API: {best_baseline_api[0].upper()} ({best_baseline_api[1]}分)")
        report.append(f"    - 可作为其他API的优化参考")
        report.append(f"    - 分析其成功策略，推广到其他API")
    
    if enhanced_rankings:
        best_enhanced_api = enhanced_rankings[0]
        report.append(f"  最佳增强方法API: {best_enhanced_api[0].upper()} ({best_enhanced_api[1]}分)")
        report.append(f"    - 其RAG集成策略值得学习")
        report.append(f"    - 可作为增强方法的标杆")
    
    report.append("")
    report.append("  通用优化建议:")
    report.append("    - 对于表现较差的API，重点优化其提示词设计")
    report.append("    - 分析高评分API的成功模式，推广最佳实践")
    report.append("    - 建立API性能监控机制，持续跟踪改进效果")
    
    report.append("")
    report.append("=" * 80)
    
    return "\n".join(report)

def main():
    """主函数"""
    results_dir = "results_4050_4080"
    
    if not os.path.exists(results_dir):
        print(f"结果目录不存在: {results_dir}")
        return
    
    # 查找所有user_format文件
    user_format_files = glob.glob(f"{results_dir}/**/*user_format*.json", recursive=True)
    
    if not user_format_files:
        print(f"在 {results_dir} 中未找到user_format文件")
        return
    
    print(f"找到 {len(user_format_files)} 个user_format文件")
    
    # 合并所有API性能数据
    all_api_performance = defaultdict(list)
    
    for file_path in user_format_files:
        print(f"分析文件: {file_path}")
        api_performance = extract_api_performance(file_path)
        
        # 合并数据
        for api_name, performances in api_performance.items():
            all_api_performance[api_name].extend(performances)
    
    # 分析API性能
    analysis = analyze_api_performance(dict(all_api_performance))
    
    # 生成报告
    report = generate_api_analysis_report(analysis)
    
    # 保存报告
    output_file = f"{results_dir}/api_performance_analysis.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\nAPI性能分析报告已保存到: {output_file}")
    print("\n" + "="*80)
    print("🔌 API性能分析报告预览:")
    print("="*80)
    print(report)

if __name__ == "__main__":
    main()
