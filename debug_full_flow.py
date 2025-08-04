#!/usr/bin/env python3

import sys
import os
import yaml
from pathlib import Path

sys.path.insert(0, '.')

print("=== Simulating Full Runner Flow ===")

# Simulate what the runner does
module_dir = Path('examples/modules/react')
original_cwd = os.getcwd()
os.chdir(module_dir)

try:
    # Import the module (this creates the client and loads config)
    print("1. Importing module...")
    import react
    import xopt
    from xopt.client import client
    
    print(f"   Initial client config: {list(client().config.keys())}")
    
    # Load config like runner does
    print("2. Loading config like runner...")
    config_path = Path("xopt.yaml")
    with open(config_path) as f:
        config = yaml.safe_load(f)
        module_config = {
            'tunables': config.get('tunables', {}),
            'configurables': config.get('configurables', {})
        }
        module_spec = f"{config['name']}@{config.get('version', '1.0.0')}"
    
    print(f"   Module spec: {module_spec}")
    print(f"   Module config keys: {list(module_config.keys())}")
    
    # Set client config like runner does
    print("3. Setting client config...")
    client_instance = client()
    client_instance.config = {module_spec: module_config}
    
    print(f"   New client config keys: {list(client_instance.config.keys())}")
    print(f"   Config structure: {client_instance.config}")
    
    # Test tunables
    print("4. Testing tunables...")
    print(f"   react_prompt(): {react.react_prompt()[:50]}...")
    print(f"   output_parser(): {react.output_parser()}")
    
    # Start module like runner does
    print("5. Starting module...")
    module_name = module_spec.split("@")[0]
    module_instance = xopt.start(
        module=module_name,
        configurables=module_config.get("configurables", {}),
        tunables=module_config.get("tunables", {})
    )
    
    # Call module
    print("6. Calling module...")
    result = module_instance.call("What is 2+2?")
    print(f"   Result: {result}")
    print(f"   Result type: {type(result)}")
    print(f"   Result content: {repr(result.content)}")
    
    # Test the final output logic
    print("7. Testing output logic...")
    output = result.content if hasattr(result, 'content') else str(result)
    print(f"   Final output: {repr(output)}")
    
finally:
    os.chdir(original_cwd)