#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG评估系统 - 报告级症状聚合处理
将同一报告的所有症状聚合处理，提取统一的相关器官和解剖位置
"""

import os
import sys
import json
import argparse
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

# 添加src目录到Python路径
sys.path.append(str(Path(__file__).parent.parent / "src"))

from config_loader import ConfigLoader
from data_loader import DataLoader
from api_manager import APIManager
from evaluator import Evaluator
from utils.logger import ReportLogger


class ReportLevelWorkflow:
    """报告级症状聚合处理工作流程类"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """初始化报告级工作流程"""
        self.config = ConfigLoader(config_path)
        self.data_loader = DataLoader()
        self.api_manager = APIManager()
        self.evaluator = Evaluator()
        self.logger = ReportLogger()
        
        # 创建结果目录
        self.results_dir = Path("results_report_level")
        self.results_dir.mkdir(exist_ok=True)
        
        # 创建日志目录
        self.logs_dir = Path("logs")
        self.logs_dir.mkdir(exist_ok=True)
    
    def aggregate_report_symptoms(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """聚合报告中的所有症状"""
        symptoms = report_data.get('symptoms', [])
        
        # 收集所有症状文本
        all_symptoms = []
        for symptom_item in symptoms:
            symptom_text = symptom_item.get('symptom_text', '')
            if symptom_text.strip():
                all_symptoms.append(symptom_text)
        
        # 收集所有期望的器官和位置信息
        expected_organs_map = {}
        all_expected_locations = []
        
        for symptom_item in symptoms:
            expected_results = symptom_item.get('expected_results', [])
            for expected in expected_results:
                organ_name = expected.get('organName')
                locations = expected.get('anatomicalLocations', [])
                
                if organ_name:
                    if organ_name not in expected_organs_map:
                        expected_organs_map[organ_name] = set()
                    expected_organs_map[organ_name].update(locations)
                    all_expected_locations.extend(locations)
        
        # 转换为标准格式
        expected_organs_list = []
        for organ_name, locations in expected_organs_map.items():
            expected_organs_list.append({
                'organName': organ_name,
                'anatomicalLocations': sorted(list(locations))
            })
        
        return {
            'report_id': report_data.get('report_id'),
            'aggregated_symptoms': all_symptoms,
            'aggregated_text': '; '.join(all_symptoms),
            'expected_organs': expected_organs_list,
            'all_expected_locations': sorted(list(set(all_expected_locations))),
            'symptom_count': len(symptoms)
        }
    
    def process_report_aggregate(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """使用聚合症状处理整个报告"""
        report_id = report_data.get('report_id', 'unknown')
        
        print(f"\n正在处理报告 {report_id}，聚合处理 {len(report_data.get('symptoms', []))} 个症状")
        
        # 聚合症状
        aggregated_data = self.aggregate_report_symptoms(report_data)
        
        report_results = {
            'report_id': report_id,
            'timestamp': datetime.now().isoformat(),
            'processing_mode': 'aggregate',
            'aggregated_symptoms': aggregated_data['aggregated_text'],
            'symptom_count': aggregated_data['symptom_count'],
            'expected_organs': aggregated_data['expected_organs'],
            'api_responses': {}
        }
        
        # 使用聚合症状调用API
        try:
            # 加载系统提示词
            system_prompt_path = Path("prompt/system_prompt_report_level.txt")
            if system_prompt_path.exists():
                with open(system_prompt_path, 'r', encoding='utf-8') as f:
                    system_prompt = f.read().strip()
            else:
                system_prompt = """你是一个医学专家，请根据以下病人的所有症状，识别需要检查的相关器官和解剖位置。
                
