#!/usr/bin/env python3
"""
Simple xopt functionality test - tests core commands without breaking existing installation
"""

import subprocess
import tempfile
import shutil
import os
import sys
from pathlib import Path

def run_cmd(cmd, description):
    """Run command and show result"""
    print(f"🔄 {description}")
    print(f"   Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"✅ PASS")
            if result.stdout:
                # Show first line of output
                first_line = result.stdout.strip().split('\n')[0]
                print(f"   Output: {first_line}")
        else:
            print(f"❌ FAIL")
            if result.stderr:
                print(f"   Error: {result.stderr.strip()[:100]}")
        return result.returncode == 0
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def main():
    print("🧪 xopt Simple Functionality Test")
    print("=" * 40)
    
    if not Path("examples/modules/react").exists():
        print("❌ Must run from xoptpy project root")
        sys.exit(1)
    
    passed = 0
    total = 0
    
    # Test basic commands
    print("\n=== Basic Commands ===")
    tests = [
        (["xopt", "--help"], "Display help"),
        (["xopt", "list"], "List installed modules"),
        (["make", "version"], "Show version info"),
        (["make", "check-deps"], "Check dependencies"),
    ]
    
    for cmd, desc in tests:
        total += 1
        if run_cmd(cmd, desc):
            passed += 1
    
    # Test packaging (non-destructive)
    print("\n=== Module Packaging ===")
    
    # Clean up any existing packages first
    for pkg in Path(".").glob("xopt_*.xopt"):
        if pkg.is_file():
            pkg.unlink()
    
    tests = [
        (["xopt", "package", "examples/modules/react"], "Package react module"),
        (["xopt", "package", "examples/modules/react-custom"], "Package custom module"),
    ]
    
    for cmd, desc in tests:
        total += 1
        if run_cmd(cmd, desc):
            passed += 1
    
    # Check if packages were created
    for pkg_name in ["xopt_react-0.1.0.xopt", "xopt_react-custom-0.1.0.xopt"]:
        if Path(pkg_name).exists():
            print(f"✅ Package created: {pkg_name}")
        else:
            print(f"❌ Package missing: {pkg_name}")
    
    # Test project workflow in temp directory
    print("\n=== Project Workflow ===")
    with tempfile.TemporaryDirectory() as temp_dir:
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)
            
            tests = [
                (["xopt", "init"], "Initialize project"),
                (["xopt", "sync"], "Sync dependencies"),
            ]
            
            for cmd, desc in tests:
                total += 1
                if run_cmd(cmd, desc):
                    passed += 1
                    
        finally:
            os.chdir(original_cwd)
    
    # Test module execution (only if modules are installed)
    print("\n=== Module Execution ===")
    
    # Check if modules are installed
    result = subprocess.run(["xopt", "list"], capture_output=True, text=True)
    if result.returncode == 0 and "xopt/react@0.1.0" in result.stdout:
        tests = [
            (["xopt", "run", "xopt/react", "Hello world"], "Run react module"),
        ]
        
        for cmd, desc in tests:
            total += 1
            if run_cmd(cmd, desc):
                passed += 1
    else:
        print("⚠️  Skipping execution tests - modules not installed")
    
    # Test error handling
    print("\n=== Error Handling ===")
    error_tests = [
        (["xopt", "run", "nonexistent/module", "test"], "Run non-existent module (should fail)"),
        (["xopt", "package", "nonexistent/directory"], "Package non-existent directory (should fail)"),
    ]
    
    for cmd, desc in error_tests:
        total += 1
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:  # Should fail
            print(f"✅ {desc}")
            passed += 1
        else:
            print(f"❌ {desc}")
    
    # Clean up
    print("\n=== Cleanup ===")
    for pkg in Path(".").glob("xopt_*.xopt"):
        if pkg.is_file():
            pkg.unlink()
            print(f"   Removed {pkg}")
    
    # Summary
    print(f"\n{'='*40}")
    print(f"TEST SUMMARY")
    print(f"{'='*40}")
    print(f"✅ Passed: {passed}/{total}")
    print(f"📊 Pass Rate: {passed/total*100:.1f}%")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        return True
    else:
        print(f"\n⚠️  {total-passed} tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)