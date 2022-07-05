# ##### BEGIN GPL LICENSE BLOCK #####
#
#   Copyright (C) 2020- 2022  Blake Darrow <contact@blakedarrow.com>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####

import bpy
import os
import mathutils
from bpy_extras.io_utils import ExportHelper
import webbrowser

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
            Var_prompt = bpy.context.scene.exportObjectsWithoutPromptBool
            objs = context.selected_objects
            advancedBool = bpy.context.scene.showAdvancedOptionsBool

            if context.mode == 'OBJECT':
                scn = context.scene
                box = layout.column()
                box.scale_y = 2.33
                
                if len(objs) != 0:
                    Var_allowFBX = True
                if Var_prompt == False:
                    box.operator('export_selected.darrow', icon="EXPORT", text = "Export Selection")
                else:
                    box.operator(
                        'export_selected_promptless.darrow', icon="EXPORT", text = "Export Selection")

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
                box.prop(context.scene, 'exportPresets')

                if bpy.context.scene.userDefinedExportPath != "":
                    box.separator()
                    box.operator('file.export_folder',
                                 text="Open Output Folder", icon="FILE_PARENT")

                split.prop(scn, 'usePrefixBool', text="Use Prefix",toggle=True)
                split.prop(scn, 'useSuffixBool', text="Use Suffix",toggle=True)

                if advancedBool == True:
                    col = box.column(align=True)
                    col.separator()
                    col.scale_y = 1.1
                    col.prop(scn, 'useSmartNamingBool', text="Use Smart Naming", toggle=True)
                    col.prop(scn, 'exportObjectsWithoutPromptBool', text="Direct Export",toggle=True)
                    col.prop(scn, 'exportAsSingleUser', text="Force Single User", toggle=True)
                    col.prop(scn, 'separateAllActionsBool',
                             text="Separate All Actions", toggle=True)
                    col.prop(scn, 'useLeafBonesBool', text="Use Leaf Bones", toggle=True)

                    col.separator()
                    col.operator("open.docs", icon="HELP")

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
            if DarrowCheckErrors(self, path_no_prompt) == False:
                DarrowSetUpExport(self, context, path_no_prompt)

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

            if DarrowCheckErrors(self, path_prompt) == False:
                DarrowSetUpExport(self, context, path_prompt)

        return {'FINISHED'}

class DarrowOpenRenderFolder(bpy.types.Operator):
    """Open the Render Folder in a file Browser"""
    bl_idname = "file.export_folder"
    bl_description = "Open export folder"
    bl_label = "ExportFolder"

    def execute(self, context):
        if not os.path.exists(bpy.context.scene.userDefinedExportPath):
            os.makedirs(bpy.context.scene.userDefinedExportPath)

        bpy.ops.wm.path_open(filepath=bpy.context.scene.userDefinedExportPath)

        return {'FINISHED'}

class DarrowIterativeReset(bpy.types.Operator):
    bl_idname = "reset.counter"
    bl_description = "Resets FBX suffix counter"
    bl_label = "Reset Suffix Counter"

    def execute(self, context):
        context.scene.iterativeExportAmount = 0

        self.report({'INFO'}, "Set suffix count to 0")
        return {'FINISHED'}

class DarrowOpenDocs(bpy.types.Operator):
    bl_idname = "open.docs"
    bl_description = "Open Docs"
    bl_label = "Open Docs"

    def execute(self, context):
        webbrowser.open('https://darrow.tools/EasyExport')
        self.report({'INFO'}, "Opened documentation")
        return {'FINISHED'}

class DarrowStoredVectorList:
  def __init__(self, name='VectorList', vector=[]):
    self.name = name
    self.vector = vector

class DarrowStoredBooleanList:
  def __init__(self, name='BooleanList', booleans=[]):
    self.name = name
    self.booleans = booleans

def turn_collection_hierarchy_into_path(obj):
    parent_names = []
    parent_names.append(bpy.context.view_layer.active_layer_collection.name)
    return '\\'.join(parent_names)

def make_path_absolute(key):
    """From https://sinestesia.co/blog/tutorials/avoid-relative-paths/"""
    """ Prevent Blender's relative paths of doom """

    props = bpy.context.scene
    def sane_path(p): return os.path.abspath(bpy.path.abspath(p))

    if key in props and props[key].startswith('//'):
        props[key] = sane_path(props[key])

def ClearParent(child):    
    """https://blenderartists.org/t/preserving-child-transform-after-removing-parent/616845/3"""
    # Save the transform matrix before de-parenting
    matrixcopy = child.matrix_world.copy()
    
    # Clear the parent
    child.parent = None
        
    # Restore childs location / rotation / scale
    child.matrix_world = matrixcopy

