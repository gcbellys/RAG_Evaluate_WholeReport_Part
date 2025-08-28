#!/usr/bin/env python3
"""
症状聚合处理器
将同一报告的所有症状聚合为一个整体进行处理
"""

import json
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path

class AggregationProcessor:
    """症状聚合处理器 - 将报告级症状聚合处理"""
    
    def __init__(self):
        self.original_symptoms_data = []  # 保存原始症状数据
    
    def aggregate_symptoms_for_report(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """将报告中的所有症状聚合为一个整体"""
        if not report_data.get('symptoms'):
            return {
                'report_id': report_data.get('report_id', ''),
                'aggregated_symptoms': '',
                'total_symptoms': 0,
                'error': '没有症状数据'
            }
        
        # 聚合所有症状文本
        symptom_texts = []
        for symptom in report_data['symptoms']:
            symptom_text = symptom.get('symptom_text', '').strip()
            if symptom_text:
                symptom_texts.append(symptom_text)
        
        # 合并症状文本，用分号分隔
        aggregated_text = '; '.join(symptom_texts)
        
        # 收集所有期望结果并去重
        all_expected_results = []
        seen_combinations = set()
        
        for symptom in report_data.get('symptoms', []):
            # DataLoader已经处理了expected_results，直接使用
            expected_results = symptom.get('expected_results', [])
            
            for expected_result in expected_results:
                if expected_result:
                    organ_name = expected_result.get('organName', '')
                    locations = expected_result.get('anatomicalLocations', [])
                    
                    # 创建唯一标识
                    locations_tuple = tuple(sorted(locations)) if locations else ()
                    combination_key = (organ_name, locations_tuple)
                    
                    if combination_key not in seen_combinations:
                        seen_combinations.add(combination_key)
                        all_expected_results.append(expected_result)
        
        # 保存原始症状数据供后续使用
        self.original_symptoms_data = report_data['symptoms']
        
        return {
            'report_id': report_data['report_id'],
            'file_path': report_data['file_path'],
            'aggregated_symptoms': aggregated_text,
            'total_symptoms': len(symptom_texts),
            'valid_symptoms': len(report_data['symptoms']),
            'all_expected_results': all_expected_results,
            'aggregation_timestamp': datetime.now().isoformat()
        }
    
    def process_aggregated_report(self, aggregated_data: Dict[str, Any], api_manager, system_prompt: str) -> Dict[str, Any]:
        """处理聚合后的报告数据"""
        print(f"🔄 处理聚合报告 {aggregated_data['report_id']} ({aggregated_data['total_symptoms']} 个症状)")
        
        # 使用聚合的症状文本调用API
        aggregated_symptoms = aggregated_data['aggregated_symptoms']
        
        # 调用API处理聚合症状
        api_responses = {}
        for client_name, client in api_manager.clients.items():
            try:
                response = client.generate_response(
                    system_prompt=system_prompt,
                    user_prompt=aggregated_symptoms
                )
                
                # 确保响应包含解析后的数据
                if response.get('success') and not response.get('organ_name'):
                    if 'response' in response and response['response']:
                        parsed_data = api_manager._extract_and_parse_json(response['response'])
                        response['parsed_data'] = parsed_data
                        response['organ_name'] = parsed_data.get('organ_name', '')
                        response['anatomical_locations'] = parsed_data.get('anatomical_locations', [])
                
                # 将期望结果附加到响应中
                response['expected_results'] = aggregated_data['all_expected_results']
                api_responses[client_name] = response
                
            except Exception as e:
                api_responses[client_name] = {
                    'success': False,
                    'error': str(e),
                    'expected_results': aggregated_data['all_expected_results']
                }
        
        return {
            'report_id': aggregated_data['report_id'],
            'file_path': aggregated_data['file_path'],
            'total_symptoms': aggregated_data['total_symptoms'],
            'valid_symptoms': aggregated_data['valid_symptoms'],
            'aggregated_symptoms': aggregated_symptoms,
            'processing_timestamp': datetime.now().isoformat(),
            'api_responses': api_responses
        }
    
    def batch_process_reports(self, report_files: List[Path], api_manager, system_prompt: str, 
                            data_loader, output_dir: Path) -> List[Dict[str, Any]]:
        """批量处理多个报告文件"""
        results = []
        
        for file_path in report_files:
            try:
                print(f"\n📋 处理报告: {file_path.name}")
                
                # 加载报告数据
                report_data = data_loader.load_report_data(file_path)
                if 'error' in report_data:
                    print(f"❌ 加载报告失败: {report_data['error']}")
                    continue
                
                # 聚合症状
                aggregated_data = self.aggregate_symptoms_for_report(report_data)
                if 'error' in aggregated_data:
                    print(f"❌ 症状聚合失败: {aggregated_data['error']}")
                    continue
                
                # 处理聚合报告
                result = self.process_aggregated_report(aggregated_data, api_manager, system_prompt)
                results.append(result)
                
                print(f"✅ 报告 {report_data['report_id']} 处理完成")
                
            except Exception as e:
                print(f"❌ 处理报告 {file_path.name} 时出错: {e}")
                continue
        
        return results
    
    def save_aggregated_results(self, results: List[Dict[str, Any]], output_dir: Path) -> List[str]:
        """保存聚合处理结果"""
        output_dir.mkdir(parents=True, exist_ok=True)
        saved_files = []
        
        for result in results:
            try:
                report_id = result['report_id']
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                # 保存详细结果
                detailed_file = output_dir / f"report_{report_id}_aggregate_evaluation_{timestamp}.json"
                with open(detailed_file, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                
                # 保存标准化结果
                standardized_file = output_dir / f"report_{report_id}_aggregate_standardized_{timestamp}.json"
                standardized_result = self._standardize_result(result)
                with open(standardized_file, 'w', encoding='utf-8') as f:
                    json.dump(standardized_result, f, ensure_ascii=False, indent=2)
                
                saved_files.extend([str(detailed_file), str(standardized_file)])
                print(f"✅ 报告 {report_id} 结果已保存")
                
            except Exception as e:
                print(f"❌ 保存报告 {result.get('report_id', 'unknown')} 结果失败: {e}")
                continue
        
        return saved_files
    
    def _standardize_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """标准化结果格式"""
        standardized = {
            'metadata': {
                'report_id': result['report_id'],
                'file_path': result['file_path'],
                'processing_timestamp': result['processing_timestamp'],
                'total_symptoms': result['total_symptoms'],
                'valid_symptoms': result['valid_symptoms'],
                'api_clients': list(result['api_responses'].keys())
            },
            'aggregated_symptoms': result['aggregated_symptoms'],
            'api_responses': {}
        }
        
        # 标准化API响应
        for client_name, response in result['api_responses'].items():
            parsed_response = {}
            if response.get('success'):
                try:
                    # 去除可能的Markdown代码块标记
                    text = response['response'].strip().replace('```json', '').replace('```', '').strip()
                    parsed_response = json.loads(text)
                except (json.JSONDecodeError, AttributeError):
                    response['success'] = False
                    response['error'] = "Failed to parse JSON response"
            
            standardized['api_responses'][client_name] = {
                'success': response.get('success', False),
                'model': response.get('model', 'Unknown'),
                'organ_name': parsed_response.get('organName', ''),
                'anatomical_locations': parsed_response.get('anatomicalLocations', []),
                'usage': response.get('usage', {}),
                'error': response.get('error')
            }
        
        return standardized

    def predict_overall_organs_and_locations(self, aggregated_data: Dict[str, Any], api_manager) -> Dict[str, Any]:
        """基于聚合症状进行整体预测 - 使用正确的system prompt"""
        # 加载正确的system prompt
        system_prompt_path = Path("prompt/system_prompt.txt")
        if system_prompt_path.exists():
            with open(system_prompt_path, 'r', encoding='utf-8') as f:
                system_prompt = f.read().strip()
        else:
            # 如果文件不存在，使用简化版本
            system_prompt = """You are a professional medical anatomy and diagnostic expert. Based on the provided patient symptoms, determine which organs and anatomical locations are MOST LIKELY related to the symptom. Return results in strict JSON format with organs array containing organName, anatomicalLocations, and relevance fields."""

        user_prompt = f"Patient symptoms: {aggregated_data['aggregated_symptoms']}"
        
        try:
            # 调用所有API客户端
            api_responses = {}
            for client_name, client in api_manager.clients.items():
                try:
                    response = client.generate_response(system_prompt, user_prompt)
                    api_responses[client_name] = response
                except Exception as e:
                    api_responses[client_name] = {
                        'success': False,
                        'error': str(e)
                    }
            
            return {
                'success': True,
                'api_responses': api_responses,
                'aggregated_symptoms': aggregated_data['aggregated_symptoms'],
                'expected_results': aggregated_data.get('all_expected_results', []),
                'timestamp': datetime.now().isoformat()
            }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def intelligently_split_symptoms(self, aggregated_data: Dict[str, Any], api_manager) -> Dict[str, Any]:
        """让LLM智能分割聚合症状"""
        system_prompt = """你是一个医学专家。请将以下聚合症状智能分割成独立的症状单元。

请以JSON格式返回结果：
{
    "split_symptoms": [
        {
            "symptom_id": "s1",
            "symptom_text": "症状描述",
            "primary_organ": "主要相关器官",
            "severity": "严重程度"
        }
    ],
    "total_count": 分割后的症状总数,
    "reasoning": "分割逻辑说明"
}"""

        user_prompt = f"聚合症状：{aggregated_data['aggregated_symptoms']}"
        
        try:
            # 调用API进行智能分割
            api_response = api_manager.clients['moonshot'].generate_response(system_prompt, user_prompt)
            
            if api_response.get('success'):
                return {
                    'success': True,
                    'response': api_response['response'],
                    'parsed_data': api_response['parsed_data'],
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {
                    'success': False,
                    'error': api_response.get('error', 'API调用失败'),
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def rag_search_for_split_symptoms(self, intelligent_symptoms: Dict[str, Any], search_engine=None) -> Dict[str, Any]:
        """对智能分割的症状进行真正的RAG搜索"""
        if not intelligent_symptoms.get('success') or 'parsed_data' not in intelligent_symptoms:
            return {'error': '智能分割结果无效'}
        
        split_symptoms = intelligent_symptoms['parsed_data'].get('full_response', {}).get('split_symptoms', [])
        
        # 初始化搜索引擎（如果没有提供）
        if search_engine is None:
            default_index_dir = "/home/duojiechen/Projects/Rag_system/Rag_Build/enhanced_faiss_indexes"
            rag_index_dir = os.getenv("RAG_INDEX_DIR", default_index_dir)
            try:
                import sys
                import os
                sys.path.append("/home/duojiechen/Projects/Rag_system/Rag_Build/src")
                from enhanced_search_engine import EnhancedMedicalSearchEngine
                search_engine = EnhancedMedicalSearchEngine(rag_index_dir)
                print(f"✅ RAG搜索引擎已初始化: {rag_index_dir}")
            except Exception as e:
                print(f"❌ RAG搜索引擎初始化失败: {e}")
                return {
                    'success': False,
                    'error': f'RAG搜索引擎初始化失败: {e}',
                    'total_searched': 0,
                    'symptom_rag_results': {},
                    'timestamp': datetime.now().isoformat()
                }
        
        rag_results = {}
        
        for symptom in split_symptoms:
            symptom_id = symptom.get('symptom_id', 'unknown')
            symptom_text = symptom.get('symptom_text', '')
            
            if symptom_text:
                print(f"  🔍 RAG搜索症状: {symptom_text[:50]}...")
                # 获取该症状的期望器官和位置（这里需要从原始数据中提取）
                expected_organs = []
                expected_locations = []
                
                # 从原始症状数据中查找对应的期望结果
                for original_symptom in self.original_symptoms_data:
                    if original_symptom.get('symptom_text') == symptom_text:
                        expected_results = original_symptom.get('expected_results', [])
                        for result in expected_results:
                            if result.get('organName'):
                                expected_organs.append(result['organName'])
                            if result.get('anatomicalLocations'):
                                expected_locations.extend(result['anatomicalLocations'])
                        break
                
                rag_result = self._perform_rag_search(symptom_text, search_engine)
                rag_results[symptom_id] = {
                    'symptom_text': symptom_text,
                    'rag_result': rag_result
                }
        
        # 生成与原系统一致的RAG搜索输出格式
        rag_search_output = []
        for symptom_id, search_result in rag_results.items():
            if search_result.get('rag_result', {}).get('success'):
                rag_output = search_result['rag_result']['rag_output']
                rag_search_output.append(rag_output)
        
        return {
            'success': True,
            'total_searched': len(rag_results),
            'symptom_rag_results': rag_results,
            'rag_search_output': rag_search_output,  # 添加标准格式输出
            'timestamp': datetime.now().isoformat()
        }

    def _perform_rag_search(self, symptom_text: str, search_engine=None) -> Dict[str, Any]:
        """执行单个症状的RAG搜索 - 返回与原系统一致的结构"""
        try:
            if search_engine is None:
                # 初始化RAG搜索引擎
                default_index_dir = "/home/duojiechen/Projects/Rag_system/Rag_Build/enhanced_faiss_indexes"
                rag_index_dir = os.getenv("RAG_INDEX_DIR", default_index_dir)
                try:
                    # 延迟导入以避免不必要依赖
                    import sys
                    import os
                    sys.path.append("/home/duojiechen/Projects/Rag_system/Rag_Build/src")
                    from enhanced_search_engine import EnhancedMedicalSearchEngine
                    search_engine = EnhancedMedicalSearchEngine(rag_index_dir)
                except Exception as e:
                    return {
                        'success': False,
                        'error': f'RAG搜索引擎初始化失败: {e}',
                        'search_timestamp': datetime.now().isoformat()
                    }
            
            # 执行RAG搜索 - 优化搜索参数提高置信度
            rag_results = search_engine.comprehensive_search(
                query=symptom_text,
                top_k=15,  # 增加搜索数量，后续筛选高质量结果
                rerank=True,  # 启用重排序
                force_query_type='symptom'
            )
            
            # 构建与原系统一致的RAG搜索结果结构
            rag_output = {
                "query": symptom_text,
                "expected_organs": [],  # 这里需要从症状数据中获取
                "expected_a_locations": [],  # 这里需要从症状数据中获取
                "s": {}
            }
            
            # 处理主检索结果 - 只保留高置信度结果
            primary_results = rag_results.get('primary_results', [])
            seen_texts = set()  # 用于去重
            high_confidence_results = []
            
            # 筛选高置信度结果 (相似度 > 0.7)
            for item in primary_results:
                score = item.get('similarity_score', item.get('distance', 0.0))
                if score > 0.7:  # 只保留高置信度结果
                    high_confidence_results.append(item)
            
            # 按置信度排序，取前3个最高质量的结果
            high_confidence_results.sort(key=lambda x: x.get('similarity_score', 0.0), reverse=True)
            
            for i, item in enumerate(high_confidence_results[:3], 1):
                data = item.get('data', {})
                # 优先使用diagnosis_text，然后是symptom_text，最后是data中的text
                text = item.get('diagnosis_text') or item.get('symptom_text') or data.get('text') or data.get('diagnosis_text', '')
                
                # 去重检查
                if text in seen_texts:
                    continue
                seen_texts.add(text)
                
                organ = data.get('organ', 'Unknown')
                score = item.get('similarity_score', item.get('distance', 0.0))
                
                # 构建unit结构
                unit = {
                    "u_id": f"u_{hash(text) % 100000}",
                    "u_unit": {
                        "d_diagnosis": text,
                        "o_organ": {
                            "organName": organ if organ and organ != "Unknown" else self._extract_organ_from_text(text),
                            "anatomicalLocations": [organ] if organ and organ != "Unknown" else self._extract_anatomical_locations_from_text(text)
                        },
                        "b_textual_basis": {
                            "medicalInference": text
                        }
                    }
                }
                
                # 添加到结果中
                rag_s_id = f"rag_s_{i}_id"
                rag_output["s"][rag_s_id] = {
                    "s_text": symptom_text,
                    "units": [unit]
                }
            
            # 处理上下文相关诊断 - 只保留高置信度结果
            context_results = rag_results.get('context_results', {}).get('related_diagnoses', [])
            context_seen = set()
            high_confidence_context = []
            
            # 筛选高置信度上下文结果 (相似度 > 0.65)
            for diag in context_results:
                score = diag.get('similarity_score', 0.0)
                if score > 0.65:  # 上下文结果阈值稍低，但仍有质量保证
                    high_confidence_context.append(diag)
            
            # 按置信度排序，取前2个最高质量的结果
            high_confidence_context.sort(key=lambda x: x.get('similarity_score', 0.0), reverse=True)
            
            for i, diag in enumerate(high_confidence_context[:2], 1):
                text = diag.get('diagnosis_text', '')
                if text in context_seen:
                    continue
                context_seen.add(text)
                
                organ = diag.get('organ', 'Unknown')
                score = diag.get('similarity_score', 0.0)
                
                # 构建unit结构
                unit = {
                    "u_id": f"u_{hash(text) % 100000}",
                    "u_unit": {
                        "d_diagnosis": text,
                        "o_organ": {
                            "organName": organ if organ and organ != "Unknown" else self._extract_organ_from_text(text),
                            "anatomicalLocations": [organ] if organ and organ != "Unknown" else self._extract_anatomical_locations_from_text(text)
                        },
                        "b_textual_basis": {
                            "medicalInference": text
                        }
                    }
                }
                
                # 添加到结果中
                rag_s_id = f"rag_s_{i+3}_id"  # 避免ID冲突
                rag_output["s"][rag_s_id] = {
                    "s_text": symptom_text,
                    "units": [unit]
                }
            
            return {
                'success': True,
                'rag_output': rag_output,  # 返回与原系统一致的格式
                'search_timestamp': datetime.now().isoformat()
            }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'search_timestamp': datetime.now().isoformat()
            }

    def rag_enhanced_prediction(self, aggregated_data: Dict[str, Any], rag_search_results: Dict[str, Any], api_manager) -> Dict[str, Any]:
        """基于RAG搜索结果进行增强预测 - 让API自主选择是否使用RAG结果"""
        # 加载基础system prompt
        system_prompt_path = Path("prompt/system_prompt.txt")
        if system_prompt_path.exists():
            with open(system_prompt_path, 'r', encoding='utf-8') as f:
                base_system_prompt = f.read().strip()
        else:
            base_system_prompt = """You are a professional medical anatomy and diagnostic expert. Based on the provided patient symptoms, determine which organs and anatomical locations are MOST LIKELY related to the symptom. Return results in strict JSON format with organs array containing organName, anatomicalLocations, and relevance fields."""

        # 增强system prompt - 优化RAG集成策略，只使用高置信度结果
        enhanced_system_prompt = base_system_prompt + """

CRITICAL INSTRUCTIONS: You will be provided with patient symptoms and HIGH-CONFIDENCE RAG search results from a medical knowledge base.

**CONFIDENCE-BASED RAG INTEGRATION**:
- ONLY use RAG results with similarity scores > 0.7 (high confidence)
- Results with scores 0.65-0.7 may provide supporting context
- IGNORE results with scores < 0.65 (low confidence)
- Each RAG result includes a confidence score - prioritize higher scores

**MULTIPLE ORGANS ANALYSIS**:
- The symptoms may affect MULTIPLE different organs and anatomical locations
- You MUST identify ALL relevant organs, not just the primary one
- Consider both direct effects and secondary/systemic effects
- Each organ may have different anatomical locations involved

**RAG Integration Strategy**:
1. **High Confidence (>0.8)**: Strong evidence - integrate directly into your analysis
2. **Medium Confidence (0.7-0.8)**: Good evidence - use as supporting information
3. **Lower Confidence (0.65-0.7)**: Context only - use cautiously for background
4. **Low Confidence (<0.65)**: Ignore completely - rely on your medical training instead
5. Always validate RAG findings with clinical reasoning
6. If RAG results are low quality, rely primarily on your medical expertise

**Output Requirements**:
- Return ALL relevant organs in your JSON response
- For each organ, include ALL relevant anatomical locations
- Set appropriate relevance levels (High/Medium/Low) for each organ
- Do not limit yourself to just one organ - be comprehensive
- Indicate which findings came from RAG vs. your medical training"""

        # 构建结构化的RAG上下文 - 突出显示置信度信息
        rag_context = ""
        if rag_search_results.get('symptom_rag_results'):
            rag_context = "\n\n=== HIGH-CONFIDENCE RAG SEARCH RESULTS ===\n"
            rag_context += "⚠️  IMPORTANT: Only use results with similarity scores > 0.7\n\n"
            
            for symptom_id, search_result in rag_search_results['symptom_rag_results'].items():
                if search_result.get('rag_result', {}).get('success'):
                    rag_context += f"\n🔍 Symptom: {search_result['symptom_text']}\n"
                    
                    # 主要相似症状匹配 - 按置信度排序
                    primary_refs = search_result['rag_result'].get('primary_refs', [])
                    if primary_refs:
                        rag_context += "📊 High-confidence matches (use if score > 0.7):\n"
                        # 按置信度排序
                        sorted_refs = sorted(primary_refs, key=lambda x: x.get('score', 0), reverse=True)
                        for i, ref in enumerate(sorted_refs[:3], 1):
                            score = ref.get('score', 0)
                            text = ref.get('text', '')[:150]
                            organ = ref.get('organ', 'Unknown')
                            
                            # 根据置信度添加标识
                            if score > 0.8:
                                confidence_level = "🟢 HIGH CONFIDENCE"
                            elif score > 0.7:
                                confidence_level = "🟡 MEDIUM CONFIDENCE"
                            else:
                                confidence_level = "🔴 LOW CONFIDENCE (IGNORE)"
                            
                            rag_context += f"  {i}. [{organ}] {text}\n"
                            rag_context += f"     Confidence: {confidence_level} (score: {score:.3f})\n"
                    
                    # 相关诊断上下文 - 只显示高置信度结果
                    context_refs = search_result['rag_result'].get('context_refs', [])
                    if context_refs:
                        high_conf_context = [ref for ref in context_refs if ref.get('score', 0) > 0.65]
                        if high_conf_context:
                            rag_context += "📚 Supporting context (use if score > 0.65):\n"
                            # 按置信度排序
                            sorted_context = sorted(high_conf_context, key=lambda x: x.get('score', 0), reverse=True)
                            for i, ref in enumerate(sorted_context[:2], 1):
                                score = ref.get('score', 0)
                                text = ref.get('text', '')[:100]
                                organ = ref.get('organ', 'Unknown')
                                rag_context += f"  {i}. [{organ}] {text} (score: {score:.3f})\n"
                    
                    rag_context += "---\n"
            
            rag_context += "=== END RAG RESULTS ===\n"
            rag_context += "\n💡 INTEGRATION GUIDANCE:\n"
            rag_context += "- 🟢 Use HIGH confidence results (>0.8) as primary evidence\n"
            rag_context += "- 🟡 Use MEDIUM confidence results (0.7-0.8) as support\n"
            rag_context += "- 🔴 IGNORE LOW confidence results (<0.7)\n"
            rag_context += "- If RAG quality is poor, rely on your medical expertise\n"

        user_prompt = f"Patient symptoms: {aggregated_data['aggregated_symptoms']}{rag_context}\n\nBased on your medical expertise and the RAG search results above (if relevant), determine the most likely organs and anatomical locations."
        
        try:
            # 调用所有API客户端
            api_responses = {}
            for client_name, client in api_manager.clients.items():
                try:
                    response = client.generate_response(enhanced_system_prompt, user_prompt)
                    api_responses[client_name] = response
                except Exception as e:
                    api_responses[client_name] = {
                        'success': False,
                        'error': str(e)
                    }
            
            return {
                'success': True,
                'api_responses': api_responses,
                'aggregated_symptoms': aggregated_data['aggregated_symptoms'],
                'rag_context': rag_context,
                'enhanced_prompt_used': True,
                'expected_results': aggregated_data.get('all_expected_results', []),
                'timestamp': datetime.now().isoformat()
            }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    
    def _extract_organ_from_text(self, text: str) -> str:
        """从医学文本中提取器官名称"""
        if not text:
            return "Unknown"
        
        text_lower = text.lower()
        
        # 心脏相关
        if any(word in text_lower for word in ['heart', 'cardiac', 'cardiovascular', 'coronary', 'atrial', 'ventricular', 'aortic', 'mitral']):
            return "Heart (Cor)"
        
        # 肺部相关
        if any(word in text_lower for word in ['lung', 'pulmonary', 'respiratory', 'bronchi', 'alveoli', 'pleura']):
            return "Lung (Pulmo)"
        
        # 大脑相关
        if any(word in text_lower for word in ['brain', 'cerebral', 'cerebrovascular', 'brainstem', 'cva', 'stroke']):
            return "Brain"
        
        # 血管相关
        if any(word in text_lower for word in ['artery', 'vein', 'vascular', 'blood vessel', 'coronary artery']):
            return "Artery (Arteria)"
        
        # 食管相关
        if any(word in text_lower for word in ['esophagus', 'esophageal', 'transesophageal']):
            return "Esophagus"
        
        # 肾脏相关
        if any(word in text_lower for word in ['kidney', 'renal', 'nephron']):
            return "Kidney (Ren)"
        
        # 肝脏相关
        if any(word in text_lower for word in ['liver', 'hepatic', 'hepatocellular']):
            return "Liver (Hepar)"
        
        # 胃肠道相关
        if any(word in text_lower for word in ['stomach', 'gastric', 'intestine', 'bowel', 'colon']):
            return "Gastrointestinal Tract"
        
        # 骨骼相关
        if any(word in text_lower for word in ['bone', 'skeletal', 'fracture', 'joint']):
            return "Bone (Os)"
        
        # 肌肉相关
        if any(word in text_lower for word in ['muscle', 'muscular', 'myocardial']):
            return "Muscle (Musculus)"
        
        # 如果都找不到，尝试从症状关键词推断
        if 'central line' in text_lower or 'catheter' in text_lower:
            return "Vein (Vena)"  # 中心静脉置管通常涉及静脉
        
        if 'chest pain' in text_lower or 'angina' in text_lower:
            return "Heart (Cor)"  # 胸痛通常与心脏相关
        
        if 'shortness of breath' in text_lower or 'dyspnea' in text_lower:
            return "Lung (Pulmo)"  # 呼吸困难通常与肺部相关
        
        return "Unknown"
    
    def _extract_anatomical_locations_from_text(self, text: str) -> List[str]:
        """从医学文本中提取解剖位置"""
        if not text:
            return []
        
        text_lower = text.lower()
        imports = []
        
        # 心脏相关位置
        if 'heart' in text_lower or 'cardiac' in text_lower:
            if 'atrial' in text_lower or 'atrium' in text_lower:
                imports.append("Left Atrium (LA)")
                imports.append("Right Atrium (RA)")
            if 'ventricular' in text_lower or 'ventricle' in text_lower:
                imports.append("Left Ventricle (LV)")
                imports.append("Right Ventricle (RV)")
            if 'aortic' in text_lower:
                imports.append("Aortic Valve")
            if 'mitral' in text_lower:
                imports.append("Mitral Valve")
            if 'coronary' in text_lower:
                imports.append("Coronary Artery")
        
        # 肺部相关位置
        if 'lung' in text_lower or 'pulmonary' in text_lower:
            if 'alveoli' in text_lower:
                imports.append("Alveoli")
            if 'bronchi' in text_lower or 'bronchioles' in text_lower:
                imports.append("Bronchioles")
            if 'pleura' in text_lower:
                imports.append("Pleural Cavity")
        
        # 大脑相关位置
        if 'heart' in text_lower or 'cerebral' in text_lower:
            if 'brainstem' in text_lower:
                imports.append("Brainstem")
            if 'medulla' in text_lower:
                imports.append("Medulla Oblongata")
            if 'cortex' in text_lower:
                imports.append("Cerebral Cortex")
        
        # 如果没有找到具体位置，返回器官名称
        if not imports:
            organ = self._extract_organ_from_text(text)
            if organ != "Unknown":
                imports.append(organ)
        
        return imports

    def _get_confidence_level(self, score: float) -> str:
        """根据相似度分数确定置信度级别"""
        if score > 0.8:
            return "HIGH"
        elif score > 0.7:
            return "MEDIUM"
        elif score > 0.65:
            return "LOW"
        else:
            return "VERY_LOW"
    
    def _get_integration_recommendation(self, score: float) -> str:
        """根据置信度提供集成建议"""
        if score > 0.8:
            return "Use as primary evidence - strong match"
        elif score > 0.7:
            return "Use as supporting information - good match"
        elif score > 0.65:
            return "Use cautiously for context - moderate match"
        else:
            return "Ignore - poor match, rely on medical expertise"
