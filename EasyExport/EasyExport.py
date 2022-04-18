#-----------------------------------------------------#  
#
#    Copyright (c) 2022 Blake Darrow <contact@blakedarrow.com>
#
#    See the LICENSE file for your full rights.
#
#-----------------------------------------------------#  
#   Imports
#-----------------------------------------------------#  

from numpy import save
import bpy
from bpy.types import WindowManager
import addon_utils
import os
from platform import system as currentOS
import math
import random
import bpy.utils.previews
from mathutils import Vector, Matrix
from os import walk
from bpy_extras.io_utils import ImportHelper
from bpy_extras.io_utils import ExportHelper
from bpy.types import (Panel,
                       Menu,
                       Operator,
                       StringProperty,
                       EnumProperty,
                       PropertyGroup
                       )
from bpy.props import (
        StringProperty,
        EnumProperty,
    )
from pathlib import Path
from bpy_extras.io_utils import (ImportHelper,
                                 ExportHelper,
                                 path_reference_mode,
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
#   handles OS file broswer if Windows
#-----------------------------------------------------# 
class meshFolder(bpy.types.Operator):
    """Open the Mesh Folder in a file Browser"""
    bl_idname = "file.mesh_folder"
    bl_label = "Mesh"
    
    def execute(self, context):
        try :
            addonpath = os.path.dirname(os.path.abspath(__file__)) #find path of current addon

            meshpath = addonpath + "\mesh\\" #add folder with the custom mesh inside
            os.makedirs(os.path.dirname(meshpath), exist_ok=True)
            path = meshpath
            bpy.ops.wm.path_open(filepath=path)
        except ValueError:
            self.report({'INFO'}, "No folder yet")
            return {'FINISHED'}
        return {'FINISHED'}

    def path(self):
        filepath = bpy.data.filepath
        relpath = bpy.path.relpath(filepath)
        path = filepath[0: -1 * (relpath.__len__() - 2)]
        return path

class renderFolder(bpy.types.Operator):
    """Open the Render Folder in a file Browser"""
    bl_idname = "file.thumbnail_folder"
    bl_label = "Thumbnails"
    
    def execute(self, context):
        try :
            addonpath = os.path.dirname(os.path.abspath(__file__)) #find path of current addon

            meshpath = addonpath + "\\thumbnails\\" #add folder with the custom mesh inside
            os.makedirs(os.path.dirname(meshpath), exist_ok=True)
            path = meshpath
            bpy.ops.wm.path_open(filepath=path)
        except ValueError:
            self.report({'INFO'}, "No folder yet")
            return {'FINISHED'}
        
        return {'FINISHED'}

    def path(self):
        filepath = bpy.data.filepath
        relpath = bpy.path.relpath(filepath)
        path = filepath[0: -1 * (relpath.__len__() - 2)]
        return path

#-----------------------------------------------------#  
#   handles directory items
#-----------------------------------------------------# 
def enum_previews_from_directory_items(self, context):
    """EnumProperty callback"""
    enum_items = []

    if context is None:
        return enum_items

    wm = context.window_manager
    addonpath = os.path.dirname(os.path.abspath(__file__)) #find path of current addon

    renderpath = addonpath + "\\thumbnails\\" #folder for renders windows
    directory = renderpath

    # Get the preview collection (defined in register func).
    pcoll = preview_collections["main"]

    if directory and os.path.exists(directory):
        # Scan the directory for png files
        image_paths = []
        for fn in os.listdir(directory):
            if fn.lower().endswith(".png"):
                image_paths.append(fn)

        for i, name in enumerate(image_paths):
            # generates a thumbnail preview for a file.
            filepath = os.path.join(directory, name)
            icon = pcoll.get(name)
            if not icon:
                thumb = pcoll.load(name, filepath, 'IMAGE')
            else:
                thumb = pcoll[name]
            enum_items.append((name, name, name, thumb.icon_id, i))
    pcoll.my_previews = enum_items
    return pcoll.my_previews

#-----------------------------------------------------#  
#     handles  ui     
#-----------------------------------------------------#  
class DarrowDevPanel:
    bl_category = "DarrowTools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_idname = "DARROW_PT_devPanel"

class DARROW_PT_panel_1(DarrowDevPanel, bpy.types.Panel):
    bl_label = "Export Panel"
    bl_idname = "DARROW_PT_panel_1"

    def draw_header(self, context):
        self.layout.prop(context.scene, 'advancedLibraryBool',
                         icon="MOD_HUE_SATURATION", text="")

    def draw(self, context):
        all = bpy.data.objects
        if len(all) != 0:
            layout = self.layout
            settings = context.preferences.addons[__package__].preferences
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

                box.prop(settings, 'userDefinedExportPath')
                box.prop(context.scene, 'exportPresets')
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
                    box.label(text="Prefix Options")
                    box.prop(obj, 'PrefixOption')
                    if Var_custom_prefix == 'OP2':
                        box.prop(context.scene,
                                "custom_name_string", text="Prefix")
                    
                if Var_suffix_bool == True:
                    box = layout.box()
                    box.label(text="Suffix Options")
                    box.label(text="Increase the suffix by (+1)")
                    currentSuffixAmt = str(context.scene.counter)
                    box.operator(
                        'reset.counter', text="Reset suffix count ("+currentSuffixAmt+")")

                if context.mode != 'OBJECT':
                    self.layout.enabled = False

class DARROW_PT_panel_2(DarrowDevPanel, bpy.types.Panel):
    bl_parent_id = "DARROW_PT_panel_1"
    bl_label = "External Mesh Library"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        if os.name != 'posix':
            obj = context.active_object
            layout = self.layout
            obj = context.object
            scn = context.scene
            wm = context.window_manager
            objs = context.selected_objects
            getBool = bpy.context.scene.getBool
            addBool = bpy.context.scene.addBool
            folderBool = bpy.context.scene.advancedLibraryBool
            box = layout.box()
            box.label(text="Library Operations", icon="DOCUMENTS")
            if folderBool == True:
                box = layout.box()
                box.label(text="Folder Locations", icon="FILE_FOLDER")
                box.scale_y = 1.2
                box = box.row(align=True)
                box.operator('file.mesh_folder', icon="FILE_PARENT")
                box.operator('file.thumbnail_folder')

            label_add = "Add" if getBool ^ 1 else "Add"
            label_get = "Get" if addBool ^ 1 else "Get"

            if getBool and addBool == True:
                getBool = False
                addBool = False
                label_get = "select one"
                label_add = "select one"

            row = layout.row(align=True)
            row.scale_y = 2
            row.prop(scn, 'addBool',  toggle=True, text=label_add, icon="EXPORT")
            if getBool == True:
                row.enabled = False

            row = layout.row(align=True)
            row.scale_y = 2
            row.prop(scn, 'getBool',  toggle=True, text=label_get, icon="IMPORT")
            if addBool == True:
                row.enabled = False
            if addBool == True:
                if obj is not None:
                    box = layout.box()
                    box.label(text="Settings")
                    box.prop(scn, 'autoCamGenBool')
                    box.prop(scn, 'showWireframeRenderBool')

                    box = layout.box()
                    box = box.column(align=True)
                    box.scale_y = 3
                    box.operator('darrow.add_to_library',
                                text="Add to library", icon="EXPORT")
                    row = layout.column(align=False)
                    row.scale_y = 1
                    row.prop(context.scene, "tag_name",
                            text="Tag", icon="WORDWRAP_ON")

            if getBool == True:
                layout = self.layout
                layout.label(text="Previews")
                row = layout.row()
                row.scale_y = .5
                row.template_icon_view(
                    wm, "my_previews", show_labels=1, scale=18.5, scale_popup=5)
                row = layout.column(align=False)
                row.scale_y = 2.5
                row.operator_menu_enum(
                    "object.asset_library", "mesh_enum_prop", text="Get from library", icon="IMPORT")
                row = layout.column(align=False)
                row.scale_y = 1
                row.prop(scn, 'tag_enum_prop', text="Filter")

            if obj is None and addBool == True:
                box = layout.box()
                box = box.column(align=True)
                box.label(text="Please select a mesh")

            if context.mode != 'OBJECT':
                self.layout.enabled = False
        else:
            layout = self.layout
            layout.label(text="currently unavailable on mac")
    
#-----------------------------------------------------#  
#    Handles Thumbnail Creation
#-----------------------------------------------------#  
class DarrowThumbnail(bpy.types.Operator):
    bl_idname= "darrow.create_thumbnail"
    bl_label = "Generate Thumbnail"

    def execute(self, context):
        print("execute")

        fbxname = bpy.context.view_layer.objects.active
        name = fbxname.name
        print(name)

        if bpy.context.scene.autoCamGenBool == True:
            camera_data = bpy.data.cameras.new(name='Thumbnail_Camera_Darrow')
            camera_object = bpy.data.objects.new('Thumbnail_Camera_Darrow', camera_data)
            bpy.context.scene.collection.objects.link(camera_object)

            cam = camera_object
            target = bpy.context.view_layer.objects.active

            dist = target.dimensions * 2.5
            cam.location = dist
            bpy.context.scene.render.resolution_x = 1080
            bpy.context.scene.render.resolution_y = 1080

            constraint = cam.constraints.new(type='TRACK_TO')
            constraint2 = cam.constraints.new(type='LIMIT_DISTANCE')
            
            constraint.target = target
            constraint2.target = target
            constraint2.limit_mode = 'LIMITDIST_OUTSIDE'
            constraint2.distance = 5

            bpy.context.view_layer.objects.active = cam
            bpy.ops.view3d.object_as_camera()
            target.select_set(state=False)
        else:
            fbxname.select_set(state=False)

        addonpath = os.path.dirname(os.path.abspath(__file__)) #find path of current addon

        meshpath = addonpath + "\\thumbnails\\" #folder for renders

        if bpy.context.scene.showWireframeRenderBool == True:
            bpy.context.space_data.show_gizmo = False
            bpy.context.space_data.overlay.show_floor = False
            bpy.context.space_data.overlay.show_axis_y = False
            bpy.context.space_data.overlay.show_axis_x = False
            bpy.context.space_data.overlay.show_cursor = False
            bpy.context.space_data.overlay.show_object_origins = False
            #bpy.context.space_data.overlay.show_wireframes = True

        print(bpy.context.scene.showWireframeRenderBool)
        bpy.context.scene.render.filepath = meshpath + name + ".jpg"
        #bpy.ops.render.render(write_still = True)
        bpy.ops.render.opengl(write_still = True)
        if bpy.context.scene.autoCamGenBool == True:
            bpy.data.objects.remove(cam)
        else:
            print("no auto camera")

        if bpy.context.scene.showWireframeRenderBool == True:
            bpy.context.space_data.show_gizmo = True
            bpy.context.space_data.overlay.show_floor = True
            bpy.context.space_data.overlay.show_axis_y = True
            bpy.context.space_data.overlay.show_axis_x = True
            bpy.context.space_data.overlay.show_cursor = True
            bpy.context.space_data.overlay.show_object_origins = True
            #bpy.context.space_data.overlay.show_wireframes = False

        fbxname.select_set(state=True)
        return {'FINISHED'}

#-----------------------------------------------------#  
#    Returns a dict of all mesh with unique identifier
#-----------------------------------------------------#  
def mesh_items(scene, context):
    f = []

    currentTag = bpy.context.scene.tag_enum_prop
    addonpath = os.path.dirname(os.path.abspath(__file__)) #find path of current addon
    meshpath = addonpath + "\mesh\\" + currentTag #add folder with the custom mesh inside

    for (dirpath, dirnames, filenames) in walk(meshpath):
        f.extend(filenames)
        break

    meshNames = { i : f[i] for i in range(0, len(f) ) }

    items = []
    for name, name in meshNames.items():
        items.append((name, name, str(name)))  # name is used as identifier
    print(items)
    return items

def tag_items(scene,context):
    tags = []
    addonpath = os.path.dirname(os.path.abspath(__file__)) #find path of current addon

    meshpath = addonpath + "\mesh\\" #add folder with the custom mesh inside
    try:
        os.chdir(meshpath)
    except:
        os.makedirs(os.path.dirname(meshpath), exist_ok=True)
        os.chdir(meshpath)

    foldernames= os.listdir (".") # get all files' and folders' names in the current directory
    for name in foldernames: # loop through all the files and folders
        if os.path.isdir(os.path.join(os.path.abspath("."), name)): # check whether the current object is a folder or not
            tags.append(name)
    tagData = { i : tags[i] for i in range(0, len(tags) ) }

    folders = []
    for name, name in tagData.items():
        folders.append((name, name, str(name)))  # name is used as identifier
    print(folders)
    return folders

#-----------------------------------------------------#  
#    Get mesh from library
#-----------------------------------------------------#  
class OBJECT_OT_mesh_library(bpy.types.Operator):
    """Get mesh from current library"""
    bl_idname = "object.asset_library"
    bl_label = "Import to scene"
    bl_options = {'REGISTER', 'UNDO'}

    mesh_enum_prop : bpy.props.EnumProperty(items=mesh_items, description="Mesh to import")
    
    def execute(self, context):
        print("Hello world")
        name = self.mesh_enum_prop
        currentTag = bpy.context.scene.tag_enum_prop
        print(name)
  
        addonpath = os.path.dirname(os.path.abspath(__file__)) #find path of current addon
        meshpath = addonpath + "\mesh\\" #add folder with the custom mesh inside
        
        tagpath = meshpath + currentTag + "\\"
        finalpath = tagpath + name #add name of custom mesh to the end
        print(finalpath)

        cursorLocBool = bpy.context.scene.cursorLocBool

        bpy.ops.import_scene.fbx(filepath = finalpath) #import the selected mesh
        if cursorLocBool == True:
            bpy.ops.view3d.snap_selected_to_cursor(use_offset=False)

        mesh_items(self,context) #update enum list of assets
        self.report({'INFO'}, f"{name}")
        return {'FINISHED'}

#-----------------------------------------------------#  
#    Add mesh to library
#-----------------------------------------------------#  
class DarrowAddMeshtoLibrary(Operator):
    """Add selected mesh to the library using the current tag"""
    bl_idname = "darrow.add_to_library"
    bl_label = "Add Selected to Library"
    filename_ext    = ".fbx";
    
    def execute(self, context):
        objs = context.selected_objects
        if len(objs) != 0: 
            tagString = bpy.context.scene.tag_name #if this is null, no folder is created
            fbxname = bpy.context.view_layer.objects.active
            exportmeshName = bpy.path.clean_name(fbxname.name)
            addonpath = os.path.dirname(os.path.abspath(__file__)) #find path of current addon
            meshpath = addonpath + "\mesh\\" #add folder with the custom mesh inside
            os.makedirs(os.path.dirname(meshpath), exist_ok=True)
            finalpath = meshpath + tagString + "\\"+ exportmeshName + ".fbx" #add name of selected mesh to the end

            os.chdir(meshpath)
            try:
                os.mkdir(tagString)
            except:
                print("tag folder already created")

            bpy.ops.export_scene.fbx(
            filepath = finalpath,
            use_selection=True,
                )

            DarrowThumbnail.execute(self,context)
        else:
            self.report({'INFO'}, "None Selected")
        return {'FINISHED'}

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
        path_no_prompt = settings.userDefinedExportPath
        Var_actionsBool = bpy.context.scene.allactionsBool
        Var_leafBool = bpy.context.scene.isleafBool
        Var_PrefixBool = bpy.context.scene.useprefixBool
        Var_custom_prefix = bpy.context.scene.PrefixOption
        Var_presets = bpy.context.scene.exportPresets
        Var_counterBool = bpy.context.scene.usecounterBool
        Var_nlaBool = False
        Var_forcestartkey = False

        if Var_presets == 'OP1':  # Unity preset
            Var_leafBool = False
            Var_actionsBool = False
            Var_nlaBool = False
            Var_forcestartkey = False
            if (amt > one):
                Var_axisUp = 'Y'
                Var_axisForward = 'X'
                Var_scale = 1
            else:
                bpy.ops.object.transform_apply(
                    location=False, rotation=True, scale=False)
                bpy.context.active_object.rotation_euler[0] = math.radians(
                    -90)
                print("rotated -90")
                bpy.ops.object.transform_apply(
                    location=False, rotation=True, scale=False)
                print("rotations applied")
                bpy.context.active_object.rotation_euler[0] = math.radians(
                    90)
                print("rotated 90")
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
        bake_anim_use_all_actions=Var_actionsBool,
        add_leaf_bones=Var_leafBool,
        bake_anim_use_nla_strips=Var_nlaBool,
        bake_anim_force_startend_keying=Var_forcestartkey,
        check_existing=True,
        axis_forward=Var_axisForward,
        axis_up=Var_axisUp,
        use_selection=True,
        global_scale=Var_scale,
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
            settings = context.preferences.addons[__package__].preferences
            path_no_prompt = settings.userDefinedExportPath
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
classes = ( DarrowExportFBXNoPrompt, DarrowThumbnail, DarrowAddMeshtoLibrary, OBJECT_OT_mesh_library,
            meshFolder, renderFolder, DarrowExportFBX, DarrowCounterReset, DARROW_PT_panel_1, DARROW_PT_panel_2)

def register():

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
               ('OP2', "custom", ""),
               ]
    )

    WindowManager.my_previews = EnumProperty(
        items=enum_previews_from_directory_items,

    )
    pcoll = bpy.utils.previews.new()
    pcoll.my_previews = ()
    preview_collections["main"] = pcoll

    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.tag_enum_prop = bpy.props.EnumProperty(
        items=tag_items, 
        description="Tag to show",
        name="",
        )

    bpy.types.Scene.mesh_name = bpy.props.StringProperty(
        subtype="FILE_PATH",
    )

    bpy.types.Scene.tag_name = bpy.props.StringProperty(
        name = "",
        description = "Master",
        default = "Master"
    )

    bpy.types.Scene.cursorLocBool = bpy.props.BoolProperty(
        default = True,
        name = "Spawn at Cursor Location"
    )

    bpy.types.Scene.showWireframeRenderBool = bpy.props.BoolProperty(
        default = True,
        name = "Hide Overlays"
    )
    
    bpy.types.Scene.library_list = bpy.props.StringProperty()

    bpy.types.Scene.autoCamGenBool = bpy.props.BoolProperty(
    name = "Generate Camera",
    default = True,
    description = "Generate camera for thumbnail automatically(limited)"
    )
    bpy.types.Scene.tmpCustomName = bpy.props.StringProperty()

    bpy.types.Scene.getBool = bpy.props.BoolProperty(
    name = "Get bool",
    default = False,
    description="Get mesh overlay"
    )

    bpy.types.Scene.addBool = bpy.props.BoolProperty(
    name = "Add bool",
    default = False,
    description="Add mesh overlay"
    )

    bpy.types.Scene.nullBool = bpy.props.BoolProperty(
    name = "",
    default = False
    )

def unregister():

    del WindowManager.my_previews

    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    preview_collections.clear()

    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()