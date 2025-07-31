# xopt YAML Interface

xopt uses YAML files to define, manage, and optimize prompts. This provides version control, team collaboration, and automated optimization capabilities.

## Standard YAML Format

```yaml
# Required metadata about your prompt collection
metadata:
  name: "my_app"
  version: "1.0.0"
  description: "Application prompts for xopt optimization"
  created: "2024-01-15"
  author: "Development Team"

# Static prompts - complete text that can be optimized as units
prompts:
  system_message: |
    You are a helpful AI assistant specialized in code analysis.
    You provide clear, actionable feedback to developers.
  
  welcome: "Hello! Welcome to our platform."
  
  error_fallback: "I apologize, but I encountered an error. Please try again."

# Template prompts - contain variables {like_this}
templates:
  code_review: |
    Please review this {language} code for {focus_areas}:
    
    ```{language}
    {code_content}
    ```
    
    Provide feedback on quality, performance, and best practices.
  
  task_instruction: |
    Task: {action} the following {content_type}
    
    Requirements:
    - Use {methodology} approach
    - Focus on {priority_aspects}
    - Provide {output_format} output
    
    Content: {content}

# Configuration for optimization and runtime
config:
  # DSPy optimization settings
  optimization:
    enabled: true
    target_metric: "accuracy"
    max_iterations: 50
    validation_split: 0.2
    
  # Model configuration
  model:
    provider: "openai"
    name: "gpt-4"
    temperature: 0.1
    max_tokens: 2000
    
  # Constraints for optimization
  constraints:
    max_prompt_length: 4000
    preserve_variables: true
    maintain_format: true

# What to optimize for
optimization_targets:
  primary:
    - metric: "task_accuracy"
      weight: 0.7
    - metric: "response_clarity" 
      weight: 0.3
      
  secondary:
    - metric: "response_speed"
      weight: 0.4
    - metric: "token_efficiency"
      weight: 0.6

# Test cases for validation during optimization
test_cases:
  - name: "code_review_test"
    prompt: "code_review"
    inputs:
      language: "Python"
      focus_areas: "performance"
      code_content: "def slow_func(): time.sleep(1)"
    expected_qualities:
      - "identifies performance issue"
      - "suggests improvements"
      - "clear and actionable"
```

## Usage in Code

```python
from xoptpy import create_client_from_yaml

# Load prompts from YAML
client = create_client_from_yaml("my_prompts.yaml")

# Use static prompts
system_msg = client.prompt("system_message")

# Use templates with variables
review = client.template("code_review", 
                        language="Python",
                        focus_areas="security", 
                        code_content="user_input = input()")

# Get optimization info
optimization_data = client.optimize()
```

## Application Integration

```python
class MyService:
    def __init__(self):
        # All prompts loaded from version-controlled YAML
        self.xopt = create_client_from_yaml("service_prompts.yaml")
    
    def process_request(self, user_input):
        # Use prompts anywhere in your code
        system = self.xopt.prompt("system_message")
        task = self.xopt.template("task_instruction", 
                                 action="process",
                                 content=user_input)
        return f"{system}\n{task}"
```

## Benefits

### 🔧 **Easy Management**
- Prompts separated from code
- Version control friendly
- Team collaboration ready

### 🎯 **Optimization Ready**
- Define optimization targets
- Include validation test cases
- Ready for automated DSPy tuning

### 📁 **Version Control**
- Track prompt changes over time
- Review prompt modifications
- Rollback to previous versions

### 🚀 **Production Ready**
- Different YAML files for environments
- A/B testing with file swaps
- Hot reloading capabilities

## File Organization

```
my_project/
├── prompts/
│   ├── auth_service.yaml      # Authentication prompts
│   ├── chat_bot.yaml          # Chat bot prompts
│   └── code_analysis.yaml     # Code analysis prompts
├── src/
│   ├── auth_service.py        # Loads auth_service.yaml
│   ├── chat_bot.py           # Loads chat_bot.yaml
│   └── analyzer.py           # Loads code_analysis.yaml
└── tests/
    └── test_prompts.py       # Test prompt functionality
```

## Optimization Workflow

1. **Define prompts in YAML** with optimization targets
2. **Load in application** with `create_client_from_yaml()`
3. **Use prompts** with `client.prompt()` and `client.template()`
4. **Run optimization** with DSPy integration
5. **Update YAML** with optimized prompts
6. **Deploy** updated prompts without code changes

This makes xopt perfect for enterprise AI applications where prompts need professional management, optimization, and deployment workflows.