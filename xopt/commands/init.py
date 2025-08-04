"""Init command for xopt CLI"""

import sys
from pathlib import Path


def cmd_init(args):
    """Initialize a new xopt project"""
    try:
        xopt_dir = Path(".xopt")
        xopt_dir.mkdir(exist_ok=True)
        
        # Create deps.toml
        deps_file = xopt_dir / "deps.toml"
        if not deps_file.exists():
            deps_content = """# xopt module dependencies
[modules]
# "xopt/react" = "0.1.0"
# "xopt/calculator" = "0.1.0"

# Optional: sources for modules (for development)
[sources]
# "xopt/react" = { path = "examples/modules/react" }
# "xopt/calculator" = { path = "examples/modules/calculator" }

# Optional: registries for finding modules
[registries]  
# default = "https://registry.xopt.ai"
# local = "file://./packages"
"""
            deps_file.write_text(deps_content)
            print(f"✅ Created {deps_file}")
        else:
            print(f"📁 {deps_file} already exists")
        
        print(f"\n🎉 Initialized xopt project in {xopt_dir}")
        print("\n📝 Next steps:")
        print(f"   1. Edit {deps_file} to add your module dependencies")
        print(f"   2. Run 'xopt sync' to install dependencies")
        print(f"   3. Create module config files like .xopt/xopt-react.toml")
        
    except Exception as e:
        print(f"Error initializing project: {e}", file=sys.stderr)
        sys.exit(1)