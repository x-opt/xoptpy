"""Uninstall command for xopt CLI"""

import sys
from xopt.client import client


def cmd_uninstall(args):
    """Uninstall a module"""
    try:
        success = client().uninstall(args.module)
        if not success:
            sys.exit(1)
    except Exception as e:
        print(f"Error uninstalling module: {e}", file=sys.stderr)
        sys.exit(1)