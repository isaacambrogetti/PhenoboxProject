import open3d as o3d
import numpy as np

# Charger les deux nuages de points (remplace par tes fichiers)
print("Loading files...\n")
source = o3d.io.read_point_cloud("scans/A2L-D6-8-C-0_pc.ply")
target = o3d.io.read_point_cloud("scans/A2L-D6-8-C-8_pc.ply")
print("Done.\n")

# Downsampling pour réduire le nombre de points (facultatif)
print("Downsampling to reduce number of points...\n")
source_down = source.voxel_down_sample(voxel_size=0.02)
target_down = target.voxel_down_sample(voxel_size=0.02)
print("Done.\n")

# Estimation de normales (facultatif, mais utile pour un meilleur alignement)
print("Estimating Normals...\n")
source_down.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))
target_down.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))
print("Done.\n")

# Calcul des features FPFH pour les correspondances
print("computing Features...\n")
source_fpfh = o3d.pipelines.registration.compute_fpfh_feature(
    source_down, o3d.geometry.KDTreeSearchParamHybrid(radius=0.25, max_nn=100))
target_fpfh = o3d.pipelines.registration.compute_fpfh_feature(
    target_down, o3d.geometry.KDTreeSearchParamHybrid(radius=0.25, max_nn=100))
print("Done.\n")

# Alignement initial par RANSAC
print("RANSAC...\n")
distance_threshold = 0.05  # Distance maximale pour considérer une correspondance
result_ransac = o3d.pipelines.registration.registration_ransac_based_on_feature_matching(
    source_down, target_down, source_fpfh, target_fpfh, True,
    distance_threshold,
    o3d.pipelines.registration.TransformationEstimationPointToPoint(),
    ransac_n=4,
    checkers=[
        o3d.pipelines.registration.CorrespondenceCheckerBasedOnEdgeLength(0.9),
        o3d.pipelines.registration.CorrespondenceCheckerBasedOnDistance(distance_threshold)
    ],
    criteria=o3d.pipelines.registration.RANSACConvergenceCriteria(4000000, 500)
)
print("Done.\n")

# Affiner l'alignement avec ICP
print("Adjusting alignment...\n")
result_icp = o3d.pipelines.registration.registration_icp(
    source, target, 0.02, result_ransac.transformation,
    o3d.pipelines.registration.TransformationEstimationPointToPoint()
)
print("Done.\n")

# Appliquer la transformation sur le nuage de points source
print("Applying result on source...\n")
source.transform(result_icp.transformation)
print("Done.\n")

# Fusionner les nuages de points alignés
print("Merging pointclouds...\n")
merged_pcd = source + target
print("Done.\n")

# Afficher le résultat
o3d.visualization.draw_geometries([merged_pcd], window_name="Nuage de points fusionné")
