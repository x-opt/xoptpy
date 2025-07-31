from typing import Dict, Any, Callable
import yaml
import os


class XOptClient:
    """Client for managing xopt configuration and modules"""
    
    def __init__(self, config_path: str = "xopt.yaml"):
        self.config_path = config_path
        self.config = self._load_config()
        self._modules = {}
        self._instances = {}
    
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
        for module_config in self.config.values():
            if 'configurables' in module_config and name in module_config['configurables']:
                return module_config['configurables'][name]
        return []


# Global client instance
_client = None

def client() -> XOptClient:
    """Get the global xopt client"""
    global _client
    if _client is None:
        _client = XOptClient()
    return _client