#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新的RAG工作流程 - 4步处理逻辑
1. 报告级症状聚合
2. LLM分解为小子症状
3. 每个小子症状RAG搜索
4. LLM整合所有RAG结果
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


class NewRAGWorkflow:
    """新的RAG工作流程 - 4步处理逻辑"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """初始化新的RAG工作流程"""
        self.config = ConfigLoader(config_path)
        self.data_loader = DataLoader()
        self.api_manager = APIManager()
        self.evaluator = Evaluator()
        self.logger = ReportLogger()
        
        # 创建结果目录
        self.results_dir = Path("results_new_rag")
        self.results_dir.mkdir(exist_ok=True)
        
        # 创建日志目录
        self.logs_dir = Path("logs")
        self.logs_dir.mkdir(exist_ok=True)
        
        # RAG相关目录
        self.rag_cache_dir = Path("rag_cache")
        self.rag_cache_dir.mkdir(exist_ok=True)
    
    def aggregate_report_symptoms(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """第1步：聚合报告中的所有症状"""
        symptoms = report_data.get('symptoms', [])
        
        # 收集所有症状文本
        all_symptoms = []
        symptom_details = []
        
        for symptom_item in symptoms:
            symptom_text = symptom_item.get('symptom_text', '')
            if symptom_text.strip():
                all_symptoms.append(symptom_text)
                symptom_details.append({
                    'symptom_id': symptom_item.get('symptom_id'),
                    'symptom_text': symptom_text,
                    'expected_organs': symptom_item.get('expected_results', [])
                })
        
        return {
            'report_id': report_data.get('report_id'),
            'aggregated_symptoms': all_symptoms,
            'aggregated_text': '; '.join(all_symptoms),
            'symptom_details': symptom_details,
            'total_symptoms': len(symptoms)
        }
    
    def decompose_symptoms_llm(self, aggregated_data: Dict[str, Any]) -> Dict[str, Any]:
        """第2步：使用LLM将聚合症状分解为小症状"""
        print(f"\n=== 第2步：LLM分解症状 ===")
        
        # 构建分解提示词
        decomposition_prompt = f"""你是一个医学专家，请根据以下病人的完整症状集合，将其分解为更小的、独立的医学症状或体征。

病人的完整症状描述：
{aggregated_data['aggregated_text']}

要求：
1. 将复杂症状分解为更小、更具体的医学症状
2. 每个小症状应该是独立的医学概念
3. 保持医学准确性
4. 返回JSON格式

