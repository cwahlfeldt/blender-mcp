import os
import json
from pathlib import Path
import tempfile

class UVTools:
    """Tools for UV mapping operations in Blender"""
    
    def __init__(self, executor):
        """
        Initialize UV tools with a BlenderExecutor
        
        Args:
            executor: BlenderExecutor instance for running scripts
        """
        self.executor = executor
        self.temp_dir = Path(tempfile.gettempdir()) / "blender_mcp_uv"
        self._setup()
    
    def _setup(self):
        """Setup the UV tools, create necessary directories"""
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def unwrap_object(self, object_name, method="ANGLE_BASED", blend_file=None):
        """
        Unwrap a specific object in a blend file
        
        Args:
            object_name (str): Name of the object to unwrap
            method (str): Unwrapping method (ANGLE_BASED, CONFORMAL, or SMART_PROJECT)
            blend_file (str): Path to the blend file
            
        Returns:
            dict: Result of the operation
        """
        if blend_file is None or not os.path.exists(blend_file):
            return {"error": f"Blend file not found: {blend_file}"}
        
        script = f"""
import bpy
import json

result = {{"success": False, "message": ""}}

# Check if the object exists
if "{object_name}" not in bpy.data.objects:
    result["message"] = f"Object '{object_name}' not found in the blend file"
else:
    obj = bpy.data.objects["{object_name}"]
    
    # Check if it's a mesh
    if obj.type != 'MESH':
        result["message"] = f"Object '{object_name}' is not a mesh (type: {{obj.type}})"
    else:
        # Select only this object and make it active
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        
        # Go to edit mode
        bpy.ops.object.mode_set(mode='EDIT')
        
        # Select all faces
        bpy.ops.mesh.select_all(action='SELECT')
        
        # Perform the unwrap operation
        try:
            method = "{method}"
            if method == "SMART_PROJECT":
                bpy.ops.uv.smart_project(angle_limit=66, island_margin=0.02)
            else:
                # ANGLE_BASED or CONFORMAL
                bpy.ops.uv.unwrap(method=method, margin=0.02)
                
            result["success"] = True
            result["message"] = f"Successfully unwrapped {{obj.name}} using {{method}} method"
            
            # Get UV stats
            me = obj.data
            if me.uv_layers:
                result["uv_layers"] = [layer.name for layer in me.uv_layers]
                result["active_uv"] = me.uv_layers.active.name if me.uv_layers.active else None
                result["uv_count"] = len(me.uv_layers)
            else:
                result["message"] += "\\nNo UV layers found after unwrapping. This may indicate an error."
        except Exception as e:
            result["message"] = f"Error during unwrapping: {{str(e)}}"
        
        # Return to object mode
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # Save the file
        bpy.ops.wm.save_mainfile()

# Print the result as JSON for parsing
print(json.dumps(result))
"""
        
        # Execute the script
        output = self.executor.execute("unwrap_object", script, blend_file)
        
        # Try to parse the JSON result
        try:
            # Extract JSON from the output (it may contain other print statements)
            lines = output.strip().split('\n')
            for line in lines:
                try:
                    result = json.loads(line)
                    if isinstance(result, dict) and "success" in result:
                        return result
                except json.JSONDecodeError:
                    pass
            
            # If no valid JSON found, return the raw output
            return {"error": "Could not parse result", "output": output}
        except Exception as e:
            return {"error": f"Error parsing result: {str(e)}", "output": output}
    
    def mark_seams(self, object_name, blend_file=None, seam_angle=80):
        """
        Mark seams on an object based on angle
        
        Args:
            object_name (str): Name of the object to mark seams on
            blend_file (str): Path to the blend file
            seam_angle (float): Angle in degrees to use for marking seams
            
        Returns:
            dict: Result of the operation
        """
        if blend_file is None or not os.path.exists(blend_file):
            return {"error": f"Blend file not found: {blend_file}"}
        
        script = f"""
import bpy
import json
import math
import bmesh

result = {{"success": False, "message": ""}}

# Check if the object exists
if "{object_name}" not in bpy.data.objects:
    result["message"] = f"Object '{object_name}' not found in the blend file"
else:
    obj = bpy.data.objects["{object_name}"]
    
    # Check if it's a mesh
    if obj.type != 'MESH':
        result["message"] = f"Object '{object_name}' is not a mesh (type: {{obj.type}})"
    else:
        # Select only this object and make it active
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        
        # Go to edit mode
        bpy.ops.object.mode_set(mode='EDIT')
        
        # Get the bmesh
        me = obj.data
        bm = bmesh.from_edit_mesh(me)
        
        # Ensure we have custom data layers for seams
        if not bm.edges.layers.seam:
            bm.edges.layers.seam.new()
        
        seam_layer = bm.edges.layers.seam.active
        
        # Mark seams by angle
        seam_angle_rad = {seam_angle} * (math.pi / 180.0)
        seam_count = 0
        
        for edge in bm.edges:
            if edge.is_boundary:
                # Mark boundary edges as seams
                edge[seam_layer] = True
                seam_count += 1
                continue
            
            # Get connected faces
            if len(edge.link_faces) == 2:
                f1, f2 = edge.link_faces
                angle = f1.normal.angle(f2.normal)
                
                # If angle between faces exceeds threshold, mark as seam
                if angle > seam_angle_rad:
                    edge[seam_layer] = True
                    seam_count += 1
        
        # Update the mesh and unwrap
        bmesh.update_edit_mesh(me)
        
        # Select all faces
        bpy.ops.mesh.select_all(action='SELECT')
        
        # Unwrap using the seams
        bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.02)
        
        result["success"] = True
        result["message"] = f"Marked {{seam_count}} seams on {{obj.name}} using angle threshold of {seam_angle}° and unwrapped"
        result["seam_count"] = seam_count
        
        # Return to object mode
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # Save the file
        bpy.ops.wm.save_mainfile()

# Print the result as JSON for parsing
print(json.dumps(result))
"""
        
        # Execute the script
        output = self.executor.execute("mark_seams", script, blend_file)
        
        # Try to parse the JSON result
        try:
            # Extract JSON from the output
            lines = output.strip().split('\n')
            for line in lines:
                try:
                    result = json.loads(line)
                    if isinstance(result, dict) and "success" in result:
                        return result
                except json.JSONDecodeError:
                    pass
            
            # If no valid JSON found, return the raw output
            return {"error": "Could not parse result", "output": output}
        except Exception as e:
            return {"error": f"Error parsing result: {str(e)}", "output": output}
    
    def texture_object(self, object_name, blend_file=None, texture_type="checker", color1=None, color2=None):
        """
        Apply a textured material to an object using its UV maps
        
        Args:
            object_name (str): Name of the object to texture
            blend_file (str): Path to the blend file
            texture_type (str): Type of texture (checker, gradient, grid)
            color1 (list): First color as [r, g, b] (0.0-1.0 range)
            color2 (list): Second color as [r, g, b] (0.0-1.0 range)
            
        Returns:
            dict: Result of the operation
        """
        if blend_file is None or not os.path.exists(blend_file):
            return {"error": f"Blend file not found: {blend_file}"}
        
        # Set default colors if none provided
        if color1 is None:
            color1 = [0.8, 0.1, 0.1]  # Red
        if color2 is None:
            color2 = [0.1, 0.1, 0.8]  # Blue
        
        script = f"""
import bpy
import json

result = {{"success": False, "message": ""}}

# Check if the object exists
if "{object_name}" not in bpy.data.objects:
    result["message"] = f"Object '{object_name}' not found in the blend file"
else:
    obj = bpy.data.objects["{object_name}"]
    
    # Check if it's a mesh
    if obj.type != 'MESH':
        result["message"] = f"Object '{object_name}' is not a mesh (type: {{obj.type}})"
    else:
        # Check if the object has UVs
        if not obj.data.uv_layers:
            result["message"] = f"Object '{object_name}' has no UV layers. Unwrap it first."
        else:
            # Create a new material
            mat_name = f"{{obj.name}}_{{'{texture_type}'}}_Material"
            mat = bpy.data.materials.new(name=mat_name)
            mat.use_nodes = True
            
            # Clear default nodes
            node_tree = mat.node_tree
            for node in node_tree.nodes:
                node_tree.nodes.remove(node)
            
            # Create texture coordinate node
            tex_coord = node_tree.nodes.new(type='ShaderNodeTexCoord')
            tex_coord.location = (-600, 0)
            
            # Create BSDF node
            bsdf = node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')
            bsdf.location = (0, 0)
            
            # Create output node
            output = node_tree.nodes.new(type='ShaderNodeOutputMaterial')
            output.location = (200, 0)
            
            # Different texture setup based on type
            texture_type = "{texture_type}".lower()
            
            if texture_type == "checker":
                # Create checker texture node
                checker = node_tree.nodes.new(type='ShaderNodeTexChecker')
                checker.location = (-400, 0)
                checker.inputs['Scale'].default_value = 4.0
                checker.inputs['Color1'].default_value = {color1 + [1.0]}
                checker.inputs['Color2'].default_value = {color2 + [1.0]}
                
                # Link nodes
                node_tree.links.new(tex_coord.outputs['UV'], checker.inputs['Vector'])
                node_tree.links.new(checker.outputs['Color'], bsdf.inputs['Base Color'])
                
            elif texture_type == "gradient":
                # Create gradient texture node
                gradient = node_tree.nodes.new(type='ShaderNodeTexGradient')
                gradient.location = (-400, 0)
                
                # Create color ramp for the gradient
                color_ramp = node_tree.nodes.new(type='ShaderNodeValToRGB')
                color_ramp.location = (-200, 0)
                # Customize the color ramp
                color_ramp