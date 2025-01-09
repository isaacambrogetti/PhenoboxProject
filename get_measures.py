bl_info = {
    "name" : "Obtain Plant Volume",
    "author" : "Isaac Ambrogetti",
    "version" : (1, 0),
    "blender" : (4, 1, 1),
    "location" : "View3d > Tool",
    "warning" : "",
    "wiki:url" : "",
    "category" : "Add Mesh",
}

import bpy
import numpy as np
from scipy.spatial import ConvexHull
# To get the volume
import math

from bpy.types import Operator
from bpy.props import (
    IntProperty,
    FloatProperty,
)
import bmesh
from bpy.app.translations import pgettext_tip as tip_
from object_print3d_utils import report
from mathutils import Vector


def clean_float(value: float, precision: int = 0) -> str:
    """
    Convert a floating-point number to a string with a specified precision,
    avoiding scientific notation and stripping trailing zeros.

    Args:
        value (float): The floating-point number to be converted.
        precision (int, optional): The number of decimal places to include. Defaults to 0.

    Returns:
        str: The formatted floating-point number as a string.
    """

    text = f"{value:.{precision}f}"
    index = text.rfind(".")

    if index != -1:
        index += 2
        head, tail = text[:index], text[index:]
        tail = tail.rstrip("0")
        text = head + tail

    return text


def get_unit(unit_system: str, unit: str) -> tuple[float, str]:
    """
    Returns the unit length relative to a meter and the unit symbol.

    Args:
        unit_system (str): The system of units to use. Should be either "METRIC" or "IMPERIAL".
        unit (str): The specific unit to retrieve. For "METRIC", valid units are "KILOMETERS", "METERS", 
                    "CENTIMETERS", "MILLIMETERS", and "MICROMETERS". For "IMPERIAL", valid units are 
                    "MILES", "FEET", "INCHES", and "THOU".

    Returns:
        tuple[float, str]: A tuple containing the unit length relative to a meter and the unit symbol.

    Raises:
        KeyError: If the unit_system or unit is not found in the predefined units dictionary.

    Notes:
        If the specified unit is not found, the function will return "CENTIMETERS" for the "METRIC" system 
        and "INCHES" for the "IMPERIAL" system as fallback units.
    """
    # Returns unit length relative to meter and unit symbol

    units = {
        "METRIC": {
            "KILOMETERS": (1000.0, "km"),
            "METERS": (1.0, "m"),
            "CENTIMETERS": (0.01, "cm"),
            "MILLIMETERS": (0.001, "mm"),
            "MICROMETERS": (0.000001, "µm"),
        },
        "IMPERIAL": {
            "MILES": (1609.344, "mi"),
            "FEET": (0.3048, "\'"),
            "INCHES": (0.0254, "\""),
            "THOU": (0.0000254, "thou"),
        },
    }

    try:
        return units[unit_system][unit]
    except KeyError:
        fallback_unit = "CENTIMETERS" if unit_system == "METRIC" else "INCHES"
        return units[unit_system][fallback_unit]


# ------


class OBJECT_separate(bpy.types.Operator):
    bl_idname = "object.separate"
    bl_label = "Separate by loose part"
    bl_description = "Separate the mesh in cube and plant"
    bl_options = {'REGISTER', 'UNDO'} # Enable undo for the operator
    
    def execute(self, context):
        ### 2
        ## after importing the file, enter edit mode
        bpy.ops.object.editmode_toggle()
        
        # select all
        bpy.ops.mesh.select_all(action='SELECT')
        
        # select by loose part
        bpy.ops.mesh.separate(type='LOOSE')
        
        # Object mode
        bpy.ops.object.editmode_toggle()
        
        return {'FINISHED'}
        
        
