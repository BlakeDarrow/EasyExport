import bpy
import os

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

def register():
    print()

def unregister():
    print()
