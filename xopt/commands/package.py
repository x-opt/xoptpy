"""Package command for xopt CLI"""

import sys
from xopt.client import client


def cmd_package(args):
    """Package a module directory"""
    try:
        output_path = client().package(args.module_dir, args.output)
        print(f"Package created: {output_path}")
    except Exception as e:
        print(e)
        print(f"Error packaging module: {e}", file=sys.stderr)
        sys.exit(1)