import bpy
op = bpy.context.active_operator

op.filepath=''
op.use_selection=True
op.global_scale=1.0
op.use_scene_unit=False
op.ascii=False
op.use_mesh_modifiers=True
op.batch_mode='OFF'
op.axis_forward='Y'
op.axis_up='Z'