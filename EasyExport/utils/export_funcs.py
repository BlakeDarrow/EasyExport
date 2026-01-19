import bpy
import os
from . import common
from ..ops import export_ops 
import time
import datetime
import socket

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
        drive = os.path.splitdrive(path)[0]
        
        # Only check drive on Windows (when drive letter exists)
        if drive and not os.path.exists(drive):
            print(f"ERROR: Drive/root does not exist!")
            return True
        
        if not os.path.exists(path):
            os.makedirs(path)
        else:
            print(f"Path exists: '{path}'")

        bpy.context.scene.userDefinedExportPath = path
        if bpy.context.view_layer.objects.active != None and bpy.context.scene.batchExport == False:
            error = False
        elif bpy.context.scene.batchExport == True:
            error = False
        else:
            error = True
            bpy.context.scene.DarrowPopup_text = "Must define active object"
            bpy.context.window_manager.popup_menu(DarrowPopup, title="Error", icon='ERROR')

    # Now I am creating files in appdata/tmp if nothing is defined      
    #else:
        #error = True
        #bpy.context.scene.DarrowPopup_text = "Must define export path or save scene."
        #bpy.context.window_manager.popup_menu(DarrowPopup, title="Error", icon='ERROR')
    
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
        
        # Filter out render-disabled objects if option is enabled
        if bpy.context.scene.skipRenderDisabled:
            sel_objs = [obj for obj in sel_objs if not obj.hide_render]

        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.active_object.select_set(False)

        for obj in sel_objs:
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
            DarrowExport(path)
            DarrowPostExport(self, context)
            obj.select_set(False)
            bpy.context.active_object.select_set(False)

def DarrowPopup(self, context):
    pop_up_text = bpy.context.scene.DarrowPopup_text
    text = pop_up_text.split('\n')
    
    for line in text:
        self.layout.label(text=line)

def DarrowPopup_text(self, context):
    pop_up_text = bpy.context.scene.DarrowPopup_text
    text = pop_up_text.split('\n')
    
    for line in text:
        self.layout.label(text=line)
    
def DarrowPostExport(self, context):
    active_obj = bpy.context.active_object

    DarrowMoveToSavedLocation(active_obj)

    end_time = time.perf_counter()
    bpy.context.scene.end_time = end_time

    bpy.context.scene.darrowVectors.vector.clear()
    bpy.context.scene.darrowBooleans.moveList.clear()

    if bpy.context.scene.openFolderBool == True:
        print("Opening Folder")
        bpy.ops.file.export_folder("INVOKE_DEFAULT")

    print(bpy.context.scene.end_time)

    # report results to blender viewport
    run_time = bpy.context.scene.end_time - bpy.context.scene.start_time
    execution_time_delta = datetime.timedelta(seconds=run_time)
    minutes = execution_time_delta.seconds // 60
    seconds = execution_time_delta.seconds % 60
    milliseconds = execution_time_delta.microseconds // 1000
    total_time = f"Time: {minutes} minutes and {seconds}.{milliseconds:03} seconds."

    if bpy.context.view_layer.objects.active != None and bpy.context.scene.batchExport == False and not bpy.context.scene.showOutputInfo:
        bpy.context.scene.DarrowPopup_text = "Exported: '" + bpy.context.scene.exportedObjectName + "'.\nPath: '" + context.scene.userDefinedExportPath + "'.\n"+ total_time
        bpy.context.window_manager.popup_menu(DarrowPopup, title="Exported Object", icon='EXPORT')

    elif bpy.context.scene.batchExport and not bpy.context.scene.showOutputInfo:
        bpy.context.scene.DarrowPopup_text = "Exported Multiple Objects.\nPath: '" + context.scene.userDefinedExportPath + "'.\n"+ total_time
        bpy.context.window_manager.popup_menu(DarrowPopup, title="Exported Objects", icon='EXPORT')

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

def DarrowSendMayaCommand(command):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect(('127.0.0.1', 12345))
        print("Attempting to send command...")
        client_socket.sendall(command.encode('utf-8'))

        response = client_socket.recv(1024).decode('utf-8')
        print(f"Sent: {command}")
        print(f"Response: {response}")

def DarrowSendCustomSocketCommand(command):
    # Throw your custom client socket connection code in here
    # The command argument is the string to send to your host
    # You'll need to also update the upstream function name that sends the path at the end of DarrowExport.


    print(command)

