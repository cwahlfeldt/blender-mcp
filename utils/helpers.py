import os
import sys
import subprocess
from pathlib import Path
import logging

def setup_logger(name, level=logging.INFO):
    """Set up and return a logger"""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Create console handler
    ch = logging.StreamHandler()
    ch.setLevel(level)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(ch)
    
    return logger

def verify_blender_installation():
    """
    Verify Blender is installed and return its version
    
    Returns:
        tuple: (bool, str) - (is_installed, version_or_error_message)
    """
    common_paths = [
        "blender",  # If it's in PATH
        "/usr/bin/blender",
        "/usr/local/bin/blender",
        "/Applications/Blender.app/Contents/MacOS/Blender",
        "C:\\Program Files\\Blender Foundation\\Blender\\blender.exe",
    ]
    
    for path in common_paths:
        try:
            result = subprocess.run(
                [path, "--version"], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                timeout=5,
                text=True
            )
            
            # Extract version from output
            version_output = result.stdout
            return True, version_output.strip()
        except (subprocess.SubprocessError, FileNotFoundError):
            continue
    
    return False, "Blender not found. Please install Blender or set the correct path."

def generate_example_script():
    """Generate an example Blender script"""
    return """
import bpy

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create a cube
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))

# Create a material
mat = bpy.data.materials.new(name="Red Material")
mat.diffuse_color = (1, 0, 0, 1)  # Red

# Assign material to the cube
cube = bpy.context.active_object
if cube.data.materials:
    cube.data.materials[0] = mat
else:
    cube.data.materials.append(mat)

# Print confirmation
print("Created a red cube at the origin!")
"""

def generate_blend_file_example_script():
    """Generate an example script that works with a blend file"""
    return """
import bpy
import os

# Print information about the current scene
print(f"Current Blender version: {bpy.app.version_string}")
print(f"Current file: {bpy.data.filepath}")

# List all objects in the scene
print("\\nObjects in the scene:")
for obj in bpy.data.objects:
    print(f" - {obj.name} ({obj.type})")

# List all materials
print("\\nMaterials in the scene:")
for mat in bpy.data.materials:
    print(f" - {mat.name}")

# List all scenes
print("\\nScenes in the file:")
for scene in bpy.data.scenes:
    print(f" - {scene.name}")

# Make a small change to demonstrate saving
if bpy.data.objects:
    # Move the first object up by 1 unit
    obj = bpy.data.objects[0]
    original_loc = obj.location.copy()
    obj.location.z += 1
    print(f"\\nMoved {obj.name} up by 1 unit (from {original_loc.z} to {obj.location.z})")

    # Note about saving
    print("\\nNote: To save changes to the blend file, uncomment the save line below.")
    # bpy.ops.wm.save_mainfile()
"""

def generate_readme():
    """Generate README content for the project"""
    return """# Blender MCP Server

A Model Context Protocol (MCP) server for managing and executing Blender scripts.

## Features

- Add, edit, execute, and remove Blender Python scripts
- Execute scripts in a headless Blender environment
- View execution results and errors
- Track script metadata (creation date, last modified, execution count)

## Requirements

- Python 3.7+
- Blender installed and accessible
- MCP library (`pip install mcp`)

## Usage

1. Start the server:
   ```
   python server.py
   ```

2. Connect to the server using an MCP client (like Claude Desktop)

3. Use the provided tools to manage scripts:
   - `add_script(name, content)` - Add a new script
   - `edit_script(name, content)` - Edit an existing script
   - `execute_script(name)` - Execute a script in Blender
   - `remove_script(name)` - Remove a script

4. Access resources to get information:
   - `scripts://list` - Get list of available scripts
   - `script://{name}` - Get content of a specific script
   - `result://{name}` - Get execution result of a script

## Example

```python
# Add a simple script
add_script("hello_cube", '''
import bpy

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create a cube
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
print("Cube created!")
''')

# Execute the script
execute_script("hello_cube")

# Get the result
result = get_resource("result://hello_cube")
print(result)
```

## License

MIT
"""

def create_empty_init_files(root_dir):
    """
    Create empty __init__.py files in all subdirectories
    
    Args:
        root_dir (str): Root directory path
    """
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Skip hidden directories
        dirnames[:] = [d for d in dirnames if not d.startswith('.')]
        
        # Create __init__.py if it doesn't exist
        init_file = os.path.join(dirpath, "__init__.py")
        if not os.path.exists(init_file):
            with open(init_file, 'w') as f:
                pass  # Create empty file
