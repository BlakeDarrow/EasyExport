import bpy
import os
import webbrowser
from bpy_extras.io_utils import ExportHelper
from ..utils import export_funcs
import time

class DARROW_OT_exportFBX(bpy.types.Operator):
    bl_idname = "darrow.export_prompt"
    bl_label = "FBX Base Name:"
    bl_description = "Export selection as an FBX using the settings and presets below."
    bl_options = {'REGISTER', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        """either export directly to the user defined path or prompt the user for the output.
        We have these functions separate so we can utilize the export helper for the destination popup"""

        if bpy.context.scene.exportObjectsWithoutPromptBool == True:
            bpy.ops.export_selected_promptless.darrow('INVOKE_DEFAULT')
        
        else:
            bpy.ops.export_selected.darrow('INVOKE_DEFAULT')

        self.report({'INFO'}, "Attempted Export")
        return {'FINISHED'}
    
    def invoke(self, context, event):
        start_time = time.perf_counter()
        bpy.context.scene.start_time = start_time
        print(bpy.context.scene.start_time)
        if bpy.context.scene.namingOptions == 'OP3'and bpy.context.scene.batchExport == False:
            return context.window_manager.invoke_props_dialog(self)
        else:
            return self.execute(context)

    def draw(self, context):
        row = self.layout
        row.prop(context.scene, "userDefinedBaseName", text="")
    
class DarrowExportFBXDirect(bpy.types.Operator):
    bl_idname = "export_selected_promptless.darrow"
    bl_label = 'Export Selection'
    bl_description = "Export selection as an FBX using the settings bellow"
    bl_options = {'PRESET'}
    filename_ext = ".fbx"

    def execute(self, context):
        objs = context.selected_objects

        if len(objs) != 0:
            path_no_prompt = context.scene.userDefinedExportPath

            if path_no_prompt == "" and bpy.data.filepath:
                filepath = bpy.data.filepath
                path_no_prompt = os.path.dirname(filepath) + "\\"
                context.scene.userDefinedExportPath = path_no_prompt

            if not path_no_prompt.endswith("\\") and path_no_prompt != "":
                path_no_prompt += "\\"
                context.scene.userDefinedExportPath = path_no_prompt
            elif path_no_prompt != "":
                context.scene.userDefinedExportPath = ""

            bpy.context.scene.setupExportPath = path_no_prompt
            if export_funcs.DarrowCheckErrors(self, path_no_prompt):
                return {'CANCELLED'}
            else:
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

            if export_funcs.DarrowCheckErrors(self, path_prompt):
                return {'CANCELLED'}
            else:
                export_funcs.DarrowSetUpExport(self, context, path_prompt)
                return {'FINISHED'}

class DarrowOpenExportFolder(bpy.types.Operator):
    """Open the Render Folder in a file Browser"""
    bl_idname = "file.export_folder"
    bl_description = "Open last export destination"
    bl_label = "ExportFolder"

    def execute(self, context):
        path = bpy.context.scene.setupExportPath.replace(".fbx", "")
        if path == "":
            path = bpy.context.scene.userDefinedExportPath
        if not os.path.exists(path):
            os.makedirs(path)
    
        bpy.ops.wm.path_open(filepath=path)

        return {'FINISHED'}

class DarrowOpenPresetFolder(bpy.types.Operator):
    bl_idname = "open.presets"
    bl_description = "Open Blender Preset Folder"
    bl_label = "User Presets"

    def execute(self, context):
        blender_version = bpy.app.version
        if bpy.context.scene.exportType == 'OP1':
            path = bpy.utils.preset_paths('operator/export_scene.fbx/')
        elif bpy.context.scene.exportType == 'OP2':
            if int(blender_version[0]) >= 4:
                path = bpy.utils.preset_paths('operator/wm.obj_export/')
            elif int(blender_version[0]) <= 4:
                path = bpy.utils.preset_paths('operator/export_scene.obj/')
            else:
                path = bpy.utils.preset_paths('operator/export_scene.obj/')

        if not os.path.exists(path[0]):
            os.makedirs(path[0])
        bpy.ops.wm.path_open(filepath=path[0])
        return {'FINISHED'}

class DarrowEditDefaultPreset(bpy.types.Operator):
    bl_idname = "edit.default"
    bl_description = "Edit default export preset in windows default text editor."
    bl_label = "User Presets"

    def execute(self, context):
        blender_version = bpy.app.version
        default_path = bpy.utils.user_resource('SCRIPTS')
        if bpy.context.scene.exportType == 'OP1':
            path = default_path + "/addons/EasyExport/utils/default.py"
        elif bpy.context.scene.exportType == 'OP2':
            if int(blender_version[0]) >= 4:
                path = default_path + "/addons/EasyExport/utils/default_obj_4.0.py"
            elif int(blender_version[0]) <= 4:
                path = default_path + "/addons/EasyExport/utils/default_obj.py"
            else:
                path = default_path + "/addons/EasyExport/utils/default_obj.py"

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

classes = (DarrowExportFBXWithPrompt,DarrowExportFBXDirect, DARROW_OT_exportFBX,DarrowIterativeReset,DarrowOpenDocs,DarrowOpenExportFolder,DarrowOpenPresetFolder,DarrowEditDefaultPreset)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)