# Blender MCP Server

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
   - `execute_script(name, blend_file=None)` - Execute a script in Blender, optionally specifying a .blend file
   - `remove_script(name)` - Remove a script

4. Access resources to get information:
   - `scripts://list` - Get list of available scripts
   - `script://{name}` - Get content of a specific script
   - `result://{name}` - Get execution result of a script

## Examples

### Basic Example

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
# Access using: result://hello_cube
```

### Working with Blend Files

```python
# Add a script that works with a blend file
add_script("analyze_scene", '''
import bpy

# Print information about the current scene
print(f"Current Blender version: {bpy.app.version_string}")
print(f"Current file: {bpy.data.filepath}")

# List all objects in the scene
print("\\nObjects in the scene:")
for obj in bpy.data.objects:
    print(f" - {obj.name} ({obj.type})")
''')

# Execute with a specific blend file
execute_script("analyze_scene", blend_file="/path/to/your/project.blend")

# Get the result
# Access using: result://analyze_scene
```

## How It Works

1. When a script is added, it's stored in the `script_files/scripts` directory
2. When executed, the script is run in a headless Blender instance
   - If a blend file is specified, Blender will open that file before running the script
   - Otherwise, a default empty Blender scene is used
3. Output and errors are captured and stored in the `script_files/results` directory
4. Metadata about scripts is tracked in `script_files/metadata.json`

## Installation

1. Clone this repository
2. Install the MCP library: `pip install mcp`
3. Ensure Blender is installed and accessible from your PATH

## License

MIT
