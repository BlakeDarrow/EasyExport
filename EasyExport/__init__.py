from bpy.types import AddonPreferences
from bpy.props import IntProperty, BoolProperty

bl_info = {
    "name": "Easy Export",
    "author": "Blake Darrow",
    "version": (1, 2, 3),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > DarrowTools",
    "description": "Easy FBX exporting including a batch exporter",
    "category": "Tools",
    "doc_url": "https://darrow.tools/EasyExport",
    }
    
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
    anyWarningsMet : BoolProperty(
        name="Warning Conditions Met",
        description="",
        default=False
    )
    advancedExportBool: BoolProperty(
        name="Advanced",
        description="Show advanced options",
        default=False
    )

    def draw(self, context):
        addon_updater_ops.update_settings_ui(self, context)

modulesFullNames = {}
for currentModuleName in modulesNames:
    modulesFullNames[currentModuleName] = ('{}.{}'.format(__name__, currentModuleName))

for currentModuleFullName in modulesFullNames.values():
    if currentModuleFullName in sys.modules:
        importlib.reload(sys.modules[currentModuleFullName])
    else:
        globals()[currentModuleFullName] = importlib.import_module(currentModuleFullName)
        setattr(globals()[currentModuleFullName], 'modulesNames', modulesFullNames)

classes = (DarrowAddonPreferences,)

def register():
    addon_updater_ops.register(bl_info)
    for cls in classes:
        bpy.utils.register_class(cls)
        
    for currentModuleName in modulesFullNames.values():
        if currentModuleName in sys.modules:
            if hasattr(sys.modules[currentModuleName], 'register'):
                sys.modules[currentModuleName].register()

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