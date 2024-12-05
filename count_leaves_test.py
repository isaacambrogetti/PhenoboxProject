import open3d as o3d
import numpy as np
from skimage.morphology import skeletonize
from skimage import img_as_bool

# Function to convert a point cloud to voxel grid and then to binary image
def point_cloud_to_binary_image(pcd, voxel_size=2.1):
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
def skeletonize_point_cloud(pcd, voxel_size=2.1):
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


def count_leaf_tips(point_cloud, radius=2):
    """
    Count points with exactly one neighbor in the point cloud.
    
    Args:
        point_cloud (o3d.geometry.PointCloud): The input point cloud.
        radius (float): The radius to consider for neighborhood search.
        
    Returns:
        tuple: A list of tip points and the count of leaf tips.
    """
    # Create a KDTree for the point cloud
    pcd_tree = o3d.geometry.KDTreeFlann(point_cloud)
    
    # Extract points
    points = np.asarray(point_cloud.points)
    
    # List to store tip points
    tip_points = []
    
    # Iterate through each point
    for i, point in enumerate(points):
        # Find neighbors within the radius
        [_, idx, _] = pcd_tree.search_radius_vector_3d(point, radius)
        
        # If exactly one neighbor exists, it's a tip
        if len(idx) == 2:  # Include the point itself and one neighbor
            tip_points.append(point)
        
    # Check if tip_points is empty
    if not tip_points:
        print("No tip points found. Check your radius or point cloud density.")
    
    # Convert tip points to a point cloud for visualization
    tip_pcd = o3d.geometry.PointCloud()
    tip_pcd.points = o3d.utility.Vector3dVector(np.array(tip_points))
    
    return tip_pcd, len(tip_points)



# Load your point cloud
pcd = o3d.io.read_point_cloud("scans/Merge_01_pc_Plant_Filtered.ply")  # Replace with your path

# Skeletonize the point cloud
skeleton, min_bound, voxel_size = skeletonize_point_cloud(pcd)

# Convert the skeleton back to a point cloud for visualization
skeleton_pcd = skeleton_to_point_cloud(skeleton, min_bound, voxel_size)

# Visualize the original point cloud and skeleton
o3d.visualization.draw_geometries([skeleton_pcd])


# Count leaf tips
radius = 3.9  # Adjust based on point cloud scale and resolution
tip_pcd, tip_count = count_leaf_tips(skeleton_pcd, radius)

# Print results
print(f"Number of leaf tips: {tip_count}")

# Visualize the tip points
o3d.visualization.draw_geometries([pcd, tip_pcd.paint_uniform_color([1, 0, 0])])