def DarrowExport(path):
    print(f"\n=== DarrowExport ===")
    print(f"Export path received: '{path}'")
    objs = bpy.context.selected_objects
    print(f"Selected objects: {[obj.name for obj in objs]}")
    
    # Filter out render-disabled objects if option is enabled
    if bpy.context.scene.skipRenderDisabled:
        objs = [obj for obj in objs if not obj.hide_render]
        print(f"After render filter: {[obj.name for obj in objs]}")
    
    active_obj = bpy.context.active_object
    print(f"Active object: {active_obj.name if active_obj else 'None'}")

    DarrowSaveLocation(active_obj)

    if len(objs) != 0:
        Var_presets = bpy.context.scene.blenderExportPresets # Default and custom user presets per type
        obj = bpy.context.view_layer.objects.active
        parent_coll = common.turn_collection_hierarchy_into_path(obj)
        
        if bpy.context.scene.exportAsSingleUser == True:
            for obj in objs:
                bpy.ops.object.make_single_user(
                    object=True, obdata=True, material=False, animation=False)

        if bpy.context.scene.namingOptions == 'OP1': #Active collection
            name = parent_coll.name
            print("Active Collection")

        if bpy.context.scene.namingOptions == 'OP2': #Active object
            name = bpy.context.view_layer.objects.active.name
            print("Active Object")

        if bpy.context.scene.namingOptions == 'OP3': #Prompt
            name = bpy.context.scene.userDefinedBaseName
            print("Prompt User")

        if bpy.context.scene.namingOptions == 'OP4': #Common Parent
            from ..utils import preset_funcs
            common_parent_name = preset_funcs.DarrowGetCommonParent()
            if common_parent_name:
                name = common_parent_name
                print("Common Parent: " + name)
            else:
                name = bpy.context.scene.userDefinedBaseName
                print("Common Parent (Prompted)")

        if bpy.context.scene.batchExport == True:
            name = bpy.context.view_layer.objects.active.name
            print("Batch Export")

        exportName = DarrowGenerateExportName(name)
        print(f"Generated export name: '{exportName}'")
        #exportName = DarrowDoublePath(exportName)

        saveLoc = os.path.join(path, exportName)
        print(f"Save location (before extension): '{saveLoc}'")

    bpy.context.scene.exportedObjectName = exportName
    DarrowMoveToOrigin(active_obj)

    print(f"Export type: {bpy.context.scene.exportType}")
    print(f"Preset selection: {Var_presets}")
    
    if Var_presets == 'OP1': # Default preset selected. Meaning my custom presets per type.
        path = bpy.utils.user_resource('EXTENSIONS')
        print(f"Extensions path: '{path}'")
        if bpy.context.scene.exportType == 'FBX':
            filepath = os.path.join(path, "user_default", "easy_export", "utils", "default.py")
        elif bpy.context.scene.exportType == 'OBJ':
            filepath = os.path.join(path, "user_default", "easy_export", "utils", "default_obj.py")
        elif bpy.context.scene.exportType == 'STL':
            filepath = os.path.join(path, "user_default", "easy_export", "utils", "default_stl.py")
        print(f"Preset file: '{filepath}'")

    else:
        user_path = bpy.utils.resource_path('USER')
        if bpy.context.scene.exportType == 'FBX':
            path = os.path.join(user_path, "scripts/presets/operator/export_scene.fbx/")
        elif bpy.context.scene.exportType == 'OBJ':
            path = os.path.join(user_path, "scripts/presets/operator/wm.obj_export/")
        elif bpy.context.scene.exportType == 'STL':
            path = os.path.join(user_path, "scripts/presets/operator/export_scene.stl/")

        filepath = os.path.join(path, bpy.context.scene.blenderExportPresets + ".py")
    
    class Container(object):
        __slots__ = ('__dict__',)

    op = Container()
    file = open(filepath, 'r')

    for line in file.readlines()[3::]:
        exec(line, globals(), locals())

    kwargs = op.__dict__

    if bpy.context.scene.exportType == 'FBX': #FBX
        kwargs["filepath"] = saveLoc.replace('.fbx','') + ".fbx"
        print(f"Final FBX export path: '{kwargs['filepath']}'")
        print(f"Calling bpy.ops.export_scene.fbx()...")
        bpy.ops.export_scene.fbx(**kwargs)
        print(f"FBX export completed!")

    elif bpy.context.scene.exportType == 'STL':
        kwargs["filepath"] = saveLoc.replace('.stl','') + ".stl"
        print(f"Final STL export path: '{kwargs['filepath']}'")
        print(f"Calling bpy.ops.export_mesh.stl()...")
        bpy.ops.export_mesh.stl(**kwargs)
        print(f"STL export completed!")

    elif bpy.context.scene.exportType == 'OBJ': #OBJ
        kwargs["filepath"] = saveLoc.replace('.obj','') + ".obj"
        print(f"Final OBJ export path: '{kwargs['filepath']}'")
        print(f"Calling bpy.ops.wm.obj_export()...")
        bpy.ops.wm.obj_export(**kwargs)
        print(f"OBJ export completed!")

    # Experimental 
    if bpy.context.scene.experimentalOptions and bpy.context.scene.exportType == 'FBX':
        print("Experimental Bridging.")
        if bpy.context.scene.remoteFBXConnect == 'Maya':
            print("Bridge: Maya")
            toSendPath = kwargs["filepath"].replace("\\", "\\\\")

            # mayaFbxImport() is a custom function that resides in a Maya plugin, that when called will import the FBX.
            # Experimental export bridge to Maya via sockets
            # THIS NEEDS TO BE ADDED TO MAYA!!! THIS IS JUST AN EXAMPLE
            # You need the following code in maya as a plugin or ran in the console:
            '''
            import socket
            import threading
            import traceback

            def handle_client(client_socket, addr):
                try:
                    command = client_socket.recv(1024).decode('utf-8')

                    try:
                        # Execute the received command
                        exec(command)
                        print(f"Executing: {command}")
                    except Exception as e:
                        # Send back any errors
                        client_socket.sendall(str(e).encode('utf-8'))
                    else:
                        # Or confirm successful execution
                        client_socket.sendall("Command executed successfully.".encode('utf-8'))

                finally:
                    client_socket.close()

            def start_server():
                server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server_socket.bind(('127.0.0.1', 12345))
                server_socket.listen()

                print("Server is listening...")

                try:
                    while True:
                        client_socket, addr = server_socket.accept()
                        print(f"Connection from {addr} has been established.")

                        client_thread = threading.Thread(target=handle_client, args=(client_socket, addr))
                        client_thread.start()

                except KeyboardInterrupt:
                    print("\nServer shutting down.")
                except Exception as e:
                    print(f"Error: {e}")
                    traceback.print_exc()

                finally:
                    server_socket.close()

            def run_server():
                server_thread = threading.Thread(target=start_server)
                server_thread.start()

            def mayaFbxImport(path):
                utils.executeDeferred(lambda: cmds.file(path, i=True, type="FBX", options="fbx"))

            if __name__ == "__main__":
                run_server()
            '''

            DarrowSendMayaCommand(f"mayaFbxImport(\"{toSendPath}\")")

        if bpy.context.scene.remoteFBXConnect == 'Custom':
            print("Bridge: Custom")
            toSendPath = kwargs["filepath"].replace("\\", "\\\\")
            # Make sure you set up your custom client socket code in that DarrowSendCustomSocketCommand function.
            # Also ensure you edit the function argument to contain the properly sent function call
            DarrowSendCustomSocketCommand(f"customFbxImport(\"{toSendPath}\")")

