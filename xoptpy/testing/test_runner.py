"""
Test runner for xopt modules and tools.
"""

import json
import time
import logging
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum

from pydantic import BaseModel, ValidationError
import yaml

from ..models import Manifest


class TestStatus(str, Enum):
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass
class TestResult:
    """Result of a single test case."""
    test_name: str
    status: TestStatus
    execution_time: float
    input_data: Dict[str, Any]
    expected_output: Optional[Dict[str, Any]]
    actual_output: Optional[Dict[str, Any]]
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class TestCase:
    """Test case configuration."""
    name: str
    description: Optional[str]
    input_data: Dict[str, Any]
    expected_output: Optional[Dict[str, Any]] = None
    config_overrides: Optional[Dict[str, Any]] = None
    should_fail: bool = False
    timeout: Optional[int] = None
    skip: bool = False
    skip_reason: Optional[str] = None


class TestConfig(BaseModel):
    """Test configuration schema."""
    module_path: str
    test_cases: List[Dict[str, Any]]
    default_timeout: int = 30
    mock_dependencies: bool = True
    parallel_execution: bool = False
    output_validation: bool = True


class ModuleTestRunner:
    """Test runner for xopt modules."""
    
    def __init__(self, module_path: str, mock_dependencies: bool = True):
        self.module_path = Path(module_path)
        self.mock_dependencies = mock_dependencies
        self.logger = logging.getLogger(__name__)
        
        # Load manifest
        self.manifest = self._load_manifest()
        
        # Initialize dependency manager
        from .mock_dependencies import DependencyManager
        self.dependency_manager = DependencyManager(use_virtual_env=mock_dependencies)
    
    def _load_manifest(self) -> Manifest:
        """Load and validate module manifest."""
        manifest_files = list(self.module_path.glob("manifest.yaml")) + list(self.module_path.glob("manifest.yml"))
        if not manifest_files:
            raise FileNotFoundError(f"No manifest.yaml found in {self.module_path}")
        
        manifest_file = manifest_files[0]
        
        with open(manifest_file, 'r') as f:
            manifest_data = yaml.safe_load(f)
        
        try:
            return Manifest(**manifest_data)
        except ValidationError as e:
            raise ValueError(f"Invalid manifest: {e}")
    
    def load_test_config(self, config_path: str) -> TestConfig:
        """Load test configuration from file."""
        config_path = Path(config_path)
        
        if not config_path.exists():
            raise FileNotFoundError(f"Test config file not found: {config_path}")
        
        with open(config_path, 'r') as f:
            if config_path.suffix.lower() in ['.yaml', '.yml']:
                config_data = yaml.safe_load(f)
            else:
                config_data = json.load(f)
        
        try:
            return TestConfig(**config_data)
        except ValidationError as e:
            raise ValueError(f"Invalid test config: {e}")
    
    def create_test_cases(self, test_data: List[Dict[str, Any]]) -> List[TestCase]:
        """Create TestCase objects from test data."""
        test_cases = []
        
        for i, test_data_item in enumerate(test_data):
            name = test_data_item.get('name', f'test_{i+1}')
            
            test_case = TestCase(
                name=name,
                description=test_data_item.get('description'),
                input_data=test_data_item.get('input', {}),
                expected_output=test_data_item.get('expected_output'),
                config_overrides=test_data_item.get('config', {}),
                should_fail=test_data_item.get('should_fail', False),
                timeout=test_data_item.get('timeout'),
                skip=test_data_item.get('skip', False),
                skip_reason=test_data_item.get('skip_reason')
            )
            test_cases.append(test_case)
        
        return test_cases
    
    def run_single_test(self, test_case: TestCase, default_timeout: int = 30) -> TestResult:
        """Run a single test case."""
        if test_case.skip:
            return TestResult(
                test_name=test_case.name,
                status=TestStatus.SKIPPED,
                execution_time=0.0,
                input_data=test_case.input_data,
                expected_output=test_case.expected_output,
                actual_output=None,
                error_message=test_case.skip_reason
            )
        
        start_time = time.time()
        
        try:
            # Setup dependencies
            if not self.dependency_manager.setup_dependencies(self.manifest):
                return TestResult(
                    test_name=test_case.name,
                    status=TestStatus.ERROR,
                    execution_time=0.0,
                    input_data=test_case.input_data,
                    expected_output=test_case.expected_output,
                    actual_output=None,
                    error_message="Failed to setup dependencies"
                )
            
            # Load and execute module
            actual_output = self._execute_module(test_case, default_timeout)
            
            execution_time = time.time() - start_time
            
            # Validate results
            if test_case.should_fail:
                # Test was expected to fail but didn't
                return TestResult(
                    test_name=test_case.name,
                    status=TestStatus.FAILED,
                    execution_time=execution_time,
                    input_data=test_case.input_data,
                    expected_output=test_case.expected_output,
                    actual_output=actual_output,
                    error_message="Test was expected to fail but succeeded"
                )
            
            # Check expected output if provided
            if test_case.expected_output is not None:
                if not self._validate_output(actual_output, test_case.expected_output):
                    return TestResult(
                        test_name=test_case.name,
                        status=TestStatus.FAILED,
                        execution_time=execution_time,
                        input_data=test_case.input_data,
                        expected_output=test_case.expected_output,
                        actual_output=actual_output,
                        error_message="Actual output does not match expected output"
                    )
            
            return TestResult(
                test_name=test_case.name,
                status=TestStatus.PASSED,
                execution_time=execution_time,
                input_data=test_case.input_data,
                expected_output=test_case.expected_output,
                actual_output=actual_output
            )
        
        except Exception as e:
            execution_time = time.time() - start_time
            
            if test_case.should_fail:
                # Test was expected to fail and did
                return TestResult(
                    test_name=test_case.name,
                    status=TestStatus.PASSED,
                    execution_time=execution_time,
                    input_data=test_case.input_data,
                    expected_output=test_case.expected_output,
                    actual_output=None,
                    error_message=f"Test failed as expected: {str(e)}"
                )
            else:
                return TestResult(
                    test_name=test_case.name,
                    status=TestStatus.ERROR,
                    execution_time=execution_time,
                    input_data=test_case.input_data,
                    expected_output=test_case.expected_output,
                    actual_output=None,
                    error_message=str(e)
                )
        finally:
            # Cleanup dependencies
            self.dependency_manager.cleanup_dependencies()
    
    def _execute_module(self, test_case: TestCase, timeout: int) -> Any:
        """Execute the module with test inputs."""
        import sys
        import importlib.util
        
        # Parse entry point
        entry_point = self.manifest.spec.implementation.entry_point
        if ':' not in entry_point:
            raise ValueError(f"Invalid entry point format: {entry_point}")
        
        file_path, function_name = entry_point.split(':', 1)
        module_file = self.module_path / file_path.lstrip('./')
        
        if not module_file.exists():
            raise FileNotFoundError(f"Module file not found: {module_file}")
        
        # Prepare execution parameters
        run_params = {}
        
        # Add default parameters from manifest
        if self.manifest.spec.tunable and self.manifest.spec.tunable.parameters:
            for param_name, param_def in self.manifest.spec.tunable.parameters.items():
                if param_def.default_value is not None:
                    run_params[param_name] = param_def.default_value
        
        # Add config overrides
        if test_case.config_overrides:
            run_params.update(test_case.config_overrides)
        
        # Add test input data
        run_params.update(test_case.input_data)
        
        # Add module directory to path
        sys.path.insert(0, str(self.module_path))
        
        try:
            # Import module dynamically
            spec = importlib.util.spec_from_file_location("test_module", module_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Get function
            if hasattr(module, function_name):
                func = getattr(module, function_name)
            else:
                raise AttributeError(f"Function '{function_name}' not found in {module_file}")
            
            # Execute function with timeout
            result = func(**run_params)
            return result
        
        finally:
            # Remove from path
            if str(self.module_path) in sys.path:
                sys.path.remove(str(self.module_path))
    
    def _validate_output(self, actual: Any, expected: Any) -> bool:
        """Validate actual output against expected output."""
        if isinstance(expected, dict) and isinstance(actual, dict):
            # Check if all expected keys are present with correct values
            for key, expected_value in expected.items():
                if key not in actual:
                    return False
                if not self._validate_output(actual[key], expected_value):
                    return False
            return True
        elif isinstance(expected, list) and isinstance(actual, list):
            if len(expected) != len(actual):
                return False
            for exp_item, act_item in zip(expected, actual):
                if not self._validate_output(act_item, exp_item):
                    return False
            return True
        else:
            return actual == expected
    
    def run_tests(self, test_cases: List[TestCase], parallel: bool = False, default_timeout: int = 30) -> List[TestResult]:
        """Run multiple test cases."""
        results = []
        
        if parallel:
            # TODO: Implement parallel execution
            self.logger.warning("Parallel execution not yet implemented, running sequentially")
        
        for test_case in test_cases:
            self.logger.info(f"Running test: {test_case.name}")
            result = self.run_single_test(test_case, default_timeout)
            results.append(result)
            
            # Log result
            if result.status == TestStatus.PASSED:
                self.logger.info(f"✓ {test_case.name} passed ({result.execution_time:.2f}s)")
            elif result.status == TestStatus.FAILED:
                self.logger.error(f"✗ {test_case.name} failed: {result.error_message}")
            elif result.status == TestStatus.SKIPPED:
                self.logger.info(f"- {test_case.name} skipped: {result.error_message}")
            elif result.status == TestStatus.ERROR:
                self.logger.error(f"E {test_case.name} error: {result.error_message}")
        
        return results
    
    def generate_test_report(self, results: List[TestResult]) -> Dict[str, Any]:
        """Generate test report from results."""
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r.status == TestStatus.PASSED)
        failed_tests = sum(1 for r in results if r.status == TestStatus.FAILED)
        error_tests = sum(1 for r in results if r.status == TestStatus.ERROR)
        skipped_tests = sum(1 for r in results if r.status == TestStatus.SKIPPED)
        
        total_time = sum(r.execution_time for r in results)
        
        return {
            "module": f"{self.manifest.metadata.namespace}/{self.manifest.metadata.name}@{self.manifest.metadata.version}",
            "summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "errors": error_tests,
                "skipped": skipped_tests,
                "success_rate": passed_tests / total_tests if total_tests > 0 else 0,
                "total_execution_time": total_time
            },
            "test_results": [result.to_dict() for result in results],
            "timestamp": time.time()
        }