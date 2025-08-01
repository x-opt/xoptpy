from pydantic import BaseModel, Field
from typing import List, Optional, Tuple, Dict, Any
import xopt
from xopt.models import StepResult, Module, Context
import json
import math
import re


class ReactInput(BaseModel):
    """Input for ReAct step"""
    input: str


class ReactOutput(BaseModel):
    """Output from ReAct step"""
    thought: str
    action: Optional[str] = None
    action_input: Optional[Dict[str, Any]] = None
    observation: Optional[str] = None
    response: Optional[str] = None


class ReactLLMResponse(BaseModel):
    """Structured parser for ReAct LLM responses"""
    thought: Optional[str] = Field(None, description="The reasoning thought")
    action: Optional[str] = Field(None, description="The action to take")
    action_input: Optional[str] = Field(None, description="The input for the action")
    final_answer: Optional[str] = Field(None, description="The final answer")
    
    @classmethod
    def from_text(cls, text: str) -> "ReactLLMResponse":
        """Parse ReAct response from text using field extraction"""
        # Extract thought
        thought_match = re.search(r"Thought:\s*(.+?)(?=\n(?:Action|Final Answer)|\Z)", text, re.DOTALL)
        thought = thought_match.group(1).strip() if thought_match else None
        
        # Extract action
        action_match = re.search(r"Action:\s*([^\s\n]+)", text)
        action = None
        action_input = None
        
        if action_match:
            action_text = action_match.group(1).strip()
            if action_text.lower() not in ['none', 'null', 'n/a']:
                action = action_text
                
                # Extract action input
                action_input_match = re.search(r"Action Input:\s*(.+?)(?=\n(?:Observation|Final Answer)|\Z)", text, re.DOTALL)
                if action_input_match:
                    action_input = action_input_match.group(1).strip()
                    # Strip quotes if present
                    if action_input.startswith('"') and action_input.endswith('"'):
                        action_input = action_input[1:-1]
                    elif action_input.startswith("'") and action_input.endswith("'"):
                        action_input = action_input[1:-1]
        
        # Extract final answer - get the last occurrence if multiple exist
        final_answer_matches = re.findall(r"Final Answer:\s*(.+?)(?=\n\n|\n(?:Thought|Action)|$)", text, re.DOTALL)
        final_answer = final_answer_matches[-1].strip() if final_answer_matches else None
        
        return cls(
            thought=thought,
            action=action,
            action_input=action_input, 
            final_answer=final_answer
        )


xopt_client = xopt.client()

# Global variable to track current trace instance for LLM calls  
_current_trace_instance = None

def set_current_trace_instance(instance):
    """Set the current trace instance for LLM calls"""
    global _current_trace_instance
    _current_trace_instance = instance


class ReActContext(Context):
    """ReAct context implementation that accumulates reasoning steps and observations"""
    
    def __init__(self, query: str):
        self.query = query
        self.reasoning_history = []
        self.current_observation = None
    
    def add_reasoning(self, content: str):
        """Add reasoning content to history"""
        self.reasoning_history.append(content)
    
    def set_observation(self, observation: str):
        """Set the current observation from tool execution"""
        self.current_observation = observation
    
    def get_context(self, text: Optional[str] = None) -> str:
        """Get the full context for ReAct reasoning"""
        context_parts = []
        
        # Add query
        context_parts.append(f"User question: {self.query}")
        
        # Add reasoning history
        if self.reasoning_history:
            context_parts.append("\nPrevious reasoning:")
            for reasoning in self.reasoning_history:
                context_parts.append(reasoning)
        
        # Add current observation if available
        if self.current_observation:
            context_parts.append(f"\nObservation: {self.current_observation}")
            context_parts.append("\nContinue reasoning:")
        
        # Add new text if provided
        if text:
            context_parts.append(f"\n{text}")
            
        return "\n".join(context_parts)

react_prompt = xopt_client.tunable(
    name="react_prompt",
    description="Prompt for the ReAct module",
)

tool_list = xopt_client.configurable(
    name="tool_list",
    description="List of tools that the ReAct module can use",
)



