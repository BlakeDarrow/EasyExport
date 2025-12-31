import bpy
import os

"""Have to store a reference for python so blender UI enum wont freak out"""
items = []
count = -1
file = ""
ext = ".py"

class ExportPresetOperator(bpy.types.Operator):
    bl_idname = "export.preset_operator"
    bl_label = "Export Preset Operator"

    def update(self, context):
        bpy.context.scene.blenderExportPresets = 'OP1'

        return

    def get_export_presets(self, context):
        user_path = bpy.utils.resource_path('USER')
        blender_version = bpy.app.version
        if bpy.context.scene.exportType == 'FBX':
            path = os.path.join(user_path, "scripts/presets/operator/export_scene.fbx/")
        elif bpy.context.scene.exportType == 'OBJ':

            if int(blender_version[0]) >= 4:
                path = os.path.join(user_path, "scripts/presets/operator/wm.obj_export/")
            elif int(blender_version[0]) <= 4:
                path = os.path.join(user_path, "scripts/presets/operator/export_scene.obj/")
            else:
                path = os.path.join(user_path, "scripts/presets/operator/export_scene.obj/")
        elif bpy.context.scene.exportType == 'STL':
            path = os.path.join(user_path, "scripts/presets/operator/export_scene.stl/")

        count = 1
        items.clear()

        if not items.__contains__(("OP1", "Default", "Darrow Default Export")):
            items.append(("OP1", "Default", "Darrow Default Export"))
            items.append(None)

        if os.path.exists(path):
            for file in os.listdir(path):
                if file[-len(ext):] == ext:
                    name = file.replace(".py", "")
                    if not items.__contains__(("OP" + str(count), name, "User Preset")):
                        items.append((name, name, "User Preset"))
        else:
            os.makedirs(path)

        return items


def DarrowGetCommonParent():
    """Find the immediate (closest) common parent of all selected objects.
    Checks both object parent relationships and collection hierarchies.
    Returns the parent name if found, None otherwise."""
    selected_objs = bpy.context.selected_objects
    
    if len(selected_objs) == 0:
        return None
    
    # Try 1: Check for common object parent
    ancestor_sets = []
    for obj in selected_objs:
        ancestors = []
        current = obj.parent
        while current is not None:
            ancestors.append(current)
            current = current.parent
        ancestor_sets.append(set(ancestors))
    
    # Find common object ancestors
    if len(ancestor_sets) > 0:
        common_ancestors = ancestor_sets[0]
        for ancestor_set in ancestor_sets[1:]:
            common_ancestors = common_ancestors.intersection(ancestor_set)
        
        if len(common_ancestors) > 0:
            # Find the immediate (lowest-level) common parent object
            immediate_parent = None
            max_depth = -1
            
            for ancestor in common_ancestors:
                depth = 0
                current = ancestor.parent
                while current is not None:
                    depth += 1
                    current = current.parent
                
                if depth > max_depth:
                    max_depth = depth
                    immediate_parent = ancestor
            
            if immediate_parent:
                return immediate_parent.name
    
    # Try 2: Check for common parent collection
    def get_collection_ancestors(collection):
        """Get all parent collections for a given collection."""
        ancestors = []
        # Search through all collections to find parents
        for coll in bpy.data.collections:
            if collection.name in [child.name for child in coll.children]:
                ancestors.append(coll)
                ancestors.extend(get_collection_ancestors(coll))
        return ancestors
    
    # Get all collections for each selected object
    collection_ancestor_sets = []
    for obj in selected_objs:
        obj_collections = set()
        # Add all collections this object belongs to
        for coll in obj.users_collection:
            obj_collections.add(coll)
            # Add all parent collections
            obj_collections.update(get_collection_ancestors(coll))
        collection_ancestor_sets.append(obj_collections)
    
    # Find common collection ancestors
    if len(collection_ancestor_sets) > 0:
        common_collections = collection_ancestor_sets[0]
        for coll_set in collection_ancestor_sets[1:]:
            common_collections = common_collections.intersection(coll_set)
        
        if len(common_collections) > 0:
            # Find the immediate (lowest-level) common parent collection
            immediate_collection = None
            max_depth = -1
            
            for coll in common_collections:
                depth = len(get_collection_ancestors(coll))
                if depth > max_depth:
                    max_depth = depth
                    immediate_collection = coll
            
            if immediate_collection:
                return immediate_collection.name
    
    return None


def register():
    bpy.utils.register_class(ExportPresetOperator)

def unregister():
    bpy.utils.unregister_class(ExportPresetOperator)

if __name__ == "__main__":
    register()
