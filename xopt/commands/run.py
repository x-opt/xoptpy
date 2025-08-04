"""Run command for xopt CLI"""

import sys
import subprocess
import os
from pathlib import Path
from xopt.client import client


def cmd_run(args):
    """Run an installed module"""
    try:
        # Find installed module
        installed = client().list_installed()
        if args.module not in installed:
            print(f"Module {args.module} is not installed", file=sys.stderr)
            sys.exit(1)
        
        module_info = installed[args.module]
        
        # For engine reference modules, use the engine's environment
        if module_info.get("type") == "engine_reference":
            engine = module_info.get("engine")
            engine_name = engine.split("@")[0] if "@" in engine else engine
            if engine_name not in installed:
                print(f"Referenced engine {engine_name} not installed", file=sys.stderr)
                sys.exit(1)
            engine_info = installed[engine_name]
            module_dir = Path(engine_info["installed_at"])
        else:
            module_dir = Path(module_info["installed_at"])
            
        venv_python = module_dir / "venv" / ("Scripts" if os.name == "nt" else "bin") / "python"
        
        # Prepare config overrides
        config_json = None
        if args.config:
            config_json = args.config
        
        # Build command
        cmd = [str(venv_python), "-m", "xopt.runner", "--module", args.module, "--input", args.input]
        if config_json:
            cmd.extend(["--config", config_json])
        
        # For engine reference modules, run from engine directory
        if module_info.get("type") == "engine_reference":
            run_dir = module_dir  # Engine module directory
        else:
            run_dir = module_dir
            
        # Run in module's virtual environment
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(run_dir))
        
        if result.returncode == 0:
            print(result.stdout.strip())
        else:
            print(f"Error running module: {result.stderr}", file=sys.stderr)
            sys.exit(1)
    
    except Exception as e:
        print(f"Error running module: {e}", file=sys.stderr)
        sys.exit(1)