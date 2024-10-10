import pyvista as pv
import numpy as np
from sklearn.cluster import DBSCAN
import matplotlib.pyplot as plt

# Charger le fichier PLY
ply_file = 'test_pc_cluster.ply'
pcd_pv = pv.read(ply_file)
points = np.array(pcd_pv.points)

# Appliquer DBSCAN avec les param'e8tres ajust'e9s
dbscan = DBSCAN(eps=0.75, min_samples=20).fit(points)
labels = dbscan.labels_

# Récupérer les valeurs uniques des clusters
unique_labels = np.unique(labels)

# Afficher les différentes valeurs
print("Valeurs des clusters (éiquettes):", unique_labels)

# Compter combien de points appartiennent à chaque cluster
clusters={}
for label in unique_labels:
    count = np.sum(labels == label)
    clusters[label] = count

clusters_sorted=dict(sorted(clusters.items(), key=lambda item: item[1], reverse=True))
biggest_clusters = list(clusters_sorted.keys())[:2]


# Ajouter les labels au nuage de points et visualiser les clusters
pcd_pv['labels'] = labels
pcd_pv.plot(scalars='labels', render_points_as_spheres=True, point_size=5)


# Suppression du pot en filtrant le cluster qui lui correspond
plant_clusters = biggest_clusters  # Définir le cluster correspondant à la plante
mask = labels in plant_clusters
filtered_points = points[mask]


# Sauvegarder les points filtrés
filtered_pcd = pv.PolyData(filtered_points)
filtered_pcd.save('filtered_plants.ply')


# essayer d'ordonner les clusters par taille et de filtrer et garder les deux plus grands