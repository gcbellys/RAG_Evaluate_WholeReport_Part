# RAG_Evaluate_WholeReport 重构系统使用说明

## 🎯 系统概述

这是一个重构后的RAG评估系统，核心组件与 `Rag_Evaluate` 完全一致，同时添加了**症状聚合处理**功能。系统支持两种处理模式：

1. **基线方法**：逐个症状处理（与Rag_Evaluate一致）
2. **聚合方法**：报告级症状聚合处理（新增功能）

## 🏗️ 系统架构

### 核心组件（与Rag_Evaluate一致）
- `src/api_manager.py` - API客户端管理
- `src/evaluator.py` - 评估引擎
- `src/data_loader.py` - 数据加载器
- `src/config_loader.py` - 配置管理

### 新增聚合模块
- `src/aggregation_processor.py` - 症状聚合处理器
- `src/aggregation_evaluator.py` - 聚合结果评估器

### 工作流程
- `workflows/main_workflow.py` - 基线方法工作流程
- `workflows/aggregation_workflow.py` - 聚合方法工作流程
- `workflows/comparison_workflow.py` - 对比分析工作流程

## 🚀 使用方法

### 1. 运行基线方法（逐个症状处理）

```bash
# 处理指定范围的报告
python workflows/main_workflow.py \
    --data_path test_set \
    --output_dir results_baseline \
    --start_id 1 \
    --end_id 10 \
    --max_files 5

# 处理所有报告
python workflows/main_workflow.py \
    --data_path test_set \
    --output_dir results_baseline
```

### 2. 运行聚合方法（报告级聚合处理）

```bash
# 处理指定范围的报告
python workflows/aggregation_workflow.py \
    --data_path test_set \
    --output_dir results_aggregation \
    --start_id 1 \
    --end_id 10 \
    --max_files 5

# 处理所有报告
python workflows/aggregation_workflow.py \
    --data_path test_set \
    --output_dir results_aggregation
```

### 3. 运行对比分析（同时运行两种方法）

```bash
# 对比分析指定范围的报告
python workflows/comparison_workflow.py \
    --data_path test_set \
    --output_dir results_comparison \
    --start_id 1 \
    --end_id 10 \
    --max_files 5

# 对比分析所有报告
python workflows/comparison_workflow.py \
    --data_path test_set \
    --output_dir results_comparison
```

## 📊 输出结果

### 基线方法输出
```
results_baseline/
├── report_diagnostic_1_baseline_evaluation_standardized.json
├── report_diagnostic_2_baseline_evaluation_standardized.json
└── baseline_summary_report_20250101_120000.json
```

### 聚合方法输出
```
results_aggregation/
├── report_diagnostic_1_aggregate_evaluation_20250101_120000.json
├── report_diagnostic_1_aggregate_standardized_20250101_120000.json
└── aggregation_summary_report_20250101_120000.json
```

### 对比分析输出
```
results_comparison/
├── baseline_results/
├── aggregation_results/
├── comparison_results/
│   ├── comparison_results_20250101_120000.json
│   └── summary_report_20250101_120000.txt
```

## 🔍 核心特性

### 症状聚合处理
- **智能聚合**：将同一报告的所有症状合并为一个整体
- **上下文关联**：考虑症状间的相互关系
- **效率提升**：每个报告只需1次API调用（vs 每个症状1次）

### 评估指标
- **Precision (精确率)**：40%权重
- **Recall (召回率)**：40%权重
- **Overgeneration Penalty (过度生成惩罚)**：20%权重
- **Overall Score (综合评分)**：100分制

### 多API支持
- OpenAI (GPT-4)
- Anthropic (Claude-3.5-Sonnet)
- Google Gemini
- Moonshot AI
- DeepSeek

## ⚙️ 配置说明

### 配置文件结构
```yaml
# config/config.yaml
api_config:
  openai:
    api_key_env: OPENAI_API_KEY
    model: gpt-4
    base_url: https://api.openai.com/v1
  
  anthropic:
    api_key_env: ANTHROPIC_API_KEY
    model: claude-3-5-sonnet-20241022

system_prompt: "你是一个医学专家，请根据症状识别相关的器官和解剖位置..."
```

### 环境变量设置
```bash
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"
export GEMINI_API_KEY="your-gemini-key"
export MOONSHOT_API_KEY="your-moonshot-key"
export DEEPSEEK_API_KEY="your-deepseek-key"
```

## 📈 性能对比

### 基线方法 vs 聚合方法

| 指标 | 基线方法 | 聚合方法 | 改进 |
|------|----------|----------|------|
| API调用次数 | 症状数 × API数 | 1 × API数 | 减少80%+ |
| 处理时间 | 较长 | 较短 | 显著提升 |
| 症状关联性 | 独立处理 | 综合考虑 | 更准确 |
| 资源消耗 | 较高 | 较低 | 更高效 |

## 🛠️ 故障排除

### 常见问题

1. **API密钥错误**
   ```bash
   # 检查环境变量
   echo $OPENAI_API_KEY
   echo $ANTHROPIC_API_KEY
   ```

2. **配置文件路径错误**
   ```bash
   # 使用绝对路径
   --config /path/to/config.yaml
   ```

3. **数据目录不存在**
   ```bash
   # 检查数据路径
   ls -la test_set/
   ```

### 调试模式
```bash
# 启用详细日志
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python -u workflows/main_workflow.py --data_path test_set --output_dir results
```

## 🔄 工作流程对比

### 基线方法流程
```
报告 → 症状1 → API调用 → 评估
     → 症状2 → API调用 → 评估
     → 症状3 → API调用 → 评估
     → 汇总结果
```

### 聚合方法流程
```
报告 → 症状聚合 → 单次API调用 → 评估 → 结果
```

### 对比分析流程
```
报告 → 并行处理 → 基线方法 + 聚合方法 → 性能对比 → 分析报告
```

## 📝 注意事项

1. **数据格式**：确保输入数据符合诊断报告格式
2. **API限制**：注意各API的调用频率限制
3. **内存使用**：大量报告处理时注意内存消耗
4. **结果验证**：建议先用小数据集测试

## 🎉 总结

重构后的系统保持了与 `Rag_Evaluate` 的完全兼容性，同时通过症状聚合处理显著提升了处理效率和准确性。系统支持灵活的配置和多种运行模式，适合不同规模的医学症状分析需求。
