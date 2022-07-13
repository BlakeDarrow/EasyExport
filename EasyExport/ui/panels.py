import bpy
from ..utils import common
import os
class DarrowDevPanel:
    bl_category = "DarrowTools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_idname = "DARROW_PT_devPanel"

class DARROW_PT_panel(DarrowDevPanel, bpy.types.Panel):
    bl_label = "Easy Export"
    bl_idname = "DARROW_PT_exportPanel"

    def draw_header(self, context):
        self.layout.prop(context.scene, 'showAdvancedOptionsBool',
                         icon="MOD_HUE_SATURATION", text="")

    def draw(self, context):
        all = bpy.data.objects
        if len(all) != 0:
            layout = self.layout
            Var_prefix_bool = bpy.context.scene.usePrefixBool
            Var_suffix_bool = bpy.context.scene.useSuffixBool
            Var_custom_prefix = bpy.context.scene.prefixOptions
            Var_custom_suffix = bpy.context.scene.suffixOptions
            Var_suffix_string = bpy.context.scene.custom_suffix_string
            Var_batch_bool = bpy.context.scene.batchExport
            Var_low_suffix = bpy.context.scene.addLowSuffixBool
            Var_high_suffix = bpy.context.scene.addHighSuffixBool
            Var_allowFBX = bpy.context.scene.allowExportingBool
            objs = context.selected_objects
            advancedBool = bpy.context.scene.showAdvancedOptionsBool

            if context.mode == 'OBJECT':
                scn = context.scene
                box = layout.column()
                box.scale_y = 2.33

                if len(objs) != 0:
                    Var_allowFBX = True

                box.operator('darrow.export_prompt', icon="EXPORT", text = "Export Selection")

                if Var_allowFBX == False:
                    box.enabled = False
                box = layout.box().column(align=True)
                box.scale_y = 1.25
                box.prop(context.scene, "batchExport", text="Batch Exporter", toggle= True)
                
                origins = box.column(align=True)
                if Var_batch_bool == True:
                    text = "Use Individual Origins"
                else:
                    text = "Use Active Origin"
                
                origins.prop(context.scene, 'exportAtActiveObjectOriginBool', text=text,toggle=True,)
            
                split = box.split(align=True)
                box = box.box().column(align=False)
                box.prop(context.scene, 'userDefinedExportPath')
                box.prop(scn, 'blenderExportPresets', text="Preset")

                split.prop(scn, 'usePrefixBool', text="Use Prefix",toggle=True)
                split.prop(scn, 'useSuffixBool', text="Use Suffix",toggle=True)

                if bpy.context.scene.userDefinedExportPath != "":
                    box.separator()
                    box.operator('file.export_folder', text="Open Output Folder", icon="FILE_PARENT")

                if advancedBool == True:
                    col = layout.box().column(align=True)
                    col.scale_y = 1.1

                    smtName = col.column(align=True)
                    smtName.prop(scn, 'useSmartNamingBool', text="Smart Output Name", toggle=True)

                    promptName = col.column(align=True)
                    promptName.prop(scn, 'promptForBaseNameBool', text="Prompt Output Name", toggle=True)

                    col.separator()
                    col.prop(scn, 'exportObjectsWithoutPromptBool', text="Direct Export",toggle=True)
                    col.prop(scn, 'openFolderBool', text="Open Folder on Export", toggle=True)
                    col.prop(scn, 'exportAsSingleUser', text="Force Single Users", toggle=True)

                    if bpy.context.scene.promptForBaseNameBool == True:
                        smtName.enabled = False
                        
                    if bpy.context.scene.useSmartNamingBool == True:
                        promptName.enabled = False

                    if bpy.context.scene.batchExport == True:
                        promptName.enabled = False
                        smtName.enabled = False
                    
                    col.separator()
                    col.operator("open.docs", icon="HELP")
                    col.operator("open.presets", icon="FILE")

                if Var_prefix_bool == True:
                    box = layout.box()
                    box.label(text="Prefix Options")
                    flds = box.column(align=True)
                    flds.scale_y = 1.2
                    flds.prop(scn, 'prefixOptions', text="")
                    if Var_custom_prefix == 'OP2':
                        flds.prop(context.scene,
                                 "custom_prefix_string", text="",icon="ALIGN_LEFT")

                if Var_suffix_bool == True:
                    box = layout.box()
                    box.label(text="Suffix Options")
                   
                    bools = box.row(align=True)
                    bools.scale_y = 1.2
                    low = bools.column(align=True)
                    high = bools.column(align=True)
                    low.prop(context.scene,"addLowSuffixBool", toggle=True, text="_low")

                    if Var_high_suffix == True or Var_suffix_string != "":
                        low.enabled = False

                    high.prop(context.scene,"addHighSuffixBool", toggle=True, text="_high")
                    if Var_low_suffix == True or Var_suffix_string != "":
                        high.enabled = False

                    flds = box.column(align=True)
                    flds.scale_y = 1.2

                    if Var_high_suffix == True or Var_low_suffix == True:
                        flds.enabled = False
                    else:
                        flds.enabled = True

                    flds.prop(scn, 'suffixOptions', text="")
                    if Var_custom_suffix == 'OP1':
                        flds.prop(context.scene,
                                 "custom_suffix_string", text="", icon="ALIGN_LEFT")

                    if Var_custom_suffix == 'OP2':
                        btn = box.column(align=True)
                        btn.scale_y = 1.2
                        currentSuffixAmt = str(context.scene.iterativeExportAmount)
                        btn.operator('reset.counter', text="Reset (" + (currentSuffixAmt) + ")")

                if context.mode != 'OBJECT':
                    self.layout.enabled = False

