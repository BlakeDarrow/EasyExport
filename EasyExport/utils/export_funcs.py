import bpy
import os
from . import common
import webbrowser

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

def DarrowCheckErrors(self, path):
    error = False

    if len(path) != 0:
        if not os.path.exists(bpy.context.scene.userDefinedExportPath):
            os.makedirs(bpy.context.scene.userDefinedExportPath)
    
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

    if bpy.context.scene.openFolderBool == True:
        print("Opening Folder")
        bpy.ops.file.export_folder("INVOKE_DEFAULT")

def DarrowGenerateExportCount():
    Var_custom_suffix = bpy.context.scene.suffixOptions
    Var_useSuffix = bpy.context.scene.useSuffixBool

    if Var_custom_suffix == 'OP2'and Var_useSuffix: # Iterative
        bpy.context.scene.iterativeExportAmount += 1
        count = bpy.context.scene.iterativeExportAmount
        count = str(count)
    return count

def DarrowBlendSaveErrorMessage(self, context):
    self.layout.label(text="When using "".blend"" prefix, the Blend file must be saved.")

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
                bpy.context.window_manager.popup_menu(DarrowBlendSaveErrorMessage, title="Error", icon='ERROR')
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

def DarrowClearParent(child):    
    """https://blenderartists.org/t/preserving-child-transform-after-removing-parent/616845/3"""
    matrixcopy = child.matrix_world.copy()
    child.parent = None
    child.matrix_world = matrixcopy

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
            DarrowClearParent(child)

            bpy.ops.object.select_all(action='DESELECT')

        for child in bpy.context.scene.darrowBooleans.booleans:
            print(child)
            i = bpy.context.scene.darrowBooleans.booleans.index(child)
            child[i].select_set(state=True)
            DarrowClearParent(child[i])

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
        parent_coll = common.turn_collection_hierarchy_into_path(obj)
        
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

        if bpy.context.scene.promptForBaseNameBool == True and bpy.context.scene.batchExport == False:
            exportName = DarrowGenerateExportName(bpy.context.scene.userDefinedBaseName)
        else:
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

classes = (DarrowIterativeReset,DarrowOpenDocs,DarrowOpenExportFolder,)

def register():
    bpy.types.Scene.darrowVectors = DarrowStoredVectorList()
    bpy.types.Scene.darrowBooleans = DarrowStoredBooleanList()

    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.objStoredLocation = bpy.props.StringProperty()

    bpy.types.Scene.setupExportPath = bpy.props.StringProperty()

    bpy.types.Scene.ExportAxisForward = bpy.props.EnumProperty(
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

    bpy.types.Scene.allowExportingBool = bpy.props.BoolProperty()

    bpy.types.Scene.exportedObjectName = bpy.props.StringProperty()

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)