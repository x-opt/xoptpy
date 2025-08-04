#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, '.')

# Change to react directory  
os.chdir('examples/modules/react')

# Import the module
import react
import xopt

print("=== Debug Client Config Structure ===")

# Check client config structure
client = xopt.client()
print(f"Full client config: {client.config}")
print(f"Config keys: {list(client.config.keys())}")
print(f"Config values: {list(client.config.values())}")

print("\n=== Testing tunable lookup manually ===")
# Test the tunable lookup logic manually
def debug_tunable_lookup(name):
    print(f"\nLooking for tunable '{name}':")
    for key, module_config in client.config.items():
        print(f"  Checking module '{key}': {type(module_config)}")
        if isinstance(module_config, dict):
            print(f"    Has 'tunables'? {'tunables' in module_config}")
            if 'tunables' in module_config:
                print(f"    Tunables: {list(module_config['tunables'].keys())}")
                if name in module_config['tunables']:
                    print(f"    Found '{name}': {repr(module_config['tunables'][name][:100])}...")
                    return module_config['tunables'][name]
        else:
            print(f"    Module config is not dict: {module_config}")
    print(f"  Not found, returning default")
    return f"Default {name}"

result1 = debug_tunable_lookup("react_prompt")
result2 = debug_tunable_lookup("output_parser")

print(f"\nManual lookup results:")
print(f"react_prompt: {repr(result1[:50])}...")
print(f"output_parser: {repr(result2)}")

print(f"\nActual tunable calls:")
print(f"react_prompt(): {repr(react.react_prompt()[:50])}...")
print(f"output_parser(): {repr(react.output_parser())}")