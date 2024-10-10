import bpy
import open3d as o3d
import numpy as np
from sklearn.cluster import DBSCAN
from mathutils import Matrix

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

# Extract points from the point cloud
points = np.asarray(pcd.points)

# Apply DBSCAN clustering to the point cloud
eps = 0.1  # Adjust epsilon as needed (max distance between two points in a cluster)
min_samples = 10  # Minimum number of points to form a cluster

clustering = DBSCAN(eps=eps, min_samples=min_samples).fit(points)
labels = clustering.labels_

# Identify each cluster's dimensions
unique_labels = set(labels)
cluster_dimensions = {}

for label in unique_labels:
    if label == -1:  # Ignore noise points (label == -1)
        continue
    cluster_points = points[labels == label]
    
    # Calculate dimensions: height (range in Z) and width (ranges in X and Y)
    height = cluster_points[:, 2].ptp()  # ptp() gives the range (max - min)
    width = max(cluster_points[:, 0].ptp(), cluster_points[:, 1].ptp())
    
    cluster_dimensions[label] = (height, width)

# Known dimensions of the tige (adjust according to your data)
known_tige_height = 1.0  # Replace with the actual height of the tige
known_tige_width = 0.1   # Replace with the actual width (fineness) of the tige
known_cube_width = 0.2   # Width of the cube at the top

# Function to compare cluster dimensions to the known tige dimensions
def is_tige(cluster_height, cluster_width, known_height, known_width, cube_width, tolerance=0.1):
    # Check if the width includes both the tige and the cube
    return (abs(cluster_height - known_height) <= tolerance * known_height and
            known_width <= cluster_width <= cube_width)

# Find the cluster that matches the tige's dimensions (including the cube)
tige_label = None
for label, (height, width) in cluster_dimensions.items():
    if is_tige(height, width, known_tige_height, known_tige_width, known_cube_width):
        tige_label = label
        break

# Check if a tige cluster was found
if tige_label is None:
    raise ValueError("No cluster matching the tige's dimensions was found.")

# Filter points and colors for the tige (including the cube)
mask = labels == tige_label
filtered_points = points[mask]
filtered_colors = np.asarray(pcd.colors)[mask]

# Calculate the vector of the tige (from the bottom to the top)
base = filtered_points[np.argmin(filtered_points[:, 2])]  # Point with lowest Z coordinate
top = filtered_points[np.argmax(filtered_points[:, 2])]   # Point with highest Z coordinate
direction = top - base
direction /= np.linalg.norm(direction)  # Normalize the vector

# Calculate the rotation matrix to align the tige vertically (along the Z-axis)
target = np.array([0, 0, 1])
axis = np.cross(direction, target)
angle = np.arccos(np.dot(direction, target))

if np.linalg.norm(axis) > 1e-6:  # If axis is not zero
    axis /= np.linalg.norm(axis)
    rotation_matrix = Matrix.Rotation(angle, 4, axis)
else:
    rotation_matrix = Matrix.Identity(4)  # If the tige is already aligned

# Apply the rotation to the entire point cloud
rotated_points = np.array([rotation_matrix @ bpy.context.object.matrix_world @ v.co for v in bpy.context.object.data.vertices])

# Update point cloud with rotated points
pcd.points = o3d.utility.Vector3dVector(rotated_points)

# Convert the rotated and filtered point cloud back to Blender mesh
open3d_to_blender_mesh(pcd)
