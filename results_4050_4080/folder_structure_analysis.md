# 📁 results_4050_4080 文件夹结构与结果分析

## 🏗️ 文件夹整体结构

```
results_4050_4080/
├── 📊 分析报告文件
│   ├── complete_evaluation_report.md          # 完整评估报告(MD格式)
│   ├── complete_evaluation_report.txt         # 完整评估报告(TXT格式)
│   ├── api_performance_analysis.txt           # API性能分析报告
│   └── comprehensive_score_analysis.txt       # 综合评分分析
├── 🔍 基线方法结果
│   ├── baseline_results/                      # 基线方法结果目录
│   │   ├── baseline_summary_report_*.json     # 基线方法汇总报告
│   │   └── report:diagnostic_*_baseline_evaluation_standardized.json  # 各报告基线评估结果
├── 🚀 增强方法结果
│   ├── aggregation_results/                   # 增强方法结果目录
│   │   ├── baseline_results/                  # 增强方法中的基线结果
│   │   ├── rag_search_output/                 # RAG搜索输出结果
│   │   │   ├── report_*_ragoutcome_*.jsonl   # RAG搜索结果(JSONL格式)
│   │   │   └── report_*_ragoutcome_*_pretty.json  # RAG搜索结果(美化格式)
│   │   ├── report_*_comprehensive_*.json     # 综合结果文件
│   │   ├── report_*_evaluation_standardized_*.json  # 标准化评估结果
│   │   ├── report_*_user_format_*.json       # 用户格式结果
│   │   └── aggregation_summary_report_*.json # 增强方法汇总报告
└── 📈 对比分析结果
    └── comparison_results/                    # 对比分析结果目录
        ├── summary_report_*.txt               # 对比总结报告
        └── comparison_results/                # 详细对比结果
```

## 📊 文件数量统计

- **总报告数**: 31个 (diagnostic_4050-4080)
- **基线方法文件**: 31个标准化评估文件 + 1个汇总报告
- **增强方法文件**: 31个综合结果文件 + 31个用户格式文件 + 31个标准化评估文件 + 31个RAG搜索输出文件 + 1个汇总报告
- **分析报告文件**: 4个不同格式的分析报告
- **对比分析文件**: 对比总结和详细结果

## 🔍 关键文件类型说明

### 1. **基线方法结果** (`baseline_results/`)
- **文件命名**: `report:diagnostic_{ID}_baseline_evaluation_standardized.json`
- **内容**: 仅使用症状聚合的基线方法评估结果
- **特点**: 不包含RAG搜索，直接LLM预测

### 2. **增强方法结果** (`aggregation_results/`)
- **综合结果文件**: `report_diagnostic_{ID}_comprehensive_*.json`
  - 包含完整的处理流程和结果
  - 文件较大(40KB+)，包含所有中间数据
  
- **用户格式文件**: `report_diagnostic_{ID}_user_format_*.json`
  - 用户友好的结果展示格式
  - 包含基线方法和增强方法的对比
  
- **标准化评估文件**: `report_diagnostic_{ID}_evaluation_standardized_*.json`
  - 标准化的评估结果格式
  - 便于程序化处理和分析

### 3. **RAG搜索输出** (`rag_search_output/`)
- **JSONL格式**: 原始搜索结果，便于流式处理
- **美化格式**: 人类可读的JSON格式，便于分析
- **内容**: 每个分割症状的RAG搜索结果，包含器官和位置信息

## 📈 数据流程分析

### **基线方法流程**
```
症状聚合 → LLM整体预测 → 直接评估 → 保存结果
```

### **增强方法流程**
```
症状聚合 → LLM整体预测 → 智能分割 → RAG搜索 → LLM增强预测 → 评估对比 → 保存结果
```

## 🎯 文件夹特点总结

1. **结构完整**: 包含了从原始数据到最终分析报告的完整链路
2. **格式多样**: 提供了多种格式的结果文件，满足不同使用需求
3. **对比清晰**: 基线方法和增强方法的结果分别存储，便于对比分析
4. **RAG详细**: RAG搜索输出单独保存，便于深入分析知识检索效果
5. **报告全面**: 从技术细节到用户友好的分析报告，覆盖全面

## 💡 使用建议

### **研究人员**
- 查看 `comprehensive_*.json` 文件获取完整技术细节
- 分析 `rag_search_output/` 了解RAG搜索效果
- 对比基线方法和增强方法的差异

### **产品经理**
- 查看 `user_format_*.json` 了解用户视角的结果
- 阅读分析报告了解系统整体表现
- 关注API性能对比和优化建议

### **开发人员**
- 分析 `evaluation_standardized_*.json` 了解评估逻辑
- 查看 `baseline_results/` 和 `aggregation_results/` 的差异
- 参考分析脚本了解数据处理流程