def register():
    bpy.types.Scene.namingOptions = bpy.props.EnumProperty(
            items=[
            (("OP1", "Active Collection", "File name will be the **active** collection")), 
            (("OP2", "Active Object", "File name will be the **active** object")),
            (("OP3", "Prompt User", "File name will be prompted at export")), 
            (("OP4", "Common Parent", "File name will be the immediate common parent of selected objects")), 
            ],
            default='OP2',
            name="Export Naming Options",
            description = "How the exporter should name the output files.",
        )
        
    bpy.types.Scene.darrowVectors = DarrowStoredVectorList()

    bpy.types.Scene.darrowBooleans = DarrowStoredMoveList()

    bpy.types.Scene.objStoredLocation = bpy.props.StringProperty()

    bpy.types.Scene.setupExportPath = bpy.props.StringProperty()

    bpy.types.Scene.exportedObjectName = bpy.props.StringProperty()

    bpy.types.Scene.DarrowPopup_text = bpy.props.StringProperty()

    bpy.types.Scene.start_time = bpy.props.FloatProperty()

    bpy.types.Scene.end_time = bpy.props.FloatProperty()

    bpy.types.Scene.skipRenderDisabled = bpy.props.BoolProperty(
        name="Skip Render Disabled",
        description="Skip objects that are hidden in render (hide_render=True) during export",
        default=False
    )

def unregister():
    print("Nothing to unregister")