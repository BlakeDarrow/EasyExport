import bpy
import os
from . import common

class DarrowStoredVectorList:
  def __init__(self, name='VectorList', vector=[]):
    self.name = name
    self.vector = vector

class DarrowStoredMoveList:
  def __init__(self, name='moveList', moveList=[]):
    self.name = name
    self.moveList = moveList

def DarrowCheckErrors(self, path):
    error = False

    if len(path) != 0:
        if not os.path.exists(path):
            os.makedirs(path)

        bpy.context.scene.userDefinedExportPath = path
        if bpy.context.view_layer.objects.active != None and bpy.context.scene.batchExport == False:
            error = False
        elif bpy.context.scene.batchExport == True:
            error = False
        else:
            error = True
            self.report({'ERROR'}, "Must define active object")
    else:
        error = True
        self.report({'ERROR'}, "Must define export path or save scene.")

    if path == "":
        self.report({'INFO'}, "Invalid path. Either your path is empty and your scene is not saved, or that location is throwing an error.")
        error = True
    
    return error

def DarrowChangeNames(self, string, remove):
    sel_objs = bpy.context.selected_objects
    if not remove:
        for obj in sel_objs:
            obj.name = obj.name + string
    
    if remove:
        for obj in sel_objs:
            obj.name = obj.name.replace(string, "")

def DarrowModifyAllSuffix(self,context, bool):
    if context.scene.addSuffixToModelNames:
        if context.scene.suffixOptions:
            if context.scene.addHighSuffixBool:
                DarrowChangeNames(self, "_high", bool)
            if context.scene.addLowSuffixBool:
                DarrowChangeNames(self, "_low", bool)
            if context.scene.custom_suffix_string != "" and not context.scene.addHighSuffixBool and not context.scene.addLowSuffixBool:

                if not context.scene.custom_suffix_string.startswith("_"):
                    customString = "_" + context.scene.custom_suffix_string
                else:
                    customString = context.scene.custom_suffix_string

                DarrowChangeNames(self, customString, bool)

def DarrowDoubleModel(self, context):
    doubles = ["_high", "_low", context.scene.custom_suffix_string]
    sel_objs = bpy.context.selected_objects
    for obj in sel_objs:
        name = obj.name
        count = 0
        for target in doubles:
            if target in name:
                count += 1

            if count > 1:
                obj.name.replace(target, "", 1)
        print(obj.name)

def DarrowDoublePath(path):
    words = path.split("_")
    unique_words = []
    for word in words:
        if word not in unique_words:
            unique_words.append(word)
    name = "_".join(unique_words)
    return name

def DarrowSetUpExport(self, context, path):
    Var_batch_bool = bpy.context.scene.batchExport
    sel_objs = bpy.context.selected_objects

    DarrowModifyAllSuffix(self, context, False)
    DarrowDoubleModel(self,context)

    if Var_batch_bool == True:
        DarrowBatchExport(self, context, path) 
    else:
        DarrowExport(path)
        DarrowPostExport(self, context)

    if Var_batch_bool:
        bpy.context.view_layer.objects.active = sel_objs[0]
        bpy.context.active_object.select_set(True)

        for obj in sel_objs:
            obj.select_set(True)
            
    DarrowModifyAllSuffix(self, context, True)

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
    bpy.context.scene.darrowBooleans.moveList.clear()

    if bpy.context.scene.openFolderBool == True:
        print("Opening Folder")
        bpy.ops.file.export_folder("INVOKE_DEFAULT")

    # report results to blender viewport
    if bpy.context.view_layer.objects.active != None and bpy.context.scene.batchExport == False:
        self.report({'INFO'}, "Exported object as '" + bpy.context.scene.exportedObjectName + "'")

    elif bpy.context.scene.batchExport:
        self.report({'INFO'}, "Exported multiple objects")

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
                if modifier.type == 'BOOLEAN' and modifier.object != None:
                    owner.append(obj)
                    target.append(modifier.object)
                    bpy.context.scene.darrowBooleans.moveList.append(target)
                if modifier.type == 'MIRROR' and modifier.mirror_object != None:
                    owner.append(obj)
                    target.append(modifier.mirror_object)
                    bpy.context.scene.darrowBooleans.moveList.append(target)

        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = None

        for tar in target:
            hiddenBool = tar.hide_get()
            parent = tar.users_collection[0].name
            if parent != "Scene Collection":
                bpy.data.collections[parent].hide_viewport = False

            tar.hide_set(False)
            i = target.index(tar)
            ownerObj = owner[i]

            tar.select_set(state=True)
            ownerObj.select_set(state=True)

            bpy.context.view_layer.objects.active = ownerObj

            bpy.ops.object.parent_set(type='OBJECT', keep_transform=False)
            bpy.ops.object.select_all(action='DESELECT')
            tar.hide_set(hiddenBool)

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

        for child in bpy.context.scene.darrowBooleans.moveList:
            i = bpy.context.scene.darrowBooleans.moveList.index(child)
            child[i].select_set(state=True)
            DarrowClearParent(child[i])

            bpy.ops.object.select_all(action='DESELECT')
       
        for child in sel_obj:
            child.select_set(state=True)

        obj.select_set(state=True)

        bpy.context.view_layer.objects.active = obj

