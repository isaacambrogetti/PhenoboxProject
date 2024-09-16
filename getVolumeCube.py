import bpy

# 1
# importing the file


# 2
# enter edit mode
bpy.ops.object.editmode_toggle()

# select all
bpy.ops.mesh.select_all(action='SELECT')

# separate by loose parts
bpy.ops.mesh.separate(type='LOOSE')



# 3
# Object mode
bpy.ops.object.editmode_toggle()