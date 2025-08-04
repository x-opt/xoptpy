#!/usr/bin/env python3
"""
Module runner for executing xopt modules in isolated virtual environments
"""

import sys
import json
import importlib.util
import os
from pathlib import Path
from typing import Dict, Any, Optional
import argparse
import yaml


def load_module_from_path(module_path: Path, module_name: str):
    """Load a Python module from a file path"""
    # Look for the main module file - try common patterns
    candidates = [
        module_path / f"{module_name.split('/')[-1]}.py",
        module_path / "main.py",
        module_path / "__init__.py"
    ]
    
    # Also check any .py files in the directory
    for py_file in module_path.glob("*.py"):
        if py_file.name not in ["__init__.py", "main.py"]:
            candidates.insert(0, py_file)
    
    for candidate in candidates:
        if candidate.exists():
            spec = importlib.util.spec_from_file_location("xopt_module", candidate)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                sys.modules["xopt_module"] = module
                spec.loader.exec_module(module)
                return module
    
    raise ImportError(f"Could not find module file in {module_path}")


def run_installed_module(module_name: str, input_data: str, config_overrides: Optional[Dict[str, Any]] = None) -> str:
    """Run an installed module with given input"""
    from xopt.client import client
    
    # Find installed module
    installed_modules = client().list_installed()
    if module_name not in installed_modules:
        raise ValueError(f"Module {module_name} is not installed")
    
    module_info = installed_modules[module_name]
    module_dir = Path(module_info["installed_at"])
    
    # Handle engine references
    if module_info.get("type") == "engine_reference":
        engine = module_info.get("engine")
        engine_name = engine.split("@")[0] if "@" in engine else engine
        
        if engine_name not in installed_modules:
            raise ValueError(f"Referenced engine '{engine}' is not installed")
        
        # Use the engine's directory and virtual environment
        engine_info = installed_modules[engine_name]
        engine_dir = Path(engine_info["installed_at"])
        
        # Load module config (this module's tunables/configurables)
        config_path = module_dir / "xopt.yaml"
        if config_path.exists():
            with open(config_path) as f:
                config = yaml.safe_load(f)
                if 'name' in config:
                    # New format
                    module_config = {
                        'tunables': config.get('tunables', {}),
                        'configurables': config.get('configurables', {})
                    }
                else:
                    # Legacy format
                    module_spec = list(config.keys())[0]
                    module_config = config[module_spec]
        else:
            module_config = module_info.get("config", {})
        
        # Apply config overrides
        if config_overrides:
            if "tunables" in config_overrides:
                module_config.setdefault("tunables", {}).update(config_overrides["tunables"])
            if "configurables" in config_overrides:
                module_config.setdefault("configurables", {}).update(config_overrides["configurables"])
        
        # Execute using the engine's directory
        return _execute_module(engine_dir, engine_name, module_config, input_data)
    else:
        # Local engine - use this module's directory
        return _execute_local_module(module_dir, module_name, module_info, config_overrides, input_data)


def _execute_module(module_dir: Path, module_name: str, module_config: Dict[str, Any], input_data: str) -> str:
    """Execute a module with given configuration"""
    import os
    from xopt.client import client
    
    # Set up environment for module execution
    original_cwd = os.getcwd()
    os.chdir(module_dir)
    
    try:
        # Load and register ALL installed modules so they can be discovered by other modules
        installed_modules = client().list_installed()
        for installed_name, installed_info in installed_modules.items():
            if installed_name != module_name:  # Don't double-load the target module
                try:
                    installed_path = Path(installed_info["installed_at"])
                    load_module_from_path(installed_path, installed_name)
                except Exception:
                    # Skip modules that can't be loaded
                    pass
        
        # Create module spec for legacy compatibility  
        module_spec = f"{module_name}@1.0.0"  # Default version for execution
        
        # Update client configuration with module config BEFORE loading modules
        client_instance = client()
        client_instance.config = {module_spec: module_config}
        
        # Load and register the target module
        module_py = load_module_from_path(module_dir, module_name)
        
        # Find and start the module
        import xopt
        if module_name in client()._modules:
            module_instance = xopt.start(
                module=module_name,
                configurables=module_config.get("configurables", {}),
                tunables=module_config.get("tunables", {})
            )
            
            # Execute the module
            result = module_instance.call(input_data)
            
            # Return result content
            if hasattr(result, 'content'):
                return str(result.content)
            else:
                return str(result)
        else:
            raise ValueError(f"Module {module_name} not found in registry after loading")
    
    finally:
        os.chdir(original_cwd)


