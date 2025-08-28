#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
评分数据分析脚本
分析4050-4080范围内所有报告的基线方法和增强方法的评分对比
"""

import json
import os
import glob
from typing import Dict, List, Tuple
import statistics

def load_json_file(file_path: str) -> dict:
    """加载JSON文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"加载文件失败 {file_path}: {e}")
        return {}

def extract_scores_from_file(file_path: str) -> Dict[str, List[float]]:
    """从文件中提取评分数据"""
    data = load_json_file(file_path)
    if not data:
        return {}
    
    scores = {
        'baseline': {'overall': [], 'precision': [], 'recall': [], 'penalty': []},
        'rag_enhanced': {'overall': [], 'precision': [], 'recall': [], 'penalty': []}
    }
    
    for report in data:
        if 'method' not in report:
            continue
            
        method = report['method']
        if 'baseline' in method:
            target = 'baseline'
        elif 'rag_enhanced' in method:
            target = 'rag_enhanced'
        else:
            continue
            
        # 提取API评估分数
        for api_response in report.get('api_responses', []):
            if 'api_eva' in api_response and api_response['api_eva']:
                eva = api_response['api_eva']
                scores[target]['overall'].append(eva.get('overall_score', 0))
                scores[target]['precision'].append(eva.get('precision', 0))
                scores[target]['recall'].append(eva.get('recall', 0))
                scores[target]['penalty'].append(eva.get('overgeneration_penalty', 0))
    
    return scores

def analyze_scores(scores: Dict[str, List[float]]) -> Dict[str, Dict[str, float]]:
    """分析评分数据，计算统计信息"""
    analysis = {}
    
    for method, metrics in scores.items():
        analysis[method] = {}
        for metric_name, values in metrics.items():
            if values:
                analysis[method][metric_name] = {
                    'count': len(values),
                    'mean': round(statistics.mean(values), 2),
                    'median': round(statistics.median(values), 2),
                    'min': round(min(values), 2),
                    'max': round(max(values), 2),
                    'std': round(statistics.stdev(values), 2) if len(values) > 1 else 0
                }
            else:
                analysis[method][metric_name] = {
                    'count': 0,
                    'mean': 0,
                    'median': 0,
                    'min': 0,
                    'max': 0,
                    'std': 0
                }
    
    return analysis