请返回以下格式的JSON：
{{
  "decomposed_symptoms": [
    {{
      "symptom": "具体的小症状描述",
      "category": "症状类别",
      "severity": "严重程度",
      "description": "详细描述"
    }}
  ],
  "reasoning": "症状分解的医学推理"
}}"""
        
        # 创建症状数据用于API调用
        symptom_data = {
            'symptom_text': decomposition_prompt
        }
        
        # 加载系统提示词
        system_prompt = "你是一个医学专家，专门进行症状分析和分解。"
        
        # 调用API进行分解
        decomposition_result = self.api_manager.process_symptom(symptom_data, system_prompt)
        
        # 解析分解结果
        decomposed_symptoms = []
        for api_name, response in decomposition_result.items():
            if response.get('success'):
                try:
                    # 提取JSON响应
                    response_text = response.get('response', '')
                    json_data = self._extract_json_from_response(response_text)
                    
                    if 'decomposed_symptoms' in json_data:
                        decomposed_symptoms = json_data['decomposed_symptoms']
                        break
                except Exception as e:
                    print(f"解析LLM分解结果时出错: {e}")
        
        # 如果LLM分解失败，使用简单分割
        if not decomposed_symptoms:
            decomposed_symptoms = self._simple_decomposition(aggregated_data['aggregated_text'])
        
        return {
            'report_id': aggregated_data['report_id'],
            'original_symptoms': aggregated_data['symptom_details'],
            'decomposed_symptoms': decomposed_symptoms,
            'decomposition_api_responses': decomposition_result
        }
    
    def _simple_decomposition(self, text: str) -> List[Dict[str, str]]:
        """简单分解方法，当LLM分解失败时使用"""
        # 按分号分割
        parts = text.split(';')
        return [
            {
                'symptom': part.strip(),
                'category': 'general',
                'severity': 'moderate',
                'description': f'从聚合症状中提取: {part.strip()}'
            }
            for part in parts
            if part.strip()
        ]
    
    def rag_search_per_symptom(self, decomposed_data: Dict[str, Any]) -> Dict[str, Any]:
        """第3步：对每个分解的小症状进行RAG搜索"""
        print(f"\n=== 第3步：RAG搜索 ===")
        
        rag_results = []
        
        for i, symptom in enumerate(decomposed_data['decomposed_symptoms']):
            symptom_text = symptom['symptom']
            print(f"  处理症状 {i+1}: {symptom_text}")
            
            # 模拟RAG搜索
            # 在实际实现中，这里会调用真正的RAG系统
            rag_result = self._simulate_rag_search(symptom_text)
            
            rag_results.append({
                'original_symptom': symptom,
                'rag_search_result': rag_result,
                'search_timestamp': datetime.now().isoformat()
            })
        
        return {
            'report_id': decomposed_data['report_id'],
            'decomposed_symptoms': decomposed_data['decomposed_symptoms'],
            'rag_results': rag_results,
            'total_searches': len(rag_results)
        }
    
    def _simulate_rag_search(self, symptom_text: str) -> Dict[str, Any]:
        """模拟RAG搜索 - 实际实现中会调用真实RAG系统"""
        # 这里应该调用真实的RAG系统
        # 现在返回模拟数据
        return {
            'retrieved_documents': [
                {
                    'content': f'与症状"{symptom_text}"相关的医学信息',
                    'organ': '相关器官',
                    'locations': ['位置1', '位置2'],
                    'confidence': 0.85,
                    'source': '医学知识库'
                }
            ],
            'total_hits': 3,
            'search_query': symptom_text,
            'search_time': 0.5
        }
    
    def llm_integrate_results(self, rag_data: Dict[str, Any]) -> Dict[str, Any]:
        """第4步：LLM整合所有RAG结果"""
        print(f"\n=== 第4步：LLM整合结果 ===")
        
        # 构建整合提示词
        integration_prompt = self._build_integration_prompt(rag_data)
        
        # 创建症状数据用于API调用
        symptom_data = {
            'symptom_text': integration_prompt
        }
        
        # 加载系统提示词
        system_prompt = "你是一个医学专家，专门整合多个医学信息源进行综合分析。"
        
        # 调用API进行整合
        integration_result = self.api_manager.process_symptom(symptom_data, system_prompt)
        
        return {
            'report_id': rag_data['report_id'],
            'integration_results': integration_result,
            'rag_data_used': rag_data,
            'integration_timestamp': datetime.now().isoformat()
        }
    
    def _build_integration_prompt(self, rag_data: Dict[str, Any]) -> str:
        """构建LLM整合提示词"""
        
        # 构建RAG结果摘要
        rag_summary_parts = []
        for i, result in enumerate(rag_data['rag_results']):
            symptom = result['original_symptom']['symptom']
            rag_result = result['rag_search_result']
            
            rag_summary_parts.append(f"""
症状 {i+1}: {symptom}
RAG搜索结果:
{json.dumps(rag_result, ensure_ascii=False, indent=2)}
""")
        
        rag_summary = "".join(rag_summary_parts)
        
        integration_prompt = f"""You are a professional medical anatomy and diagnostic expert. Based on the provided RAG search results, you need to determine which organs and anatomical locations are MOST LIKELY and DIRECTLY related to the complete symptom set.

IMPORTANT: Focus on HIGH RELEVANCE organs and locations based on the aggregated RAG evidence.

Original decomposed symptoms:
{json.dumps([s['symptom'] for s in rag_data['decomposed_symptoms']], ensure_ascii=False, indent=2)}

RAG search results summary:
{rag_summary}

