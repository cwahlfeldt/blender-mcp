import bpy
import bmesh
from mathutils import Vector

def create_cube_with_uv():
    # Clear existing objects
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    # Create a cube
    bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
    cube = bpy.context.active_object
    cube.name = "UV_Cube"
    
    # Switch to edit mode to modify mesh and create UVs
    bpy.ops.object.mode_set(mode='EDIT')
    
    # Get the mesh data in edit mode
    me = cube.data
    bm = bmesh.from_edit_mesh(me)
    
    # Ensure UV layers exist
    if not bm.loops.layers.uv:
        bm.loops.layers.uv.new("UVMap")
    
    uv_layer = bm.loops.layers.uv.active
    
    # Create a simple UV mapping (cube unwrap)
    # Each face will get a portion of the UV space
    faces = [f for f in bm.faces]
    
    # Simple planar UV mapping based on face normal direction
    for i, face in enumerate(faces):
        # Calculate uv position (divide UV space into a 3x2 grid)
        row = i // 3
        col = i % 3
        
        # Define UV coordinates for this face
        min_u, max_u = col / 3, (col + 1) / 3
        min_v, max_v = row / 2, (row + 1) / 2
        
        # Define corner indices for different UV layouts based on face orientation
        if face.normal.to_tuple(1) in [(0, 0, 1), (0, 0, -1)]:  # top/bottom
            indices = [0, 1, 2, 3]
        elif face.normal.to_tuple(1) in [(0, 1, 0), (0, -1, 0)]:  # front/back
            indices = [0, 1, 2, 3]
        else:  # sides
            indices = [0, 1, 2, 3]
        
        # UV coordinates for the corners of this face in the UV grid
        uvs = [
            Vector((min_u, min_v)),
            Vector((max_u, min_v)),
            Vector((max_u, max_v)),
            Vector((min_u, max_v))
        ]
        
        # Assign UV coordinates to the face
        for j, loop in enumerate(face.loops):
            loop[uv_layer].uv = uvs[indices[j]]
    
    # Update the mesh
    bmesh.update_edit_mesh(me)
    
    # Switch back to object mode
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Create a material with a texture
    create_textured_material(cube)
    
    print("Created a cube with UV mapping")
    return cube

def create_textured_material(obj):
    # Create a new material
    mat = bpy.data.materials.new(name="Textured_Material")
    mat.use_nodes = True
    
    # Clear default nodes
    node_tree = mat.node_tree
    for node in node_tree.nodes:
        node_tree.nodes.remove(node)
    
    # Create texture coordinate node
    tex_coord = node_tree.nodes.new(type='ShaderNodeTexCoord')
    tex_coord.location = (-600, 0)
    
    # Create checker texture node
    checker = node_tree.nodes.new(type='ShaderNodeTexChecker')
    checker.location = (-400, 0)
    checker.inputs['Scale'].default_value = 4.0  # Larger checkers
    checker.inputs['Color1'].default_value = (0.8, 0.1, 0.1, 1.0)  # Red
    checker.inputs['Color2'].default_value = (0.1, 0.1, 0.8, 1.0)  # Blue
    
    # Create BSDF node
    bsdf = node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (-100, 0)
    
    # Create output node
    output = node_tree.nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (200, 0)
    
    # Link nodes
    node_tree.links.new(tex_coord.outputs['UV'], checker.inputs['Vector'])
    node_tree.links.new(checker.outputs['Color'], bsdf.inputs['Base Color'])
    node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    # Assign material to object
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)
    
    print("Created textured material with checker pattern")

def create_uv_mapped_plane():
    # Create a plane
    bpy.ops.mesh.primitive_plane_add(size=2, location=(3, 0, 0))
    plane = bpy.context.active_object
    plane.name = "UV_Plane"
    
    # Subdivide for more detail
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.subdivide(number_cuts=4)
    
    # Smart UV project
    bpy.ops.uv.smart_project(angle_limit=66, island_margin=0.02)
    
    # Switch back to object mode
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Create a gradient material
    create_gradient_material(plane)
    
    print("Created a plane with smart UV projection")
    return plane

