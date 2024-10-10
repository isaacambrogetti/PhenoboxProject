import bpy
import open3d as o3d   # installed in \'Program Files'\'Blender Foundation'\'Blender 4.1'\4.1\python\
import numpy as np

# Function to convert Blender mesh to Open3D point cloud
def blender_mesh_to_open3d():
    obj = bpy.context.active_object
    mesh = obj.data
    vertices = np.array([v.co for v in mesh.vertices])
    colors = np.array([obj.data.vertex_colors.active.data[i].color[:3] for i in range(len(mesh.vertices))])
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(vertices)
    pcd.colors = o3d.utility.Vector3dVector(colors)
    return pcd

# Function to convert Open3D point cloud to Blender mesh
def open3d_to_blender_mesh(pcd):
    vertices = np.asarray(pcd.points)
    colors = np.asarray(pcd.colors)
    mesh = bpy.data.meshes.new("FilteredMesh")
    mesh.from_pydata(vertices, [], [])
    obj = bpy.data.objects.new("FilteredObject", mesh)
    bpy.context.collection.objects.link(obj)
    # Add vertex colors
    color_layer = mesh.vertex_colors.new(name="Col")
    for i, col in enumerate(colors):
        color_layer.data[i].color = (*col, 1.0)
    return obj

# Load the point cloud from Blender
pcd = blender_mesh_to_open3d()

# Define the color to filter out (e.g., red color)
color_to_filter = np.array([1.0, 0.0, 0.0])  # RGB values in range [0, 1]
tolerance = 0.1  # Adjust tolerance as needed

# Create a mask for points that do not match the color
colors = np.asarray(pcd.colors)
mask = np.linalg.norm(colors - color_to_filter, axis=1) > tolerance

# Filter points and colors
filtered_points = np.asarray(pcd.points)[mask]
filtered_colors = colors[mask]

# Create a new point cloud with the filtered points
filtered_pcd = o3d.geometry.PointCloud()
filtered_pcd.points = o3d.utility.Vector3dVector(filtered_points)
filtered_pcd.colors = o3d.utility.Vector3dVector(filtered_colors)

# Convert the filtered point cloud back to Blender mesh
open3d_to_blender_mesh(filtered_pcd)