# 🧠 RAG_Evaluate_WholeReport

A comprehensive Python framework for evaluating medical diagnostic reports using Retrieval-Augmented Generation (RAG) techniques with symptom aggregation.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Usage](#usage)
- [Directory Structure](#directory-structure)
- [Configuration](#configuration)
- [API Support](#api-support)
- [Evaluation Methods](#evaluation-methods)
- [Contributing](#contributing)
- [License](#license)
- [Troubleshooting](#troubleshooting)

## 🎯 Overview

RAG_Evaluate_WholeReport is a sophisticated medical diagnostic evaluation system that leverages Large Language Models (LLMs) and RAG (Retrieval-Augmented Generation) techniques to analyze medical reports. The system implements two primary evaluation approaches:

- **Baseline Method**: Traditional symptom-by-symptom processing
- **Aggregation Method**: Report-level symptom aggregation with enhanced RAG integration

## ✨ Features

### Core Capabilities
- **Multi-API Support**: Compatible with OpenAI, Anthropic, DeepSeek, Gemini, and Moonshot APIs
- **Symptom Aggregation**: Intelligent grouping and processing of medical symptoms
- **RAG Integration**: Knowledge retrieval for enhanced diagnostic accuracy
- **Comprehensive Evaluation**: Detailed performance metrics and comparative analysis
- **Batch Processing**: Efficient handling of multiple diagnostic reports

### Evaluation Metrics
- **Overall Score**: Weighted performance across all dimensions
- **Precision**: Accuracy of predicted diagnoses
- **Recall**: Completeness of symptom identification
- **Over-generation Penalty**: Control for excessive predictions

## 🏗️ Architecture

### System Components
```
┌─────────────────────────────────────────────────────────────┐
│                    RAG_Evaluate_WholeReport                  │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────────┐ │
│  │   API       │  │   Symptom    │  │   RAG               │ │
│  │   Clients   │  │   Processing │  │   Integration       │ │
│  └─────────────┘  └──────────────┘  └─────────────────────┘ │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────────┐ │
│  │   Workflow  │  │   Evaluation │  │   Reporting         │ │
│  │   Management│  │   Engine     │  │   System            │ │
│  └─────────────┘  └──────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Workflow Process
1. **Data Ingestion**: Load diagnostic reports (JSON format)
2. **Symptom Extraction**: Parse and identify medical symptoms
3. **Processing Strategy**: Apply baseline or aggregation method
4. **RAG Enhancement**: Retrieve relevant medical knowledge
5. **Evaluation**: Generate comprehensive performance metrics
6. **Reporting**: Create detailed analysis reports

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- API keys for supported LLM providers

### Setup Instructions
```bash
# Clone the repository
git clone https://github.com/gcbellys/RAG_Evaluate_WholeReport_Part.git
cd RAG_Evaluate_WholeReport_Part

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure API keys
cp config/config.yaml config/config_local.yaml
# Edit config/config_local.yaml with your API keys
```

### Environment Configuration
```bash
# Set up environment variables
export OPENAI_API_KEY="your_openai_key"
export ANTHROPIC_API_KEY="your_anthropic_key"
export DEEPSEEK_API_KEY="your_deepseek_key"
export GEMINI_API_KEY="your_gemini_key"
export MOONSHOT_API_KEY="your_moonshot_key"
```

## 📖 Usage

### Quick Start
```bash
# Run complete evaluation workflow
python bin/run_complete_workflow.py --data_path test_set --output_dir results

# Run specific evaluation range
python bin/run_smart_workflow.py --start_id 4050 --end_id 4080

# Run concurrent evaluation
python bin/run_concurrent_evaluation.py --data_path test_set --max_workers 4

# Single report evaluation
python start.py --mode baseline --start_id 4050 --end_id 4050
```

### Configuration Options
```bash
# Use custom configuration