class OBJECT_check_quantity(bpy.types.Operator):
    bl_idname = "object.check_quantity"
    bl_label = "Check number of meshes"
    bl_description = "check if the mesh has been separated in just cube and plant"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        """
        Executes the main functionality of the operator.
        Args:
            context (bpy.types.Context): The context in which the operator is executed.
        Returns:
            dict: A dictionary indicating the result of the operation. 
                  Returns {'CANCELLED'} if the number of selected objects is not equal to 2.
        Notes:
            This function checks if the number of selected objects in the Blender context is exactly two.
            If not, it reports a warning and cancels the operation.
        """

        ### 3
        selected_obj = bpy.context.selected_objects
        
        # check if the objects are just two (plant and cube)
        if len(selected_obj) != 2:
            self.report({'WARNING'}, "The mesh is divided in more than just 2 pieces! Check the quality of the scan, delete the smaller chunks of mesh and go on.")
            return {'CANCELLED'}


class OBJECT_volumePlant(bpy.types.Operator):
    bl_idname = "object.plant_volume"
    bl_label = "Get plant volume"
    bl_description = "get volume of the cube, calculate the ratio, get the plant volume and multiplicate it by the ratio"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        """
        Executes the volume calculation and ratio determination for selected objects in Blender.
        Parameters:
        context (bpy.types.Context): The context in which the operator is called.
        Returns:
        dict: A dictionary indicating the result of the operation, either {'FINISHED'} or {'CANCELLED'}.
        The function performs the following steps:
        1. Checks if exactly one object (the cube) is selected.
        2. Calculates the volume of the selected cube.
        3. Computes the ratio of a theoretical volume to the calculated volume of the cube.
        4. Selects all objects and deselects the cube to isolate the plant object.
        5. Checks if exactly one object (the plant) is selected.
        6. Calculates the total volume of the plant object.
        7. Adjusts the plant volume based on the previously computed ratio.
        8. Updates the report with the calculated volumes and ratio.
        Raises:
        Warning: If more than one object is selected at any point or if the plant mesh is split into multiple meshes.
        """
        
        ### 4
        # check if one object is selected (the cube)
        selected_obj = bpy.context.selected_objects
        if len(selected_obj) != 1:
            self.report({'WARNING'}, "Select only the cube!")
            return {'CANCELLED'}
        
        # get the volume of the selected object
        obj = selected_obj[0]
        bpy.context.view_layer.objects.active = obj
        
        
        from object_print3d_utils import mesh_helpers

        scene = context.scene
        unit = scene.unit_settings
        scale = 1.0 if unit.system == 'NONE' else unit.scale_length
        obj = context.active_object

        bm = mesh_helpers.bmesh_copy_from_object(obj, apply_modifiers=True)
        volume = bm.calc_volume()
        bm.free()

        if unit.system == 'NONE':
            volume_fmt = clean_float(volume, 8)
        else:
            length, symbol = get_unit(unit.system, unit.length_unit)

            volume_unit = volume * (scale ** 3.0) / (length ** 3.0)
            volume_str = clean_float(volume_unit, 2)
            volumeCube_fmt = f"{volume_str} "

        # calculate the ratio realVol : theoVol
        ratio = 3.765/volume_unit
        ratio_str = clean_float(ratio, 2)
        
        # select the other object (the plant)
        bpy.ops.object.select_all(action='SELECT')
        obj.select_set(False)
        
        #####################################################

        # check if it's only one object
        selected_obj = bpy.context.selected_objects
        if len(selected_obj) != 1:
            self.report({'WARNING'}, "The plant mesh is splitted in more than one mesh! Please, check if they're all belonging to the plant.")
        
        tot_volume = 0.0

        for obj in selected_obj:
            # calculate the volume of the plant
            bpy.context.view_layer.objects.active = obj
            
            scene = context.scene
            obj = context.active_object

            bm = mesh_helpers.bmesh_copy_from_object(obj, apply_modifiers=True)
            volume = bm.calc_volume()
            bm.free()
            tot_volume += volume

        if unit.system == 'NONE':
            volume_fmt = clean_float(tot_volume, 8)
        else:
            length, symbol = get_unit(unit.system, unit.length_unit)

            volume_unit = tot_volume * (scale ** 3.0) / (length ** 3.0)
            volPlant_str = clean_float(tot_volume, 2)
            volPlant_fmt = f"{volPlant_str}"
            volumeReal_unit = volume_unit*ratio
            volume_str = clean_float(volumeReal_unit, 2)
            volumePlant_fmt = f"{volume_str} cm"
        
        
        
        report.update((tip_("Cube vol: {}³").format(volumeCube_fmt), None),
        (tip_("Ratio T/R: {}").format(ratio), None),
        (tip_("Plant calc: {}").format(volPlant_fmt), None),
        (tip_("Plant vol: {}³").format(volumePlant_fmt), None))
        
        return {'FINISHED'}
        
 
