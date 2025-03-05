import os
import subprocess
import sys
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class UVIntegration:
    """Integration with UV Python for package management"""
    
    def __init__(self):
        """Initialize UV integration utils"""
        self.uv_path = self._find_uv_executable()
        self.has_uv = self.uv_path is not None
    
    def _find_uv_executable(self):
        """Find the UV executable in the system"""
        # Try common locations
        common_names = ["uv", "uv.exe"]
        
        for name in common_names:
            try:
                # Just check if we can run it with --version
                subprocess.run([name, "--version"], 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE, 
                               timeout=5)
                return name
            except (subprocess.SubprocessError, FileNotFoundError):
                continue
        
        return None
    
    def is_available(self):
        """Check if UV is available on the system"""
        return self.has_uv
    
    def install_dependencies(self, dependencies, venv_path=None):
        """
        Install dependencies using UV
        
        Args:
            dependencies (list): List of dependencies to install
            venv_path (str, optional): Path to virtual environment
            
        Returns:
            dict: Result of the operation
        """
        if not self.has_uv:
            return {
                "success": False,
                "message": "UV Python is not available. Please install it first."
            }
        
        cmd = [self.uv_path, "pip", "install"]
        cmd.extend(dependencies)
        
        env = os.environ.copy()
        if venv_path:
            # Set virtual environment path
            if sys.platform == "win32":
                env["VIRTUAL_ENV"] = venv_path
                env["PATH"] = os.path.join(venv_path, "Scripts") + os.pathsep + env["PATH"]
            else:
                env["VIRTUAL_ENV"] = venv_path
                env["PATH"] = os.path.join(venv_path, "bin") + os.pathsep + env["PATH"]
        
        try:
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                text=True
            )
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "message": f"Successfully installed dependencies: {', '.join(dependencies)}",
                    "output": result.stdout
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to install dependencies",
                    "error": result.stderr,
                    "output": result.stdout
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error during installation: {str(e)}"
            }
    
    def create_venv(self, path):
        """
        Create a virtual environment using UV
        
        Args:
            path (str): Path for the virtual environment
            
        Returns:
            dict: Result of the operation
        """
        if not self.has_uv:
            return {
                "success": False,
                "message": "UV Python is not available. Please install it first."
            }
        
        path = os.path.abspath(path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        cmd = [self.uv_path, "venv", path]
        
        try:
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "message": f"Successfully created virtual environment at {path}",
                    "path": path,
                    "output": result.stdout
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to create virtual environment",
                    "error": result.stderr,
                    "output": result.stdout
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error creating virtual environment: {str(e)}"
            }
    
    def get_installed_packages(self, venv_path=None):
        """
        Get list of installed packages
        
        Args:
            venv_path (str, optional): Path to virtual environment
            
        Returns:
            dict: Result of the operation with list of packages
        """
        if not self.has_uv:
            return {
                "success": False,
                "message": "UV Python is not available. Please install it first."
            }
        
        cmd = [self.uv_path, "pip", "list", "--format=json"]
        
        env = os.environ.copy()
        if venv_path:
            # Set virtual environment path
            if sys.platform == "win32":
                env["VIRTUAL_ENV"] = venv_path
                env["PATH"] = os.path.join(venv_path, "Scripts") + os.pathsep + env["PATH"]
            else:
                env["VIRTUAL_ENV"] = venv_path
                env["PATH"] = os.path.join(venv_path, "bin") + os.pathsep + env["PATH"]
        
        try:
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                text=True
            )
            
            if result.returncode == 0:
                try:
                    packages = json.loads(result.stdout)
                    return {
                        "success": True,
                        "packages": packages,
                        "count": len(packages)
                    }
                except json.JSONDecodeError:
                    return {
                        "success": False,
                        "message": "Failed to parse package list",
                        "output": result.stdout
                    }
            else:
                return {
                    "success": False,
                    "message": "Failed to get list of packages",
                    "error": result.stderr,
                    "output": result.stdout
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error getting packages: {str(e)}"
            }
    
    def run_script_in_venv(self, script_path, venv_path):
        """
        Run a Python script in a virtual environment
        
        Args:
            script_path (str): Path to the script
            venv_path (str): Path to virtual environment
            
        Returns:
            dict: Result of the operation
        """
        if not os.path.exists(script_path):
            return {
                "success": False,
                "message": f"Script not found: {script_path}"
            }
        
        if not os.path.exists(venv_path):
            return {
                "success": False,
                "message": f"Virtual environment not found: {venv_path}"
            }
        
        # Get path to Python in the virtual environment
        if sys.platform == "win32":
            python_path = os.path.join(venv_path, "Scripts", "python.exe")
        else:
            python_path = os.path.join(venv_path, "bin", "python")
        
        if not os.path.exists(python_path):
            return {
                "success": False,
                "message": f"Python not found in virtual environment: {python_path}"
            }
        
        try:
            result = subprocess.run(
                [python_path, script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            return {
                "success": result.returncode == 0,
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error running script: {str(e)}"
            }
