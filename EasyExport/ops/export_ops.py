import bpy
import os
import webbrowser
from bpy_extras.io_utils import ExportHelper
from ..utils import export_funcs

class DarrowExportFBXNoPrompt(bpy.types.Operator):
    bl_idname = "export_selected_promptless.darrow"
    bl_label = 'Export Selection'
    bl_description = "Export selection as an FBX using the settings bellow"
    bl_options = {'PRESET'}
    filename_ext = ".fbx"

    def execute(self, context):
        objs = context.selected_objects

        if len(objs) != 0:
            path_no_prompt = context.scene.userDefinedExportPath
            bpy.context.scene.setupExportPath = path_no_prompt
            if export_funcs.DarrowCheckErrors(self, path_no_prompt) == False:
                export_funcs.DarrowSetUpExport(self, context, path_no_prompt)

        return {'FINISHED'}

class DarrowExportFBXWithPrompt(bpy.types.Operator, ExportHelper):
    bl_idname = "export_selected.darrow"
    bl_label = 'Export Selection'
    bl_description = "Export selection as FBX using setting bellow"
    bl_options = {'PRESET'}
    filename_ext = ".fbx"

    def execute(self, context):
        objs = context.selected_objects

        if len(objs) != 0:
            path_prompt = self.filepath.replace("untitled", "")
            bpy.context.scene.setupExportPath = path_prompt

            if export_funcs.DarrowCheckErrors(self, path_prompt) == False:
                export_funcs.DarrowSetUpExport(self, context, path_prompt)

        return {'FINISHED'}

class DarrowOpenExportFolder(bpy.types.Operator):
    """Open the Render Folder in a file Browser"""
    bl_idname = "file.export_folder"
    bl_description = "Open export folder"
    bl_label = "ExportFolder"

    def execute(self, context):
        path = bpy.context.scene.setupExportPath.replace(".fbx", "")

        if not os.path.exists(path):
            os.makedirs(path)

        bpy.ops.wm.path_open(filepath=path)

        return {'FINISHED'}

class DarrowOpenDocs(bpy.types.Operator):
    bl_idname = "open.docs"
    bl_description = "Open Docs"
    bl_label = "Open Docs"

    def execute(self, context):
        webbrowser.open('https://darrow.tools/EasyExport')
        self.report({'INFO'}, "Opened documentation")
        return {'FINISHED'}

class DarrowIterativeReset(bpy.types.Operator):
    bl_idname = "reset.counter"
    bl_description = "Resets FBX suffix counter"
    bl_label = "Reset Suffix Counter"

    def execute(self, context):
        context.scene.iterativeExportAmount = 0

        self.report({'INFO'}, "Set suffix count to 0")
        return {'FINISHED'}

class DarrowStoredVectorList:
  def __init__(self, name='VectorList', vector=[]):
    self.name = name
    self.vector = vector

class DarrowStoredBooleanList:
  def __init__(self, name='BooleanList', booleans=[]):
    self.name = name
    self.booleans = booleans

classes = (DarrowIterativeReset,DarrowOpenDocs,DarrowOpenExportFolder,DarrowExportFBXWithPrompt,DarrowExportFBXNoPrompt,)

def register():
    bpy.types.Scene.darrowVectors = DarrowStoredVectorList()
    bpy.types.Scene.darrowBooleans = DarrowStoredBooleanList()

    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
