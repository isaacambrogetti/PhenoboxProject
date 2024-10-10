
import numpy as np
import pyvista as pv
from sklearn.cluster import DBSCAN


# Charger le fichier PLY
pcd_pv = pv.read('0905_pl3_pot_pc.ply')
points = np.array(pcd_pv.points)


# Appliquer DBSCAN
dbscan = DBSCAN(eps=0.03, min_samples=3).fit(points)  # Ajuste 'eps' selon tes données
labels = dbscan.labels_


# Visualiser les clusters
pcd_pv['labels'] = labels
pcd_pv.plot(scalars='labels')


# Suppression du pot en filtrant le cluster qui lui correspond
pot_cluster = 0  # Définir le cluster correspondant au pot
mask = labels != pot_cluster
filtered_points = points[mask]


# Sauvegarder les points filtrés
filtered_pcd = pv.PolyData(filtered_points)
filtered_pcd.save('filtered_plants.ply')
