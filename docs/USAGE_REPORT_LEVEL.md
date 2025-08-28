# 报告级症状聚合处理使用指南

## 概述

本系统新增了报告级症状聚合处理功能，允许您将同一报告中的所有症状作为一个整体进行处理，而不是单独处理每个症状。

## 新功能介绍

### 1. 报告级处理 (Report-Level Processing)
- **功能**: 将同一报告中的所有症状聚合为一个整体，让API基于所有症状的综合分析来预测需要检查的器官和解剖位置
- **优势**: 考虑症状之间的关联性，提供更全面的医学推理
- **使用**: `python workflows/report_level_workflow.py`

### 2. 对比工作流程 (Comparison Workflow)
- **功能**: 同时运行个体症状处理和报告级聚合处理，进行对比分析
- **优势**: 可以清楚地看到两种处理模式的差异和改进效果
- **使用**: `python workflows/comparison_workflow.py`

## 使用方法

### 方法一：直接运行报告级处理

```bash
cd /path/to/Rag_Evaluate_WholeReport

# 运行所有报告
python workflows/report_level_workflow.py

# 运行特定范围的报告
python workflows/report_level_workflow.py --start_id 1 --end_id 10

# 限制处理文件数量
python workflows/report_level_workflow.py --max_files 5
```

### 方法二：使用便捷脚本

```bash
cd /path/to/Rag_Evaluate_WholeReport

# 运行报告级处理
python scripts/run_report_level.py

# 运行对比分析
python scripts/run_comparison.py
```

### 方法三：运行对比工作流程

```bash
cd /path/to/Rag_Evaluate_WholeReport

# 运行对比工作流程
python workflows/comparison_workflow.py

# 运行特定范围的对比
python workflows/comparison_workflow.py --start_id 1 --end_id 5 --max_files 3
```

## 输出结果

### 报告级处理结果
- **目录**: `results_report_level/`
- **文件格式**:
  - `report_{report_id}_aggregate_evaluation_{timestamp}.json` - 详细结果
  - `report_{report_id}_aggregate_standardized_{timestamp}.json` - 标准化结果
  - `summary_report_aggregate_{timestamp}.json` - 汇总报告

### 对比分析结果
- **目录**: `results_comparison/`
- **文件格式**:
  - `comparison_{report_id}_{timestamp}.json` - 单个报告详细对比
  - `comparison_summary_{report_id}_{timestamp}.json` - 简化对比摘要
  - `overall_comparison_summary_{timestamp}.json` - 整体对比汇总

## 结果解读

### 对比分析中的关键指标

1. **Precision Improvement**: 精确率改进程度
2. **Recall Improvement**: 召回率改进程度
3. **Score Improvement**: 总体评分改进程度
4. **Organ Coverage**: 器官覆盖度对比
5. **Location Coverage**: 解剖位置覆盖度对比

### 示例输出解读

```json
{
  "api_specific_comparisons": {
    "openai": {
      "average_precision_improvement": 12.5,
      "average_recall_improvement": 8.3,
      "average_score_improvement": 10.7,
      "improvement_count": 15
    }
  }
}
```

## 配置说明

系统使用相同的配置文件 (`config/config.yaml`)，无需额外配置。

## 注意事项

1. **API调用次数**: 报告级处理减少了API调用次数（每个报告一次，而不是每个症状一次）
2. **处理时间**: 报告级处理通常更快，因为减少了API调用次数
3. **结果差异**: 由于处理逻辑不同，结果可能会有显著差异，这属于正常现象
4. **内存使用**: 报告级处理可能会使用更多内存来存储聚合数据

## 故障排除

如果遇到问题，请检查：

1. API配置是否正确
2. 网络连接是否正常
3. 数据文件是否存在且格式正确
4. 查看 `logs/` 目录下的日志文件

## 扩展使用

您可以通过修改以下文件来自定义报告级处理逻辑：

- `prompt/system_prompt_report_level.txt` - 系统提示词
- `workflows/report_level_workflow.py` - 处理逻辑
- `workflows/comparison_workflow.py` - 对比分析逻辑