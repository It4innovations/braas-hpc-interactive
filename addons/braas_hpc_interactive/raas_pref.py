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
                
                for p in braas_hpc.raas_pref.preferences().cluster_presets:
                    if p.cluster_name == cl[0] and p.is_enabled and preferences().raas_interactive_scripts_installed == False:
                        
                        # Install scripts
                        self.report({'INFO'}, "Install scripts on '%s'" % (cl[0]))
                        #cmd = raas_config.GetGitAddonCommand(preferences().raas_scripts_repository, preferences().raas_scripts_repository_branch)
                        cmd = context.scene.raas_config_functions.call_get_git_addon_command_interactive(preferences().raas_interactive_scripts_repository, preferences().raas_interactive_scripts_repository_branch)
                        if len(cmd) > 0:
                            #server = raas_config.GetServerFromType(cl[0])
                            server = context.scene.raas_config_functions.call_get_server_from_type(cl[0])
                            braas_hpc.raas_connection.ssh_command_sync(server, cmd, p)

                        if len(preferences().raas_interactive_blenderphi_link) > 0:
                            # Install BlenderPhi
                            self.report({'INFO'}, "Install BlenderPhi on '%s'" % (cl[0]))
                            cmd = context.scene.raas_config_functions.call_get_blenderphi_install_command(p, preferences().raas_interactive_blenderphi_link)
                            if len(cmd) > 0:
                                #server = raas_config.GetServerFromType(cl[0])
                                server = context.scene.raas_config_functions.call_get_server_from_type(cl[0])
                                braas_hpc.raas_connection.ssh_command_sync(server, cmd, p)

                            #preferences().raas_blender_installed = True

                        preferences().raas_interactive_scripts_installed = True

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

    raas_interactive_scripts_repository: StringProperty(
        name='Repository',
        default='https://github.com/It4innovations/braas-hpc-interactive.git'
    ) # type: ignore

    raas_interactive_scripts_repository_branch: StringProperty(
        name='Branch',
        default='main'
    ) # type: ignore

    raas_interactive_blenderphi_link: StringProperty(
        name='Link',
        default='https://ftp.nluug.nl/pub/graphics/blender/release/Blender4.5/blender-4.5.5-linux-x64.tar.xz'
    ) # type: ignore    

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.label(text='Install scripts:')
        rep_split = box.split(**factor(0.25), align=True)
        rep_split.label(text='Git Repository (Scripts):')
        rep_box1 = rep_split.row(align=True)
        rep_box = rep_box1.row(align=True)
        # rep_box.enabled = False
        rep_box.prop(self, 'raas_interactive_scripts_repository', text='')
        rep_box = rep_box1.row(align=True)
        # rep_box.enabled = True
        rep_box.prop(self, 'raas_interactive_scripts_repository_branch', text='')
        # box = layout.box()

        rep_split = box.split(**factor(0.25), align=True)
        rep_split.label(text='Link (BlenderPhi):')
        rep_box1 = rep_split.row(align=True)
        rep_box = rep_box1.row(align=True)
        rep_box.prop(self, 'raas_interactive_blenderphi_link', text='')

        rep_split = box.split(**factor(0.25), align=True)
        rep_split.label(text='Manual Installation / Scripts allready installed:')
        rep_box1 = rep_split.row(align=True)
        rep_box = rep_box1.row(align=True)
        rep_box.prop(self, 'raas_interactive_scripts_installed', text='')

        if self.raas_interactive_scripts_installed == False: # or self.raas_blender_installed == False:
            if not self.raas_interactive_scripts_installed:
                box.label(text='Scripts are not installed', icon='ERROR')

            box.operator(RAASINTERACTIVE_OT_install_scripts.bl_idname,
                            icon="CONSOLE", text="Install scripts on the cluster(s)")
        else:
            box.operator(RAASINTERACTIVE_OT_install_scripts.bl_idname,
                            icon="CONSOLE", text="Update scripts on the cluster(s)")        

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
    bpy.utils.register_class(RaasInteractivePreferences)

    return

def unregister():
    """unregister."""

    bpy.utils.unregister_class(RAASINTERACTIVE_OT_install_scripts)
    bpy.utils.unregister_class(RaasInteractivePreferences)

    return