def get_export_presets(self, context):
        ext = ".py"
        items = []
        path = bpy.utils.preset_paths('operator/export_scene.fbx/')

        items.append(("OP1", "Unity", "Predefined Unity Export"))
        items.append(("OP2", "Unreal", "Predefined Unreal Export"))
        items.append(None)
        count = 1

        for file in os.listdir(path[0]):
            if file[-len(ext):] == ext:
                count = count + 1
                preset = str(file.replace(".py", ""))
                items.append((preset,preset,"*User Preset*"))
        return items

classes = (DARROW_PT_panel,)

def register():

    bpy.types.Scene.blenderExportPresets = bpy.props.EnumProperty(
        items=get_export_presets, name="FBX Operator Presets", description = "User defined export presets created in Blender's exporter."
)

    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.promptForBaseNameBool = bpy.props.BoolProperty(
        name="Prompt base name",
        description="Ask user for the output base name",
        default=False
    )

    bpy.types.Scene.userDefinedExportPath = bpy.props.StringProperty(
        name='Path',
        update=lambda s, c: common.make_path_absolute('userDefinedExportPath'),
        subtype='FILE_PATH'
        )

    bpy.types.Scene.openFolderBool = bpy.props.BoolProperty(
        name="Open Folder on Export",
        description="Open Folder on Export",
        default=False
    )

    bpy.types.Scene.batchExport = bpy.props.BoolProperty(
        name="Batch Export",
        description="Export as separate objects",
        default=False
    )

    bpy.types.Scene.userDefinedBaseName = bpy.props.StringProperty(
        name='Base Name',
    )

    bpy.types.Scene.exportAsSingleUser = bpy.props.BoolProperty(
        name="Export as single user",
        description="Make object single user on export",
        default=False
    )

    bpy.types.Scene.exportAtActiveObjectOriginBool = bpy.props.BoolProperty(
        name="Use object origin",
        description="Export at object origin(s) rather than the world origin (0,0,0)",
        default= False
    )

    bpy.types.Scene.exportObjectsWithoutPromptBool = bpy.props.BoolProperty(
        name="Direct Export",
        description="Directly Export to user defined path",
        default=True
    )

    bpy.types.Scene.showAdvancedOptionsBool = bpy.props.BoolProperty(
        name="Advanced",
        description="Show advanced options",
        default=False
    )

    bpy.types.Scene.separateAllActionsBool = bpy.props.BoolProperty(
        name="All actions",
        description="Export each action separately",
        default=False
    )

    bpy.types.Scene.usePrefixBool = bpy.props.BoolProperty(
        name="Use Prefix",
        description="Export selected object with custom text as a prefix",
        default=False
    )

    bpy.types.Scene.useSuffixBool = bpy.props.BoolProperty(
        name="Use Suffix",
        description="Export selected object with custom text as a suffix",
        default=False
    )

    bpy.types.Scene.addHighSuffixBool = bpy.props.BoolProperty(
        name="Use _high",
        description="Export selected object with custom text as a suffix",
        default=False
    )

    bpy.types.Scene.iterativeExportAmount = bpy.props.IntProperty(
        default=0
    )

    bpy.types.Scene.suffixOptions = bpy.props.EnumProperty(
        name="Suffix",
        description="Suffix Options",
        items=[('OP1', "Custom", ""),
               ('OP2', "Iterative","")
               ],
        default='OP1'
    )

    bpy.types.Scene.prefixOptions = bpy.props.EnumProperty(
        name="Prefix",
        description="Prefix Options.",
        items=[('OP1', ".blend", ""),
               ('OP2', "Custom", ""),
               ]
               
    )

    bpy.types.Scene.useSmartNamingBool = bpy.props.BoolProperty(
        name="Use smart naming when exporting",
        description="Use the active collection name when exporting more than one object",
        default=True
    )

    bpy.types.Scene.addLowSuffixBool = bpy.props.BoolProperty(
        name="Use _low",
        description="Export selected object with custom text as a suffix",
    )

    bpy.types.Scene.custom_prefix_string = bpy.props.StringProperty(
        name="",
        description="Custom Prefix",
        default=""
    )

    bpy.types.Scene.custom_suffix_string = bpy.props.StringProperty(
        name="",
        description="Custom Suffix",
        default=""
    )

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
