from mcp.server.fastmcp import FastMCP, Context
import os
import json
from pathlib import Path

from blender.executor import BlenderExecutor
from scripts.manager import ScriptManager

# Create an MCP server
mcp = FastMCP("BlenderScriptManager")

# Initialize script manager and blender executor
script_manager = ScriptManager()
blender_executor = BlenderExecutor()

# Scripts resources
@mcp.resource("scripts://list")
def list_scripts() -> str:
    """Get list of available scripts"""
    scripts = script_manager.list_scripts()
    return json.dumps(scripts)

@mcp.resource("script://{name}")
def get_script(name: str) -> str:
    """Get content of a specific script"""
    return script_manager.get_script(name)

@mcp.resource("result://{name}")
def get_result(name: str) -> str:
    """Get execution result of a script"""
    return script_manager.get_result(name)

# Script management tools
@mcp.tool()
def add_script(name: str, content: str) -> str:
    """Add a new script"""
    try:
        script_manager.add_script(name, content)
        return f"Script '{name}' added successfully"
    except Exception as e:
        return f"Error adding script: {str(e)}"

@mcp.tool()
def edit_script(name: str, content: str) -> str:
    """Edit an existing script"""
    try:
        script_manager.edit_script(name, content)
        return f"Script '{name}' updated successfully"
    except Exception as e:
        return f"Error updating script: {str(e)}"

@mcp.tool()
def execute_script(name: str, ctx: Context, blend_file: str = None) -> str:
    """
    Execute a script in Blender
    
    Args:
        name (str): Name of the script to execute
        ctx (Context): MCP context
        blend_file (str, optional): Path to a .blend file to use
    """
    try:
        ctx.info(f"Executing script '{name}'...")
        if blend_file:
            ctx.info(f"Using blend file: {blend_file}")
        
        script_content = script_manager.get_script(name)
        result = blender_executor.execute(name, script_content, blend_file)
        script_manager.save_result(name, result)
        return f"Script '{name}' executed successfully. Use 'result://{name}' to see the output."
    except Exception as e:
        error_msg = f"Error executing script: {str(e)}"
        script_manager.save_result(name, error_msg)
        return error_msg

@mcp.tool()
def remove_script(name: str) -> str:
    """Remove a script"""
    try:
        script_manager.remove_script(name)
        return f"Script '{name}' removed successfully"
    except Exception as e:
        return f"Error removing script: {str(e)}"

if __name__ == "__main__":
    # Run the server
    mcp.run()
