"""
Command-line interface for the AI Registry client.
"""

import json
import sys
from pathlib import Path
from typing import Optional

import click
import yaml
from pydantic import ValidationError

from . import AIRegistryClient, ComponentType
from .config import ClientConfig, load_config
from .exceptions import AIRegistryClientError, APIError, NotFoundError
from .models import Manifest


def load_yaml_file(file_path: str) -> dict:
    """Load and parse a YAML file."""
    try:
        with open(file_path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        raise click.ClickException(f"File not found: {file_path}")
    except yaml.YAMLError as e:
        raise click.ClickException(f"Invalid YAML file: {e}")


def create_client(base_url: Optional[str], timeout: Optional[int]) -> AIRegistryClient:
    """Create an AI Registry client with optional overrides."""
    config = load_config()
    return AIRegistryClient(
        base_url=base_url or config.base_url,
        timeout=timeout or config.timeout,
        config=config
    )


def handle_api_error(e: Exception):
    """Handle API errors with appropriate exit codes."""
    if isinstance(e, NotFoundError):
        click.echo(f"Error: Resource not found - {e.error_message}", err=True)
        sys.exit(404)
    elif isinstance(e, APIError):
        click.echo(f"API Error {e.status_code}: {e.error_message}", err=True)
        sys.exit(1)
    elif isinstance(e, AIRegistryClientError):
        click.echo(f"Client Error: {e}", err=True)
        sys.exit(1)
    else:
        click.echo(f"Unexpected Error: {e}", err=True)
        sys.exit(1)


@click.group()
@click.option('--base-url', help='Base URL of the AI Registry API')
@click.option('--timeout', type=int, help='Request timeout in seconds')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.pass_context
def cli(ctx, base_url: Optional[str], timeout: Optional[int], verbose: bool):
    """AI Registry CLI - Manage AI modules and tools."""
    ctx.ensure_object(dict)
    ctx.obj['base_url'] = base_url
    ctx.obj['timeout'] = timeout
    ctx.obj['verbose'] = verbose
    
    if verbose:
        import logging
        logging.basicConfig(level=logging.DEBUG)


@cli.command()
@click.pass_context
def health(ctx):
    """Check the health status of the API."""
    try:
        client = create_client(ctx.obj['base_url'], ctx.obj['timeout'])
        health_status = client.health_check()
        
        click.echo("Health Status:")
        click.echo(f"  Status: {health_status.status}")
        click.echo(f"  Database: {'✓' if health_status.database else '✗'}")
        
    except Exception as e:
        handle_api_error(e)


@cli.group()
def search():
    """Search for components."""
    pass


@search.command('components')
@click.argument('query')
@click.option('--type', 'component_type', type=click.Choice(['module', 'tool']), help='Filter by component type')
@click.option('--json-output', is_flag=True, help='Output results as JSON')
@click.pass_context
def search_components(ctx, query: str, component_type: Optional[str], json_output: bool):
    """Search for modules and tools by name or description."""
    try:
        client = create_client(ctx.obj['base_url'], ctx.obj['timeout'])
        
        component_filter = None
        if component_type:
            component_filter = ComponentType(component_type)
        
        results = client.search(query, component_filter)
        
        if json_output:
            click.echo(json.dumps([result.model_dump() for result in results], indent=2))
        else:
            if not results:
                click.echo(f"No components found matching '{query}'")
                return
            
            click.echo(f"Found {len(results)} component(s) matching '{query}':")
            for result in results:
                click.echo(f"\n  {result.namespace}/{result.name} ({result.type.value})")
                click.echo(f"    Description: {result.description or 'No description'}")
                if result.tags:
                    click.echo(f"    Tags: {', '.join(result.tags)}")
                click.echo(f"    Versions: {', '.join(result.versions)}")
        
    except Exception as e:
        handle_api_error(e)


@cli.group()
def module():
    """Manage AI modules."""
    pass


@module.command('list-versions')
@click.argument('namespace')
@click.argument('name')
@click.option('--json-output', is_flag=True, help='Output results as JSON')
@click.pass_context
def module_list_versions(ctx, namespace: str, name: str, json_output: bool):
    """List all versions of a module."""
    try:
        client = create_client(ctx.obj['base_url'], ctx.obj['timeout'])
        versions = client.get_module_versions(namespace, name)
        
        if not versions:
            click.echo(f"No versions found for module {namespace}/{name}")
            return
        
        if json_output:
            click.echo(json.dumps([v.model_dump() for v in versions], indent=2, default=str))
        else:
            click.echo(f"Versions for {namespace}/{name}:")
            for version in versions:
                click.echo(f"  {version.version} - {version.download_count} downloads - {version.created_at}")
        
    except Exception as e:
        handle_api_error(e)


@module.command('get-manifest')
@click.argument('namespace')
@click.argument('name')
@click.argument('version')
@click.option('--output', '-o', help='Save manifest to file')
@click.pass_context
def module_get_manifest(ctx, namespace: str, name: str, version: str, output: Optional[str]):
    """Get the manifest for a specific module version."""
    try:
        client = create_client(ctx.obj['base_url'], ctx.obj['timeout'])
        manifest = client.get_module_manifest(namespace, name, version)
        
        manifest_data = manifest.model_dump()
        
        if output:
            output_path = Path(output)
            if output_path.suffix.lower() in ['.yaml', '.yml']:
                with open(output_path, 'w') as f:
                    yaml.dump(manifest_data, f, default_flow_style=False, sort_keys=False)
            else:
                with open(output_path, 'w') as f:
                    json.dump(manifest_data, f, indent=2)
            click.echo(f"Manifest saved to {output}")
        else:
            click.echo(yaml.dump(manifest_data, default_flow_style=False, sort_keys=False))
        
    except Exception as e:
        handle_api_error(e)


@module.command('upload')
@click.argument('manifest_file', type=click.Path(exists=True))
@click.option('--namespace', help='Override namespace from manifest')
@click.option('--name', help='Override name from manifest')
@click.option('--version', help='Override version from manifest')
@click.pass_context
def module_upload(ctx, manifest_file: str, namespace: Optional[str], name: Optional[str], version: Optional[str]):
    """Upload a new module version from a YAML manifest file."""
    try:
        # Load and validate manifest
        manifest_data = load_yaml_file(manifest_file)
        
        # Override values if provided
        if namespace or name or version:
            if 'metadata' not in manifest_data:
                manifest_data['metadata'] = {}
            if namespace:
                manifest_data['metadata']['namespace'] = namespace
            if name:
                manifest_data['metadata']['name'] = name
            if version:
                manifest_data['metadata']['version'] = version
        
        try:
            manifest = Manifest(**manifest_data)
        except ValidationError as e:
            click.echo(f"Invalid manifest file: {e}", err=True)
            sys.exit(1)
        
        client = create_client(ctx.obj['base_url'], ctx.obj['timeout'])
        response = client.upload_module_version(
            manifest.metadata.namespace,
            manifest.metadata.name,
            manifest.metadata.version,
            manifest
        )
        
        click.echo(f"✓ Successfully uploaded module {manifest.metadata.namespace}/{manifest.metadata.name}@{manifest.metadata.version}")
        click.echo(f"  Module ID: {response.module_id}")
        click.echo(f"  Version ID: {response.version_id}")
        
    except Exception as e:
        handle_api_error(e)


@module.command('get-dependencies')
@click.argument('namespace')
@click.argument('name')
@click.argument('version')
@click.option('--json-output', is_flag=True, help='Output results as JSON')
@click.pass_context
def module_get_dependencies(ctx, namespace: str, name: str, version: str, json_output: bool):
    """Get dependencies for a specific module version."""
    try:
        client = create_client(ctx.obj['base_url'], ctx.obj['timeout'])
        dependencies = client.get_module_dependencies(namespace, name, version)
        
        if not dependencies:
            click.echo(f"No dependencies found for {namespace}/{name}@{version}")
            return
        
        if json_output:
            click.echo(json.dumps([d.model_dump() for d in dependencies], indent=2))
        else:
            click.echo(f"Dependencies for {namespace}/{name}@{version}:")
            for dep in dependencies:
                click.echo(f"  {dep.dependency_namespace}/{dep.dependency_name}@{dep.dependency_version}")
        
    except Exception as e:
        handle_api_error(e)


@module.command('get-stats')
@click.argument('namespace')
@click.argument('name')
@click.option('--json-output', is_flag=True, help='Output results as JSON')
@click.pass_context
def module_get_stats(ctx, namespace: str, name: str, json_output: bool):
    """Get usage statistics for a module."""
    try:
        client = create_client(ctx.obj['base_url'], ctx.obj['timeout'])
        stats = client.get_module_usage_stats(namespace, name)
        
        if json_output:
            click.echo(json.dumps(stats.model_dump(), indent=2, default=str))
        else:
            click.echo(f"Usage statistics for {namespace}/{name}:")
            click.echo(f"  Total downloads: {stats.total_downloads}")
            click.echo(f"  Version downloads:")
            for version, count in stats.version_stats.items():
                click.echo(f"    {version}: {count}")
            
            if stats.recent_activity:
                click.echo(f"  Recent activity:")
                for activity in stats.recent_activity[:5]:  # Show last 5
                    click.echo(f"    {activity.date}: {activity.downloads} downloads (v{activity.version})")
        
    except Exception as e:
        handle_api_error(e)


@cli.group()
def tool():
    """Manage AI tools."""
    pass


@tool.command('list-versions')
@click.argument('namespace')
@click.argument('name')
@click.option('--json-output', is_flag=True, help='Output results as JSON')
@click.pass_context
def tool_list_versions(ctx, namespace: str, name: str, json_output: bool):
    """List all versions of a tool."""
    try:
        client = create_client(ctx.obj['base_url'], ctx.obj['timeout'])
        versions = client.get_tool_versions(namespace, name)
        
        if not versions:
            click.echo(f"No versions found for tool {namespace}/{name}")
            return
        
        if json_output:
            click.echo(json.dumps([v.model_dump() for v in versions], indent=2, default=str))
        else:
            click.echo(f"Versions for {namespace}/{name}:")
            for version in versions:
                click.echo(f"  {version.version} - {version.download_count} downloads - {version.created_at}")
        
    except Exception as e:
        handle_api_error(e)


@tool.command('get-manifest')
@click.argument('namespace')
@click.argument('name')
@click.argument('version')
@click.option('--output', '-o', help='Save manifest to file')
@click.pass_context
def tool_get_manifest(ctx, namespace: str, name: str, version: str, output: Optional[str]):
    """Get the manifest for a specific tool version."""
    try:
        client = create_client(ctx.obj['base_url'], ctx.obj['timeout'])
        manifest = client.get_tool_manifest(namespace, name, version)
        
        manifest_data = manifest.model_dump()
        
        if output:
            output_path = Path(output)
            if output_path.suffix.lower() in ['.yaml', '.yml']:
                with open(output_path, 'w') as f:
                    yaml.dump(manifest_data, f, default_flow_style=False, sort_keys=False)
            else:
                with open(output_path, 'w') as f:
                    json.dump(manifest_data, f, indent=2)
            click.echo(f"Manifest saved to {output}")
        else:
            click.echo(yaml.dump(manifest_data, default_flow_style=False, sort_keys=False))
        
    except Exception as e:
        handle_api_error(e)


@tool.command('upload')
@click.argument('manifest_file', type=click.Path(exists=True))
@click.option('--namespace', help='Override namespace from manifest')
@click.option('--name', help='Override name from manifest')
@click.option('--version', help='Override version from manifest')
@click.pass_context
def tool_upload(ctx, manifest_file: str, namespace: Optional[str], name: Optional[str], version: Optional[str]):
    """Upload a new tool version from a YAML manifest file."""
    try:
        # Load and validate manifest
        manifest_data = load_yaml_file(manifest_file)
        
        # Override values if provided
        if namespace or name or version:
            if 'metadata' not in manifest_data:
                manifest_data['metadata'] = {}
            if namespace:
                manifest_data['metadata']['namespace'] = namespace
            if name:
                manifest_data['metadata']['name'] = name
            if version:
                manifest_data['metadata']['version'] = version
        
        try:
            manifest = Manifest(**manifest_data)
        except ValidationError as e:
            click.echo(f"Invalid manifest file: {e}", err=True)
            sys.exit(1)
        
        client = create_client(ctx.obj['base_url'], ctx.obj['timeout'])
        response = client.upload_tool_version(
            manifest.metadata.namespace,
            manifest.metadata.name,
            manifest.metadata.version,
            manifest
        )
        
        click.echo(f"✓ Successfully uploaded tool {manifest.metadata.namespace}/{manifest.metadata.name}@{manifest.metadata.version}")
        click.echo(f"  Tool ID: {response.tool_id}")
        click.echo(f"  Version ID: {response.version_id}")
        
    except Exception as e:
        handle_api_error(e)


@tool.command('get-dependencies')
@click.argument('namespace')
@click.argument('name')
@click.argument('version')
@click.option('--json-output', is_flag=True, help='Output results as JSON')
@click.pass_context
def tool_get_dependencies(ctx, namespace: str, name: str, version: str, json_output: bool):
    """Get dependencies for a specific tool version."""
    try:
        client = create_client(ctx.obj['base_url'], ctx.obj['timeout'])
        dependencies = client.get_tool_dependencies(namespace, name, version)
        
        if not dependencies:
            click.echo(f"No dependencies found for {namespace}/{name}@{version}")
            return
        
        if json_output:
            click.echo(json.dumps([d.model_dump() for d in dependencies], indent=2))
        else:
            click.echo(f"Dependencies for {namespace}/{name}@{version}:")
            for dep in dependencies:
                click.echo(f"  {dep.dependency_namespace}/{dep.dependency_name}@{dep.dependency_version}")
        
    except Exception as e:
        handle_api_error(e)


@tool.command('get-stats')
@click.argument('namespace')
@click.argument('name')
@click.option('--json-output', is_flag=True, help='Output results as JSON')
@click.pass_context
def tool_get_stats(ctx, namespace: str, name: str, json_output: bool):
    """Get usage statistics for a tool."""
    try:
        client = create_client(ctx.obj['base_url'], ctx.obj['timeout'])
        stats = client.get_tool_usage_stats(namespace, name)
        
        if json_output:
            click.echo(json.dumps(stats.model_dump(), indent=2, default=str))
        else:
            click.echo(f"Usage statistics for {namespace}/{name}:")
            click.echo(f"  Total downloads: {stats.total_downloads}")
            click.echo(f"  Version downloads:")
            for version, count in stats.version_stats.items():
                click.echo(f"    {version}: {count}")
            
            if stats.recent_activity:
                click.echo(f"  Recent activity:")
                for activity in stats.recent_activity[:5]:  # Show last 5
                    click.echo(f"    {activity.date}: {activity.downloads} downloads (v{activity.version})")
        
    except Exception as e:
        handle_api_error(e)


@cli.command()
@click.argument('args', nargs=-1)
@click.option('--input', '-i', help='Input data as JSON string or file path')
@click.option('--config', '-c', help='Configuration YAML file path')
@click.option('--output', '-o', help='Output file path')
@click.option('--install-deps', is_flag=True, help='Install module dependencies automatically')
@click.option('--dry-run', is_flag=True, help='Validate inputs without running')
@click.pass_context
def run(ctx, args: tuple, input: Optional[str], config: Optional[str], output: Optional[str], install_deps: bool, dry_run: bool):
    """
    Run a module locally with given inputs and configuration.
    
    If no MODULE_PATH is provided, runs the module in the current directory (like npm run).
    
    Examples:
    
    \b
    # Run module in current directory (npm-style)
    cd /path/to/module && xopt run --input "I love this!" confidence_threshold=0.8
    
    \b
    # Run specific module path
    xopt run ./modules/nlp/sentiment-analyzer --input "I love this!" confidence_threshold=0.8
    
    \b
    # Run with YAML configuration file
    xopt run --config config.yaml
    
    \b
    # Mix config file with CLI parameter overrides  
    xopt run --config config.yaml confidence_threshold=0.9 use_gpu=false
    
    \b
    # Run with JSON input file
    xopt run --input input.json batch_size=32
    
    \b
    # Install dependencies automatically
    xopt run --install-deps --input "Test text"
    """
    import os
    import sys
    import json
    import subprocess
    import importlib.util
    from pathlib import Path
    
    try:
        # Parse arguments to separate module_path from params
        module_path = None
        params = []
        
        if args:
            # Check if the first argument is a valid directory path
            first_arg = args[0]
            if os.path.isdir(first_arg) or first_arg in ['.', '..']:
                module_path = first_arg
                params = args[1:]
            else:
                # Check if it looks like a parameter (contains =)
                if '=' in first_arg:
                    # All arguments are parameters
                    params = args
                else:
                    # Assume first argument is module path even if it doesn't exist yet
                    module_path = first_arg
                    params = args[1:]
        
        # Auto-detect current directory if no module path provided
        if module_path is None:
            module_dir = Path.cwd()
            click.echo(f"Auto-detected module directory: {module_dir}")
        else:
            module_dir = Path(module_path)
        
        if not module_dir.is_dir():
            click.echo(f"Error: {module_dir} is not a directory", err=True)
            sys.exit(1)
        
        # Find manifest file
        manifest_files = list(module_dir.glob("manifest.yaml")) + list(module_dir.glob("manifest.yml"))
        if not manifest_files:
            click.echo(f"Error: No manifest.yaml found in {module_dir}", err=True)
            sys.exit(1)
        
        manifest_file = manifest_files[0]
        
        # Load manifest
        manifest_data = load_yaml_file(str(manifest_file))
        try:
            manifest = Manifest(**manifest_data)
        except ValidationError as e:
            click.echo(f"Invalid manifest: {e}", err=True)
            sys.exit(1)
        
        click.echo(f"Running module: {manifest.metadata.namespace}/{manifest.metadata.name}@{manifest.metadata.version}")
        
        # Install dependencies if requested
        if install_deps and manifest.spec.implementation.requirements:
            click.echo("Installing dependencies...")
            for req in manifest.spec.implementation.requirements:
                click.echo(f"  Installing {req}")
                try:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", req], 
                                        stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
                except subprocess.CalledProcessError as e:
                    click.echo(f"Warning: Failed to install {req}: {e.stderr.decode()}", err=True)
        
        # Parse entry point
        entry_point = manifest.spec.implementation.entry_point
        if ':' not in entry_point:
            click.echo(f"Error: Invalid entry point format: {entry_point}", err=True)
            sys.exit(1)
        
        file_path, function_name = entry_point.split(':', 1)
        module_file = module_dir / file_path.lstrip('./')
        
        if not module_file.exists():
            click.echo(f"Error: Module file not found: {module_file}", err=True)
            sys.exit(1)
        
        # Load input data
        input_data = {}
        if input:
            if os.path.isfile(input):
                # Load from file
                with open(input, 'r') as f:
                    if input.endswith('.json'):
                        input_data = json.load(f)
                    elif input.endswith(('.yaml', '.yml')):
                        input_data = yaml.safe_load(f)
                    else:
                        input_data = {"text": f.read()}
            else:
                # Parse as JSON string
                try:
                    input_data = json.loads(input)
                except json.JSONDecodeError:
                    # Treat as plain text
                    input_data = {"text": input}
        
        # Load configuration from YAML file if provided
        config_data = {}
        if config:
            config_data = load_yaml_file(config)
            click.echo(f"Loaded configuration from {config}")
        
        # Parse command line parameters (key=value pairs)
        cli_params = {}
        for param in params:
            if '=' in param:
                key, value = param.split('=', 1)
                # Try to parse as JSON, fall back to string
                try:
                    cli_params[key] = json.loads(value)
                except json.JSONDecodeError:
                    # Handle boolean values
                    if value.lower() in ('true', 'false'):
                        cli_params[key] = value.lower() == 'true'
                    # Handle numeric values
                    elif value.isdigit():
                        cli_params[key] = int(value)
                    elif '.' in value and value.replace('.', '').isdigit():
                        cli_params[key] = float(value)
                    else:
                        cli_params[key] = value
            else:
                click.echo(f"Warning: Ignoring invalid parameter format: {param} (expected key=value)", err=True)
        
        # Add tunable parameters from manifest as defaults
        if manifest.spec.tunable and manifest.spec.tunable.parameters:
            for param_name, param_def in manifest.spec.tunable.parameters.items():
                if param_name not in config_data and param_name not in cli_params and param_def.default_value is not None:
                    config_data[param_name] = param_def.default_value
        
        # Combine parameters with precedence: CLI args > config file > input data > defaults
        run_params = {}
        run_params.update(config_data)  # Defaults and config file
        run_params.update(input_data)   # Input data
        run_params.update(cli_params)   # CLI parameters (highest priority)
        
        if dry_run:
            click.echo("Dry run - would execute with parameters:")
            click.echo(json.dumps(run_params, indent=2))
            return
        
        # Load and execute module
        click.echo("Executing module...")
        
        # Add module directory to path
        sys.path.insert(0, str(module_dir))
        
        try:
            # Import module dynamically
            spec = importlib.util.spec_from_file_location("module", module_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Get function
            if hasattr(module, function_name):
                func = getattr(module, function_name)
            else:
                click.echo(f"Error: Function '{function_name}' not found in {module_file}", err=True)
                sys.exit(1)
            
            # Execute function
            result = func(**run_params)
            
            # Output result
            if output:
                with open(output, 'w') as f:
                    if output.endswith('.json'):
                        json.dump(result, f, indent=2, default=str)
                    elif output.endswith(('.yaml', '.yml')):
                        yaml.dump(result, f, default_flow_style=False)
                    else:
                        f.write(str(result))
                click.echo(f"Result saved to {output}")
            else:
                click.echo("Result:")
                if isinstance(result, (dict, list)):
                    click.echo(json.dumps(result, indent=2, default=str))
                else:
                    click.echo(str(result))
        
        except Exception as e:
            click.echo(f"Error executing module: {e}", err=True)
            if ctx.obj.get('verbose'):
                import traceback
                traceback.print_exc()
            sys.exit(1)
        finally:
            # Remove from path
            if str(module_dir) in sys.path:
                sys.path.remove(str(module_dir))
        
    except Exception as e:
        handle_api_error(e)


@cli.command()
@click.argument('module_path', type=click.Path(exists=True), required=False)
@click.option('--test-config', '-t', help='Test configuration file path')
@click.option('--install-deps', is_flag=True, help='Install dependencies in virtual environment')
@click.option('--output', '-o', help='Test report output file')
@click.option('--verbose', is_flag=True, help='Verbose test output')
@click.option('--parallel', is_flag=True, help='Run tests in parallel (if supported)')
@click.pass_context
def test(ctx, module_path: Optional[str], test_config: Optional[str], install_deps: bool, output: Optional[str], verbose: bool, parallel: bool):
    """Test a module with predefined test cases. If no MODULE_PATH is provided, tests the module in the current directory."""
    import json
    from pathlib import Path
    from .testing import ModuleTestRunner, TestCase
    
    try:
        # Auto-detect current directory if no module path provided
        if module_path is None:
            module_dir = Path.cwd()
            click.echo(f"Auto-detected module directory: {module_dir}")
        else:
            module_dir = Path(module_path)
        
        if not module_dir.is_dir():
            click.echo(f"Error: {module_dir} is not a directory", err=True)
            sys.exit(1)
        
        # Initialize test runner
        runner = ModuleTestRunner(str(module_dir), mock_dependencies=install_deps)
        click.echo(f"Testing module: {runner.manifest.metadata.namespace}/{runner.manifest.metadata.name}@{runner.manifest.metadata.version}")
        
        # Load test configuration
        if test_config:
            if not Path(test_config).exists():
                click.echo(f"Error: Test config file not found: {test_config}", err=True)
                sys.exit(1)
            
            config = runner.load_test_config(test_config)
            test_cases = runner.create_test_cases(config.test_cases)
            default_timeout = config.default_timeout
        else:
            # Look for default test files
            test_files = list(module_dir.glob("test*.yaml")) + list(module_dir.glob("test*.yml")) + list(module_dir.glob("test*.json"))
            if not test_files:
                click.echo("No test configuration found. Creating basic test...")
                # Create a basic test case
                test_cases = [TestCase(
                    name="basic_test",
                    description="Basic functionality test",
                    input_data={"text": "This is a test input"},
                    expected_output=None
                )]
                default_timeout = 30
            else:
                # Use first test file found
                config = runner.load_test_config(str(test_files[0]))
                test_cases = runner.create_test_cases(config.test_cases)
                default_timeout = config.default_timeout
        
        if not test_cases:
            click.echo("No test cases found to run", err=True)
            sys.exit(1)
        
        click.echo(f"Running {len(test_cases)} test case(s)...")
        
        # Run tests
        results = runner.run_tests(test_cases, parallel=parallel, default_timeout=default_timeout)
        
        # Generate report
        report = runner.generate_test_report(results)
        
        # Display summary
        summary = report["summary"]
        click.echo(f"\nTest Results Summary:")
        click.echo(f"  Total tests: {summary['total_tests']}")
        click.echo(f"  Passed: {summary['passed']} ✓")
        if summary['failed'] > 0:
            click.echo(f"  Failed: {summary['failed']} ✗")
        if summary['errors'] > 0:
            click.echo(f"  Errors: {summary['errors']} E")
        if summary['skipped'] > 0:
            click.echo(f"  Skipped: {summary['skipped']} -")
        click.echo(f"  Success rate: {summary['success_rate']:.1%}")
        click.echo(f"  Total time: {summary['total_execution_time']:.2f}s")
        
        # Show detailed results if verbose or if there are failures
        if verbose or summary['failed'] > 0 or summary['errors'] > 0:
            click.echo(f"\nDetailed Results:")
            for result in results:
                status_icon = {
                    "passed": "✓",
                    "failed": "✗", 
                    "error": "E",
                    "skipped": "-"
                }[result.status.value]
                
                click.echo(f"  {status_icon} {result.test_name} ({result.execution_time:.2f}s)")
                
                if result.error_message and (verbose or result.status.value in ["failed", "error"]):
                    click.echo(f"    Error: {result.error_message}")
                
                if verbose and result.actual_output:
                    click.echo(f"    Output: {json.dumps(result.actual_output, default=str)[:100]}...")
        
        # Save report if requested
        if output:
            with open(output, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            click.echo(f"\nTest report saved to {output}")
        
        # Exit with appropriate code
        if summary['failed'] > 0 or summary['errors'] > 0:
            sys.exit(1)
        else:
            click.echo(f"\n✓ All tests passed!")
            sys.exit(0)
        
    except Exception as e:
        if ctx.obj.get('verbose'):
            import traceback
            traceback.print_exc()
        click.echo(f"Error running tests: {e}", err=True)
        sys.exit(1)


def main():
    """Main CLI entry point."""
    cli()