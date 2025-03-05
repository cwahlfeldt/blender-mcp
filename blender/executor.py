import subprocess
import os
import tempfile
from pathlib import Path
import logging

class BlenderExecutor:
    """Class to handle script execution in Blender"""
    
    def __init__(self, blender_path=None, timeout=60):
        """
        Initialize the BlenderExecutor
        
        Args:
            blender_path (str, optional): Path to the Blender executable. If None, will try to find it.
            timeout (int, optional): Timeout for script execution in seconds
        """
        self.blender_path = blender_path or self._find_blender_executable()
        self.timeout = timeout
        self.temp_dir = Path(tempfile.gettempdir()) / "blender_mcp"
        self._setup()
    
    def _setup(self):
        """Setup the executor, create necessary directories"""
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def _find_blender_executable(self):
        """Find Blender executable path"""
        # Try common locations
        common_paths = [
            "blender",  # If it's in PATH
            "/usr/bin/blender",
            "/usr/local/bin/blender",
            "/Applications/Blender.app/Contents/MacOS/Blender",
            "C:\\Program Files\\Blender Foundation\\Blender\\blender.exe",
        ]
        
        for path in common_paths:
            try:
                # Just check if we can run it with --version
                subprocess.run([path, "--version"], 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE, 
                               timeout=5)
                return path
            except (subprocess.SubprocessError, FileNotFoundError):
                continue
        
        # If we couldn't find it, default to "blender" and hope it's in PATH
        return "blender"
    
    def execute(self, script_name, script_content, blend_file=None):
        """
        Execute a script in Blender
        
        Args:
            script_name (str): Name of the script
            script_content (str): Content of the script to execute
            blend_file (str, optional): Path to a .blend file to use
            
        Returns:
            str: Output of the script execution
        """
        # Create a temporary script file
        script_file = self.temp_dir / f"{script_name}.py"
        output_file = self.temp_dir / f"{script_name}.out"
        
        # Write the script content with output capture
        with open(script_file, "w") as f:
            # Add code to capture stdout and stderr
            wrapped_script = f"""
import sys
import io
import traceback

# Redirect stdout and stderr
old_stdout = sys.stdout
old_stderr = sys.stderr
stdout_buffer = io.StringIO()
stderr_buffer = io.StringIO()
sys.stdout = stdout_buffer
sys.stderr = stderr_buffer

try:
    # Execute the script
{script_content.replace('\n', '\n    ')}
except Exception as e:
    print(f"Error executing script: {{e}}")
    traceback.print_exc()
finally:
    # Restore stdout and stderr
    sys.stdout = old_stdout
    sys.stderr = old_stderr
    
    # Write output to file
    with open(r"{output_file}", "w") as output:
        output.write(stdout_buffer.getvalue())
        output.write("\\n\\n")
        output.write(stderr_buffer.getvalue())
"""
            f.write(wrapped_script)
        
        try:
            # Run Blender with the script
            cmd = [
                self.blender_path,
                "--background",  # Run without GUI
            ]
            
            # Add blend file if provided
            if blend_file:
                if os.path.exists(blend_file):
                    cmd.extend(["--file", blend_file])
                else:
                    return f"Error: Blend file not found: {blend_file}"
            
            # Add Python script
            cmd.extend(["--python", str(script_file)])
            
            process = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=self.timeout,
                text=True
            )
            
            # Check if the output file exists
            if output_file.exists():
                with open(output_file, "r") as f:
                    script_output = f.read()
            else:
                script_output = "No output captured from script."
            
            # Add Blender's stdout/stderr if there was an error
            if process.returncode != 0:
                script_output += "\n\nBlender process output:\n"
                script_output += f"STDOUT: {process.stdout}\n"
                script_output += f"STDERR: {process.stderr}"
            
            return script_output
        
        except subprocess.TimeoutExpired:
            return f"Script execution timed out after {self.timeout} seconds"
        except Exception as e:
            return f"Error executing script: {str(e)}"
        finally:
            # Clean up temp files
            try:
                if script_file.exists():
                    script_file.unlink()
                if output_file.exists():
                    output_file.unlink()
            except Exception as e:
                logging.warning(f"Failed to clean up temp files: {e}")