Task Requirements:
1. Carefully analyze all RAG search results
2. Identify organs with DIRECT and STRONG relevance based on the evidence
3. Focus on PRIMARY anatomical locations that are most likely involved
4. Consider the MAIN pathophysiological mechanisms across all symptoms
5. Only include secondary effects if they have CLEAR and STRONG relevance

Output Format Requirements (Must return in strict JSON format):
```json
{{
  "organs": [
    {{
      "organName": "Organ name (e.g., Heart (Cor), Lung (Pulmo), Brain, etc.)",
      "anatomicalLocations": [
        "Specific anatomical location 1",
        "Specific anatomical location 2",
        "Specific anatomical location 3"
      ],
      "relevance": "High/Medium/Low"
    }}
  ]
}}
```

Based on the following RAG search results, provide your comprehensive medical analysis:"""
        
        return integration_prompt
    
    def _extract_json_from_response(self, response_text: str) -> Dict[str, Any]:
        """从API响应中提取JSON"""
        import re
        import json
        
        # 移除可能的Markdown代码块标记
        response_text = response_text.replace('```json', '').replace('```', '').strip()
        
        # 查找JSON模式
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except:
                pass
        
        return {}
    
    def process_report_new_rag(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """使用新的4步RAG流程处理单个报告"""
        report_id = report_data.get('report_id', 'unknown')
        
        print(f"\n=== 新的RAG工作流程处理报告 {report_id} ===")
        
        try:
            # 第1步：聚合症状
            print("1. 聚合报告症状...")
            aggregated_data = self.aggregate_report_symptoms(report_data)
            
            # 第2步：LLM分解
            print("2. LLM分解症状...")
            decomposed_data = self.decompose_symptoms_llm(aggregated_data)
            
            # 第3步：RAG搜索
            print("3. 每个症状RAG搜索...")
            rag_data = self.rag_search_per_symptom(decomposed_data)
            
            # 第4步：LLM整合
            print("4. LLM整合所有结果...")
            final_result = self.llm_integrate_results(rag_data)
            
            # 保存完整结果
            final_result['report_id'] = report_id
            final_result['processing_steps'] = {
                'step1_aggregation': aggregated_data,
                'step2_decomposition': decomposed_data,
                'step3_rag_search': rag_data,
                'step4_integration': final_result['integration_results']
            }
            final_result['timestamp'] = datetime.now().isoformat()
            
            return final_result
            
        except Exception as e:
            error_msg = f"处理报告 {report_id} 时出错: {str(e)}"
            print(f"    {error_msg}")
            return {
                'report_id': report_id,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def save_results(self, final_result: Dict[str, Any]) -> str:
        """保存新的RAG处理结果"""
        report_id = final_result['report_id']
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 保存详细结果
        detailed_filename = f"report_{report_id}_new_rag_{timestamp}.json"
        detailed_path = self.results_dir / detailed_filename
        
        with open(detailed_path, 'w', encoding='utf-8') as f:
            json.dump(final_result, f, ensure_ascii=False, indent=2)
        
        # 保存简化结果
        simplified_filename = f"report_{report_id}_new_rag_simplified_{timestamp}.json"
        simplified_path = self.results_dir / simplified_filename
        
        simplified = {
            'report_id': report_id,
            'timestamp': timestamp,
            'final_prediction': final_result.get('integration_results', {}),
            'processing_summary': {
                'total_original_symptoms': len(final_result.get('processing_steps', {}).get('step1_aggregation', {}).get('symptom_details', [])),
                'total_decomposed_symptoms': len(final_result.get('processing_steps', {}).get('step2_decomposition', {}).get('decomposed_symptoms', [])),
                'total_rag_searches': final_result.get('processing_steps', {}).get('step3_rag_search', {}).get('total_searches', 0)
            }
        }
        
        with open(simplified_path, 'w', encoding='utf-8') as f:
            json.dump(simplified, f, ensure_ascii=False, indent=2)
        
        print(f"新的RAG结果已保存到:")
        print(f"  详细结果: {detailed_path}")
        print(f"  简化结果: {simplified_path}")
        
        return str(detailed_path)
    
    def run_workflow(self, start_id: int = None, end_id: int = None, max_files: int = None):
        """运行新的RAG工作流程"""
        print("=== 新的4步RAG工作流程 ===")
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
            print(f"\n3. 开始处理 {len(reports)} 个报告...")
            all_results = []
            
            for i, report in enumerate(reports, 1):
                print(f"\n进度: {i}/{len(reports)}")
                
                try:
                    result = self.process_report_new_rag(report)
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
            
            print(f"\n=== 新的RAG工作流程完成 ===")
            print(f"成功处理: {len(all_results)} 个报告")
            print(f"结果保存在: {self.results_dir}")
            
        except Exception as e:
            print(f"新的RAG工作流程执行出错: {str(e)}")
            logging.error(f"新的RAG工作流程执行出错: {str(e)}", exc_info=True)
    
    def generate_summary_report(self, all_results: List[Dict[str, Any]]) -> str:
        """生成新的RAG流程汇总报告"""
        if not all_results:
            return ""
        
        summary = {
            'total_reports': len(all_results),
            'workflow_type': 'new_4step_rag',
            'timestamp': datetime.now().isoformat(),
            'processing_summary': {
                'total_reports_processed': len(all_results),
                'successful_reports': 0,
                'failed_reports': 0,
                'average_decomposed_symptoms': 0,
                'total_rag_searches': 0
            },
            'api_performance': {},
            'report_details': []
        }
        
        successful_count = 0
        total_decomposed = 0
        total_searches = 0
        
        for result in all_results:
            if 'error' not in result:
                successful_count += 1
                
                # 收集处理统计
                processing_steps = result.get('processing_steps', {})
                
                decomposed_count = len(processing_steps.get('step2_decomposition', {}).get('decomposed_symptoms', []))
                searches_count = processing_steps.get('step3_rag_search', {}).get('total_searches', 0)
                
                total_decomposed += decomposed_count
                total_searches += searches_count
                
                # API性能统计
                integration_results = result.get('integration_results', {})
                for api_name, api_response in integration_results.items():
                    if api_name not in summary['api_performance']:
                        summary['api_performance'][api_name] = {
                            'total_calls': 0,
                            'successful_calls': 0,
                            'failed_calls': 0
                        }
                    
                    summary['api_performance'][api_name]['total_calls'] += 1
                    if api_response.get('success'):
                        summary['api_performance'][api_name]['successful_calls'] += 1
                    else:
                        summary['api_performance'][api_name]['failed_calls'] += 1
                
                summary['report_details'].append({
                    'report_id': result['report_id'],
                    'decomposed_symptoms': decomposed_count,
                    'rag_searches': searches_count,
                    'status': 'success'
                })
            else:
                summary['processing_summary']['failed_reports'] += 1
                summary['report_details'].append({
                    'report_id': result.get('report_id', 'unknown'),
                    'status': 'failed',
                    'error': result.get('error', 'Unknown error')
                })
        
        summary['processing_summary']['successful_reports'] = successful_count
        if successful_count > 0:
            summary['processing_summary']['average_decomposed_symptoms'] = total_decomposed / successful_count
        summary['processing_summary']['total_rag_searches'] = total_searches
        
        # 保存汇总报告
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        summary_filename = f"summary_new_rag_{timestamp}.json"
        summary_path = self.results_dir / summary_filename
        
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        print(f"\n新的RAG汇总报告已保存到: {summary_path}")
        return str(summary_path)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="新的4步RAG工作流程")
    parser.add_argument("--start_id", type=int, help="开始报告ID")
    parser.add_argument("--end_id", type=int, help="结束报告ID")
    parser.add_argument("--max_files", type=int, help="最大处理文件数量")
    parser.add_argument("--config", default="config/config.yaml", help="配置文件路径")
    
    args = parser.parse_args()
    
    # 创建并运行新的RAG工作流程
    workflow = NewRAGWorkflow(args.config)
    workflow.run_workflow(
        start_id=args.start_id,
        end_id=args.end_id,
        max_files=args.max_files
    )


if __name__ == "__main__":
    main()