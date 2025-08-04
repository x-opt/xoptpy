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
        
        # Extract action - only match content on the same line as Action:
        action_match = re.search(r"Action:([^\n]*)", text)
        action = None
        action_input = None
        
        if action_match:
            action_text = action_match.group(1).strip()
            # Only set action if it's not empty, not just whitespace, and has actual content
            if (action_text and 
                action_text.lower() not in ['none', 'null', 'n/a', ''] and
                len(action_text.strip()) > 0):
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

output_parser = xopt_client.tunable(
    name="output_parser",
    description="Model to parse LLM output using Pydantic",
)

tool_list = xopt_client.configurable(
    name="tool_list",
    description="List of tools that the ReAct module can use",
)



def parse_react_response(llm_response: str) -> Dict[str, Any]:
    """Parse LLM response using configurable regex parser"""
    try:
        # Get the regex pattern from tunable
        regex_pattern = output_parser()

        print(f"Using regex pattern: {regex_pattern}")
        
        # Use the regex pattern to parse the response
        match = re.search(regex_pattern, llm_response, re.DOTALL)
        
        if match:
            result = {
                "thought": match.group('thought').strip() if match.group('thought') else "",
                "action": match.group('action').strip() if match.group('action') else None,
                "action_input": match.group('action_input').strip() if match.group('action_input') else None,
                "final_answer": match.group('final_answer').strip() if match.group('final_answer') else None
            }
            
            # Clean up action - only set if it has actual content
            if result["action"]:
                action_text = result["action"]
                if not action_text or action_text.lower() in ['none', 'null', 'n/a', '']:
                    result["action"] = None
                    result["action_input"] = None
            
            # Strip quotes from action_input if present
            if result["action_input"]:
                action_input = result["action_input"]
                if action_input.startswith('"') and action_input.endswith('"'):
                    result["action_input"] = action_input[1:-1]
                elif action_input.startswith("'") and action_input.endswith("'"):
                    result["action_input"] = action_input[1:-1]
            
            # If we have an action, prioritize it over any premature final answer
            if result["action"] and result["action_input"] and result["final_answer"]:
                result["final_answer"] = None
            
            return result
        else:
            # No match found, return empty result
            return {
                "thought": "",
                "action": None,
                "action_input": None,
                "final_answer": None
            }
    except Exception:
        # Fallback to original parsing if regex parser fails
        parsed = ReactLLMResponse.from_text(llm_response)
        return {
            "thought": parsed.thought or "",
            "action": parsed.action,
            "action_input": parsed.action_input,
            "final_answer": parsed.final_answer
        }


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
        details = xopt.details(tool)
        tool_details.append(details)
    
    tool_descriptions = []
    for tool in tool_details:
        tool_descriptions.append(f"Tool name: {tool['name']}\nDescription: {tool['long_description']}")
    
    tools_text = "\n\n".join(tool_descriptions) if tool_descriptions else "No tools available."
    
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

    print(parsed)
        
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
        tunables=[react_prompt, output_parser],
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
    # Start the react module - let it load tunables from xopt.yaml
    react = xopt.start(
        module="xopt/react@0.1.0",
        configurables={"tool_list": []},
        tunables={}  # Let xopt.yaml provide the tunables
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
