from sklearn.cluster import DBSCAN
import numpy as np
import open3d as o3d
import pyvista as pv

# Charger le fichier PLY
ply_file = r'filtered_plants.ply'
pcd_pv = pv.read(ply_file)
points = np.array(pcd_pv.points)

# Appliquer DBSCAN avec les param'e8tres ajust'e9s
dbscan = DBSCAN(eps=0.75, min_samples=20).fit(points)
labels = dbscan.labels_

# Récupérer les valeurs uniques des clusters
unique_labels = np.unique(labels)

# Afficher les différentes valeurs
print("Valeurs des clusters (étiquettes):", unique_labels)

# Compter combien de points appartiennent à chaque cluster
clusters={}
for label in unique_labels:
    count = np.sum(labels == label)
    clusters[label] = count

clusters_sorted=dict(sorted(clusters.items(), key=lambda item: item[1], reverse=True))
clusters_of_interest = list(clusters_sorted.keys())[:2] 


# Ajouter les labels au nuage de points et visualiser les clusters
pcd_pv['labels'] = labels
pcd_pv.plot(scalars='labels', render_points_as_spheres=True, point_size=5)

# Save or process each object separately
#o3d.io.write_point_cloud(f"object_{label}.ply", object_pc)
