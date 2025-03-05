import os
import json
from pathlib import Path
import datetime
import re

class ScriptManager:
    """Class to manage Blender scripts"""
    
    def __init__(self, scripts_dir=None):
        """
        Initialize the ScriptManager
        
        Args:
            scripts_dir (str, optional): Directory to store scripts. If None, will use ./scripts
        """
        self.scripts_dir = Path(scripts_dir or Path.cwd() / "script_files")
        self.scripts_dir.mkdir(exist_ok=True, parents=True)
        
        # Create subdirectories
        self.scripts_path = self.scripts_dir / "scripts"
        self.results_path = self.scripts_dir / "results"
        self.metadata_path = self.scripts_dir / "metadata.json"
        
        self.scripts_path.mkdir(exist_ok=True)
        self.results_path.mkdir(exist_ok=True)
        
        # Initialize metadata
        self._init_metadata()
    
    def _init_metadata(self):
        """Initialize or load metadata file"""
        if not self.metadata_path.exists():
            self.metadata = {}
            self._save_metadata()
        else:
            try:
                with open(self.metadata_path, "r") as f:
                    self.metadata = json.load(f)
            except json.JSONDecodeError:
                # If the file is corrupted, initialize new metadata
                self.metadata = {}
                self._save_metadata()
    
    def _save_metadata(self):
        """Save metadata to file"""
        with open(self.metadata_path, "w") as f:
            json.dump(self.metadata, f, indent=2)
    
    def _validate_script_name(self, name):
        """Validate script name"""
        if not re.match(r'^[a-zA-Z0-9_-]+$', name):
            raise ValueError("Script name can only contain letters, numbers, underscores, and hyphens")
        return name
    
    def list_scripts(self):
        """List all available scripts with metadata"""
        scripts = []
        for script_name, metadata in self.metadata.items():
            script_info = metadata.copy()
            script_info["name"] = script_name
            scripts.append(script_info)
        return scripts
    
    def add_script(self, name, content):
        """
        Add a new script
        
        Args:
            name (str): Script name
            content (str): Script content
        """
        name = self._validate_script_name(name)
        script_path = self.scripts_path / f"{name}.py"
        
        if script_path.exists():
            raise ValueError(f"Script '{name}' already exists")
        
        # Save script content
        with open(script_path, "w") as f:
            f.write(content)
        
        # Update metadata
        now = datetime.datetime.now().isoformat()
        self.metadata[name] = {
            "created": now,
            "last_modified": now,
            "last_executed": None,
            "execution_count": 0
        }
        self._save_metadata()
    
    def edit_script(self, name, content):
        """
        Edit an existing script
        
        Args:
            name (str): Script name
            content (str): New script content
        """
        name = self._validate_script_name(name)
        script_path = self.scripts_path / f"{name}.py"
        
        if not script_path.exists():
            raise ValueError(f"Script '{name}' not found")
        
        # Save script content
        with open(script_path, "w") as f:
            f.write(content)
        
        # Update metadata
        now = datetime.datetime.now().isoformat()
        self.metadata[name]["last_modified"] = now
        self._save_metadata()
    
    def get_script(self, name):
        """
        Get script content
        
        Args:
            name (str): Script name
            
        Returns:
            str: Script content
        """
        name = self._validate_script_name(name)
        script_path = self.scripts_path / f"{name}.py"
        
        if not script_path.exists():
            raise ValueError(f"Script '{name}' not found")
        
        with open(script_path, "r") as f:
            return f.read()
    
    def remove_script(self, name):
        """
        Remove a script
        
        Args:
            name (str): Script name
        """
        name = self._validate_script_name(name)
        script_path = self.scripts_path / f"{name}.py"
        result_path = self.results_path / f"{name}.txt"
        
        if not script_path.exists():
            raise ValueError(f"Script '{name}' not found")
        
        # Remove script file
        script_path.unlink()
        
        # Remove result file if it exists
        if result_path.exists():
            result_path.unlink()
        
        # Update metadata
        if name in self.metadata:
            del self.metadata[name]
            self._save_metadata()
    
    def save_result(self, name, result):
        """
        Save script execution result
        
        Args:
            name (str): Script name
            result (str): Execution result
        """
        name = self._validate_script_name(name)
        result_path = self.results_path / f"{name}.txt"
        
        # Save result
        with open(result_path, "w") as f:
            f.write(result)
        
        # Update metadata
        if name in self.metadata:
            now = datetime.datetime.now().isoformat()
            self.metadata[name]["last_executed"] = now
            self.metadata[name]["execution_count"] = self.metadata[name].get("execution_count", 0) + 1
            self._save_metadata()
    
    def get_result(self, name):
        """
        Get script execution result
        
        Args:
            name (str): Script name
            
        Returns:
            str: Execution result
        """
        name = self._validate_script_name(name)
        result_path = self.results_path / f"{name}.txt"
        
        if not result_path.exists():
            return f"No execution results found for script '{name}'"
        
        with open(result_path, "r") as f:
            return f.read()
