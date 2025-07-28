# xopt

<div align="center">
  <img src="logo.jpg" alt="xopt Logo" width="200"/>
  
  **The Open Source Registry for AI Modules and Tools**
  
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
  [![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
  [![GitHub issues](https://img.shields.io/github/issues/x-opt/xopt)](https://github.com/x-opt/xopt/issues)
</div>

---

## 🚀 What is xopt?

**xopt** is the open source registry for composable AI modules and tools. Think of it as npm for AI components - discover, share, and optimize reusable AI functionality across your entire organization.

Stop rebuilding the same AI components. Start composing intelligent systems from battle-tested modules.

```bash
# Install and run any AI module instantly
xopt run nlp/sentiment-analyzer text="This product is amazing!"

# Compose complex workflows from simple modules
xopt run research-agent topic="quantum computing" --with nlp/summarizer
```

## 🎯 Why xopt Exists

**The Problem**: Every team rebuilds the same AI components - sentiment analysis, text summarization, data extraction. This wastes time, creates inconsistencies, and prevents optimization at scale.

**Our Solution**: A centralized registry where teams can:
- **Share** reusable AI modules and tools
- **Discover** battle-tested components from the community  
- **Optimize** entire workflows, not just individual pieces
- **Compose** complex AI systems from simple building blocks

## ✨ Key Features

### 🔧 **Instant Module Execution**
```bash
# No setup, no configuration - just run
xopt run nlp/sentiment-analyzer text="Great product!"
```

### 📦 **npm-like Experience**
- Semantic versioning and dependency management
- Global and local module installation
- Automatic dependency resolution

### 🧩 **True Composability**
- Modules expose standardized interfaces
- Chain outputs → inputs seamlessly
- Build complex workflows from simple parts

### ⚡ **Optimization Ready**
- Every module exposes tunable parameters
- System-wide optimization across module boundaries
- Real-world performance metrics and benchmarks

### 🌍 **Community Driven**
- Open source registry with public/private modules
- Community ratings and quality scores
- Documentation and examples for every module

## 🚀 Quick Start

### Installation

```bash
pip install xoptpy
```

### Run Your First Module

```bash
# Analyze sentiment instantly
xopt run nlp/sentiment-analyzer text="This startup idea is brilliant!"

# Summarize long text
xopt run nlp/text-summarizer --input document.txt

# Process data in batches
xopt run data/batch-processor --config batch_config.yaml
```

### Browse Available Modules

```bash
# Search the registry
xopt search sentiment
xopt search "text processing"

# Get module details
xopt module info nlp/sentiment-analyzer

# See what's trending
xopt search --trending
```

## 🏗️ For Developers

### Create Your First Module

```yaml
# manifest.yaml
apiVersion: xopt-registry/v1
kind: module
metadata:
  name: my-classifier
  namespace: ml
  version: 1.0.0
  description: Custom text classifier

spec:
  interface:
    input_schema:
      type: object
      properties:
        text: {type: string}
    output_schema:
      type: object
      properties:
        category: {type: string}
        confidence: {type: number}
  
  implementation:
    type: function
    entry_point: ./classifier.py:classify
    requirements:
      - scikit-learn>=1.0.0
```

### Test and Publish

```bash
# Test locally
xopt run . text="sample input"

# Publish to registry
xopt module publish

# Install and use in other projects
xopt install ml/my-classifier
```

---

<div align="center">

**Ready to stop rebuilding AI components?**

⭐ **[Star this repo](https://github.com/x-opt/xoptpy)** • 📖 **[Read the docs](https://docs.xopt.dev)** • 💬 **[Join Discord](https://discord.gg/QbXQ82Cz)**

*Building the future of composable AI, one module at a time.* 🚀

</div>
