<div align="center">
  <img src="logo.jpg" alt="xoptpy Logo" width="200"/>
</div>

**eXtreme OPTimization** - Declarative framework for building and optimizing agentic AI systems

Create optimized agents with natural language descriptions. No prompt engineering required.

```python
from xoptpy import AutoAgent
from xoptpy.core.llm_provider import Budget

# Create an intelligent agent from a simple description
agent = AutoAgent(
    'analyze customer feedback and extract key insights',
    budget=Budget.MEDIUM
).prepare()

# Use it immediately  
insights = agent("The product is amazing but shipping was slow")
```

## ✨ Key Features

### 🧠 **LLM-Powered Task Understanding**
- Natural language task descriptions → intelligent agent architectures
- Automatic domain detection (medical, financial, technical, etc.)
- Complexity analysis and capability inference
- No manual prompt engineering needed

### 💰 **Budget-Aware Architecture** 
- **LOW**: Fast & cheap (1-2s, simple architectures)
- **MEDIUM**: Balanced performance (2-5s, moderate complexity)
- **HIGH**: Premium quality (5-15s, sophisticated multi-module systems)

### 🔧 **Optimizable by Design**
- All modules expose `tunable_parameters` for DSPy-style optimization
- No "black box" code that optimizers can't control
- Parameter constraints prevent optimization gaps
- Tool learning from usage patterns

### 🛠️ **Intelligent Tool Integration**
- Automatic tool suggestion based on task analysis
- Built-in tools (web search, PDF processing, data analysis)
- Custom tool registration and learning
- Usage pattern optimization

## 🚀 Quick Start

### Installation

```bash
# Core installation
pip install xoptpy

# With LLM providers  
pip install xoptpy[openai]     # OpenAI support
pip install xoptpy[anthropic]  # Anthropic support

# Full installation
pip install xoptpy[all]
```

### Setup

```bash
# Choose your LLM provider
export XOPTPY_LLM_PROVIDER=openai
export OPENAI_API_KEY=your-api-key

# Or use Anthropic
export XOPTPY_LLM_PROVIDER=anthropic  
export ANTHROPIC_API_KEY=your-api-key
```

Works without API keys (uses mock LLM for development).

### Basic Usage

```python
from xoptpy import AutoAgent
from xoptpy.core.llm_provider import Budget

# Research assistant
research_agent = AutoAgent(
    'research recent developments in AI and summarize key findings',
    budget=Budget.HIGH
).prepare()

results = research_agent("neural architecture search")

# Data analysis agent  
analysis_agent = AutoAgent(
    'analyze sales data and identify trends',
    budget=Budget.MEDIUM
).prepare()

insights = analysis_agent("sales_data.csv")

# Quick classification
classifier = AutoAgent(
    'classify customer feedback sentiment', 
    budget=Budget.LOW
).prepare()

sentiment = classifier("The product is okay but could be better")
```

### With Custom Tools

```python
def literature_search(query: str) -> str:
    # Your custom research tool
    return f"Research results for: {query}"

def data_processor(filepath: str) -> str:
    # Your custom data processing 
    return f"Processed data from: {filepath}"

agent = AutoAgent(
    'comprehensive research analysis with data processing',
    tools=[literature_search, data_processor],
    budget=Budget.HIGH
).prepare()

result = agent("analyze market trends for renewable energy")
```

## 🏗️ How It Works

1. **LLM Task Analysis**: Understands your natural language description
2. **Architecture Design**: Creates optimal module composition for your budget  
3. **Parameter Generation**: Configures optimizable parameters
4. **Tool Integration**: Automatically suggests and binds relevant tools
5. **Agent Compilation**: Builds executable agent with full optimization support

### Budget Impact

```python
# Fast & cheap
quick_agent = AutoAgent('summarize text', budget=Budget.LOW)
# → Single module, gpt-3.5-turbo, <2s response

# Balanced  
standard_agent = AutoAgent('analyze customer data', budget=Budget.MEDIUM) 
# → 1-2 modules, gpt-4, 2-5s response

# Premium quality
premium_agent = AutoAgent('comprehensive research analysis', budget=Budget.HIGH)
# → 3+ modules with planning & memory, gpt-4-turbo, 5-15s response
```

## 📚 Documentation

- **[Getting Started](docs/docs/intro.md)** - Installation and basic usage
- **[API Reference](docs/docs/api.md)** - Complete API documentation  
- **[Architecture Guide](docs/docs/architecture.md)** - How xoptpy works internally
- **[Budget Guide](docs/docs/budgets.md)** - Choosing the right performance level
- **[Examples](examples/)** - Real-world usage examples

## 🎯 Why xoptpy?

### vs Manual Prompt Engineering
- **Automatic**: No manual prompt crafting needed
- **Intelligent**: LLM understands task requirements  
- **Optimizable**: All parameters exposed for training

### vs DSPy
- **Full Control**: No arbitrary code optimizers can't touch
- **Budget Aware**: Automatic cost/performance trade-offs
- **LLM Architecture**: Intelligent module composition

### vs LangChain  
- **Optimization First**: Everything designed for parameter tuning
- **Declarative**: Natural language → working agent
- **Budget Intelligence**: Cost-aware architectural decisions

## 🛣️ Roadmap

- ✅ **AutoAgent API** - Declarative agent creation
- ✅ **LLM-powered task analysis** - Intelligent requirement understanding  
- ✅ **Budget-aware architectures** - Performance vs cost optimization
- 🔲 **Agent Garden** - Reusable agent repository and composition
- 🔲 **Domain Knowledge** - Textbook/Wikipedia integration for specialized agents
- 🔲 **DSPy Integration** - Advanced prompt optimization
- 🔲 **LangGraph Support** - Complex workflow patterns
- 🔲 **MLFlow Integration** - Experiment tracking and model management

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines for details.

---

**Create optimized AI agents in seconds, not hours.** 🚀