def DarrowCheckErrors(self, path):
    error = False
    
    if not os.path.exists(bpy.context.scene.userDefinedExportPath):
        os.makedirs(bpy.context.scene.userDefinedExportPath)

    if len(path) != 0:
    
        if bpy.context.view_layer.objects.active != None and bpy.context.scene.batchExport == False:
            error = False
        elif bpy.context.scene.batchExport == True:
            error = False
        else:
            error = True
            self.report({'ERROR'}, "Must define active object")
    else:
        error = True
        self.report({'ERROR'}, "Must define export path")

    return error

def DarrowSetUpExport(self, context, path):
    Var_batch_bool = bpy.context.scene.batchExport

    if Var_batch_bool == True:
        DarrowBatchExport(self, context, path) 
    else:
        DarrowExport(path)
        DarrowPostExport(self, context)

def DarrowBatchExport(self, context, path):
    Var_batch_bool = bpy.context.scene.batchExport

    if Var_batch_bool == True:
        sel_objs = bpy.context.selected_objects

        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.active_object.select_set(False)

        for obj in sel_objs:
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
            DarrowExport(path)
            DarrowPostExport(self, context)
            obj.select_set(False)
            bpy.context.active_object.select_set(False)

def DarrowPostExport(self, context):
    active_obj = bpy.context.active_object

    DarrowMoveToSavedLocation(active_obj)

    bpy.context.scene.darrowVectors.vector.clear()
    bpy.context.scene.darrowBooleans.booleans.clear()

    if bpy.context.view_layer.objects.active != None and bpy.context.scene.batchExport == False:
       self.report({'INFO'}, "Exported object as '" + bpy.context.scene.exportedObjectName + "'")
    elif bpy.context.scene.batchExport == True:
       self.report({'INFO'}, "Exported multiple objects")

def DarrowGenerateExportCount():
    Var_custom_suffix = bpy.context.scene.suffixOptions
    Var_useSuffix = bpy.context.scene.useSuffixBool

    if Var_custom_suffix == 'OP2'and Var_useSuffix: # Iterative
        bpy.context.scene.iterativeExportAmount += 1
        count = bpy.context.scene.iterativeExportAmount
        count = str(count)
    return count

def DarrowGenerateExportName(name):
    blendName = bpy.path.basename(bpy.context.blend_data.filepath).replace(".blend", "")
    Var_usePrefix = bpy.context.scene.usePrefixBool
    Var_useSuffix = bpy.context.scene.useSuffixBool
    Var_custom_prefix = bpy.context.scene.prefixOptions
    Var_custom_suffix = bpy.context.scene.suffixOptions
    Var_prefix_string = bpy.context.scene.custom_prefix_string
    Var_suffix_string = bpy.context.scene.custom_suffix_string
    Var_addHigh = bpy.context.scene.addHighSuffixBool
    Var_addLow = bpy.context.scene.addLowSuffixBool
    
    prefix = ""
    name = name
    suffix = ""

    if Var_usePrefix == True:
        if Var_custom_prefix == 'OP1':  # .blend prefix
            if not bpy.data.is_saved:
                raise Exception("Blend file is not saved")
            else:
                prefix = blendName

        if Var_custom_prefix == 'OP2':  # custom prefix string
            prefix = Var_prefix_string
         
    if Var_useSuffix == True:
        if Var_custom_suffix == 'OP1': #custom suffix string
            if Var_suffix_string != "":
                suffix = Var_suffix_string

            elif Var_suffix_string == "":
                Var_HorLowSuffix = ""

                if Var_addHigh == False and Var_addLow == True:
                    Var_HorLowSuffix = "low"
                if Var_addHigh == True and Var_addLow == False:
                    Var_HorLowSuffix ="high"
                if Var_addHigh == True and Var_addLow == True:
                    Var_HorLowSuffix = "Error"
            
                suffix = Var_HorLowSuffix

        if Var_custom_suffix == 'OP2': # Iterative counter
            suffix = DarrowGenerateExportCount()
 
    if prefix == "" and suffix =="":
        exportName = name
    elif prefix == "" and suffix != "":
        exportName = name + "_"+ suffix
    elif prefix != "" and suffix == "":
        exportName = prefix + "_" + name
    elif prefix != "" and suffix != "":
        exportName = prefix + "_" + name + "_" + suffix
    
    return exportName   

