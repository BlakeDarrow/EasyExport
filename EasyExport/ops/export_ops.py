import bpy

from bpy_extras.io_utils import ExportHelper
from ..utils import export_funcs

class DARROW_OT_exportFBX(bpy.types.Operator):
    bl_idname = "darrow.export_prompt"
    bl_label = "FBX Base Name:"
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

        # report results to blender viewport
        if bpy.context.view_layer.objects.active != None and bpy.context.scene.batchExport == False:
            self.report({'INFO'}, "Exported object as '" + bpy.context.scene.exportedObjectName + "'")

        elif bpy.context.scene.batchExport == True:
            self.report({'INFO'}, "Exported multiple objects")

        return {'FINISHED'}

    def invoke(self, context, event):
        if bpy.context.scene.promptForBaseNameBool == True and bpy.context.scene.batchExport == False:
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

classes = (DarrowExportFBXWithPrompt,DarrowExportFBXDirect, DARROW_OT_exportFBX,)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
