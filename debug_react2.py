#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, '.')

# Change to react directory
os.chdir('examples/modules/react')

# Import the module
import react
import xopt

print("=== Debug React Module Tunables ===")

# Test: Start the module and check tunable values
react_instance = xopt.start(
    module='xopt/react',
    configurables={'tool_list': []},
    tunables={}  # Let it load from xopt.yaml
)

# Check if tunables are loaded
print(f"Client config: {xopt.client().config}")
print(f"React prompt tunable: {repr(react.react_prompt())}")
print(f"Output parser tunable: {repr(react.output_parser())}")

# Test LLM call directly
print("\n=== Testing LLM call ===")
try:
    response = xopt.call_llm("What is 2+2?", model="ollama/llama3.2:3b")
    print(f"LLM Response: {repr(response)}")
    
    # Test parsing
    parsed = react.parse_react_response(response)
    print(f"Parsed response: {parsed}")
except Exception as e:
    print(f"LLM call error: {e}")
    import traceback
    traceback.print_exc()