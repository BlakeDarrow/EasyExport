# ##### BEGIN GPL LICENSE BLOCK #####
#
#   Copyright (C) 2022  Blake Darrow <contact@blakedarrow.com>
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

#-----------------------------------------------------#  
#   Imports
#-----------------------------------------------------#  
from numpy import save
import bpy
import addon_utils
import os
import math
import bpy.utils.previews
from mathutils import Vector, Matrix
from os import walk
from bpy_extras.io_utils import ExportHelper

from bpy.props import (
        StringProperty,
        EnumProperty,
    )
from pathlib import Path
from bpy_extras.io_utils import (ImportHelper,
                                 ExportHelper,
                                 )
from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       EnumProperty,
                       )
from bpy.types import (Panel,
                       Menu,
                       Operator,
                       )

#-----------------------------------------------------#  
#     handles  ui     
#-----------------------------------------------------#  
class DarrowDevPanel:
    bl_category = "DarrowTools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_idname = "DARROW_PT_devPanel"

class DARROW_PT_panel(DarrowDevPanel, bpy.types.Panel):
    bl_label = "Export Panel"
    bl_idname = "DARROW_PT_exportPanel"
    
    def draw_header(self, context):
        self.layout.prop(context.scene, 'advancedLibraryBool',
                         icon="MOD_HUE_SATURATION", text="")

    def draw(self, context):
        all = bpy.data.objects
        if len(all) != 0:
            layout = self.layout
            Var_prefix_bool = bpy.context.scene.useprefixBool
            Var_suffix_bool = bpy.context.scene.usecounterBool
            Var_custom_prefix = bpy.context.scene.PrefixOption
            Var_allowFBX = bpy.context.scene.fbxBool
            Var_prompt = bpy.context.scene.useDefinedPathBool
            obj = context.object
            objs = context.selected_objects
            folderBool = bpy.context.scene.advancedLibraryBool
           
            if context.mode == 'OBJECT':
                box = layout.column()
                box.scale_y = 2
                
                if len(objs) != 0:
                    Var_allowFBX = True
                if Var_prompt == False:
                    box.operator('export_selected.darrow', icon="EXPORT")
                else:
                    box.operator('export_selected_promptless.darrow', icon="EXPORT")
        
                if Var_allowFBX == False:
                    box.enabled = False
                box = layout.box()
                box.prop(
                    context.scene, 'useDefinedPathBool', text="Promptless Export",)
                split = box.split()
                box = box.box().column(align=False)        
                obj = context.scene
                box.scale_y = 1.2
                box.prop(context.scene, 'userDefinedExportPath')
                box.prop(context.scene, 'exportPresets')
                
                if bpy.context.scene.userDefinedExportPath != "":
                    box.separator()
                    box.operator('file.export_folder', text="Open Export Folder", icon="FILE_PARENT")
                
                split.prop(obj, 'useprefixBool', text="Use Prefix")
                split.prop(obj, 'usecounterBool', text="Use Suffix")
            
                if folderBool == True:
                    anim = layout.box()
                    col = anim.column(align=True)
                    col.prop(obj, 'collectionBool', text="Multi-Object Naming")
                    col.prop(obj, 'allactionsBool', text="Separate All Actions")
                    col.prop(obj, 'isleafBool', text ="Use Leaf Bones")

                if Var_prefix_bool == True:
                    box = layout.box()
                    box.label(text="Prefix Settings:")
                    box.prop(obj, 'PrefixOption')
                    if Var_custom_prefix == 'OP2':
                        box.prop(context.scene,
                                "custom_name_string", text="Prefix")
                    
                if Var_suffix_bool == True:
                    box = layout.box()
                    box.label(text="Suffix Settings:")
                    box.label(text="Increase the suffix by (+1)")
                    currentSuffixAmt = str(context.scene.counter)
                    box.operator(
                        'reset.counter', text="Reset suffix count ("+currentSuffixAmt+")")
                    
                if context.mode != 'OBJECT':
                    self.layout.enabled = False