def DarrowSaveLocation(active):
    if bpy.context.scene.exportAtActiveObjectOriginBool == True:
        bpy.context.scene.darrowVectors.vector.append((str(active.location.x) + "," + str(active.location.y) + "," + str(active.location.z)))
            
def DarrowMoveToOrigin(active):
    if bpy.context.scene.exportAtActiveObjectOriginBool == True:
        sel_obj = bpy.context.selected_objects
        owner = []
        target = []

        for obj in sel_obj:
            for modifier in obj.modifiers:
                if modifier.type == 'BOOLEAN':
                    owner.append(obj)
                    target.append(modifier.object)
                    bpy.context.scene.darrowBooleans.booleans.append(target)

        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = None

        for tar in target:
            i = target.index(tar)
            ownerObj = owner[i]

            tar.select_set(state=True)
            ownerObj.select_set(state=True)

            bpy.context.view_layer.objects.active = ownerObj

            bpy.ops.object.parent_set(type='OBJECT', keep_transform=False)
            bpy.ops.object.select_all(action='DESELECT')

        sel_obj.remove(active)
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = None

        for child in sel_obj:

             child.select_set(state=True)
             active.select_set(state=True)

             bpy.context.view_layer.objects.active = active

             bpy.ops.object.parent_set(type='OBJECT', keep_transform=False)
             bpy.ops.object.select_all(action='DESELECT')

        for child in sel_obj:
             child.select_set(state=True)

        active.select_set(state=True)

        bpy.context.view_layer.objects.active = active
        active.location = (0,0,0)

def DarrowMoveToSavedLocation(obj):
    if bpy.context.scene.exportAtActiveObjectOriginBool == True:
        obj.location= eval(bpy.context.scene.darrowVectors.vector[0])

        sel_obj = bpy.context.selected_objects
        sel_obj.remove(obj)

        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = None

        for child in sel_obj:
            child.select_set(state=True)
            ClearParent(child)

            bpy.ops.object.select_all(action='DESELECT')

        for child in bpy.context.scene.darrowBooleans.booleans:
            print(child)
            i = bpy.context.scene.darrowBooleans.booleans.index(child)
            child[i].select_set(state=True)
            ClearParent(child[i])

            bpy.ops.object.select_all(action='DESELECT')
       
        for child in sel_obj:
            child.select_set(state=True)

        obj.select_set(state=True)

        bpy.context.view_layer.objects.active = obj

def DarrowExport(path):
    objs = bpy.context.selected_objects
    Var_batch_bool = bpy.context.scene.batchExport
    active_obj = bpy.context.active_object

    DarrowSaveLocation(active_obj)

    if len(objs) != 0:
        Var_actionsBool = bpy.context.scene.separateAllActionsBool
        Var_leafBool = bpy.context.scene.useLeafBonesBool
        Var_presets = bpy.context.scene.exportPresets
        Var_nlaBool = False
        Var_forceStartKey = False
        Var_spaceTransform = True
        Var_scale = 1
        Var_axisForward = bpy.context.scene.ExportAxisForward
        Var_axisUp = bpy.context.scene.ExportAxisForward
        Var_useSmartNamingBool = bpy.context.scene.useSmartNamingBool
        Var_batch_bool = bpy.context.scene.batchExport

        if bpy.context.view_layer.objects.active != None:
            fbxName = bpy.context.view_layer.objects.active
            name = bpy.path.clean_name(fbxName.name)
        else:
            fbxName = "No Active Object"
            name = "No Active Object"
        
        amt = len(bpy.context.selected_objects)
        one = 1
        obj = bpy.context.view_layer.objects.active
        parent_coll = turn_collection_hierarchy_into_path(obj)
        
        if bpy.context.scene.exportAsSingleUser == True:
            for obj in objs:
                bpy.ops.object.make_single_user(
                    object=True, obdata=True, material=False, animation=False)

        if (Var_useSmartNamingBool == True) and (amt > one) and Var_batch_bool == False:
            fbxName = parent_coll
            name = bpy.path.clean_name(fbxName)

        for obj in objs:
            anim = obj.animation_data
            if anim is not None and anim.action is not None:
                Var_spaceTransform = False

        if Var_presets == 'OP1':  # Unity preset
            Var_axisUp = 'Y'
            Var_axisForward = 'X'
            Var_scale = 1
            Var_leafBool = False
            Var_actionsBool = False
            Var_nlaBool = False
            Var_forceStartKey = False

        elif Var_presets == 'OP2':  # Unreal preset
            Var_axisUp = 'Z'
            Var_axisForward = '-Y'
            Var_scale = 1
            Var_nlaBool = False
            Var_leafBool = False
            Var_actionsBool = False
            Var_forceStartKey = True

        exportName = DarrowGenerateExportName(name)
        saveLoc = path + exportName

    bpy.context.scene.exportedObjectName = exportName

    DarrowMoveToOrigin(active_obj)

    bpy.ops.export_scene.fbx(
          filepath= saveLoc.replace('.fbx', '') + ".fbx",
          use_mesh_modifiers=True,
          use_space_transform=True,
          bake_space_transform=Var_spaceTransform,
          bake_anim_use_all_actions=Var_actionsBool,
          add_leaf_bones=Var_leafBool,
          bake_anim_use_nla_strips=Var_nlaBool,
          bake_anim_force_startend_keying=Var_forceStartKey,
          check_existing=True,
          axis_forward=Var_axisForward,
          axis_up=Var_axisUp,
          use_selection=True,
          apply_unit_scale=True,
          global_scale=Var_scale,
          embed_textures=False,
          path_mode='AUTO')
    