def generate_comparison_report(analysis: Dict[str, Dict[str, float]]) -> str:
    """生成对比报告"""
    report = []
    report.append("=" * 80)
    report.append("🧠 RAG_Evaluate_WholeReport 症状聚合系统评分对比分析报告")
    report.append("=" * 80)
    report.append(f"分析范围: 报告4050-4080")
    report.append(f"分析时间: {os.popen('date').read().strip()}")
    report.append("")
    
    # 基线方法统计
    report.append("📊 基线方法 (症状聚合基线方法) 评分统计:")
    report.append("-" * 60)
    baseline = analysis.get('baseline', {})
    for metric, stats in baseline.items():
        if stats['count'] > 0:
            report.append(f"  {metric.upper()}:")
            report.append(f"    数量: {stats['count']}")
            report.append(f"    平均分: {stats['mean']}")
            report.append(f"    中位数: {stats['median']}")
            report.append(f"    范围: {stats['min']} - {stats['max']}")
            report.append(f"    标准差: {stats['std']}")
            report.append("")
    
    # 增强方法统计
    report.append("📊 增强方法 (增强症状聚合方法) 评分统计:")
    report.append("-" * 60)
    enhanced = analysis.get('rag_enhanced', {})
    for metric, stats in enhanced.items():
        if stats['count'] > 0:
            report.append(f"  {metric.upper()}:")
            report.append(f"    数量: {stats['count']}")
            report.append(f"    平均分: {stats['mean']}")
            report.append(f"    中位数: {stats['median']}")
            report.append(f"    范围: {stats['min']} - {stats['max']}")
            report.append(f"    标准差: {stats['std']}")
            report.append("")
    
    # 方法对比
    report.append("📈 方法对比分析:")
    report.append("-" * 60)
    
    if baseline.get('overall', {}).get('count', 0) > 0 and enhanced.get('overall', {}).get('count', 0) > 0:
        baseline_overall = baseline['overall']['mean']
        enhanced_overall = enhanced['overall']['mean']
        
        report.append(f"  整体评分对比:")
        report.append(f"    基线方法: {baseline_overall}")
        report.append(f"    增强方法: {enhanced_overall}")
        
        if enhanced_overall > baseline_overall:
            improvement = enhanced_overall - baseline_overall
            report.append(f"    增强方法提升: +{improvement:.2f} ({improvement/baseline_overall*100:.1f}%)")
        elif enhanced_overall < baseline_overall:
            decline = baseline_overall - enhanced_overall
            report.append(f"    增强方法下降: -{decline:.2f} ({decline/baseline_overall*100:.1f}%)")
        else:
            report.append("    两种方法评分相同")
        
        report.append("")
        
        # 精确率对比
        if baseline.get('precision', {}).get('count', 0) > 0 and enhanced.get('precision', {}).get('count', 0) > 0:
            baseline_precision = baseline['precision']['mean']
            enhanced_precision = enhanced['precision']['mean']
            report.append(f"  精确率对比:")
            report.append(f"    基线方法: {baseline_precision}")
            report.append(f"    增强方法: {enhanced_precision}")
            report.append("")
        
        # 召回率对比
        if baseline.get('recall', {}).get('count', 0) > 0 and enhanced.get('recall', {}).get('count', 0) > 0:
            baseline_recall = baseline['recall']['mean']
            enhanced_recall = enhanced['recall']['mean']
            report.append(f"  召回率对比:")
            report.append(f"    基线方法: {baseline_recall}")
            report.append(f"    增强方法: {enhanced_recall}")
            report.append("")
    
    # 总结
    report.append("💡 分析结论:")
    report.append("-" * 60)
    if baseline.get('overall', {}).get('count', 0) > 0 and enhanced.get('overall', {}).get('count', 0) > 0:
        baseline_overall = baseline['overall']['mean']
        enhanced_overall = enhanced['overall']['mean']
        
        if enhanced_overall > baseline_overall:
            report.append("  增强症状聚合方法在整体评分上优于基线方法")
        elif enhanced_overall < baseline_overall:
            report.append("  基线方法在整体评分上优于增强症状聚合方法")
        else:
            report.append("  两种方法在整体评分上表现相当")
        
        report.append("")
        report.append("  建议:")
        if enhanced_overall > baseline_overall:
            report.append("    - 继续使用增强症状聚合方法")
            report.append("    - 分析增强方法的优势，优化基线方法")
        elif enhanced_overall < baseline_overall:
            report.append("    - 分析增强方法的问题，改进RAG集成策略")
            report.append("    - 优化症状分割和知识检索逻辑")
        else:
            report.append("    - 两种方法各有优势，可根据具体需求选择")
            report.append("    - 进一步优化两种方法")
    
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
    
    # 合并所有评分数据
    all_scores = {
        'baseline': {'overall': [], 'precision': [], 'recall': [], 'penalty': []},
        'rag_enhanced': {'overall': [], 'precision': [], 'recall': [], 'penalty': []}
    }
    
    for file_path in user_format_files:
        print(f"分析文件: {file_path}")
        scores = extract_scores_from_file(file_path)
        
        # 合并评分数据
        for method in ['baseline', 'rag_enhanced']:
            for metric in ['overall', 'precision', 'recall', 'penalty']:
                if method in scores and metric in scores[method]:
                    all_scores[method][metric].extend(scores[method][metric])
    
    # 分析评分数据
    analysis = analyze_scores(all_scores)
    
    # 生成报告
    report = generate_comparison_report(analysis)
    
    # 保存报告
    output_file = f"{results_dir}/comprehensive_score_analysis.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n评分分析报告已保存到: {output_file}")
    print("\n" + "="*80)
    print("📊 评分分析报告预览:")
    print("="*80)
    print(report)

if __name__ == "__main__":
    main()
