import open3d as o3d
import numpy as np

pcd1 = o3d.io.read_point_cloud(r'scans/A2L-D6-8-C-8_pc.ply')
pcd2 = o3d.io.read_point_cloud(r'scans/A2L-D6-8-C-0_pc.ply')

# Correspondance par RANSAC pour l'alignement initial
source_down = pcd1.voxel_down_sample(voxel_size=0.05)
target_down = pcd2.voxel_down_sample(voxel_size=0.05)
source_fpfh = o3d.pipelines.registration.compute_fpfh_feature(
    source_down, o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=100))
target_fpfh = o3d.pipelines.registration.compute_fpfh_feature(
    target_down, o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=100))

# Correspondence Checkers: for correspondence rejection based on distance or edge length
checkers = [
    o3d.pipelines.registration.CorrespondenceCheckerBasedOnEdgeLength(0.9),
    o3d.pipelines.registration.CorrespondenceCheckerBasedOnDistance(0.075)  # Ajuster selon la taille du modèle
]

# Critères de convergence RANSAC
criteria = o3d.pipelines.registration.RANSACConvergenceCriteria(max_iteration=4000000, confidence=0.999)

# Exécuter RANSAC avec les bons arguments
result_ransac = o3d.pipelines.registration.registration_ransac_based_on_feature_matching(
    source_down, target_down, source_fpfh, target_fpfh, True,
    max_correspondence_distance=0.075,  # Distance maximale entre deux correspondances de points
    estimation_method=o3d.pipelines.registration.TransformationEstimationPointToPoint(False),
    ransac_n=4,  # Nombre de correspondances utilisées pour chaque itération RANSAC
    checkers=checkers,
    criteria=criteria
)


# Étape 2: Affiner l'alignement avec ICP (Iterative Closest Point)
threshold = 0.02  # Distance maximale pour correspondre les points (ajuster selon les données)
reg_p2p = o3d.pipelines.registration.registration_icp(pcd2, pcd1, threshold, trans_init,
                                                      o3d.pipelines.registration.TransformationEstimationPointToPoint())

# Appliquer la transformation obtenue par ICP au second nuage de points
pcd2.transform(reg_p2p.transformation)

# Étape 3: Fusionner les deux nuages de points en un seul
pcd_combined = pcd1 + pcd2  # Fusionner les nuages

# Optionnel: Réduire le bruit en filtrant les points ou en réduisant la résolution
pcd_combined = pcd_combined.voxel_down_sample(voxel_size=0.005)  # Ajuster le voxel size selon tes données

# Enregistrer le nuage fusionné
# o3d.io.write_point_cloud("merged_cloud.ply", pcd_combined)

# Visualiser le nuage de points fusionné
o3d.visualization.draw_geometries([pcd_combined], window_name="Nuage de points fusionné")
