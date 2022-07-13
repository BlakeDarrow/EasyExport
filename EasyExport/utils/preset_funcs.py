import bpy
import os

"""Have to store a reference for python so blender UI enum wont freak out"""
items = []
count = -1
file = ""
ext = ".py"
path = bpy.utils.preset_paths('operator/export_scene.fbx/')

"""Update function for populating presets in enumerator"""
def get_export_presets(self, context):
        count = 1
        items.clear()
        
        if not items.__contains__(("OP1", "Default", "Default FBX Export")):
            items.append(("OP1", "Default", "Default FBX Export"))
            items.append(None)
        
        for file in os.listdir(path[0]):
            if file[-len(ext):] == ext:
                name = file.replace(".py", "")
                if not items.__contains__(("OP" + str(count), name, "User Preset")):
                    items.append((name, name, "User Preset"))

        return items