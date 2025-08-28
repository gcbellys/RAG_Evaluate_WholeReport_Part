# 新的4步RAG工作流程使用指南

## 概述

新的RAG工作流程实现了您要求的4步处理逻辑：

1. **报告级症状聚合** - 将同一报告的所有症状整合为一个大S
2. **LLM分解** - 让LLM将大S分解为多个小子症状
3. **RAG搜索** - 对每个小子症状进行RAG检索
4. **LLM整合** - 将所有RAG结果给LLM进行最终整合

## 工作流程详解

### 📊 流程步骤

1. **症状聚合** (`Step 1`)
   - 收集报告中的所有症状
   - 整合为完整的症状描述
   - 保留原始症状的预期结果

2. **LLM分解** (`Step 2`)
   - 使用LLM将复杂症状分解为独立的小症状
   - 每个小症状包含：症状描述、类别、严重程度、详细描述
   - 如果LLM分解失败，使用简单分割作为回退

3. **RAG搜索** (`Step 3`)
   - 对每个分解的小症状进行RAG检索
   - 获取相关的医学文档和知识
   - 收集器官和解剖位置信息

4. **LLM整合** (`Step 4`)
   - 基于所有RAG结果进行综合分析
   - 考虑症状间的关联性
   - 输出统一的器官和解剖位置预测

## 🚀 使用方法

### 快速开始

```bash
cd /path/to/Rag_Evaluate_WholeReport

# 运行新的RAG工作流程
python workflows/new_rag_workflow.py

# 运行特定范围的报告
python workflows/new_rag_workflow.py --start_id 1 --end_id 5

# 限制处理文件数量
python workflows/new_rag_workflow.py --max_files 3
```

### 使用便捷脚本

```bash
# 使用便捷脚本运行
python scripts/run_new_rag.py
```

### 命令行参数

```bash
python workflows/new_rag_workflow.py [选项]

选项:
  --start_id INT     开始报告ID
  --end_id INT       结束报告ID
  --max_files INT    最大处理文件数量
  --config PATH      配置文件路径 (默认: config/config.yaml)
```

## 📁 输出结果

### 结果目录
- **详细结果**: `results_new_rag/`
- **系统提示词**: `prompt/`

### 文件格式

#### 1. 详细结果文件
`report_{report_id}_new_rag_{timestamp}.json`
包含完整的4步处理过程：
- 症状聚合结果
- LLM分解结果
- RAG搜索结果
- LLM整合结果

#### 2. 简化结果文件
`report_{report_id}_new_rag_simplified_{timestamp}.json`
只包含最终预测和关键统计信息

#### 3. 汇总报告
`summary_new_rag_{timestamp}.json`
包含所有报告的处理汇总统计

## 🔍 结果解读

### 关键字段说明

#### 最终预测结果
```json
{
  "organ": "主要相关器官",
  "anatomical_locations": ["位置1", "位置2"],
  "reasoning": "医学推理",
  "confidence": 0.95,
  "symptom_analysis": {
    "total_symptoms": 分解的症状总数,
    "key_findings": ["关键发现"]
  }
}
```

#### 处理统计
```json
{
  "total_original_symptoms": 原始症状数,
  "total_decomposed_symptoms": 分解后症状数,
  "total_rag_searches": RAG搜索次数
}
```

### 性能指标

- **分解效率**: 平均每个报告分解的症状数量
- **RAG命中率**: RAG搜索的成功率和质量
- **整合准确性**: 基于预期结果的评估

## 🛠️ 自定义配置

### 系统提示词
您可以修改以下文件来自定义LLM行为：

- `prompt/system_prompt_decomposition.txt` - LLM分解提示词
- `prompt/system_prompt_rag_integration.txt` - LLM整合提示词

### RAG搜索实现
目前使用模拟RAG搜索 (`_simulate_rag_search`)，您可以替换为真实的RAG系统：

```python
def _simulate_rag_search(self, symptom_text: str) -> Dict[str, Any]:
    # 替换为您的真实RAG系统调用
    return your_real_rag_system.search(symptom_text)
```

## 🔧 故障排除

### 常见问题

1. **LLM分解失败**
   - 检查API连接
   - 查看分解提示词是否合理
   - 系统会自动使用简单分割作为回退

2. **RAG搜索无结果**
   - 确保RAG系统配置正确
   - 检查症状描述的清晰度
   - 调整搜索参数

3. **LLM整合失败**
   - 检查整合提示词
   - 确保RAG结果格式正确
   - 验证API响应

### 调试信息

每个步骤都会打印详细的处理信息：
```
=== 新的RAG工作流程处理报告 diagnostic_1 ===
1. 聚合报告症状...
2. LLM分解症状...
3. 每个症状RAG搜索...
4. LLM整合所有结果...
```

## 🔄 与其他工作流程对比

| 工作流程 | 特点 | 适用场景 |
|---------|------|----------|
| **新的4步RAG** | 症状分解→RAG→整合 | 复杂症状、需要详细分析 |
| **报告级聚合** | 直接聚合症状处理 | 简单症状、快速处理 |
| **个体处理** | 每个症状单独处理 | 症状独立、无需关联 |
| **智能RAG** | 选择性相信RAG | 已有RAG缓存、需要置信度评估 |

## 📈 性能优化建议

1. **批量处理**: 一次处理多个症状减少API调用
2. **缓存机制**: 缓存RAG搜索结果避免重复查询
3. **并行处理**: 并行执行RAG搜索提高效率
4. **置信度过滤**: 根据置信度调整RAG权重

## 🎯 下一步扩展

1. **真实RAG集成**: 替换模拟RAG为真实系统
2. **置信度评估**: 添加RAG结果置信度评估
3. **可视化**: 添加处理过程可视化
4. **A/B测试**: 与现有工作流程进行效果对比