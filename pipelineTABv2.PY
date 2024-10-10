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



def clean_float(value: float, precision: int = 0) -> str:
    # Avoid scientific notation and strip trailing zeros: 0.000 -> 0.0

    text = f"{value:.{precision}f}"
    index = text.rfind(".")

    if index != -1:
        index += 2
        head, tail = text[:index], text[index:]
        tail = tail.rstrip("0")
        text = head + tail

    return text


def get_unit(unit_system: str, unit: str) -> tuple[float, str]:
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
    bl_options = {'REGISTER', 'UNDO'} ## ?????
    
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
    bl_options = {'REGISTER', 'UNDO'} ## ?????
    
    def execute(self, context):
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
    bl_options = {'REGISTER', 'UNDO'} ## ?????
    
    def execute(self, context):
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
        
        
        
        
        # multiplicate the volume of the plant with the ratio obtained before
        
        # output the value obtained (real volume of the plant)
        

class OBJECT_PT_GetPlantVolume_panel(bpy.types.Panel):
    bl_label = "Plant Volume Panel"
    bl_idname = "OBJECT_PT_align_and_snap_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'PlantVolume'
    
    def draw_report(self, context):
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
        self.draw_report(context)


def register():
    bpy.utils.register_class(OBJECT_separate)
    bpy.utils.register_class(OBJECT_check_quantity)
    bpy.utils.register_class(OBJECT_volumePlant)
    bpy.utils.register_class(OBJECT_PT_GetPlantVolume_panel)


def unregister():
    bpy.utils.unregister_class(OBJECT_separate)
    bpy.utils.unregister_class(OBJECT_check_quantity)
    bpy.utils.unregister_class(OBJECT_volumePlant)
    bpy.utils.unregister_class(OBJECT_PT_GetPlantVolume_panel)


register()