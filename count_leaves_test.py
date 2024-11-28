import open3d as o3d
import numpy as np
from skimage.morphology import skeletonize
from skimage import img_as_bool

# Function to convert a point cloud to voxel grid and then to binary image
def point_cloud_to_binary_image(pcd, voxel_size=0.01):
    # Voxel grid downsampling
    voxel_grid = pcd.voxel_down_sample(voxel_size)
    
    # Convert the point cloud to numpy array
    points = np.asarray(voxel_grid.points)
    
    # Create a 3D grid that bounds the point cloud
    min_bound = points.min(axis=0)
    max_bound = points.max(axis=0)
    shape = np.ceil((max_bound - min_bound) / voxel_size).astype(int)

    # Translate the points to fit within the grid
    translated_points = ((points - min_bound) / voxel_size).astype(int)
    
    # Initialize a 3D binary grid (False means empty, True means filled)
    binary_image = np.zeros(shape, dtype=bool)
    
    # Mark the points as occupied in the binary image
    for pt in translated_points:
        binary_image[tuple(pt)] = True
    
    return binary_image, min_bound, voxel_size

# Function to perform skeletonization
def skeletonize_point_cloud(pcd, voxel_size=0.2):
    # Convert the point cloud to a binary 3D image
    binary_image, min_bound, voxel_size = point_cloud_to_binary_image(pcd, voxel_size)
    
    # Perform skeletonization on the binary image (skimage's skeletonize function)
    skeleton = skeletonize(binary_image)
    
    return skeleton, min_bound, voxel_size

# Function to convert skeleton back to point cloud (visualization)
def skeleton_to_point_cloud(skeleton, min_bound, voxel_size):
    # Get the indices of the skeleton points
    skeleton_points = np.argwhere(skeleton)
    
    # Scale back to the original point cloud scale
    scaled_points = skeleton_points * voxel_size + min_bound
    
    # Create Open3D point cloud from the skeleton points
    skeleton_pcd = o3d.geometry.PointCloud()
    skeleton_pcd.points = o3d.utility.Vector3dVector(scaled_points)
    
    return skeleton_pcd

# Load your point cloud
pcd = o3d.io.read_point_cloud("scans/V2L-D5-12-C-0_pc_filtered_pc.ply")  # Replace with your path

# Skeletonize the point cloud
skeleton, min_bound, voxel_size = skeletonize_point_cloud(pcd)

# Convert the skeleton back to a point cloud for visualization
skeleton_pcd = skeleton_to_point_cloud(skeleton, min_bound, voxel_size)

# Visualize the original point cloud and skeleton
o3d.visualization.draw_geometries([pcd, skeleton_pcd])