class DARROW_PT_panel_2(DarrowDevPanel, bpy.types.Panel):
    bl_parent_id = "DARROW_PT_exportPanel"
    bl_label = "Show Warnings"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        obj = bpy.context.view_layer.objects.active
        anim = obj.animation_data
        if context.object.scale[0] != 1 or context.object.scale[1] != 1 or context.object.scale[2] != 1 or context.object.rotation_euler[0] != 0 or context.object.rotation_euler[1] != 0 or context.object.rotation_euler[2] != 0 or context.object.location[0] != 0 or context.object.location[1] != 0 or context.object.location[2] != 0:  
            return True
        elif bpy.context.scene.userDefinedExportPath == "" and bpy.context.scene.useDefinedPathBool == True:
            return True
        elif anim is not None:
            return True
        else: 
            return False

    def draw(self, context):
        obj = bpy.context.view_layer.objects.active
        anim = obj.animation_data
        column = self.layout.column()
        column.scale_y = 1.1
        if bpy.context.scene.userDefinedExportPath == "" and bpy.context.scene.useDefinedPathBool == True:
            column.label(text="Must Define Export Path", icon="CANCEL")
        if context.object.scale[0] != 1 or context.object.scale[1] != 1 or context.object.scale[2] != 1 or context.object.rotation_euler[0] != 0 or context.object.rotation_euler[1] != 0 or context.object.rotation_euler[2] != 0:
            column.label(text="Apply Transformations", icon="ERROR")
        if context.object.location[0] != 0 or context.object.location[1] != 0 or context.object.location[2] != 0: 
            column.label(text="Not at World Origin", icon="ERROR")
        if anim is not None:
            column.label(text="Has Animation Data (Might not export correctly)", icon="ERROR")

#-----------------------------------------------------#
#    Turn active collection into path
#-----------------------------------------------------#
def turn_collection_hierarchy_into_path(obj):
    parent_names = []
    parent_names.append(bpy.context.view_layer.active_layer_collection.name)
    return '\\'.join(parent_names)

