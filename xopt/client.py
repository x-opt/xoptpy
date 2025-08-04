from typing import Dict, Any, Callable, Optional
import yaml
import os
import subprocess
import sys
import tempfile
import tarfile
import json
from pathlib import Path


class XOptClient:
    """Client for managing xopt configuration and modules"""
    
    def __init__(self, config_path: str = "xopt.yaml"):
        self.config_path = config_path
        self.config = self._load_config()
        self._modules = {}
        self._instances = {}
        self.modules_dir = Path.home() / ".xopt" / "modules"
        self.modules_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from xopt.yaml"""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        return {}
    
    def tunable(self, name: str, description: str = "") -> Callable:
        """Create a tunable parameter that reads from config"""
        def get_tunable_value():
            # Find the tunable value in config
            for module_config in self.config.values():
                if 'tunables' in module_config and name in module_config['tunables']:
                    return module_config['tunables'][name]
            return f"Default {name}"
        
        return get_tunable_value
    
    def configurable(self, name: str, description: str = "") -> Any:
        """Create a configurable parameter that reads from config"""
        # Find the configurable value in config
        for config_key, module_config in self.config.items():
            if 'configurables' in module_config and name in module_config['configurables']:
                return module_config['configurables'][name]
        return []
    
    def package(self, module_dir: str, output_path: Optional[str] = None, output_dir: Optional[str] = None) -> str:
        """Package a module directory into a .xopt archive"""
        module_path = Path(module_dir)
        if not module_path.exists():
            raise ValueError(f"Module directory {module_dir} does not exist")
        
        # Load module metadata
        if (module_path / "xopt.yaml").exists():
            with open(module_path / "xopt.yaml") as f:
                config = yaml.safe_load(f)
                
                # Handle new schema format
                if 'name' in config and 'version' in config:
                    module_name = config['name']
                    version = config['version']
                    engine = config.get('engine')
                else:
                    # Handle legacy format for backwards compatibility
                    module_name = list(config.keys())[0].split("@")[0]
                    version = list(config.keys())[0].split("@")[1]
                    engine = None
        else:
            raise ValueError("Module must have xopt.yaml file")
        
        # Create output path if not specified
        if not output_path:
            safe_name = module_name.replace("/", "_")
            filename = f"{safe_name}-{version}.xopt"
            if output_dir:
                output_path = str(Path(output_dir) / filename)
            else:
                output_path = filename
        
        # For engine references, validate the referenced engine exists
        if engine and not engine.startswith("./"):
            # This is an engine reference - validate it exists in installed modules
            installed = self.list_installed()
            engine_name = engine.split("@")[0] if "@" in engine else engine
            if engine_name not in installed:
                print(f"⚠️  Warning: Referenced engine '{engine}' is not installed")
                print(f"   Make sure to install the base engine before using this module")
        
        # Create package archive
        with tarfile.open(output_path, "w:gz") as tar:
            # Add all module files
            tar.add(module_path, arcname=".")
        
        print(f"📦 Packaged {module_name}@{version} to {output_path}")
        if engine and not engine.startswith("./"):
            print(f"   🔗 References engine: {engine}")
        
        return output_path
    

    def install(self, package_path: str) -> str:
        """Install a .xopt package with virtual environment"""
        package_path = Path(package_path)
        if not package_path.exists():
            raise ValueError(f"Package {package_path} does not exist")
        
        # Create temporary directory for extraction
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Extract package
            with tarfile.open(package_path, "r:gz") as tar:
                tar.extractall(temp_path)
            
            # Load module metadata
            config_path = temp_path / "xopt.yaml"
            if not config_path.exists():
                raise ValueError("Package missing xopt.yaml")
            
            with open(config_path) as f:
                config = yaml.safe_load(f)
                
                # Handle new schema format
                if 'name' in config and 'version' in config:
                    module_name = config['name']
                    version = config['version']
                    engine = config.get('engine')
                else:
                    # Handle legacy format for backwards compatibility
                    module_spec = list(config.keys())[0]
                    module_name = module_spec.split("@")[0]
                    version = module_spec.split("@")[1]
                    engine = None
            
            # Create module directory
            module_dir = self.modules_dir / module_name.replace("/", "_")
            if module_dir.exists():
                print(f"⚠️  Module {module_name} already installed, removing old version")
                import shutil
                shutil.rmtree(module_dir)
            
            module_dir.mkdir(parents=True)
            
            # Copy module files
            import shutil
            for item in temp_path.iterdir():
                if item.is_dir():
                    shutil.copytree(item, module_dir / item.name)
                else:
                    shutil.copy2(item, module_dir / item.name)
            
            # Handle engine references vs local engines
            if engine and not engine.startswith("./"):
                # This is an engine reference - validate base engine exists
                installed = self.list_installed()
                engine_name = engine.split("@")[0] if "@" in engine else engine
                if engine_name not in installed:
                    raise ValueError(f"Referenced engine '{engine}' is not installed. Install it first.")
                
                print(f"🔗 Module references engine: {engine}")
                install_info = {
                    "name": module_name,
                    "version": version,
                    "installed_at": str(module_dir),
                    "type": "engine_reference",
                    "engine": engine,
                    "config": config
                }
            else:
                # This is a local engine - create virtual environment
                venv_path = module_dir / "venv"
                print(f"🐍 Creating virtual environment at {venv_path}")
                # Try python3 first, then python
                python_cmd = "python3"
                subprocess.run([python_cmd, "-m", "venv", str(venv_path)], check=True)
                
                # Install dependencies
                if (module_dir / "pyproject.toml").exists() or (module_dir / "requirements.txt").exists():
                    venv_python = venv_path / ("Scripts" if os.name == "nt" else "bin") / "python"
                    
                    # Install xopt in the venv first
                    print("📦 Installing xopt in module environment")
                    
                    # Try to determine if we're in a development environment or installed
                    xopt_source_path = Path(__file__).parent.parent
                    dev_path = Path("/mnt/c/Users/jaked/Documents/dev/xopt/xoptpy")
                    
                    # Check if we can find the development version with the fix
                    if (dev_path.exists() and (dev_path / "pyproject.toml").exists()):
                        # Development environment available - install in editable mode with fix
                        subprocess.run([str(venv_python), "-m", "pip", "install", "-e", str(dev_path)], check=True)
                    elif (xopt_source_path / "pyproject.toml").exists():
                        # Fallback to detected source path
                        subprocess.run([str(venv_python), "-m", "pip", "install", "-e", str(xopt_source_path)], check=True)
                    else:
                        # Installed environment - install from PyPI
                        subprocess.run([str(venv_python), "-m", "pip", "install", "xoptpy"], check=True)
                    
                    # Install module dependencies
                    if (module_dir / "pyproject.toml").exists():
                        print("📦 Installing module dependencies from pyproject.toml")
                        subprocess.run([str(venv_python), "-m", "pip", "install", "-e", str(module_dir)], check=True)
                    else:
                        print("📦 Installing module dependencies from requirements.txt")
                        subprocess.run([str(venv_python), "-m", "pip", "install", "-r", str(module_dir / "requirements.txt")], check=True)
                
                # Handle config format for backwards compatibility
                if 'name' in config:
                    config_data = config
                else:
                    config_data = config[module_spec]
                
                install_info = {
                    "name": module_name,
                    "version": version,
                    "installed_at": str(module_dir),
                    "type": "local_engine",
                    "engine": engine,
                    "config": config_data
                }
            
            with open(module_dir / "install_info.json", "w") as f:
                json.dump(install_info, f, indent=2)
            
            print(f"✅ Installed {module_name}@{version} to {module_dir}")
            return module_name
    
    def list_installed(self) -> Dict[str, Dict[str, Any]]:
        """List all installed modules"""
        installed = {}
        
        for module_path in self.modules_dir.iterdir():
            if module_path.is_dir():
                install_info_path = module_path / "install_info.json"
                if install_info_path.exists():
                    with open(install_info_path) as f:
                        info = json.load(f)
                        installed[info["name"]] = info
        
        return installed
    
    def uninstall(self, module_name: str) -> bool:
        """Uninstall a module"""
        module_dir = self.modules_dir / module_name.replace("/", "_")
        if module_dir.exists():
            import shutil
            shutil.rmtree(module_dir)
            print(f"🗑️  Uninstalled {module_name}")
            return True
        else:
            print(f"❌ Module {module_name} not found")
            return False


# Global client instance
_client = None

def client() -> XOptClient:
    """Get the global xopt client"""
    global _client
    if _client is None:
        _client = XOptClient()
    return _client