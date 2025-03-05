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
    "version": (1, 2, 26),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > DarrowTools",
    "description": "Easy FBX and OBJ exporting including a batch exporter. Shortcut 'E'",
    "category": "Tools",
    "doc_url": "https://darrow.tools/EasyExport",
    }
    
from .ui import panels
import bpy
from bpy.props import *
from bpy.types import AddonPreferences
import sys

from .ops import export_ops
from .ui import panels
from .utils import common
from .utils import export_funcs

if __package__ != "easy_export":
    sys.modules["easy_export"] = sys.modules[__package__]

modules = (export_ops, panels, common, export_funcs)

def register():
    for mod in modules:
        mod.register()

def unregister():
    for mod in modules:
        mod.unregister()