class OBJECT_measureLeaf(bpy.types.Operator):
    bl_label = "Measure Leaf"
    bl_idname = "object.measure_leaf"
    bl_description = "Get length, width and area of the selected leaf"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        """
        Executes the measurement process for the selected leaf object in Blender.
        This function performs the following steps:
        1. Ensures only one object is selected and it is of type 'MESH'.
        2. Extracts the vertices of the selected object.
        3. Computes the Convex Hull of the vertices.
        4. Finds the two farthest points on the Convex Hull to determine the leaf length.
        5. Projects the vertices onto a plane defined by the longest span to determine the leaf width.
        6. Computes the 2D Convex Hull of the projected points to determine the leaf area.
        7. Converts the measurements to real-world values using a scale factor.
        8. Reports the leaf length, width, and area.
        Args:
            context (bpy.types.Context): The context in which the operator is called.
        Returns:
            dict: A dictionary indicating the result of the operation, either {'FINISHED'} or {'CANCELLED'}.
        """

        # Ensure only one object is selected (the leaf of interest)
        selected_obj = bpy.context.selected_objects
        if len(selected_obj) != 1:
            self.report({'WARNING'}, "Select only the leaf of interest!")
            return {'CANCELLED'}
        
        obj = context.active_object
        
        if obj.type != 'MESH':
            self.report({'WARNING'}, "The selected object is not in MESH format.")
            return {'CANCELLED'}
        
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        vertices = [v.co for v in bm.verts]
        bm.free()

        # Convert vertices to NumPy array
        points = np.array([(v.x, v.y, v.z) for v in vertices])
        
        # Compute Convex Hull
        hull = ConvexHull(points)
        hull_points = points[hull.vertices]
        
        # Find the two farthest points on the Convex Hull
        max_dist = 0
        point_a = point_b = None
        for i, p1 in enumerate(hull_points):
            for p2 in hull_points[i + 1:]:
                dist = np.linalg.norm(p1 - p2)
                if dist > max_dist:
                    max_dist = dist
                    point_a, point_b = p1, p2
        
        # Draw the points and line for the longest span
        if point_a is not None and point_b is not None:
            # Convert back to Blender Vector for visualization
            point_a = Vector(point_a)
            point_b = Vector(point_b)
            
            #bpy.ops.object.mode_set(mode='OBJECT')  # Ensure we're in OBJECT mode
            self.create_visual_point(context, point_a, name="Point_A")
            self.create_visual_point(context, point_b, name="Point_B")
            
            self.create_visual_line(context, point_a, point_b, name="Leaf_Length_Line")
            
            # Project vertices onto the plane defined by the longest span
            length_dir = (point_b - point_a).normalized()
            perp_dir = Vector((-length_dir.y, length_dir.x, length_dir.z))  # Perpendicular direction in 3D
        
            projections = [Vector((v.dot(length_dir), v.dot(perp_dir), 0)) for v in vertices]
            proj_points = np.array([(p.x, p.y) for p in projections])

            # Find the bounding box of the projected points
            min_proj = min(projections, key=lambda p: p.dot(perp_dir))
            max_proj = max(projections, key=lambda p: p.dot(perp_dir))
        
            # Calculate the full width
            max_width = (max_proj - min_proj).length

            # Compute 2D Convex Hull for the projected points
            area_hull = ConvexHull(proj_points)
            leaf_area = area_hull.volume  # The volume of the 2D hull is the area
        
            # Draw the points and line for the width
