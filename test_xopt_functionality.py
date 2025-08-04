#!/usr/bin/env python3
"""
Comprehensive test script for xopt CLI functionality
Tests all commands and workflows to ensure everything is working correctly.
"""

import subprocess
import tempfile
import shutil
import json
import os
import sys
from pathlib import Path
import time

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

class XoptTester:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        self.test_results = []
        
        # Check if we're in the right directory
        if not Path("examples/modules/react").exists():
            print(f"{Colors.RED}❌ Must run from xoptpy project root directory{Colors.END}")
            sys.exit(1)
    
    def run_command(self, cmd, description="", expect_success=True, capture_output=True):
        """Run a command and return result"""
        print(f"{Colors.BLUE}🔄 {description}{Colors.END}")
        print(f"   Command: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
        
        try:
            if isinstance(cmd, str):
                result = subprocess.run(cmd, shell=True, capture_output=capture_output, text=True, timeout=60)
            else:
                result = subprocess.run(cmd, capture_output=capture_output, text=True, timeout=60)
            
            success = result.returncode == 0 if expect_success else result.returncode != 0
            
            if success:
                print(f"{Colors.GREEN}✅ PASS{Colors.END}")
                if result.stdout and capture_output:
                    print(f"   Output: {result.stdout.strip()[:200]}...")
                self.passed += 1
                self.test_results.append((description, "PASS", ""))
            else:
                print(f"{Colors.RED}❌ FAIL{Colors.END}")
                if result.stderr and capture_output:
                    print(f"   Error: {result.stderr.strip()[:200]}...")
                if result.stdout and capture_output:
                    print(f"   Output: {result.stdout.strip()[:200]}...")
                self.failed += 1
                self.test_results.append((description, "FAIL", result.stderr.strip() if result.stderr else ""))
            
            return result
            
        except subprocess.TimeoutExpired:
            print(f"{Colors.RED}❌ TIMEOUT{Colors.END}")
            self.failed += 1
            self.test_results.append((description, "TIMEOUT", "Command timed out"))
            return None
        except Exception as e:
            print(f"{Colors.RED}❌ ERROR: {e}{Colors.END}")
            self.failed += 1
            self.test_results.append((description, "ERROR", str(e)))
            return None
    
    def test_basic_commands(self):
        """Test basic CLI functionality"""
        print(f"\n{Colors.BOLD}=== Testing Basic Commands ==={Colors.END}")
        
        # Test help
        self.run_command(["xopt", "--help"], "Display help")
        
        # Test version info
        self.run_command(["make", "version"], "Check version information")
        
        # Test list (should work even if empty)
        self.run_command(["xopt", "list"], "List installed modules")
    
    def test_packaging(self):
        """Test module packaging"""
        print(f"\n{Colors.BOLD}=== Testing Module Packaging ==={Colors.END}")
        
        # Clean up any existing packages
        for pkg in Path(".").glob("*.xopt"):
            if pkg.is_file():
                pkg.unlink()
        
        # Test packaging base react module
        result = self.run_command(
            ["xopt", "package", "examples/modules/react"],
            "Package react module (local engine)"
        )
        
        # Check if package was created
        react_pkg = Path("xopt_react-0.1.0.xopt")
        if react_pkg.exists():
            print(f"{Colors.GREEN}✅ Package file created: {react_pkg}{Colors.END}")
        else:
            print(f"{Colors.RED}❌ Package file not found{Colors.END}")
            self.failed += 1
        
        # Test packaging custom react module
        self.run_command(
            ["xopt", "package", "examples/modules/react-custom"],
            "Package react-custom module (engine reference)"
        )
        
        # Check if custom package was created
        custom_pkg = Path("xopt_react-custom-0.1.0.xopt")
        if custom_pkg.exists():
            print(f"{Colors.GREEN}✅ Custom package file created: {custom_pkg}{Colors.END}")
        else:
            print(f"{Colors.RED}❌ Custom package file not found{Colors.END}")
            self.failed += 1
    
    def test_installation(self):
        """Test module installation"""
        print(f"\n{Colors.BOLD}=== Testing Module Installation ==={Colors.END}")
        
        # Install base react module from package
        react_pkg = Path("xopt_react-0.1.0.xopt")
        if react_pkg.exists():
            self.run_command(
                ["xopt", "install", str(react_pkg)],
                "Install react module from package"
            )
        
        # Install custom module from package
        custom_pkg = Path("xopt_react-custom-0.1.0.xopt")
        if custom_pkg.exists():
            self.run_command(
                ["xopt", "install", str(custom_pkg)],
                "Install react-custom module from package"
            )
        
        # Test directory-based installation
        with tempfile.TemporaryDirectory() as temp_dir:
            # Copy react-custom to temp directory
            temp_module = Path(temp_dir) / "test-module"
            shutil.copytree("examples/modules/react-custom", temp_module)
            
            # Change to temp directory and test install
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_module)
                self.run_command(
                    ["xopt", "install"],
                    "Directory-based installation"
                )
            finally:
                os.chdir(original_cwd)
        
        # List installed modules
        result = self.run_command(["xopt", "list"], "List installed modules after installation")
        
        # Verify modules are listed
        if result and result.stdout:
            if "xopt/react@0.1.0" in result.stdout:
                print(f"{Colors.GREEN}✅ React module listed{Colors.END}")
            else:
                print(f"{Colors.YELLOW}⚠️  React module not found in list{Colors.END}")
                self.warnings += 1
            
            if "xopt/react-custom@0.1.0" in result.stdout:
                print(f"{Colors.GREEN}✅ React-custom module listed{Colors.END}")
            else:
                print(f"{Colors.YELLOW}⚠️  React-custom module not found in list{Colors.END}")
                self.warnings += 1
    
    def test_execution(self):
        """Test module execution"""
        print(f"\n{Colors.BOLD}=== Testing Module Execution ==={Colors.END}")
        
        # Test running base module
        self.run_command(
            ["xopt", "run", "xopt/react", "What is 2+2?"],
            "Run react module"
        )
        
        # Test running custom module (engine reference)
        self.run_command(
            ["xopt", "run", "xopt/react-custom", "What is 5*6?"],
            "Run react-custom module (engine reference)"
        )
        
        # Test dev mode with absolute path
        abs_path = Path("examples/modules/react").resolve()
        self.run_command(
            ["xopt", "dev", str(abs_path), "xopt/react", "Hello world"],
            "Dev mode with absolute path"
        )
    
    def test_project_workflow(self):
        """Test project initialization and workflow"""
        print(f"\n{Colors.BOLD}=== Testing Project Workflow ==={Colors.END}")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)
                
                # Test project initialization
                self.run_command(["xopt", "init"], "Initialize xopt project")
                
                # Check if .xopt directory was created
                xopt_dir = Path(".xopt")
                if xopt_dir.exists():
                    print(f"{Colors.GREEN}✅ .xopt directory created{Colors.END}")
                    
                    # Check if deps.toml was created
                    deps_file = xopt_dir / "deps.toml"
                    if deps_file.exists():
                        print(f"{Colors.GREEN}✅ deps.toml created{Colors.END}")
                    else:
                        print(f"{Colors.RED}❌ deps.toml not found{Colors.END}")
                        self.failed += 1
                else:
                    print(f"{Colors.RED}❌ .xopt directory not created{Colors.END}")
                    self.failed += 1
                
                # Test sync (should handle empty dependencies gracefully)
                self.run_command(["xopt", "sync"], "Sync project dependencies", expect_success=True)
                
            finally:
                os.chdir(original_cwd)
    
    def test_error_handling(self):
        """Test error conditions"""
        print(f"\n{Colors.BOLD}=== Testing Error Handling ==={Colors.END}")
        
        # Test running non-existent module
        self.run_command(
            ["xopt", "run", "nonexistent/module", "test"],
            "Run non-existent module (should fail)",
            expect_success=False
        )
        
        # Test packaging non-existent directory
        self.run_command(
            ["xopt", "package", "nonexistent/directory"],
            "Package non-existent directory (should fail)",
            expect_success=False
        )
        
        # Test installing non-existent package
        self.run_command(
            ["xopt", "install", "nonexistent.xopt"],
            "Install non-existent package (should fail)",
            expect_success=False
        )
    
    def test_makefile_commands(self):
        """Test Makefile functionality"""
        print(f"\n{Colors.BOLD}=== Testing Makefile Commands ==={Colors.END}")
        
        # Test basic make commands
        self.run_command(["make", "help"], "Make help")
        self.run_command(["make", "check-deps"], "Check dependencies")
        self.run_command(["make", "version"], "Show version info")
        self.run_command(["make", "dev-test"], "Development test")
        
        # Note: We skip make update/build-exe here to avoid rebuilding during tests
    
    def cleanup(self):
        """Clean up test artifacts"""
        print(f"\n{Colors.BOLD}=== Cleaning Up ==={Colors.END}")
        
        # Remove package files
        for pkg in Path(".").glob("*.xopt"):
            if pkg.is_file():
                pkg.unlink()
                print(f"   Removed {pkg}")
            elif pkg.is_dir():
                print(f"   Skipped directory: {pkg}")
    
    def print_summary(self):
        """Print test summary"""
        print(f"\n{Colors.BOLD}{'='*50}")
        print(f"           TEST SUMMARY")
        print(f"{'='*50}{Colors.END}")
        
        total = self.passed + self.failed
        pass_rate = (self.passed / total * 100) if total > 0 else 0
        
        print(f"{Colors.GREEN}✅ Passed: {self.passed}{Colors.END}")
        print(f"{Colors.RED}❌ Failed: {self.failed}{Colors.END}")
        print(f"{Colors.YELLOW}⚠️  Warnings: {self.warnings}{Colors.END}")
        print(f"{Colors.BOLD}📊 Pass Rate: {pass_rate:.1f}%{Colors.END}")
        
        if self.failed == 0:
            print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 ALL TESTS PASSED! xopt is working correctly.{Colors.END}")
        else:
            print(f"\n{Colors.RED}{Colors.BOLD}⚠️  SOME TESTS FAILED. See details above.{Colors.END}")
            
            # Print failed tests
            print(f"\n{Colors.BOLD}Failed Tests:{Colors.END}")
            for test, status, error in self.test_results:
                if status in ["FAIL", "ERROR", "TIMEOUT"]:
                    print(f"{Colors.RED}❌ {test}: {status}{Colors.END}")
                    if error:
                        print(f"   Error: {error[:100]}...")
        
        return self.failed == 0

def main():
    """Run all tests"""
    print(f"{Colors.BOLD}🧪 xopt Functionality Test Suite{Colors.END}")
    print(f"{Colors.BOLD}===================================={Colors.END}")
    
    tester = XoptTester()
    
    try:
        # Run all test suites
        tester.test_basic_commands()
        tester.test_packaging()
        tester.test_installation()
        tester.test_execution()
        tester.test_project_workflow()
        tester.test_error_handling()
        tester.test_makefile_commands()
        
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️  Tests interrupted by user{Colors.END}")
    except Exception as e:
        print(f"\n{Colors.RED}❌ Test suite error: {e}{Colors.END}")
    finally:
        tester.cleanup()
        success = tester.print_summary()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()