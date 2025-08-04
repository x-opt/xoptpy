"""Dev command for xopt CLI"""

import sys
import subprocess
import os
from pathlib import Path


def cmd_dev_run(args):
    """Run a module from a development directory"""
    try:
        module_dir = Path(args.module_dir)
        if not module_dir.exists():
            print(f"Module directory {module_dir} does not exist", file=sys.stderr)
            sys.exit(1)
        
        # Check if we're running as a standalone executable
        if getattr(sys, 'frozen', False):
            # We're in a PyInstaller bundle - call runner directly
            from xopt.runner import main as runner_main
            
            # Save original argv and replace with runner arguments
            original_argv = sys.argv
            sys.argv = ['xopt.runner', '--module-dir', str(module_dir), '--module', args.module, '--input', args.input]
            
            if args.config:
                sys.argv.extend(['--config', args.config])
            
            try:
                runner_main()
            except SystemExit as e:
                if e.code != 0:
                    sys.exit(e.code)
            finally:
                # Restore original argv
                sys.argv = original_argv
        else:
            # Development mode - use subprocess with Python
            cmd = [sys.executable, "-m", "xopt.runner", "--module-dir", str(module_dir), "--module", args.module, "--input", args.input]
            
            if args.config:
                cmd.extend(["--config", args.config])
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(result.stdout.strip())
            else:
                print(f"Error running module: {result.stderr}", file=sys.stderr)
                sys.exit(1)
    
    except Exception as e:
        print(f"Error running module: {e}", file=sys.stderr)
        sys.exit(1)