"""
Configuration management for the AI Registry client.
"""

import os
import logging
from typing import Optional, Dict, Any
from pathlib import Path

from pydantic import BaseModel, Field


class ClientConfig(BaseModel):
    """Configuration for the AI Registry client."""
    
    base_url: str = Field(default="http://localhost:8080", description="Base URL of the AI Registry API")
    timeout: int = Field(default=30, description="Request timeout in seconds")
    max_retries: int = Field(default=3, description="Maximum number of retries for failed requests")
    retry_delay: float = Field(default=1.0, description="Delay between retries in seconds")
    log_level: str = Field(default="INFO", description="Logging level")
    
    class Config:
        env_prefix = "XOPTPY_"


def setup_logging(level: str = "INFO") -> logging.Logger:
    """
    Set up logging for the AI Registry client.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger("xoptpy")
    
    # Avoid adding multiple handlers if already configured
    if logger.handlers:
        return logger
    
    # Create handler
    handler = logging.StreamHandler()
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(handler)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    return logger


def load_config_from_file(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from a file.
    
    Args:
        config_path: Path to configuration file (JSON format)
    
    Returns:
        Configuration dictionary
    """
    import json
    
    if config_path is None:
        # Look for config file in common locations
        possible_paths = [
            Path.cwd() / "xoptpy.json",
            Path.home() / ".xoptpy" / "config.json",
            Path("/etc/xoptpy/config.json"),
        ]
        
        for path in possible_paths:
            if path.exists():
                config_path = str(path)
                break
    
    if config_path and Path(config_path).exists():
        with open(config_path, 'r') as f:
            return json.load(f)
    
    return {}


def load_config(config_path: Optional[str] = None) -> ClientConfig:
    """
    Load configuration from environment variables and/or config file.
    
    Args:
        config_path: Optional path to configuration file
    
    Returns:
        ClientConfig instance
    """
    # Start with file-based config
    config_data = load_config_from_file(config_path)
    
    # Override with environment variables
    env_config = {
        "base_url": os.getenv("XOPTPY_BASE_URL"),
        "timeout": os.getenv("XOPTPY_TIMEOUT"),
        "max_retries": os.getenv("XOPTPY_MAX_RETRIES"),
        "retry_delay": os.getenv("XOPTPY_RETRY_DELAY"),
        "log_level": os.getenv("XOPTPY_LOG_LEVEL"),
    }
    
    # Filter out None values
    env_config = {k: v for k, v in env_config.items() if v is not None}
    
    # Convert string values to appropriate types
    if "timeout" in env_config:
        env_config["timeout"] = int(env_config["timeout"])
    if "max_retries" in env_config:
        env_config["max_retries"] = int(env_config["max_retries"])
    if "retry_delay" in env_config:
        env_config["retry_delay"] = float(env_config["retry_delay"])
    
    # Merge configurations (env variables take precedence)
    config_data.update(env_config)
    
    return ClientConfig(**config_data)