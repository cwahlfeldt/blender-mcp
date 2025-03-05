import os
import subprocess
import sys
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class UVManager:
    """Manager for UV Python package installer and environment manager"""
    
    def __init__(self, env_dir=None):
        """
        Initialize UV manager
        
        Args:
            env_dir (str, optional): Directory to store environments
        """
        self.uv_bin = self._find_uv_executable()
        self.env_dir = Path(env_dir or Path.cwd() / "python_envs")
        self.env_dir.mkdir(exist_ok=True, parents=True)
    
    def _find_uv_executable(self):
        """Find the UV executable in the system"""
        # Check common names and locations
        common_names = ["uv", "uv.exe"]
        
        for name in common_names:
            try:
                # Check if we can run it with --version
                result = subprocess.run(
                    [name, "--version"], 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE, 
                    timeout=5,
                    text=True
                )
                if result.returncode == 0:
                    return name
            except (subprocess.SubprocessError, FileNotFoundError):
                continue
        
        # If not found, try to install it using pip
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "uv"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
            return "uv"  # Try the command directly after installation
        except Exception as e:
            logger.warning(f"Failed to install UV: {e}")
        
        return None
    
    def is_available(self):
        """Check if UV is available"""
        return self.uv_bin is not None
    
    def create_environment(self, name, python_version=None):
        """
        