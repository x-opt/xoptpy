#!/usr/bin/env python3
"""
Command-line interface for xopt module management
"""

import argparse
import sys
from xopt.commands import (
    cmd_package,
    cmd_install,
    cmd_uninstall,
    cmd_list,
    cmd_run,
    cmd_dev_run,
    cmd_init,
    cmd_sync
)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="xopt module management CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Package command
    package_parser = subparsers.add_parser("package", help="Package a module directory")
    package_parser.add_argument("module_dir", help="Directory containing the module")
    package_parser.add_argument("-o", "--output", help="Output package path")
    package_parser.set_defaults(func=cmd_package)
    
    # Install command
    install_parser = subparsers.add_parser("install", help="Install a module package or current directory")
    install_parser.add_argument("package", nargs="?", help="Path to .xopt package file (optional if in module directory)")
    install_parser.set_defaults(func=cmd_install)
    
    # Uninstall command
    uninstall_parser = subparsers.add_parser("uninstall", help="Uninstall a module")
    uninstall_parser.add_argument("module", help="Module name to uninstall")
    uninstall_parser.set_defaults(func=cmd_uninstall)
    
    # List command
    list_parser = subparsers.add_parser("list", help="List installed modules")
    list_parser.set_defaults(func=cmd_list)
    
    # Run command
    run_parser = subparsers.add_parser("run", help="Run an installed module")
    run_parser.add_argument("module", help="Module name to run")
    run_parser.add_argument("input", help="Input data for the module")
    run_parser.add_argument("-c", "--config", help="JSON config overrides")
    run_parser.set_defaults(func=cmd_run)
    
    # Dev command
    dev_parser = subparsers.add_parser("dev", help="Run a module from development directory")
    dev_parser.add_argument("module_dir", help="Module directory path")
    dev_parser.add_argument("module", help="Module name")
    dev_parser.add_argument("input", help="Input data for the module")
    dev_parser.add_argument("-c", "--config", help="JSON config overrides")
    dev_parser.set_defaults(func=cmd_dev_run)
    
    # Init command
    init_parser = subparsers.add_parser("init", help="Initialize a new xopt project")
    init_parser.set_defaults(func=cmd_init)
    
    # Sync command  
    sync_parser = subparsers.add_parser("sync", help="Sync project dependencies")
    sync_parser.set_defaults(func=cmd_sync)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    args.func(args)


if __name__ == "__main__":
    main()