def parse_react_response(llm_response: str) -> Dict[str, Any]:
    """Parse LLM response using Pydantic parser"""
    parsed = ReactLLMResponse.from_text(llm_response)
    
    # Convert to dictionary format expected by existing code
    result = {
        "thought": parsed.thought or "",
        "action": parsed.action,
        "action_input": parsed.action_input,
        "final_answer": parsed.final_answer
    }
    
    # If we have an action, prioritize it over any premature final answer
    # The LLM should stop after Action Input and let the system provide the observation
    if result["action"] and result["action_input"] and result["final_answer"]:
        # Clear the premature final answer - the LLM should not provide this yet
        result["final_answer"] = None
    
    return result


@xopt.step
def react_starter(input_data: str) -> StepResult:
    """
    Starter step that initializes ReAct context and begins reasoning.
    
    Args:
        input_data: Initial user query string
    
    Returns:
        StepResult: Points to react_step with context
    """
    # Create initial context
    context = ReActContext(input_data)
    
    # Return step result pointing to react_step
    return StepResult(
        action="step_call",
        content="Starting ReAct reasoning",
        module_name="react_step", 
        module_input={"context": context, "previous_action_result": None}
    )


@xopt.step
def react_step(step_input: Dict[str, Any]) -> StepResult:
    """
    Full ReAct implementation using LLM reasoning.
    
    Args:
        step_input: Dict with 'context' and 'previous_action_result'
    
    Returns:
        StepResult: Either a module call or final response
    """
    # Extract parameters from step input
    context = step_input.get("context")
    previous_action_result = step_input.get("previous_action_result")
    
    # Add previous action result as observation if available
    if previous_action_result:
        context.set_observation(previous_action_result)
    # Get available tools from configurables
    available_tools = tool_list
    tool_details = []
    for tool in available_tools:
        tool_details.append(xopt.details(tool))
    
    tool_descriptions = []
    for tool in tool_details:
        tool_descriptions.append(f"{tool['name']}: {tool['long_description']}")
    
    tools_text = "\n".join(tool_descriptions) if tool_descriptions else "No tools available."
    
    # Build prompt using context
    base_prompt = react_prompt()
    current_prompt = f"""{base_prompt}

Available tools:
{tools_text}

{context.get_context()}

Response:"""
        
    llm_response = xopt.call_llm(current_prompt, model="ollama/llama3.2:3b", trace_instance=_current_trace_instance)
    
    # Add this reasoning to context
    context.add_reasoning(llm_response)
        
    parsed = parse_react_response(llm_response)
        
    if parsed["final_answer"]:
        return StepResult(
            action="response",
            content=parsed["final_answer"]
        )
        
    if parsed["action"] and parsed["action_input"]:
        action = parsed["action"]
        action_input = parsed["action_input"]
            
        # Return module call with context so instance knows to continue ReAct flow
        return StepResult(
            action="module_call",
            content=f"Need to call {action} with: {action_input}",
            module_name=action,
            module_input={"input": action_input, "context": context}
        )
    else:
        return StepResult(
            action="response",  
            content=parsed["thought"] or "I'm not sure how to help with that."
        ) 

@xopt.module
def react_module() -> Module:
    """
    ReAct module that processes input and generates a response.
    
    Returns:
        Module: Configured ReAct module.
    """

    module = Module(
        name="xopt/react",
        version="0.1.0",
        description="ReAct framework",
        long_description="This module takes a user's input and generates a response using the ReAct framework. It can call other modules for specific actions. The input is a question or request, and the output is a response based on reasoning and available tools. The question or request can be arbitrary. The success of the response is based on the tools available.",
        tunables=[react_prompt],
        configurables=[tool_list]
    )

    module.register(
        name="react_starter",
        step=react_starter,
        input_type=str
    )
    
    module.register(
        name="react_step", 
        step=react_step,
        input_type=dict
    )

    module.set_start_step("react_starter")
    
    return module

xopt.register(react_module)

if __name__ == "__main__":
    # Start the react module
    react = xopt.start(
        module="xopt/react@0.1.0",
        configurables={"tool_list": []},
        tunables={"react_prompt": react_prompt()}
    )
    
    # Interactive loop
    print("ReAct Assistant with Calculator Tool")
    print("Type 'quit' to exit")
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ['quit', 'exit']:
            break
            
        try:
            result = react.call(user_input)
            print(f"Assistant: {result.content}")
        except Exception as e:
            print(f"Error: {e}")
