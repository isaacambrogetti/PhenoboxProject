import open3d as o3d
import numpy as np

# Load the point cloud
pcd = o3d.io.read_point_cloud('scans/Merge_01_pc.ply')

# Check if color information is available
if pcd.has_colors():
    colors = np.asarray(pcd.colors)  # Extract colors as a NumPy array
    print("Colors extracted from point cloud:", colors)
else:
    print("No color data found in this point cloud.")

