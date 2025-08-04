#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

# Import the modules
from examples.modules.react.react import react_module
from examples.modules.calculator.calculator import calculator_module
import xopt

def test_react():
    """Test the react module with a simple query"""
    try:
        # Register both modules
        xopt.register(calculator_module)
        xopt.register(react_module)
        
        # Start the react module with calculator as a tool
        react = xopt.start(
            module="xopt/react@0.1.0",
            configurables={"tool_list": ["xopt/calculator@0.1.0"]},
            tunables={}  # Use default tunable values from xopt.yaml
        )
        
        # Test with simple greeting
        print("Testing react module with 'hey'...")
        result = react.call("hey")
        print(f"Result: {result.content}")
        print(f"Action: {result.action}")
        
        # Test with math question
        print("\nTesting react module with math question...")
        result2 = react.call("What is 2 + 2?")
        print(f"Result: {result2.content}")
        print(f"Action: {result2.action}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_react()