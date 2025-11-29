# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# (c) IT4Innovations, VSB-TUO

import importlib
import sys
import subprocess
from collections import namedtuple
import functools
import logging
import os.path
import tempfile

import datetime
import typing

import bpy
from bpy.types import AddonPreferences, Operator, WindowManager, Scene, PropertyGroup
from bpy.props import StringProperty, EnumProperty, PointerProperty, BoolProperty, IntProperty
import rna_prop_ui

import braas_hpc
##################################################

ADDON_NAME = 'braas_hpc_interactive'

log = logging.getLogger(__name__)


@functools.lru_cache()
def factor(factor: float) -> dict:
    """Construct keyword argument for UILayout.split().

    On Blender 2.8 this returns {'factor': factor}, and on earlier Blenders it returns
    {'percentage': factor}.
    """
    if bpy.app.version < (2, 80, 0):
        return {'percentage': factor}
    return {'factor': factor}

################################################################

class RAASINTERACTIVE_OT_install_scripts(Operator):
    bl_idname = 'raas_interactive.install_scripts'
    bl_label = 'Install scripts on the cluster'
    bl_description = ("Install scripts")

    def execute(self, context):
        for cl in braas_hpc.raas_config.Cluster_items:
            try:
                #presets_tuples = [(p.cluster_name, p.is_enabled) for p in preferences().cluster_presets] 

                for p in preferences().cluster_presets:
                    if p.cluster_name == cl[0] and p.is_enabled and preferences().raas_scripts_installed == False:
                        # TODO: MJ: check if scripts are already installed?
                        preferences().raas_scripts_installed = True

                        break

            except Exception as e:
                import traceback
                traceback.print_exc()

                self.report({'ERROR'}, "Problem with %s: %s: %s" %
                            (self.bl_label, e.__class__, e))
                self.report({'ERROR'}, "Scripts could not be installed.")
                return {"CANCELLED"}

        self.report({'INFO'}, "'%s' finished" % (self.bl_label))
        return {"FINISHED"} 

##################################################################           
    
class RaasInteractivePreferences(AddonPreferences):
    bl_idname = ADDON_NAME

    raas_interactive_scripts_installed: BoolProperty(
        default=False
    ) # type: ignore    

    def draw(self, context):
        layout = self.layout

        box = layout.box()

        rep_split = box.split(**factor(0.25), align=True)
        rep_split.label(text='Manual Installation / Scripts allready installed:')
        rep_box1 = rep_split.row(align=True)
        rep_box = rep_box1.row(align=True)
        rep_box.prop(self, 'raas_interactive_scripts_installed', text='')

def ctx_preferences():
    """Returns bpy.context.preferences in a 2.79-compatible way."""
    try:
        return bpy.context.preferences
    except AttributeError:
        return bpy.context.user_preferences


def preferences() -> RaasInteractivePreferences:
    return ctx_preferences().addons[ADDON_NAME].preferences

def register():
    """register."""

    bpy.utils.register_class(RAASINTERACTIVE_OT_install_scripts)

    return

def unregister():
    """unregister."""

    bpy.utils.unregister_class(RAASINTERACTIVE_OT_install_scripts)

    return