要求：
1. 基于所有症状的综合分析，识别最相关的器官
2. 为每个器官指定具体的解剖检查位置
3. 考虑症状之间的关联性
4. 返回JSON格式：{"organ": "器官名称", "anatomical_locations": ["位置1", "位置2"]}"""
            
            # 创建症状数据对象用于API调用
            symptom_data = {
                'symptom_text': aggregated_data['aggregated_text'],
                'expected_results': aggregated_data['expected_organs']
            }
            
            api_result = self.api_manager.process_symptom(symptom_data, system_prompt)
            
            # 处理每个API的响应
            for api_name, response in api_result.items():
                api_response_data = {
                    'response': response.get('response', ''),
                    'parsed_data': response.get('parsed_data', {}),
                    'organ_name': response.get('organ_name', ''),
                    'anatomical_locations': response.get('anatomical_locations', [])
                }
                
                # 评估这个API的响应
                if response.get('success') and response.get('parsed_data'):
                    evaluation = self.evaluator.evaluate_single_response(
                        api_response=response,
                        expected_results=aggregated_data['expected_organs']
                    )
                    api_response_data['evaluation'] = evaluation
                else:
                    api_response_data['evaluation'] = {
                        'overall_score': 0.0,
                        'precision': 0.0,
                        'recall': 0.0,
                        'overgeneration_penalty': 0.0,
                        'detailed_analysis': 'API调用失败或无有效数据'
                    }
                
                report_results['api_responses'][api_name] = api_response_data
                
        except Exception as e:
            error_msg = f"处理报告 {report_id} 时出错: {str(e)}"
            print(f"    {error_msg}")
            report_results['error'] = str(e)
        
        return report_results
    
    def save_results(self, report_results: Dict[str, Any]) -> str:
        """保存报告级聚合处理结果"""
        report_id = report_results['report_id']
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 保存详细结果
        detailed_filename = f"report_{report_id}_aggregate_evaluation_{timestamp}.json"
        detailed_path = self.results_dir / detailed_filename
        
        with open(detailed_path, 'w', encoding='utf-8') as f:
            json.dump(report_results, f, ensure_ascii=False, indent=2)
        
        # 保存标准化结果
        standardized_results = self._standardize_results(report_results)
        standardized_filename = f"report_{report_id}_aggregate_standardized_{timestamp}.json"
        standardized_path = self.results_dir / standardized_filename
        
        with open(standardized_path, 'w', encoding='utf-8') as f:
            json.dump(standardized_results, f, ensure_ascii=False, indent=2)
        
        print(f"结果已保存到:")
        print(f"  详细结果: {detailed_path}")
        print(f"  标准化结果: {standardized_path}")
        
        return str(detailed_path)
    
    def _standardize_results(self, report_results: Dict[str, Any]) -> Dict[str, Any]:
        """标准化报告级结果格式"""
        standardized = {
            'report_number': report_results['report_id'],
            'timestamp': report_results['timestamp'],
            'processing_mode': report_results['processing_mode'],
            'aggregated_symptoms': report_results['aggregated_symptoms'],
            'symptom_count': report_results['symptom_count'],
            'expected_organs': report_results['expected_organs'],
            'api_responses': []
        }
        
        # 标准化每个API的响应
        api_number = 1
        for api_name, response in report_results['api_responses'].items():
            api_response_data = {
                'api_number': api_number,
                'api_name': api_name,
                'api_response': {
                    'organ': response.get('organ_name', ''),
                    'a_position': ', '.join(response.get('anatomical_locations', []))
                },
                'api_eva': response.get('evaluation', {})
            }
            standardized['api_responses'].append(api_response_data)
            api_number += 1
        
        return standardized
    
    def generate_summary_report(self, all_results: List[Dict[str, Any]]) -> str:
        """生成报告级汇总报告"""
        if not all_results:
            return ""
        
        summary = {
            'total_reports': len(all_results),
            'processing_mode': 'aggregate',
            'timestamp': datetime.now().isoformat(),
            'overall_metrics': {
                'average_precision': 0,
                'average_recall': 0,
                'average_f1_score': 0,
                'average_overgeneration_penalty': 0
            },
            'report_summaries': []
        }
        
        total_precision = 0
        total_recall = 0
        total_f1 = 0
        total_overgeneration = 0
        valid_reports = 0
        
        for result in all_results:
            report_summary = {
                'report_id': result['report_id'],
                'symptom_count': result['symptom_count'],
                'aggregated_symptoms': result['aggregated_symptoms'],
                'metrics': {}
            }
            
            # 计算该报告的平均指标
            total_scores = []
            total_precision_list = []
            total_recall_list = []
            total_overgeneration_list = []
            
            for api_name, response in result['api_responses'].items():
                evaluation = response.get('evaluation', {})
                if evaluation and 'precision' in evaluation:
                    total_scores.append(evaluation.get('overall_score', 0))
                    total_precision_list.append(evaluation.get('precision', 0))
                    total_recall_list.append(evaluation.get('recall', 0))
                    total_overgeneration_list.append(evaluation.get('overgeneration_penalty', 0))
            
            if total_scores:
                report_summary['metrics'] = {
                    'precision': sum(total_precision_list) / len(total_precision_list),
                    'recall': sum(total_recall_list) / len(total_recall_list),
                    'f1_score': sum(total_scores) / len(total_scores),
                    'overgeneration_penalty': sum(total_overgeneration_list) / len(total_overgeneration_list)
                }
                
                total_precision += report_summary['metrics']['precision']
                total_recall += report_summary['metrics']['recall']
                total_f1 += report_summary['metrics']['f1_score']
                total_overgeneration += report_summary['metrics']['overgeneration_penalty']
                valid_reports += 1
            
            summary['report_summaries'].append(report_summary)
        
        # 计算总体平均指标
        if valid_reports > 0:
            summary['overall_metrics'] = {
                'average_precision': total_precision / valid_reports,
                'average_recall': total_recall / valid_reports,
                'average_f1_score': total_f1 / valid_reports,
                'average_overgeneration_penalty': total_overgeneration / valid_reports
            }
        
        # 保存汇总报告
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        summary_filename = f"summary_report_aggregate_{timestamp}.json"
        summary_path = self.results_dir / summary_filename
        
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        print(f"\n报告级汇总报告已保存到: {summary_path}")
        return str(summary_path)
    
    def run_workflow(self, start_id: int = None, end_id: int = None, max_files: int = None):
        """运行报告级聚合工作流程"""
        print("=== RAG评估系统 - 报告级聚合处理版本 ===")
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # 测试API连接
            print("\n1. 测试API连接...")
            if not self.api_manager.initialize_clients(self.config.config):
                print("API客户端初始化失败，请检查配置")
                return
            
            if not self.api_manager.test_connectivity():
                print("API连接测试失败，请检查配置")
                return
            
            # 加载数据
            print("\n2. 加载数据...")
            data_path = Path(self.config.config.get('data_path', 'test_set'))
            
            if start_id is not None and end_id is not None:
                file_paths = self.data_loader.get_reports_by_id_range(data_path, start_id, end_id)
                print(f"找到 {len(file_paths)} 个文件 (ID范围: {start_id}-{end_id})")
            else:
                file_paths = self.data_loader.get_diagnostic_files(data_path)
                print(f"找到 {len(file_paths)} 个文件")
            
            # 加载每个文件的数据
            reports = []
            for file_path in file_paths:
                report_data = self.data_loader.load_report_data(file_path)
                if 'error' not in report_data:
                    reports.append(report_data)
            
            print(f"成功加载 {len(reports)} 个报告")
            
            if max_files:
                reports = reports[:max_files]
                print(f"限制处理文件数量: {max_files}")
            
            if not reports:
                print("没有找到可处理的报告")
                return
            
            # 处理报告
            print(f"\n3. 开始聚合处理 {len(reports)} 个报告...")
            all_results = []
            
            for i, report in enumerate(reports, 1):
                print(f"\n进度: {i}/{len(reports)}")
                
                try:
                    result = self.process_report_aggregate(report)
                    all_results.append(result)
                    
                    # 保存单个报告结果
                    self.save_results(result)
                    
                except Exception as e:
                    print(f"处理报告 {report.get('report_id', 'unknown')} 时出错: {str(e)}")
                    continue
            
            # 生成汇总报告
            if all_results:
                print(f"\n4. 生成汇总报告...")
                self.generate_summary_report(all_results)
            
            print(f"\n=== 报告级聚合处理完成 ===")
            print(f"成功处理: {len(all_results)} 个报告")
            print(f"结果保存在: {self.results_dir}")
            
        except Exception as e:
            print(f"工作流程执行出错: {str(e)}")
            logging.error(f"工作流程执行出错: {str(e)}", exc_info=True)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="RAG评估系统 - 报告级聚合处理版本")
    parser.add_argument("--start_id", type=int, help="开始报告ID")
    parser.add_argument("--end_id", type=int, help="结束报告ID")
    parser.add_argument("--max_files", type=int, help="最大处理文件数量")
    parser.add_argument("--config", default="config/config.yaml", help="配置文件路径")
    
    args = parser.parse_args()
    
    # 创建并运行工作流程
    workflow = ReportLevelWorkflow(args.config)
    workflow.run_workflow(
        start_id=args.start_id,
        end_id=args.end_id,
        max_files=args.max_files
    )


if __name__ == "__main__":
    main()