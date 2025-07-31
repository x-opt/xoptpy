#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from react import react_module, calculator, xopt

def main():
    """Simple script to run the ReAct module with a single question"""
    
    # Register modules
    xopt.register(react_module)
    xopt.register(calculator)
    
    # Start the react module
    react = xopt.start(
        module="xopt/react@0.1.0",
        configurables={"tool_list": ["xopt/calculator:0.1.0"]},
        tunables={"react_prompt": "You are a helpful assistant."}
    )
    
    # Get input from command line or prompt
    if len(sys.argv) > 1:
        question = ' '.join(sys.argv[1:])
    else:
        question = input("Question: ")
    
    # Process the question
    print(f"\n❓ Question: {question}")
    print("🤔 Processing...")
    
    try:
        result = react.call(question)
        
        # Show module calls if any were made
        if react.module_calls:
            print("\n🔧 Module calls made:")
            for i, call in enumerate(react.module_calls, 1):
                print(f"   {i}. {call['action']} → {call['module']}")
                print(f"      Input: {call['input']}")
                print(f"      Output: {call['output']}")
        
        print(f"\n🤖 Answer: {result.content}")
        print(f"\n📊 Trace saved to: {react.trace_file}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()