#            self.create_visual_point(context, min_proj + point_a, name="Width_Point_1")
#            self.create_visual_point(context, max_proj + point_a, name="Width_Point_2")
#            self.create_visual_line(context, min_proj + point_a, max_proj + point_a, name="Leaf_Width_Line")
#            
            # set the scale factor, conversion to real value
            real_cube_length = 0.036 # Cube diagonal + stick (in m)
            blender_cube_length = 34 # blender measure (in m)
            
            scale_factor = real_cube_length / blender_cube_length
            
            real_max_distance = max_dist * scale_factor * 100 # * 100 to convert in centimeters
            real_max_width = max_width * scale_factor * 100
            real_leaf_area = leaf_area * (scale_factor ** 2) * 10000  # Convert to cm^2
            
            dist_str = clean_float(real_max_distance, 3)
            width_str = clean_float(real_max_width, 3)
            area_str = clean_float(real_leaf_area, 3)
            
    
        else:
            self.report({'WARNING'}, "Failed to calculate leaf dimensions.")
            return {'CANCELLED'}


        report.update(
        (tip_("Leaf length: {}cm").format(dist_str), None),
        (tip_("Leaf width: {}cm").format(width_str), None),
        (tip_("Leaf area: {}cm²").format(area_str), None)
        )

        bm.free()
        
        return {'FINISHED'}

    def create_visual_point(self, context, location, name="Visual_Point"):
        """
        Creates a visual point in the Blender context at the specified location.

        Args:
            context: The Blender context in which to create the visual point.
            location (tuple): A tuple of three floats representing the (x, y, z) coordinates where the visual point will be created.
            name (str, optional): The name to assign to the visual point. Defaults to "Visual_Point".

        Returns:
            None
        """
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.05, location=location)
        point = bpy.context.object
        point.name = name
        point.display_type = 'WIRE'
        point.show_in_front = True  # Rendre visible même derrière d'autres objets
    
    def create_visual_line(self, context, start, end, name="Visual_Line"):
        """
        Creates a visual line in the Blender context between two points.
        Args:
            context (bpy.types.Context): The Blender context in which to create the line.
            start (tuple): A tuple of three floats representing the starting coordinates of the line.
            end (tuple): A tuple of three floats representing the ending coordinates of the line.
            name (str, optional): The name of the new line object. Defaults to "Visual_Line".
        Returns:
            None
        """
        mesh = bpy.data.meshes.new(name)
        line_obj = bpy.data.objects.new(name, mesh)
        context.collection.objects.link(line_obj)
        
        bm = bmesh.new()
        v1 = bm.verts.new(start)
        v2 = bm.verts.new(end)
        bm.edges.new([v1, v2])
        bm.to_mesh(mesh)
        bm.free()
        line_obj.display_type = 'WIRE'
        line_obj.show_in_front = True


        # multiplicate the volume of the plant with the ratio obtained before
        
        # output the value obtained (real volume of the plant)
        

class OBJECT_PT_GetPlantMeasures_panel(bpy.types.Panel):
    bl_label = "Plant Volume Panel"
    bl_idname = "OBJECT_PT_align_and_snap_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'PlantMeasures'
    
    def draw_report(self, context):
        """
        Draws a report layout in the given context.
        Args:
            context (bpy.types.Context): The context in which the report is drawn.
        The function retrieves report information and displays it in a formatted layout.
        If the context is in edit mode and the report data is available, it adds an operator
        to the layout for each report item. Otherwise, it simply labels the report items.
        """

        layout = self.layout
        info = report.info()

        if info:
            is_edit = context.edit_object is not None

            layout.label(text="Result")
            box = layout.box()
            col = box.column()

            for i, (text, data) in enumerate(info):
                if is_edit and data and data[1]:
                    bm_type, _bm_array = data
                    col.operator("mesh.print3d_select_report", text=text, icon=self._type_to_icon[bm_type],).index = i
                else:
                    col.label(text=text)

    def draw(self, context):
        layout = self.layout
        layout.operator("object.separate")
        #layout.operator("object.check_quantity")
        layout.operator("object.plant_volume")
        layout.operator("object.measure_leaf")
        self.draw_report(context)
    

classes = [
    OBJECT_separate,
    OBJECT_check_quantity,
    OBJECT_volumePlant,
    OBJECT_measureLeaf,
    OBJECT_PT_GetPlantMeasures_panel
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()