#-----------------------------------------------------#
#    Handles logic for exporting as FBX
#-----------------------------------------------------#
def DarrowExport(path):
    objs = bpy.context.selected_objects
    if len(objs) != 0:
        C = bpy.context
        if bpy.context.view_layer.objects.active != None:
            fbxname = bpy.context.view_layer.objects.active
            name = bpy.path.clean_name(fbxname.name)
        else:
            fbxname = "No Active Object"
            name="No Active Object"
        Var_collectionBool = bpy.context.scene.collectionBool
        amt = len(C.selected_objects)
        one = 1
        obj = bpy.context.view_layer.objects.active
        parent_coll = turn_collection_hierarchy_into_path(obj)
        bpy.ops.object.make_single_user(
            object=True, obdata=True, material=False, animation=True)

        if (Var_collectionBool == True) and (amt > one):
            fbxname = parent_coll
            name = bpy.path.clean_name(fbxname)

        customprefix = bpy.context.scene.custom_name_string
        blendName = bpy.path.basename(
            bpy.context.blend_data.filepath).replace(".blend", "")
        settings = bpy.context.preferences.addons[__package__].preferences

        path_no_prompt = bpy.context.scene.userDefinedExportPath
        Var_actionsBool = bpy.context.scene.allactionsBool
        Var_leafBool = bpy.context.scene.isleafBool
        Var_PrefixBool = bpy.context.scene.useprefixBool
        Var_custom_prefix = bpy.context.scene.PrefixOption
        Var_presets = bpy.context.scene.exportPresets
        Var_counterBool = bpy.context.scene.usecounterBool
        Var_nlaBool = False
        Var_forcestartkey = False
        Var_spaceTransform = True
        Var_scale = 1

        Var_axisForward = bpy.context.scene.ExportAxisForward
        Var_axisUp = bpy.context.scene.ExportAxisForward

        for obj in objs:
            anim = obj.animation_data
            if anim is not None and anim.action is not None:
               Var_spaceTransform = False
        
        if Var_presets == 'OP1':  # Unity preset
            Var_leafBool = False
            Var_actionsBool = False
            Var_nlaBool = False
            Var_forcestartkey = False
            Var_axisUp = 'Y'
            Var_axisForward = 'X'
            Var_scale = 1

        elif Var_presets == 'OP2':  # Unreal preset
            Var_axisUp = 'Z'
            Var_axisForward = '-Y'
            Var_scale = 1
            Var_nlaBool = False
            Var_leafBool = False
            Var_actionsBool = False
            Var_forcestartkey = True

        if Var_counterBool == True:
            bpy.context.scene.counter += 1
            count = bpy.context.scene.counter
            count = str(count)
            Var_exportnumber = "_" + count

        if Var_PrefixBool == True:
            if Var_custom_prefix == 'OP1':  # Unity preset
                if not bpy.data.is_saved:
                    raise Exception("Blend file is not saved")

                if Var_counterBool == True:
                    saveLoc = path_no_prompt + "_" + name + Var_exportnumber
                else:
                    saveLoc = path_no_prompt + "_" + name

            if Var_custom_prefix == 'OP2':  # Unreal preset
                if Var_counterBool == True:
                    customname = customprefix + "_" + name + Var_exportnumber
                else:
                    customname = customprefix + "_" + name

                if not bpy.data.is_saved:
                    saveLoc = path.replace(
                        "untitled", "") + customname
                else:
                    saveLoc = path.replace(
                        blendName, '') + customname

        elif Var_PrefixBool == False:
            customname = name
            if Var_counterBool == True:
                if not bpy.data.is_saved:
                    saveLoc = path.replace(
                        "untitled", "") + name + Var_exportnumber
                else:
                    saveLoc = path.replace(
                        blendName, "") + name + Var_exportnumber
            else:
                saveLoc = path.replace(blendName, "") + name
                if not bpy.data.is_saved:
                    saveLoc = path.replace("untitled", "") + name

    bpy.context.scene.tmpCustomName = customname

    bpy.ops.export_scene.fbx(
        filepath=saveLoc.replace('.fbx', '') + ".fbx",
        use_mesh_modifiers=True,
        use_space_transform=True,
        bake_space_transform=Var_spaceTransform,
        bake_anim_use_all_actions=Var_actionsBool,
        add_leaf_bones=Var_leafBool,
        bake_anim_use_nla_strips=Var_nlaBool,
        bake_anim_force_startend_keying=Var_forcestartkey,
        check_existing=True,
        axis_forward=Var_axisForward,
        axis_up=Var_axisUp,
        use_selection=True,
        apply_unit_scale=True,
        global_scale=Var_scale,
        embed_textures = False,
        path_mode='AUTO')

class DarrowExportFBXNoPrompt(bpy.types.Operator):
    bl_idname = "export_selected_promptless.darrow"
    bl_label = 'Export Selection'
    bl_description = "Export selection as an FBX using smart naming"
    bl_options = {'PRESET'}
    filename_ext = ".fbx"

    def execute(self, context):
        print("promptless")
        objs = context.selected_objects
        if len(objs) != 0:
            #settings = context.preferences.addons[__package__].preferences
            path_no_prompt = context.scene.userDefinedExportPath
            print(path_no_prompt)
 
            if len(path_no_prompt) != 0 :
                if context.scene.collectionBool == False and bpy.context.view_layer.objects.active != None:
                    DarrowExport(path_no_prompt)
                    self.report({'INFO'}, "Exported object as '" +
                                bpy.context.scene.tmpCustomName + "'")
                elif context.scene.collectionBool == True:
                    DarrowExport(path_no_prompt)
                    self.report({'INFO'}, "Exported object as '" +
                                bpy.context.scene.tmpCustomName + "'")
                else:
                    self.report({'ERROR'}, "Must define active object")
            else:
                self.report({'ERROR'}, "Must define export path")
        return {'FINISHED'}

