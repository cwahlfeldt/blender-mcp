import bpy
import os

# Print information about the current scene
print(f"Current Blender version: {bpy.app.version_string}")
print(f"Current file: {bpy.data.filepath}")

# List all objects in the scene
print("\nObjects in the scene:")
for obj in bpy.data.objects:
    print(f" - {obj.name} ({obj.type})")

# List all materials
print("\nMaterials in the scene:")
for mat in bpy.data.materials:
    print(f" - {mat.name}")

# List all scenes
print("\nScenes in the file:")
for scene in bpy.data.scenes:
    print(f" - {scene.name}")

# Make a small change to demonstrate saving
if bpy.data.objects:
    # Move the first object up by 1 unit
    obj = bpy.data.objects[0]
    original_loc = obj.location.copy()
    obj.location.z += 1
    print(f"\nMoved {obj.name} up by 1 unit (from {original_loc.z} to {obj.location.z})")

    # Note about saving
    print("\nNote: To save changes to the blend file, uncomment the save line below.")
    # bpy.ops.wm.save_mainfile()
