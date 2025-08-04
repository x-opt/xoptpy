"""List command for xopt CLI"""

import sys
from xopt.client import client


def cmd_list(args):
    """List installed modules"""
    try:
        installed = client().list_installed()
        if not installed:
            print("No modules installed")
            return
        
        print("Installed modules:")
        for name, info in installed.items():
            print(f"  {name}@{info['version']} - {info['installed_at']}")
    except Exception as e:
        print(f"Error listing modules: {e}", file=sys.stderr)
        sys.exit(1)