class DarrowExportFBX(bpy.types.Operator, ExportHelper):
    bl_idname = "export_selected.darrow"
    bl_label = 'Export Selection'
    bl_description = "Export selection as an FBX using smart naming"
    bl_options = {'PRESET'}
    filename_ext = ".fbx"

    def execute(self, context):
        objs = context.selected_objects
        if len(objs) != 0:
            path_prompt = self.filepath
            DarrowExport(path_prompt)
            self.report({'INFO'}, "Exported object as '" + bpy.context.scene.tmpCustomName + "'")
        return {'FINISHED'}

class openFolder(bpy.types.Operator):
    """Open the Render Folder in a file Browser"""
    bl_idname = "file.export_folder"
    bl_label = "ExportFolder"
    
    def execute(self, context):
        bpy.ops.wm.path_open(filepath=bpy.context.scene.userDefinedExportPath)
        return {'FINISHED'}

#-----------------------------------------------------#
#     handles reseting the suffix counter
#-----------------------------------------------------#
class DarrowCounterReset(bpy.types.Operator):
    bl_idname = "reset.counter"
    bl_description = "Resets FBX suffix counter"
    bl_label = "Reset Suffix Counter"

    def execute(self, context):
        context.scene.counter = 0

        self.report({'INFO'}, "Set suffix count to 0")
        return {'FINISHED'}

#-----------------------------------------------------#
#   Registration classes
#-----------------------------------------------------#  
preview_collections = {}
classes = ( DARROW_PT_panel, DARROW_PT_panel_2, DarrowExportFBXNoPrompt, DarrowExportFBX, DarrowCounterReset,openFolder)

def register():

    bpy.types.Scene.userDefinedExportPath = bpy.props.StringProperty(
        name="Path",
        default="",
        subtype='DIR_PATH',
    )

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

    bpy.types.Scene.useDefinedPathBool = bpy.props.BoolProperty(
        name="Promptless",
        description="",
        default=True
    )

    bpy.types.Scene.advancedLibraryBool = bpy.props.BoolProperty(
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

    bpy.types.Scene.fbxBool = bpy.props.BoolProperty()

    bpy.types.Scene.collectionBool = bpy.props.BoolProperty(
        name="Active collection name",
        description="Use active collection name when exporting more than 1 object",
        default=True
    )

    bpy.types.Scene.allactionsBool = bpy.props.BoolProperty(
        name="All actions",
        description="Export each action separated separately",
        default=False
    )

    bpy.types.Scene.isleafBool = bpy.props.BoolProperty(
        name="Leaf bones",
        description="Exporting using leaf bones",
        default=False
    )

    bpy.types.Scene.useprefixBool = bpy.props.BoolProperty(
        name="Use Prefix",
        description="Export selected object with custom text as a prefix",
        default=False
    )

    bpy.types.Scene.usecounterBool = bpy.props.BoolProperty(
        name="Use Suffix",
        description="Count exports and use as suffix",
        default=False
    )

    bpy.types.Scene.custom_name_string = bpy.props.StringProperty(
        name="",
        description="Custom Prefix",
        default="Assets"
    )

    bpy.types.Scene.counter = bpy.props.IntProperty(
        default=0
    )

    bpy.types.Scene.PrefixOption = bpy.props.EnumProperty(
        name="",
        description="Apply Data to attribute.",
        items=[('OP1', ".blend", ""),
               ('OP2', "Custom", ""),
               ]
    )

    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.tmpCustomName = bpy.props.StringProperty()

    bpy.types.Scene.nullBool = bpy.props.BoolProperty(
    name = "",
    default = False
    )

def unregister():

    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()