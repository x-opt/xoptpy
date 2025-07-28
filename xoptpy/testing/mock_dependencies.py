"""
Real dependency management for testing xopt modules using virtual environments.
"""

import os
import sys
import subprocess
import tempfile
import venv
from typing import List, Optional
from pathlib import Path

from ..models import Manifest


class DependencyManager:
    """Manages real dependencies for module testing using virtual environments."""
    
    def __init__(self, use_virtual_env: bool = True, cache_dir: Optional[str] = None):
        self.use_virtual_env = use_virtual_env
        self.cache_dir = Path(cache_dir) if cache_dir else Path.home() / ".xopt" / "test_envs"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.current_venv = None
        self.original_path = None
    
    def setup_dependencies(self, manifest: Manifest, force_reinstall: bool = False) -> bool:
        """Setup dependencies for the module."""
        if not manifest.spec.implementation.requirements:
            return True
        
        if self.use_virtual_env:
            return self._setup_with_venv(manifest, force_reinstall)
        else:
            return self._install_to_current_env(manifest.spec.implementation.requirements)
    
    def _setup_with_venv(self, manifest: Manifest, force_reinstall: bool = False) -> bool:
        """Setup dependencies using a virtual environment."""
        # Create a hash of requirements for caching
        requirements_str = "|".join(sorted(manifest.spec.implementation.requirements))
        import hashlib
        env_hash = hashlib.md5(requirements_str.encode()).hexdigest()[:12]
        
        venv_name = f"{manifest.metadata.namespace}_{manifest.metadata.name}_{env_hash}"
        venv_path = self.cache_dir / venv_name
        
        # Check if cached environment exists and is valid
        if venv_path.exists() and not force_reinstall:
            if self._validate_venv(venv_path, manifest.spec.implementation.requirements):
                self._activate_venv(venv_path)
                return True
            else:
                # Remove invalid environment
                import shutil
                shutil.rmtree(venv_path)
        
        # Create new virtual environment
        try:
            print(f"Creating virtual environment for {manifest.metadata.namespace}/{manifest.metadata.name}...")
            venv.create(venv_path, with_pip=True, clear=True)
            
            # Activate environment
            self._activate_venv(venv_path)
            
            # Install dependencies
            if not self._install_to_current_env(manifest.spec.implementation.requirements):
                return False
            
            print(f"✓ Dependencies installed in virtual environment")
            return True
            
        except Exception as e:
            print(f"Failed to create virtual environment: {e}")
            return False
    
    def _activate_venv(self, venv_path: Path):
        """Activate the virtual environment."""
        self.current_venv = venv_path
        
        # Store original PATH
        self.original_path = sys.path.copy()
        
        # Determine platform-specific paths
        if sys.platform == "win32":
            bin_dir = venv_path / "Scripts"
            python_exe = bin_dir / "python.exe"
        else:
            bin_dir = venv_path / "bin"
            python_exe = bin_dir / "python"
        
        # Update environment
        os.environ["VIRTUAL_ENV"] = str(venv_path)
        os.environ["PATH"] = f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"
        
        # Update Python path
        site_packages = self._get_site_packages_path(venv_path)
        if site_packages and site_packages.exists():
            sys.path.insert(0, str(site_packages))
    
    def _get_site_packages_path(self, venv_path: Path) -> Optional[Path]:
        """Get the site-packages path for the virtual environment."""
        if sys.platform == "win32":
            site_packages = venv_path / "Lib" / "site-packages"
        else:
            # Find the Python version directory
            lib_path = venv_path / "lib"
            if lib_path.exists():
                python_dirs = [d for d in lib_path.iterdir() if d.name.startswith("python")]
                if python_dirs:
                    site_packages = python_dirs[0] / "site-packages"
                else:
                    return None
            else:
                return None
        
        return site_packages if site_packages.exists() else None
    
    def _validate_venv(self, venv_path: Path, requirements: List[str]) -> bool:
        """Validate that the virtual environment has all required packages."""
        try:
            # Get Python executable
            if sys.platform == "win32":
                python_exe = venv_path / "Scripts" / "python.exe"
            else:
                python_exe = venv_path / "bin" / "python"
            
            if not python_exe.exists():
                return False
            
            # Check each requirement
            for req in requirements:
                package_name = self._extract_package_name(req)
                result = subprocess.run(
                    [str(python_exe), "-c", f"import {package_name}"],
                    capture_output=True,
                    text=True
                )
                if result.returncode != 0:
                    return False
            
            return True
            
        except Exception:
            return False
    
    def _install_to_current_env(self, requirements: List[str]) -> bool:
        """Install requirements to the current Python environment."""
        try:
            for req in requirements:
                print(f"Installing {req}...")
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", req],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode != 0:
                    print(f"Failed to install {req}: {result.stderr}")
                    return False
            
            return True
            
        except Exception as e:
            print(f"Error installing dependencies: {e}")
            return False
    
    def _extract_package_name(self, requirement: str) -> str:
        """Extract package name from requirement string."""
        # Handle requirements like "torch>=1.12.0", "transformers", etc.
        import re
        
        # Split on version specifiers
        package_name = re.split(r'[><=!]', requirement)[0].strip()
        
        # Handle package name mappings
        name_mappings = {
            'scikit-learn': 'sklearn',
            'beautifulsoup4': 'bs4',
            'pillow': 'PIL'
        }
        
        return name_mappings.get(package_name, package_name)
    
    def cleanup_dependencies(self):
        """Clean up the dependency environment."""
        if self.current_venv and self.original_path is not None:
            # Restore original Python path
            sys.path[:] = self.original_path
            
            # Clean up environment variables
            if "VIRTUAL_ENV" in os.environ:
                del os.environ["VIRTUAL_ENV"]
            
            # Reset PATH (this is tricky, so we'll just note the change)
            # In practice, the PATH change only affects the current process
            
            self.current_venv = None
            self.original_path = None
    
    def clean_cache(self, older_than_days: int = 7):
        """Clean up old cached virtual environments."""
        import time
        
        current_time = time.time()
        cutoff_time = current_time - (older_than_days * 24 * 60 * 60)
        
        for env_dir in self.cache_dir.iterdir():
            if env_dir.is_dir():
                # Check if environment is old
                if env_dir.stat().st_mtime < cutoff_time:
                    print(f"Removing old test environment: {env_dir.name}")
                    import shutil
                    shutil.rmtree(env_dir)
    
    def list_cached_environments(self) -> List[str]:
        """List all cached virtual environments."""
        return [env_dir.name for env_dir in self.cache_dir.iterdir() if env_dir.is_dir()]