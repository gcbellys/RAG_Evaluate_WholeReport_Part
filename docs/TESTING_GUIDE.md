# 新RAG工作流程测试指南

## 快速开始测试

### 1. 运行基础测试
```bash
cd /path/to/Rag_Evaluate_WholeReport
python scripts/test_new_rag.py basic
```

### 2. 运行所有测试
```bash
python scripts/test_new_rag.py all
```

### 3. 运行特定测试
```bash
# 单元测试
python scripts/test_new_rag.py unit

# 集成测试
python scripts/test_new_rag.py integration

# 性能测试
python scripts/test_new_rag.py performance
```

## 测试类型

### 1. 基础测试 (Basic Test)
**目的**: 验证基本功能是否正常工作
**使用**: 简单症状集合测试4步流程
**运行**: `python scripts/test_new_rag.py basic`

### 2. 单元测试 (Unit Test)
**目的**: 测试每个独立步骤
**步骤**: 
- 症状聚合
- LLM分解
- RAG搜索
- LLM整合
**运行**: `python scripts/test_new_rag.py unit`

### 3. 集成测试 (Integration Test)
**目的**: 使用真实数据测试完整流程
**数据**: 使用test_set目录中的真实诊断文件
**运行**: `python scripts/test_new_rag.py integration`

### 4. 性能测试 (Performance Test)
**目的**: 测试处理时间和资源使用
**指标**: 
- 处理时间
- 分解效率
- RAG搜索性能
**运行**: `python scripts/test_new_rag.py performance`

## 手动测试

### 使用示例数据测试
```bash
# 使用示例数据运行
python workflows/new_rag_workflow.py --max_files 1

# 使用特定ID范围
python workflows/new_rag_workflow.py --start_id 1 --end_id 2
```

### 创建自定义测试数据
在 `tests/sample_test_data.json` 中添加自定义测试用例。

## 测试输出

### 结果目录结构
```
tests/
├── basic_test_YYYYMMDD_HHMMSS.json      # 基础测试结果
├── unit_test_YYYYMMDD_HHMMSS.json       # 单元测试结果
├── integration_test_YYYYMMDD_HHMMSS.json # 集成测试结果
├── performance_test_YYYYMMDD_HHMMSS.json # 性能测试结果
└── test_summary_YYYYMMDD_HHMMSS.json    # 测试汇总
```

### 验证测试结果

#### 1. 验证JSON格式
```python
import json
from pathlib import Path

# 检查测试结果文件
test_file = Path("tests/test_summary_latest.json")
with open(test_file) as f:
    data = json.load(f)
    print(f"测试状态: {data.get('overall_status')}")
```

#### 2. 验证API响应格式
```python
# 验证器官格式
def validate_organ_format(organ_data):
    required_keys = ['organName', 'anatomicalLocations', 'relevance']
    return all(key in organ_data for key in required_keys)
```

#### 3. 验证分解结果
```python
# 检查分解症状
def validate_decomposition(decomposed_data):
    return 'decomposed_symptoms' in decomposed_data and isinstance(decomposed_data['decomposed_symptoms'], list)
```

## 故障排除

### 常见问题及解决方案

#### 1. API连接失败
```bash
# 检查配置
python -c "from config_loader import ConfigLoader; print(ConfigLoader().config)"

# 测试单个API
python -c "from api_manager import APIManager; am = APIManager(); print(am.test_connectivity())"
```

#### 2. JSON格式错误
```bash
# 验证JSON文件
python -c "import json; json.load(open('tests/latest_result.json'))"
```

#### 3. 数据加载失败
```bash
# 检查数据路径
python -c "from pathlib import Path; print(list(Path('test_set').glob('*.json')))"
```

## 测试用例

### 推荐测试用例

1. **简单症状**: "chest pain"
2. **复杂症状**: "chest pain with shortness of breath and fatigue"
3. **多系统症状**: "headache with nausea and visual disturbances"
4. **系统症状**: "fever with abdominal pain and vomiting"

### 边缘情况测试

1. **空症状**: 无有效症状
2. **重复症状**: 相同症状多次出现
3. **超长症状**: 非常长的症状描述
4. **特殊字符**: 包含特殊字符的症状

## 性能监控

### 监控指标

| 指标 | 正常范围 | 说明 |
|------|----------|------|
| 处理时间 | < 30秒/报告 | 单报告处理时间 |
| 分解症状数 | 1-8个 | 每个报告分解的小症状数量 |
| RAG搜索时间 | < 5秒/症状 | 单个症状的RAG搜索时间 |
| API响应率 | > 80% | 成功响应的API比例 |

### 性能测试命令

```bash
# 运行性能测试
python scripts/test_new_rag.py performance

# 监控内存使用
python -m memory_profiler scripts/test_new_rag.py

# 监控处理时间
time python scripts/test_new_rag.py integration
```

## 自动化测试

### 创建测试脚本

```bash
#!/bin/bash
# 创建自动化测试脚本

echo "开始新RAG工作流程测试..."

# 基础测试
echo "运行基础测试..."
python scripts/test_new_rag.py basic

# 单元测试
echo "运行单元测试..."
python scripts/test_new_rag.py unit

# 集成测试
echo "运行集成测试..."
python scripts/test_new_rag.py integration

# 性能测试
echo "运行性能测试..."
python scripts/test_new_rag.py performance

echo "所有测试完成！"
```

### CI/CD测试

创建 `.github/workflows/test.yml`:

```yaml
name: Test New RAG Workflow

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.8'
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    - name: Run tests
      run: |
        python scripts/test_new_rag.py all
```

## 测试验证清单

### 功能验证
- [ ] 症状聚合正确
- [ ] LLM分解有效
- [ ] RAG搜索运行
- [ ] LLM整合正确
- [ ] JSON格式正确
- [ ] API响应正常

### 性能验证
- [ ] 处理时间合理
- [ ] 内存使用正常
- [ ] 错误处理完善
- [ ] 回退机制有效

### 数据验证
- [ ] 器官名称正确
- [ ] 解剖位置准确
- [ ] 相关性评估合理
- [ ] 格式一致性

## 测试报告模板

测试完成后，查看 `tests/test_summary_latest.json` 获取完整测试报告。

### 测试报告解读

```json
{
  "test_timestamp": "2024-01-01T12:00:00",
  "basic_test_success": true,
  "unit_test_results": {
    "step1_aggregation": {"success": true},
    "step2_decomposition": {"success": true},
    "step3_rag_search": {"success": true},
    "step4_integration": {"success": true}
  },
  "integration_test_results": {
    "total_files": 5,
    "successful_files": 5,
    "failed_files": 0
  }
}
```