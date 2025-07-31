#!/usr/bin/env python3
"""
Convenience script to run the React module with different configurations
"""

import subprocess
import sys
import json
import argparse
from pathlib import Path


def run_react_installed(input_text: str, config_overrides: dict = None):
    """Run installed React module"""
    cmd = ["python3", "-m", "xopt", "run", "xopt/react", input_text]
    
    if config_overrides:
        cmd.extend(["-c", json.dumps(config_overrides)])
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(result.stdout.strip())
    else:
        print(f"Error: {result.stderr}", file=sys.stderr)
        sys.exit(1)


def run_react_dev(input_text: str, config_overrides: dict = None):
    """Run React module from development directory"""
    module_dir = Path("examples/modules/react")
    
    cmd = ["python3", "-m", "xopt", "dev-run", str(module_dir), "xopt/react", input_text]
    
    if config_overrides:
        cmd.extend(["-c", json.dumps(config_overrides)])
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(result.stdout.strip())
    else:
        print(f"Error: {result.stderr}", file=sys.stderr)
        sys.exit(1)


def install_and_run(package_path: str, input_text: str, config_overrides: dict = None):
    """Install package and run it"""
    print(f"Installing {package_path}...")
    install_result = subprocess.run(["python3", "-m", "xopt", "install", package_path], 
                                  capture_output=True, text=True)
    
    if install_result.returncode != 0:
        print(f"Installation failed: {install_result.stderr}", file=sys.stderr)
        sys.exit(1)
    
    print("Installation successful. Running module...")
    run_react_installed(input_text, config_overrides)


def main():
    parser = argparse.ArgumentParser(description="Run React module in different modes")
    parser.add_argument("input", help="Input text for the React module")
    parser.add_argument("--mode", choices=["installed", "dev", "package"], default="installed",
                       help="Run mode: installed (use installed module), dev (from source), package (install and run)")
    parser.add_argument("--package", help="Path to .xopt package (required for package mode)")
    parser.add_argument("--prompt", help="Custom React prompt override")
    parser.add_argument("--tools", nargs="*", default=["xopt/calculator:0.1.0"],
                       help="List of tools to configure")
    
    args = parser.parse_args()
    
    # Build config overrides
    config_overrides = {}
    
    if args.prompt:
        config_overrides["tunables"] = {"react_prompt": args.prompt}
    
    if args.tools:
        config_overrides["configurables"] = {"tool_list": args.tools}
    
    # Run based on mode
    if args.mode == "installed":
        run_react_installed(args.input, config_overrides if config_overrides else None)
    
    elif args.mode == "dev": 
        run_react_dev(args.input, config_overrides if config_overrides else None)
    
    elif args.mode == "package":
        if not args.package:
            print("Error: --package required for package mode", file=sys.stderr)
            sys.exit(1)
        install_and_run(args.package, args.input, config_overrides if config_overrides else None)
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()