def _execute_local_module(module_dir: Path, module_name: str, module_info: Dict[str, Any], config_overrides: Optional[Dict[str, Any]], input_data: str) -> str:
    """Execute a local engine module"""
    # Load module configuration
    config_path = module_dir / "xopt.yaml"
    if config_path.exists():
        with open(config_path) as f:
            config = yaml.safe_load(f)
            if 'name' in config:
                # New format
                module_config = {
                    'tunables': config.get('tunables', {}),
                    'configurables': config.get('configurables', {})
                }
            else:
                # Legacy format
                module_spec = list(config.keys())[0]
                module_config = config[module_spec]
    else:
        module_config = module_info.get("config", {})
    
    # Apply config overrides
    if config_overrides:
        if "tunables" in config_overrides:
            module_config.setdefault("tunables", {}).update(config_overrides["tunables"])
        if "configurables" in config_overrides:
            module_config.setdefault("configurables", {}).update(config_overrides["configurables"])
    
    return _execute_module(module_dir, module_name, module_config, input_data)


def main():
    """Main entry point for module runner"""
    parser = argparse.ArgumentParser(description="Run xopt modules in isolated environments")
    parser.add_argument("--module", required=True, help="Module name to run")
    parser.add_argument("--input", required=True, help="Input data for the module")
    parser.add_argument("--config", help="JSON string with config overrides")
    parser.add_argument("--module-dir", help="Path to module directory (for development)")
    
    args = parser.parse_args()
    
    try:
        # Parse config overrides if provided
        config_overrides = None
        if args.config:
            config_overrides = json.loads(args.config)
        
        if args.module_dir:
            # Development mode - run from module directory
            module_dir = Path(args.module_dir)
            original_cwd = os.getcwd()
            os.chdir(module_dir)
            
            try:
                # Load module
                module_py = load_module_from_path(module_dir, args.module)
                
                # Load config
                config_path = module_dir / "xopt.yaml"
                if config_path.exists():
                    with open(config_path) as f:
                        config = yaml.safe_load(f)
                        if 'name' in config:
                            # New format
                            module_config = {
                                'tunables': config.get('tunables', {}),
                                'configurables': config.get('configurables', {})
                            }
                            module_spec = f"{config['name']}@{config.get('version', '1.0.0')}"
                        else:
                            # Legacy format
                            module_spec = list(config.keys())[0]
                            module_config = config[module_spec]
                else:
                    module_config = {}
                    module_spec = f"{args.module}@1.0.0"
                
                # Apply overrides
                if config_overrides:
                    if "tunables" in config_overrides:
                        module_config.setdefault("tunables", {}).update(config_overrides["tunables"])
                    if "configurables" in config_overrides:
                        module_config.setdefault("configurables", {}).update(config_overrides["configurables"])
                
                # Set up client config - ensure proper nested structure
                from xopt.client import client
                client_instance = client()
                client_instance.config = {module_spec: module_config}
                
                # Start and run module
                import xopt
                module_name = module_spec.split("@")[0]
                module_instance = xopt.start(
                    module=args.module,
                    configurables=module_config.get("configurables", {}),
                    tunables=module_config.get("tunables", {})
                )
                
                result = module_instance.call(args.input)
                output = result.content if hasattr(result, 'content') else str(result)
                print(output)
            
            finally:
                os.chdir(original_cwd)
        else:
            # Production mode - run installed module  
            result = run_installed_module(args.module, args.input, config_overrides)
            print(result)
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()