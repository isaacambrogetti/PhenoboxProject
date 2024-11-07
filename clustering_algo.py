import open3d as o3d
import numpy as np
from sklearn.cluster import DBSCAN
import argparse
import time
import sys

# Loading animation function
def loading_animation(message="Loading", duration=2):
    animation = ["[■□□□□□□□□□]", "[■■□□□□□□□□]", "[■■■□□□□□□□]", "[■■■■□□□□□□]", "[■■■■■□□□□□]", "[■■■■■■□□□□]", 
                 "[■■■■■■■□□□]", "[■■■■■■■■□□]", "[■■■■■■■■■□]", "[■■■■■■■■■■]"]
    sys.stdout.write(f"\r{message}: {animation[0]}")
    for i in range(len(animation)):
        time.sleep(duration / len(animation))
        sys.stdout.write(f"\r{message}: {animation[i % len(animation)]}")
        sys.stdout.flush()
    print("\n")

def main(input_file, output_file, eps=0.5, min_samples=20):
    loading_animation("Loading point cloud")

    # Load the .ply file
    pcd = o3d.io.read_point_cloud(input_file)
    
    # Extract points and colors
    points = np.asarray(pcd.points)
    colors = np.asarray(pcd.colors)
    
    # Calculate center of mass (origin of the point cloud)
    loading_animation("Calculating center of mass")
    center_of_mass = np.mean(points, axis=0)
    
    # Apply DBSCAN clustering
    loading_animation("Applying DBSCAN clustering")
    dbscan = DBSCAN(eps=eps, min_samples=min_samples).fit(points)
    labels = dbscan.labels_
    
    # Get unique labels of clusters
    unique_labels = np.unique(labels)
    print("Cluster labels:", unique_labels)
    
    clusters = {}
    for label in unique_labels:
        # Count number of points in each cluster
        cluster_points = points[labels == label]
        count = len(cluster_points)
        
        # Compute distance of each point to the center of mass
        distances = np.linalg.norm(cluster_points - center_of_mass, axis=1)
        
        # Find minimal distance between points and center of mass
        min_distance = np.min(distances)
        
        # Store count and minimal distance for each cluster
        clusters[label] = {'count': count, 'min_distance': min_distance}
    
    # Sort clusters by size and keep the three biggest clusters
    loading_animation("Sorting clusters")
    sorted_by_size = dict(sorted(clusters.items(), key=lambda item: item[1]['count'], reverse=True))
    largest_clusters = dict(list(sorted_by_size.items())[:3])
    
    # Sort the biggest clusters by distance to the center of mass
    sorted_by_distance = dict(sorted(largest_clusters.items(), key=lambda item: item[1]['min_distance']))
    
    # Select clusters closest to the center of mass
    closest_clusters = list(sorted_by_distance.keys())[:2]
    print("Nearest clusters:", closest_clusters)
    
    # Mask to keep points in the selected clusters
    mask = np.isin(labels, closest_clusters)
    filtered_points = points[mask]
    filtered_colors = colors[mask]
    
    # # Apply brown filter to remove brownish points from the filtered clusters
    # loading_animation("Applying color filter")
    # brown_filter = (filtered_colors[:, 0] > 0.4) & (filtered_colors[:, 1] > 0.2) & (filtered_colors[:, 1] < 0.6) & (filtered_colors[:, 2] < 0.3)
    
    # # Keep only points that are not brownish
    # filtered_points = filtered_points[~brown_filter]
    # filtered_colors = filtered_colors[~brown_filter]
    
    # Create a new point cloud with the filtered points and colors
    loading_animation("Saving filtered point cloud")
    filtered_pcd = o3d.geometry.PointCloud()
    filtered_pcd.points = o3d.utility.Vector3dVector(filtered_points)
    filtered_pcd.colors = o3d.utility.Vector3dVector(filtered_colors)
    
    # Save the filtered point cloud to a file
    o3d.io.write_point_cloud(output_file, filtered_pcd)
    print(f"Filtered point cloud saved to: {output_file}")
    
    # Visualize the filtered point cloud
    o3d.visualization.draw_geometries([filtered_pcd], point_show_normal=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Filter and cluster point clouds with DBSCAN and color filtering.")
    parser.add_argument("input_file", type=str, help="Path to the input .ply file.")
    parser.add_argument("output_file", type=str, help="Path to save the filtered .ply file.")
    parser.add_argument("--eps", type=float, default=0.5, help="DBSCAN eps parameter (default: 0.5)")
    parser.add_argument("--min_samples", type=int, default=20, help="DBSCAN min_samples parameter (default: 20)")
    
    args = parser.parse_args()
    
    main(args.input_file, args.output_file, args.eps, args.min_samples)