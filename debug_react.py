#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, '.')

# Change to react directory
os.chdir('examples/modules/react')

# Import the module
import react
import xopt

print("=== Debug React Module ===")

# Test 1: Check if module is registered
print(f"Registered modules: {list(xopt.client()._modules.keys())}")

# Test 2: Start the module
print("\nStarting module...")
try:
    react_instance = xopt.start(
        module='xopt/react',
        configurables={'tool_list': []},
        tunables={}
    )
    print(f"Module instance created: {react_instance}")
    print(f"Module instance type: {type(react_instance)}")
except Exception as e:
    print(f"Error starting module: {e}")
    sys.exit(1)

# Test 3: Call the module
print(f"\nCalling module with 'What is 2+2?'...")
try:
    result = react_instance.call('What is 2+2?')
    print(f"Result: {result}")
    print(f"Result type: {type(result)}")
    if hasattr(result, 'content'):
        print(f"Result content: {repr(result.content)}")
    if hasattr(result, '__dict__'):
        print(f"Result attributes: {result.__dict__}")
except Exception as e:
    print(f"Error calling module: {e}")
    import traceback
    traceback.print_exc()