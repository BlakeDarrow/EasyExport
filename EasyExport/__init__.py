#-----------------------------------------------------#  
#     Plugin information     
#-----------------------------------------------------#  
from bpy.types import Operator, AddonPreferences
from bpy.props import StringProperty, IntProperty, BoolProperty, FloatProperty, EnumProperty
bl_info = {
    "name": "Easy Export",
    "author": "Blake Darrow",
    "version": (1, 0, 6),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > Darrow Toolkit",
    "description": "Easy FBX exporting and external mesh libraries",
    "category": "Tools",
    "wiki_url": "https://docs.darrow.tools/en/latest/index.html",
    }
    
#-----------------------------------------------------#  
#     imports    
#-----------------------------------------------------#  
import bpy
from . import addon_updater_ops
import sys
import importlib
if __package__ != "easy_export":
    sys.modules["easy_export"] = sys.modules[__package__]

modulesNames = ['EasyExport',]


@addon_updater_ops.make_annotations
class DarrowAddonPreferences(AddonPreferences):
    bl_idname = __package__

    auto_check_update: BoolProperty(
         name="Auto-check for Update",
         description="If enabled, auto-check for updates using an interval",
         default=True,
     )

    updater_intrval_months: IntProperty(
         name='Months',
         description="Number of months between checking for updates",
         default=3,
         min=0
     )
    updater_intrval_days: IntProperty(
         name='Days',
         description="Number of days between checking for updates",
         default=0,
         min=0,
     )
    updater_intrval_hours: IntProperty(
         name='Hours',
         description="Number of hours between checking for updates",
         default=0,
         min=0,
         max=23
    )
    updater_intrval_minutes: IntProperty(
         name='Minutes',
         description="Number of minutes between checking for updates",
         default=0,
         min=0,
         max=59
     )

    export_moduleBool: BoolProperty(
         name="FBX Exporter",
         default=True
     )

    library_moduleBool: BoolProperty(
        name="Mesh Library",
        default=True
    )

    userDefinedExportPath : StringProperty(
        name="Path",
        default="",
        subtype='DIR_PATH',
    )

    advancedExportBool: BoolProperty(
        name="Advanced",
        description="Show advanced options",
        default=False
    )

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.label(text="Default Module Properties")
        box.alignment = 'RIGHT'
        split = box.split(factor=0.7)
        box.scale_y = 1.1
        col1 = split.column(align=True)
        col1.prop(self,'userDefinedExportPath', text="Default Path")

        addon_updater_ops.update_settings_ui(self, context)

#-----------------------------------------------------#  
#     create a dictonary for module names    
#-----------------------------------------------------# 
modulesFullNames = {}
for currentModuleName in modulesNames:
    modulesFullNames[currentModuleName] = ('{}.{}'.format(__name__, currentModuleName))

#-----------------------------------------------------#  
#     import new modules to addon using full name from above    
#-----------------------------------------------------# 
for currentModuleFullName in modulesFullNames.values():
    if currentModuleFullName in sys.modules:
        importlib.reload(sys.modules[currentModuleFullName])
    else:
        globals()[currentModuleFullName] = importlib.import_module(currentModuleFullName)
        setattr(globals()[currentModuleFullName], 'modulesNames', modulesFullNames)

#-----------------------------------------------------#  
#     register the modules    
#-----------------------------------------------------# 
classes = (DarrowAddonPreferences,)

def register():
    addon_updater_ops.register(bl_info)
    for cls in classes:
        bpy.utils.register_class(cls)
        
    for currentModuleName in modulesFullNames.values():
        if currentModuleName in sys.modules:
            if hasattr(sys.modules[currentModuleName], 'register'):
                sys.modules[currentModuleName].register()

#-----------------------------------------------------#  
#     unregister the modules    
#-----------------------------------------------------# 
def unregister():
    addon_updater_ops.unregister()
    for cls in classes:
        bpy.utils.unregister_class(cls)

    for currentModuleName in modulesFullNames.values():
        if currentModuleName in sys.modules:
            if hasattr(sys.modules[currentModuleName], 'unregister'):
                sys.modules[currentModuleName].unregister()

if __name__ == "__main__":
    register()