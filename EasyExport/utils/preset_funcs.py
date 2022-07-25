from genericpath import exists
import bpy
import os

"""Have to store a reference for python so blender UI enum wont freak out"""
items = []
count = -1
file = ""
ext = ".py"
user_path = bpy.utils.resource_path('USER')
path = os.path.join(user_path, "scripts/presets/operator/export_scene.fbx/")

"""Update function for populating presets in enumerator"""

def get_export_presets(self, context):
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
