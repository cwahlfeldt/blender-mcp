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