def create_gradient_material(obj):
    # Create a new material
    mat = bpy.data.materials.new(name="Gradient_Material")
    mat.use_nodes = True
    
    # Clear default nodes
    node_tree = mat.node_tree
    for node in node_tree.nodes:
        node_tree.nodes.remove(node)
    
    # Create texture coordinate node
    tex_coord = node_tree.nodes.new(type='ShaderNodeTexCoord')
    tex_coord.location = (-600, 0)
    
    # Create gradient texture node
    gradient = node_tree.nodes.new(type='ShaderNodeTexGradient')
    gradient.location = (-400, 0)
    
    # Create color ramp for the gradient
    color_ramp = node_tree.nodes.new(type='ShaderNodeValToRGB')
    color_ramp.location = (-200, 0)
    # Customize the color ramp
    color_ramp.color_ramp.elements[0].color = (0.0, 0.5, 0.0, 1.0)  # Green
    color_ramp.color_ramp.elements[1].color = (1.0, 1.0, 0.0, 1.0)  # Yellow
    # Add a middle element
    element = color_ramp.color_ramp.elements.new(0.5)
    element.color = (0.0, 0.8, 0.8, 1.0)  # Cyan
    
    # Create BSDF node
    bsdf = node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)
    
    # Create output node
    output = node_tree.nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (200, 0)
    
    # Link nodes
    node_tree.links.new(tex_coord.outputs['UV'], gradient.inputs['Vector'])
    node_tree.links.new(gradient.outputs['Fac'], color_ramp.inputs['Fac'])
    node_tree.links.new(color_ramp.outputs['Color'], bsdf.inputs['Base Color'])
    node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    # Assign material to object
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)
    
    print("Created gradient material")

def create_uv_sphere_with_seams():
    # Create a sphere
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(-3, 0, 0), segments=32, ring_count=16)
    sphere = bpy.context.active_object
    sphere.name = "UV_Sphere"
    
    # Switch to edit mode
    bpy.ops.object.mode_set(mode='EDIT')
    
    # Select all edges
    bpy.ops.mesh.select_all(action='DESELECT')
    
    # Get the mesh data
    me = sphere.data
    bm = bmesh.from_edit_mesh(me)
    
    # Mark some edges as seams for better unwrapping
    # Select edges along longitude
    for edge in bm.edges:
        v1, v2 = edge.verts
        # Edges along longitude line (connecting top to bottom)
        if abs(v1.co.x) < 0.01 and abs(v2.co.x) < 0.01 and v1.co.y * v2.co.y >= 0:
            edge.select = True
    
    # Mark selected edges as seams
    bpy.ops.mesh.mark_seam(clear=False)
    
    # Select all faces
    bpy.ops.mesh.select_all(action='SELECT')
    
    # Unwrap using the seams
    bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.02)
    
    # Switch back to object mode
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Create a grid material
    create_grid_material(sphere)
    
    print("Created a sphere with seam-based UV unwrapping")
    return sphere

def create_grid_material(obj):
    # Create a new material
    mat = bpy.data.materials.new(name="Grid_Material")
    mat.use_nodes = True
    
    # Clear default nodes
    node_tree = mat.node_tree
    for node in node_tree.nodes:
        node_tree.nodes.remove(node)
    
    # Create texture coordinate node
    tex_coord = node_tree.nodes.new(type='ShaderNodeTexCoord')
    tex_coord.location = (-600, 0)
    
    # Create mapping node for extra control
    mapping = node_tree.nodes.new(type='ShaderNodeMapping')
    mapping.location = (-400, 0)
    mapping.inputs['Scale'].default_value = (10, 10, 10)  # More grid cells
    
    # Create grid texture node
    grid = node_tree.nodes.new(type='ShaderNodeTexGrid')
    grid.location = (-200, 0)
    grid.inputs['Scale'].default_value = 1.0
    grid.inputs['Line Width'].default_value = 0.02
    
    # Create BSDF node
    bsdf = node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)
    bsdf.inputs['Base Color'].default_value = (0.2, 0.5, 0.8, 1.0)  # Blue
    
    # Create output node
    output = node_tree.nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (200, 0)
    
    # Link nodes
    node_tree.links.new(tex_coord.outputs['UV'], mapping.inputs['Vector'])
    node_tree.links.new(mapping.outputs['Vector'], grid.inputs['Vector'])
    node_tree.links.new(grid.outputs['Fac'], bsdf.inputs['Emission Strength'])
    node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    # Assign material to object
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)
    
    print("Created grid material for UV visualization")

def save_blend_file(filepath="/tmp/uv_mapping_example.blend"):
    bpy.ops.wm.save_as_mainfile(filepath=filepath)
    print(f"Saved blend file to: {filepath}")
    return filepath

# Main function to create all examples
def create_uv_examples():
    # Create camera for better view
    bpy.ops.object.camera_add(location=(0, -10, 2), rotation=(1.4, 0, 0))
    bpy.context.scene.camera = bpy.context.object
    
    # Create objects with UV mappings
    cube = create_cube_with_uv()
    plane = create_uv_mapped_plane()
    sphere = create_uv_sphere_with_seams()
    
    # Set up render settings
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.device = 'CPU'
    
    # Add a light for better visualization
    bpy.ops.object.light_add(type='SUN', location=(0, 0, 5))
    
    # Save the file for later use
    filepath = save_blend_file()
    
    return {
        'objects': [cube.name, plane.name, sphere.name],
        'blend_file': filepath
    }

# Run the examples
result = create_uv_examples()
print("\nCreated examples:")
for obj_name in result['objects']:
    print(f"- {obj_name}")
print(f"\nBlend file saved to: {result['blend_file']}")
print("You can use this file to study the UV mappings or modify them further.")
