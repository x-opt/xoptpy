"""Install command for xopt CLI"""

import sys
import tempfile
from pathlib import Path
from xopt.client import client


def cmd_install(args):
    """Install a module package or current directory"""
    try:
        if args.package:
            # File mode: install specified .xopt file
            module_name = client().install(args.package)
            print(f"Module {module_name} installed successfully")
        else:
            # Directory mode: package current directory and install
            current_dir = Path(".")
            
            # Check if current directory has xopt.yaml
            if not (current_dir / "xopt.yaml").exists():
                print("No xopt.yaml found in current directory. Either provide a .xopt file or run in a module directory.", file=sys.stderr)
                sys.exit(1)
            
            print("📦 Packaging current directory...")
            
            # Package to a temporary location
            with tempfile.TemporaryDirectory() as temp_dir:
                # Package the current directory
                package_path = client().package(str(current_dir), output_dir=temp_dir)
                
                print(f"✅ Package created: {Path(package_path).name}")
                print("🔧 Installing to local package manager...")
                
                # Install the package
                module_name = client().install(package_path)
                print(f"🎉 Module {module_name} installed successfully")
                
    except Exception as e:
        print(e)
        print(f"Error installing module: {e}", file=sys.stderr)
        sys.exit(1)