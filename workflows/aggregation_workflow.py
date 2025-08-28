#!/usr/bin/env python3
"""
聚合工作流程
运行聚合方法：报告级聚合处理
"""

import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

# 添加项目根目录到路径
import sys
sys.path.append(str(Path(__file__).parent.parent))

from src.api_manager import APIManager
from src.data_loader import DataLoader
from src.evaluator import Evaluator
from src.aggregation_processor import AggregationProcessor
from src.aggregation_evaluator import AggregationEvaluator
from src.config_loader import ConfigLoader

class AggregationWorkflow:
    """聚合工作流程 - 运行聚合方法（报告级聚合处理）"""
    
    def __init__(self):
        self.config = None
        self.api_manager = None
        self.data_loader = None
        self.aggregation_processor = None
        self.aggregation_evaluator = None
        
    def initialize(self, config_path: str = None):
        """初始化所有组件"""
        print("🔧 初始化聚合工作流程...")
        
        # 加载配置
        self.config_loader = ConfigLoader(config_path) if config_path else ConfigLoader()
        self.config = self.config_loader.config
        
        # 初始化API管理器
        self.api_manager = APIManager()
        if not self.api_manager.initialize_clients(self.config):
            raise ValueError("API客户端初始化失败")
        
        # 测试API连通性
        if not self.api_manager.test_connectivity():
            print("⚠️  API连通性测试失败，但继续执行")
        
        # 初始化其他组件
        self.data_loader = DataLoader()
        self.evaluator = Evaluator()
        self.aggregation_processor = AggregationProcessor()
        self.aggregation_evaluator = AggregationEvaluator()
        
        # 初始化RAG搜索引擎
        self.search_engine = None
        try:
            import sys
            import os
            sys.path.append("/home/duojiechen/Projects/Rag_system/Rag_Build/src")
            from enhanced_search_engine import EnhancedMedicalSearchEngine
            default_index_dir = "/home/duojiechen/Projects/Rag_system/Rag_Build/enhanced_faiss_indexes"
            rag_index_dir = os.getenv("RAG_INDEX_DIR", default_index_dir)
            self.search_engine = EnhancedMedicalSearchEngine(rag_index_dir)
            print(f"✅ RAG搜索引擎已初始化: {rag_index_dir}")
        except Exception as e:
            print(f"⚠️ RAG搜索引擎初始化失败，将使用模拟搜索: {e}")
        
        print("✅ 聚合工作流程初始化完成")
    
    def process_single_report(self, file_path: Path) -> Dict[str, Any]:
        """处理单个报告文件 - 正确的4步流程"""
        try:
            print(f"\n📋 处理报告: {file_path.name}")
            
            # 加载报告数据
            report_data = self.data_loader.load_report_data(file_path)
            if 'error' in report_data:
                print(f"❌ 加载报告失败: {report_data['error']}")
                return None
            
            # 步骤1: 症状聚合 + Baseline结果（不使用RAG）
            print(f"🔄 步骤1: 聚合 {len(report_data['symptoms'])} 个症状并获取Baseline结果...")
            aggregated_data = self.aggregation_processor.aggregate_symptoms_for_report(report_data)
            baseline_results = self.aggregation_processor.predict_overall_organs_and_locations(
                aggregated_data, self.api_manager
            )
            
            # 评估Baseline结果
            print("📊 评估Baseline结果...")
            baseline_evaluation = self.evaluator.evaluate_report_responses({
                'report_id': report_data['report_id'],
                'total_symptoms': len(report_data['symptoms']),
                'valid_symptoms': len(report_data['symptoms']),
                'symptoms': [{
                    'symptom_id': 'aggregated_symptoms',
                    'symptom_text': aggregated_data['aggregated_symptoms'],
                    'expected_results': aggregated_data.get('all_expected_results', []),
                    'api_responses': baseline_results.get('api_responses', {})
                }]
            })
            
            # 将评估结果添加到API响应中
            for api_name, api_response in baseline_results.get('api_responses', {}).items():
                if api_name in baseline_evaluation.get('symptom_evaluations', [{}])[0].get('api_evaluations', {}):
                    api_response['evaluation'] = baseline_evaluation['symptom_evaluations'][0]['api_evaluations'][api_name]
            
            # 步骤2: 智能分割症状
            print("✂️ 步骤2: LLM智能分割聚合症状...")
            intelligent_symptoms = self.aggregation_processor.intelligently_split_symptoms(
                aggregated_data, self.api_manager
            )
            
            # 步骤3: RAG搜索
            print("🔍 步骤3: 基于智能分割症状进行RAG搜索...")
            rag_search_results = self.aggregation_processor.rag_search_for_split_symptoms(
                intelligent_symptoms, self.search_engine
            )
            
            # 步骤4: 使用RAG的LLM返回值
            print("🧠 步骤4: 基于RAG增强的LLM预测...")
            rag_enhanced_results = self.aggregation_processor.rag_enhanced_prediction(
                aggregated_data, rag_search_results, self.api_manager
            )
            
            # 评估RAG增强结果
            print("📊 评估RAG增强结果...")
            rag_evaluation = self.evaluator.evaluate_report_responses({
                'report_id': report_data['report_id'],
                'total_symptoms': len(report_data['symptoms']),
                'valid_symptoms': len(report_data['symptoms']),
                'symptoms': [{
                    'symptom_id': 'rag_enhanced_symptoms',
                    'symptom_text': aggregated_data['aggregated_symptoms'],
                    'expected_results': aggregated_data.get('all_expected_results', []),
                    'api_responses': rag_enhanced_results.get('api_responses', {})
                }]
            })
            
            # 将评估结果添加到API响应中
            for api_name, api_response in rag_enhanced_results.get('api_responses', {}).items():
                if api_name in rag_evaluation.get('symptom_evaluations', [{}])[0].get('api_evaluations', {}):
                    api_response['evaluation'] = rag_evaluation['symptom_evaluations'][0]['api_evaluations'][api_name]
            
            # 整合所有结果 - 按照您要求的格式
            comprehensive_result = {
                'report_id': report_data['report_id'],
                'file_path': str(file_path),
                'original_symptoms_count': len(report_data['symptoms']),
                
                # 1. Baseline结果
                'baseline': {
                    'aggregated_symptoms': aggregated_data['aggregated_symptoms'],
                    'expected_results': aggregated_data.get('all_expected_results', []),
                    'api_responses': baseline_results.get('api_responses', {}),
                    'evaluation': baseline_evaluation
                },
                
                # 2. RAG搜索输出
                'rag_search': {
                    'split_symptoms': intelligent_symptoms,
                    'search_results': rag_search_results
                },
                
                # 3. 使用RAG的LLM返回值
                'rag_enhanced': {
                    'api_responses': rag_enhanced_results.get('api_responses', {}),
                    'evaluation': rag_evaluation
                },
                
                # 4. 分数对比
                'comparison': {
                    'baseline_score': baseline_evaluation.get('summary', {}).get('average_overall_score', 0),
                    'rag_enhanced_score': rag_evaluation.get('summary', {}).get('average_overall_score', 0),
                    'improvement': rag_evaluation.get('summary', {}).get('average_overall_score', 0) - baseline_evaluation.get('summary', {}).get('average_overall_score', 0)
                },
                
                'processing_timestamp': datetime.now().isoformat()
            }
            
            return comprehensive_result
            
        except Exception as e:
            print(f"❌ 处理报告 {file_path.name} 时出错: {e}")
            return None
    
    def run_aggregation_workflow(self, data_path: str, output_dir: str, 
                               start_id: int = None, end_id: int = None, 
                               max_files: int = None):
        """运行聚合工作流程"""
        print("🚀 开始聚合工作流程（报告级聚合处理）...")
        
        # 创建输出目录
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 获取报告文件
        data_path = Path(data_path)
        report_files = self.data_loader.get_reports_by_id_range(
            data_path, start_id, end_id, max_files
        )
        
        if not report_files:
            print("❌ 没有找到符合条件的报告文件")
            return
        
        print(f"📁 找到 {len(report_files)} 个报告文件")
        
        # 处理每个报告
        processed_reports = []
        
        for i, file_path in enumerate(report_files, 1):
            print(f"\n进度: {i}/{len(report_files)}")
            
            result = self.process_single_report(file_path)
            if result:
                processed_reports.append(result)
                
                # 保存综合结果
                self._save_report_results(result, output_path)
        
        # 生成汇总报告
        if processed_reports:
            self._generate_summary_report(processed_reports, output_path)
        
        print(f"\n🎉 聚合工作流程完成！成功处理 {len(processed_reports)} 个报告")
    
    def _save_report_results(self, result: Dict[str, Any], output_dir: Path):
        """保存报告结果 - 创建与原系统一致的目录结构"""
        report_id = result['report_id']
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 创建分层目录结构
        baseline_dir = output_dir / "baseline_results"
        rag_search_dir = output_dir / "rag_search_output"
        results_of_apis_dir = output_dir / "results_of_apis"
        
        baseline_dir.mkdir(exist_ok=True)
        rag_search_dir.mkdir(exist_ok=True)
        results_of_apis_dir.mkdir(exist_ok=True)
        
        # 1. 保存详细结果
        detailed_file = output_dir / f"report_{report_id}_comprehensive_{timestamp}.json"
        with open(detailed_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        # 2. 保存标准化结果（参考原始格式）
        standardized_results = self._standardize_comprehensive_results(result)
        standardized_file = output_dir / f"report_{report_id}_evaluation_standardized_{timestamp}.json"
        with open(standardized_file, 'w', encoding='utf-8') as f:
            json.dump(standardized_results, f, ensure_ascii=False, indent=2)
        
        # 3. 保存用户期望格式
        user_format_results = self._generate_user_format_results(result)
        user_format_file = output_dir / f"report_{report_id}_user_format_{timestamp}.json"
        with open(user_format_file, 'w', encoding='utf-8') as f:
            json.dump(user_format_results, f, ensure_ascii=False, indent=2)
        
        # 4. 保存RAG搜索输出（与原系统一致）
        if 'rag_search' in result and 'search_results' in result['rag_search']:
            rag_output = result['rag_search']['search_results'].get('rag_search_output', [])
            if rag_output:
                # 保存pretty格式
                rag_pretty_file = rag_search_dir / f"report_{report_id}_ragoutcome:{timestamp}_pretty.json"
                with open(rag_pretty_file, 'w', encoding='utf-8') as f:
                    json.dump(rag_output, f, ensure_ascii=False, indent=2)
                
                # 保存JSONL格式
                rag_jsonl_file = rag_search_dir / f"report_{report_id}_ragoutcome:{timestamp}.jsonl"
                with open(rag_jsonl_file, 'w', encoding='utf-8') as f:
                    for item in rag_output:
                        f.write(json.dumps(item, ensure_ascii=False) + '\n')
                
                print(f"  RAG搜索输出: {rag_pretty_file}")
                print(f"  RAG搜索JSONL: {rag_jsonl_file}")
        
        # 5. 保存基线结果（与原系统一致）
        baseline_file = baseline_dir / f"report_diagnostic_{report_id}_evaluation_{timestamp}.json"
        baseline_data = {
            'report_id': report_id,
            'timestamp': result['processing_timestamp'],
            'symptoms': self._format_baseline_symptoms(result)
        }
        with open(baseline_file, 'w', encoding='utf-8') as f:
            json.dump(baseline_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 报告 {report_id} 聚合处理完成，结果已保存")
        print(f"  详细结果: {detailed_file}")
        print(f"  标准化结果: {standardized_file}")
        print(f"  用户格式: {user_format_file}")
        print(f"  基线结果: {baseline_file}")
    
    def _standardize_comprehensive_results(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """标准化综合结果格式"""
        return {
            'report_number': result['report_id'],
            'timestamp': result['processing_timestamp'],
            'baseline_method': {
                'aggregated_symptoms': result['baseline']['aggregated_symptoms'],
                'expected_results': result['baseline']['expected_results'],
                'api_responses': self._format_api_responses(result['baseline']['api_responses']),
                'evaluation_summary': result['baseline']['evaluation']['summary']
            },
            'rag_enhanced_method': {
                'split_symptoms': result['rag_search']['split_symptoms'],
                'rag_search_results': result['rag_search']['search_results'],
                'api_responses': self._format_api_responses(result['rag_enhanced']['api_responses']),
                'evaluation_summary': result['rag_enhanced']['evaluation']['summary']
            },
            'comparison': result['comparison']
        }
    
    def _generate_user_format_results(self, result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成用户期望的扁平化格式"""
        user_format_list = []
        
        # Baseline方法结果
        baseline_entry = {
            'report_number': result['report_id'],
            'method': 'baseline_aggregation',
            'method_name': '症状聚合基线方法',
            'aggregated_symptoms': result['baseline']['aggregated_symptoms'],
            'expected_results': self._process_expected_organs(result['baseline']['expected_results']),
            'api_responses': self._format_user_api_responses(result['baseline']['api_responses']),
            'evaluation_summary': result['baseline']['evaluation']['summary']
        }
        user_format_list.append(baseline_entry)
        
        # RAG增强方法结果
        rag_entry = {
            'report_number': result['report_id'],
            'method': 'rag_enhanced_aggregation',
            'method_name': '增强症状聚合方法',
            'aggregated_symptoms': result['baseline']['aggregated_symptoms'],
            'split_symptoms': result['rag_search']['split_symptoms'],
            'rag_search_results': result['rag_search']['search_results'],
            'expected_results': self._process_expected_organs(result['baseline']['expected_results']),
            'api_responses': self._format_user_api_responses(result['rag_enhanced']['api_responses']),
            'evaluation_summary': result['rag_enhanced']['evaluation']['summary']
        }
        user_format_list.append(rag_entry)
        
        return user_format_list
    
    def _format_baseline_symptoms(self, result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """格式化基线症状数据（与原系统一致）"""
        symptoms = []
        
        # 从智能分割的症状中提取
        if 'rag_search' in result and 'split_symptoms' in result['rag_search']:
            split_symptoms = result['rag_search']['split_symptoms'].get('parsed_data', {}).get('full_response', {}).get('split_symptoms', [])
            
            for i, split_symptom in enumerate(split_symptoms):
                symptom_id = f"{result['report_id']}_symptom_{i}"
                diagnosis = split_symptom.get('symptom_text', '')
                
                # 从原始期望结果中查找对应的器官
                expected_organs = []
                if 'baseline' in result and 'expected_results' in result['baseline']:
                    for expected in result['baseline']['expected_results']:
                        if expected.get('organName'):
                            expected_organs.append({
                                'organName': expected['organName'],
                                'anatomicalLocations': expected.get('anatomicalLocations', [])
                            })
                
                # 构建症状数据
                symptom_data = {
                    'symptom_id': symptom_id,
                    'diagnosis': diagnosis,
                    'expected_organs': expected_organs,
                    'api_responses': {}
                }
                
                # 添加API响应
                if 'baseline' in result and 'api_responses' in result['baseline']:
                    for api_name, api_response in result['baseline']['api_responses'].items():
                        if api_response.get('success'):
                            symptom_data['api_responses'][api_name] = {
                                'response': api_response.get('response', ''),
                                'parsed_data': api_response.get('parsed_data', {}),
                                'organ_name': api_response.get('organ_name', ''),
                                'anatomical_locations': api_response.get('anatomical_locations', []),
                                'evaluation': {
                                    'overall_score': 0.0,  # 这里需要计算
                                    'precision': 0.0,
                                    'recall': 0.0,
                                    'overgeneration_penalty': 0.0,
                                    'detailed_analysis': ''
                                }
                            }
                
                symptoms.append(symptom_data)
        
        return symptoms
    
    def _format_api_responses(self, api_responses: Dict[str, Any]) -> List[Dict[str, Any]]:
        """格式化API响应"""
        formatted_responses = []
        api_number = 1
        
        for api_name, response in api_responses.items():
            formatted_response = {
                'api_number': api_number,
                'api_name': api_name,
                'success': response.get('success', False),
                'organ_name': response.get('organ_name', ''),
                'anatomical_locations': response.get('anatomical_locations', []),
                'usage': response.get('usage', {})
            }
            if not response.get('success'):
                formatted_response['error'] = response.get('error', '')
            formatted_responses.append(formatted_response)
            api_number += 1
        
        return formatted_responses
    
    def _format_user_api_responses(self, api_responses: Dict[str, Any]) -> List[Dict[str, Any]]:
        """格式化用户期望的API响应格式"""
        formatted_responses = []
        api_number = 1
        
        for api_name, response in api_responses.items():
            formatted_response = {
                'api_number': api_number,
                'api_name': api_name,
                'api_response': {
                    'organ': response.get('organ_name', ''),
                    'a_position': ', '.join(response.get('anatomical_locations', []))
                },
                'api_eva': {
                    'overall_score': response.get('evaluation', {}).get('overall_score', 0.0),
                    'precision': response.get('evaluation', {}).get('precision', 0.0),
                    'recall': response.get('evaluation', {}).get('recall', 0.0),
                    'overgeneration_penalty': response.get('evaluation', {}).get('overgeneration_penalty', 0.0)
                }
            }
            formatted_responses.append(formatted_response)
            api_number += 1
        
        return formatted_responses
    
    def _process_expected_organs(self, expected_results: List[Dict[str, Any]]) -> Dict[str, str]:
        """处理期望器官数据"""
        if not expected_results:
            return {'organ': '', 'a_position': ''}
        
        # 按器官名称分组
        organ_groups = {}
        
        for expected in expected_results:
            if isinstance(expected, dict):
                organ_name = expected.get('organName', '')
                locations = expected.get('anatomicalLocations', [])
                
                if organ_name:
                    if organ_name not in organ_groups:
                        organ_groups[organ_name] = set()
                    organ_groups[organ_name].update(locations)
        
        # 构建结果
        unique_organs = list(organ_groups.keys())
        all_unique_locations = []
        
        for organ, locations in organ_groups.items():
            all_unique_locations.extend(list(locations))
        
        # 去重位置信息
        unique_locations = list(set(all_unique_locations))
        
        return {
            'organ': ', '.join(sorted(unique_organs)),
            'a_position': ', '.join(sorted(unique_locations))
        }
    
    def _generate_summary_report(self, processed_reports: List[Dict[str, Any]], output_dir: Path):
        """生成汇总报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        summary_file = output_dir / f"aggregation_summary_report_{timestamp}.json"
        
        summary = {
            'workflow_type': 'aggregation_report_level',
            'timestamp': datetime.now().isoformat(),
            'total_reports': len(processed_reports),
            'reports': [],
            'overall_statistics': {
                'total_symptoms': 0,
                'valid_symptoms': 0,
                'total_api_calls': 0,
                'successful_api_calls': 0,
                'failed_api_calls': 0,
                'average_overall_score': 0.0,
                'average_precision': 0.0,
                'average_recall': 0.0
            }
        }
        
        total_scores = []
        total_precision = []
        total_recall = []
        
        for report in processed_reports:
            # 使用新的字段结构
            original_symptoms_count = report.get('original_symptoms_count', 0)
            overall_prediction = report.get('overall_prediction', {})
            intelligent_symptoms = report.get('intelligent_symptoms', {})
            rag_results = report.get('rag_results', {})
            
            # 记录报告信息
            report_info = {
                'report_id': report['report_id'],
                'file_path': report['file_path'],
                'total_symptoms': original_symptoms_count,
                'valid_symptoms': original_symptoms_count,
                'processing_timestamp': report['processing_timestamp']
            }
            summary['reports'].append(report_info)
            
            # 累计统计
            summary['overall_statistics']['total_symptoms'] += original_symptoms_count
            summary['overall_statistics']['valid_symptoms'] += original_symptoms_count
            summary['overall_statistics']['total_api_calls'] += rag_results.get('summary', {}).get('total_api_calls', 0)
            summary['overall_statistics']['successful_api_calls'] += rag_results.get('summary', {}).get('successful_api_calls', 0)
            summary['overall_statistics']['failed_api_calls'] += rag_results.get('summary', {}).get('failed_api_calls', 0)
            
            # 累计分数
            score = rag_results.get('summary', {}).get('average_overall_score')
            precision = rag_results.get('summary', {}).get('average_precision')
            recall = rag_results.get('summary', {}).get('average_recall')
            
            if score is not None and score > 0:
                total_scores.append(score)
                total_precision.append(precision or 0)
                total_recall.append(recall or 0)
        
        # 计算平均分数
        if total_scores:
            summary['overall_statistics']['average_overall_score'] = round(sum(total_scores) / len(total_scores), 1)
            summary['overall_statistics']['average_precision'] = round(sum(total_precision) / len(total_precision), 1)
            summary['overall_statistics']['average_recall'] = round(sum(total_recall) / len(total_recall), 1)
        
        # 保存汇总报告
        try:
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)
            print(f"✅ 汇总报告已保存到: {summary_file}")
        except Exception as e:
            print(f"❌ 保存汇总报告失败: {e}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="聚合工作流程：运行聚合方法（报告级聚合处理）")
    parser.add_argument("--data_path", required=True, help="数据目录路径")
    parser.add_argument("--output_dir", required=True, help="输出目录路径")
    parser.add_argument("--config", help="配置文件路径")
    parser.add_argument("--start_id", type=int, help="开始ID")
    parser.add_argument("--end_id", type=int, help="结束ID")
    parser.add_argument("--max_files", type=int, help="最大文件数量")
    
    args = parser.parse_args()
    
    # 运行聚合工作流程
    workflow = AggregationWorkflow()
    workflow.initialize(args.config)
    workflow.run_aggregation_workflow(
        args.data_path, args.output_dir,
        args.start_id, args.end_id, args.max_files
    )

if __name__ == "__main__":
    main()
