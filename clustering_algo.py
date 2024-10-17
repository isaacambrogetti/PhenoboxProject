import pyvista as pv
import numpy as np
from sklearn.cluster import DBSCAN
import matplotlib.pyplot as plt

# load the .ply file
ply_file = r'test_plant.ply'
pcd_pv = pv.read(ply_file)
points = np.array(pcd_pv.points)

# calculate center of mass, origin of the point cloud
center_of_mass = np.mean(points, axis=0) 

# Apply DBSCAN, density based algorithm
dbscan = DBSCAN(eps=0.75, min_samples=20).fit(points) # eps = maximal distance between two points to be considered in the same neighborhood, min_samples = min nb of points to form a cluster
labels = dbscan.labels_

# get unique labels of clusters
unique_labels = np.unique(labels)

# display unique values
print("Cluster labels:", unique_labels)


clusters={}
for label in unique_labels:
    # count number of points in each cluster
    cluster_points = points[labels == label]
    count = len(cluster_points)
    
    # Compute distance of each point to the center of mass
    distances = np.linalg.norm(abs(cluster_points - center_of_mass), axis=1)

    # find minimal distance between points and center of mass
    min_distance = np.min(distances)

    # for each cluster, store number of points and minimal distance in a dictionary
    clusters[label] = {'count': count, 'min_distance': min_distance}

# sort clusters by size and keep the three biggest clusters (we assume plant and cube are part of these 3 and were grouped as one cluster for each element)
sorted_by_size = dict(sorted(clusters.items(), key=lambda item: item[1]['count'], reverse=True))
largest_clusters = dict(list(sorted_by_size.items())[:3]) # 3 biggest clusters

# sort biggest clusters by distance to the center of mass
sorted_by_distance = dict(sorted(largest_clusters.items(), key=lambda item: item[1]['min_distance']))

# Select clusters closer to the center of mass
closest_clusters = list(sorted_by_distance.keys())[:2]
print("Nearest clusters:", closest_clusters)


# Add labels to point cloud, visualize the clusters
pcd_pv['labels'] = labels
pcd_pv.plot(scalars='labels', render_points_as_spheres=True, point_size=5)



# keep points that are found in filtered clusters (cube + plant)
mask = np.isin(labels, closest_clusters)
filtered_points = points[mask]


# Save the data
filtered_pcd = pv.PolyData(filtered_points)
#filtered_pcd.save('filtered_plants2.ply')

# Plot the results
filtered_pcd.plot(eye_dome_lighting=True)