classes = (DARROW_PT_panel, DarrowExportFBXNoPrompt, DarrowOpenDocs, DarrowExportFBXWithPrompt, DarrowIterativeReset, DarrowOpenRenderFolder)

def register():

    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.darrowVectors = DarrowStoredVectorList()

    bpy.types.Scene.darrowBooleans = DarrowStoredBooleanList()

    bpy.types.Scene.objStoredLocation = bpy.props.StringProperty(
        name='Old loc',
    )

    bpy.types.Scene.setupExportPath = bpy.props.StringProperty(
        name='ExportPath',
    )

    bpy.types.Scene.userDefinedBaseName = bpy.props.StringProperty(
        name='Base Name',
    )

    bpy.types.Scene.userDefinedExportPath = bpy.props.StringProperty(
        name='Path',
        update=lambda s, c: make_path_absolute('userDefinedExportPath'),
        subtype='FILE_PATH')

    bpy.types.Scene.ExportAxisForward = bpy.props.EnumProperty(
        name="Forward Axis",
        description="Animation Export Presets",
        items=[('OP1', "X", ""),
               ('OP2', "Y", ""),
               ('OP3', "Z", ""),
               ('OP4', "-X", ""),
               ('OP5', "-Y", ""),
               ('OP6', "-Z", ""),
               ],
        default='OP5'
    )

    bpy.types.Scene.ExportAxisUp = bpy.props.EnumProperty(
        name="Up Axis",
        description="Export Up Axis",
        items=[('OP1', "X", ""),
               ('OP2', "Y", ""),
               ('OP3', "Z", ""),
               ('OP4', "-X", ""),
               ('OP5', "-Y", ""),
               ('OP6', "-Z", ""),
               ],
        default='OP3'
    )

    bpy.types.Scene.batchExport = bpy.props.BoolProperty(
        name="Batch Export",
        description="Export as separate objects",
        default=False
    )

    bpy.types.Scene.exportAsSingleUser = bpy.props.BoolProperty(
        name="Export as single user",
        description="Make object single user on export",
        default=False
    )

    bpy.types.Scene.exportAtActiveObjectOriginBool = bpy.props.BoolProperty(
        name="Use object origin",
        description="Export at object origin rather than world origin",
        default=True
    )

    bpy.types.Scene.exportObjectsWithoutPromptBool = bpy.props.BoolProperty(
        name="Promptless",
        description="",
        default=True
    )

    bpy.types.Scene.showAdvancedOptionsBool = bpy.props.BoolProperty(
        name="Advanced",
        description="Show advanced options",
        default=False
    )

    bpy.types.Scene.exportPresets = bpy.props.EnumProperty(
        name="Preset",
        description="Animation Export Presets",
        items=[('OP1', "Unity", ""),
               ('OP2', "Unreal", ""),
               ],
        default='OP2'
    )

    bpy.types.Scene.allowExportingBool = bpy.props.BoolProperty()

    bpy.types.Scene.useSmartNamingBool = bpy.props.BoolProperty(
        name="Use smart naming when exporting",
        description="Use the active collection name when exporting and combining more than 1 object",
        default=True
    )

    bpy.types.Scene.separateAllActionsBool = bpy.props.BoolProperty(
        name="All actions",
        description="Export each action separated separately",
        default=False
    )

    bpy.types.Scene.useLeafBonesBool = bpy.props.BoolProperty(
        name="Leaf bones",
        description="Exporting using leaf bones",
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

    bpy.types.Scene.exportedObjectName = bpy.props.StringProperty()

def unregister():

    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()