def DarrowExport(path):
    objs = bpy.context.selected_objects
    active_obj = bpy.context.active_object

    DarrowSaveLocation(active_obj)

    if len(objs) != 0:
        Var_presets = bpy.context.scene.blenderExportPresets
        obj = bpy.context.view_layer.objects.active
        parent_coll = common.turn_collection_hierarchy_into_path(obj)
        
        if bpy.context.scene.exportAsSingleUser == True:
            for obj in objs:
                bpy.ops.object.make_single_user(
                    object=True, obdata=True, material=False, animation=False)

        if bpy.context.scene.namingOptions == 'OP1': #Active collection
            fbxName = parent_coll
            name = bpy.path.clean_name(fbxName)

        if bpy.context.scene.namingOptions == 'OP2': #Active object
            fbxName = bpy.context.view_layer.objects.active
            name = bpy.path.clean_name(fbxName.name)

        if bpy.context.scene.namingOptions == 'OP3': #Prompt
            name = bpy.context.scene.userDefinedBaseName

        if bpy.context.scene.batchExport == True:
            fbxName = bpy.context.view_layer.objects.active
            name = bpy.path.clean_name(fbxName.name)

        exportName = DarrowGenerateExportName(name)
        exportName = DarrowDoublePath(exportName)

        saveLoc = path + exportName

    bpy.context.scene.exportedObjectName = exportName
    DarrowMoveToOrigin(active_obj)

    if Var_presets == 'OP1':
        path = bpy.utils.user_resource('SCRIPTS')
        filepath = path + "/addons/EasyExport/utils/default.py"
    else:
        user_path = bpy.utils.resource_path('USER')
        path = os.path.join(user_path, "scripts/presets/operator/export_scene.fbx/")
        filepath = (path + bpy.context.scene.blenderExportPresets + ".py")
    
    class Container(object):
        __slots__ = ('__dict__',)

    op = Container()
    file = open(filepath, 'r')

    for line in file.readlines()[3::]:
        exec(line, globals(), locals())

    kwargs = op.__dict__
    kwargs["filepath"] = saveLoc.replace('.fbx','') + ".fbx"

    bpy.ops.export_scene.fbx(**kwargs)
       
def register():
    bpy.types.Scene.namingOptions = bpy.props.EnumProperty(
            items=[
            (("OP1", "Active Collection", "File name will be the **active** collection")), 
            (("OP2", "Active Object", "File name will be the **active** object")),
            (("OP3", "Prompt User", "File name will be prompted at export")), 
            ],
            name="Export Naming Options",
            description = "How the exporter should name the outputted files.",
        )
        
    bpy.types.Scene.darrowVectors = DarrowStoredVectorList()

    bpy.types.Scene.darrowBooleans = DarrowStoredMoveList()

    bpy.types.Scene.objStoredLocation = bpy.props.StringProperty()

    bpy.types.Scene.setupExportPath = bpy.props.StringProperty()

    bpy.types.Scene.exportedObjectName = bpy.props.StringProperty()

def unregister():
    print("Nothing to unregister")