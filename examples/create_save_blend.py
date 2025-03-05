import bpy
import os

# Define the output path (use a temporary location)
output_path = "/tmp/created_scene.blend"

# Clear the default scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create a simple scene with multiple objects
# Add a cube
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "MainCube"

# Add a sphere
bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(3, 0, 0))
sphere = bpy.context.active_object
sphere.name = "Sphere"

# Add a cylinder
bpy.ops.mesh.primitive_cylinder_add(radius=0.5, depth=2, location=(0, 3, 0))
cylinder = bpy.context.active_object
cylinder.name = "Cylinder"

# Create a material and assign to cube
red_mat = bpy.data.materials.new(name="Red")
red_mat.diffuse_color = (1, 0, 0, 1)
cube.data.materials.append(red_mat)

# Create another material and assign to sphere
blue_mat = bpy.data.materials.new(name="Blue")
blue_mat.diffuse_color = (0, 0, 1, 1)
sphere.data.materials.append(blue_mat)

# Create another material and assign to cylinder
green_mat = bpy.data.materials.new(name="Green")
green_mat.diffuse_color = (0, 1, 0, 1)
cylinder.data.materials.append(green_mat)

# Add a light
bpy.ops.object.light_add(type='SUN', location=(0, 0, 5))
light = bpy.context.active_object
light.name = "MainLight"

# Add a camera
bpy.ops.object.camera_add(location=(7, -7, 5))
camera = bpy.context.active_object
camera.name = "MainCamera"
camera.rotation_euler = (0.9, 0, 0.8)

# Set the active camera
bpy.context.scene.camera = camera

# Save the file
print(f"Saving blend file to: {output_path}")
bpy.ops.wm.save_as_mainfile(filepath=output_path)

print(f"Created and saved a new blend file with:")
print(f" - {cube.name} (Cube) with {red_mat.name} material")
print(f" - {sphere.name} (Sphere) with {blue_mat.name} material")
print(f" - {cylinder.name} (Cylinder) with {green_mat.name} material")
print(f" - {light.name} (Light)")
print(f" - {camera.name} (Camera)")
print(f"\nThe file has been saved to: {output_path}")
print(f"You can now use this file with other scripts using the blend_file parameter.")
