"""Sync command for xopt CLI"""

import sys
import toml
from pathlib import Path
from xopt.client import client


def cmd_sync(args):
    """Sync project dependencies from .xopt/deps.toml"""
    try:
        xopt_dir = Path(".xopt")
        deps_file = xopt_dir / "deps.toml"
        
        if not deps_file.exists():
            print("No .xopt/deps.toml found. Run 'xopt init' to create a project.", file=sys.stderr)
            sys.exit(1)
        
        # Load dependencies
        deps = toml.load(deps_file)
        modules = deps.get("modules", {})
        sources = deps.get("sources", {})
        
        installed = client().list_installed()
        
        for module_name, version in modules.items():
            if module_name in installed:
                print(f"✅ {module_name}@{version} already installed")
                continue
            
            # Check if we have a local source
            if module_name in sources:
                source_info = sources[module_name]
                if "path" in source_info:
                    source_path = Path(source_info["path"])
                    if source_path.exists():
                        print(f"📦 Packaging {module_name} from {source_path}")
                        package_path = client().package(str(source_path))
                        print(f"📥 Installing {module_name}")
                        client().install(package_path)
                        continue
            
            print(f"❌ Module {module_name}@{version} not found locally")
            print(f"   Add to sources in deps.toml or provide .xopt package")
        
        print("\n🎉 Sync complete!")
        
    except Exception as e:
        print(f"Error syncing dependencies: {e}", file=sys.stderr)
        sys.exit(1)