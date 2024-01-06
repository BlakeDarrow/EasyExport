# ##### BEGIN GPL LICENSE BLOCK #####
#
#   Copyright (C) 2020 - 2024  Blake Darrow <contact@blakedarrow.com>
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

bl_info = {
    "name": "Easy Export",
    "author": "Blake Darrow",
    "version": (1, 2, 17),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > DarrowTools",
    "description": "Easy FBX exporting including a batch exporter. Shortcut 'E'",
    "category": "Tools",
    "doc_url": "https://darrow.tools/EasyExport",
    }
    
from .ui import panels
import bpy
from bpy.props import *
from bpy.types import AddonPreferences
from . import addon_updater_ops
import sys

from .ops import export_ops
from .ui import panels
from .utils import common
from .utils import export_funcs

if __package__ != "easy_export":
    sys.modules["easy_export"] = sys.modules[__package__]


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
        self.layout.label(text="E will bring up the viewport pie menu.")
        addon_updater_ops.update_settings_ui(self, context)

classes = (DarrowAddonPreferences,)

modules = (export_ops, panels, common, export_funcs)

def register():
    addon_updater_ops.register(bl_info)

    for cls in classes:
        bpy.utils.register_class(cls)

    for mod in modules:
        mod.register()

def unregister():
    addon_updater_ops.unregister()
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    for mod in modules:
        mod.unregister()
