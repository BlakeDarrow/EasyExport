import bpy
import os

"""Have to store a reference for python so blender UI enum wont freak out"""
items = []
count = -1
file = ""
ext = ".py"

class ExportPresetOperator(bpy.types.Operator):
    bl_idname = "export.preset_operator"
    bl_label = "Export Preset Operator"

    def update(self, context):
        bpy.context.scene.blenderExportPresets = 'OP1'

        return

    def get_export_presets(self, context):
        user_path = bpy.utils.resource_path('USER')
        blender_version = bpy.app.version
        if bpy.context.scene.exportType == 'FBX':
            path = os.path.join(user_path, "scripts/presets/operator/export_scene.fbx/")
        elif bpy.context.scene.exportType == 'OBJ':

            if int(blender_version[0]) >= 4:
                path = os.path.join(user_path, "scripts/presets/operator/wm.obj_export/")
            elif int(blender_version[0]) <= 4:
                path = os.path.join(user_path, "scripts/presets/operator/export_scene.obj/")
            else:
                path = os.path.join(user_path, "scripts/presets/operator/export_scene.obj/")

        count = 1
        items.clear()

        if not items.__contains__(("OP1", "Default", "Darrow Default Export")):
            items.append(("OP1", "Default", "Darrow Default Export"))
            items.append(None)

        if os.path.exists(path):
            for file in os.listdir(path):
                if file[-len(ext):] == ext:
                    name = file.replace(".py", "")
                    if not items.__contains__(("OP" + str(count), name, "User Preset")):
                        items.append((name, name, "User Preset"))
        else:
            os.makedirs(path)

        return items


def register():
    bpy.utils.register_class(ExportPresetOperator)

def unregister():
    bpy.utils.unregister_class(ExportPresetOperator)

if __name__ == "__main__":
    register()
