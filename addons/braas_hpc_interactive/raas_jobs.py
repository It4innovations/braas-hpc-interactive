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

import functools
import logging
import tempfile
import os
from pathlib import Path, PurePath
import typing
import json

################################
import time
################################

import bpy
from bpy.types import AddonPreferences, Operator, WindowManager, Scene, PropertyGroup, Panel
from bpy.props import StringProperty, EnumProperty, PointerProperty, BoolProperty, IntProperty

from bpy.types import Header, Menu

import pathlib
import json

import time

################################

from . import raas_pref
from . import raas_config
from . import raas_connection

import braas_hpc

################################
log = logging.getLogger(__name__)
################################
def CmdCreatePBSJob(context):
    cmd = ''
    node = ''
    jobid = ''
    server_port = 7000

    print(cmd)
    return cmd, node, jobid, server_port

def CmdCreateSLURMJob(context):
    cmd = ''

    idx = context.scene.raas_list_jobs_index

    if idx == -1:
        raise Exception('No job selected.')

    item = context.scene.raas_list_jobs[idx]    

    #node = context.scene.raas_session.ssh_tunnel_proc.remote_host
    # local_storage_interactive = raas_connection.get_job_local_storage(item.Name) / 'interactive' / 'hostname.txt'
    local_storage_interactive = braas_hpc.raas_connection.get_job_local_storage(item.Name) / 'interactive'
    # Read hostname from file
    hostname_file = local_storage_interactive / 'hostname.txt'
    with open(hostname_file, 'r') as f:
        hostname = f.read().strip()
    node = hostname.split('.')[0]  # Get just the node name

    jobid_file = local_storage_interactive / 'jobid.txt'
    with open(jobid_file, 'r') as f:
        jobid = f.read().strip()

    remote_storage_interactive = str(braas_hpc.raas_connection.convert_path_to_linux(item.Name))
    sharedBasepath = f'{braas_hpc.raas_connection.get_direct_access_remote_storage(context)}/{remote_storage_interactive}/interactive'

    da_interactive_script = context.scene.raas_config_functions.call_get_da_interactive_script(context)
    pid_name, pid_queue, pid_dir = context.scene.raas_config_functions.call_get_current_pid_info(context, braas_hpc.raas_pref.preferences())

    custom_flags = ''
    if 'gpu' in pid_queue and context.scene.raas_blender_job_info_new.cluster_type == 'KAROLINA':
        custom_flags += '--gres=gpu:1'  # fixed number of GPUs

    server_port = 7000
    try:
        server_port = int(context.scene.braas_hpc_renderengine.server_settings.braas_hpc_renderengine_port)
    except Exception:
        pass

    if context.scene.raas_config_functions.call_get_da_support_ssh_proxy_jump(context):
        cmd = f"cd {sharedBasepath}; {da_interactive_script} {server_port}"
    else:
        cmd = f"cd {sharedBasepath}; srun --overlap -n 1 --jobid={jobid} {custom_flags} {da_interactive_script} {server_port}"

    print(cmd)
    return cmd, node, jobid, server_port

def CmdCreateJob(context):
    scheduler = context.scene.raas_config_functions.call_get_scheduler_from_context(context)

    if scheduler == 'SLURM':
        return CmdCreateSLURMJob(context)
    elif scheduler == 'PBS':
        return CmdCreatePBSJob(context)
    else:
        raise ValueError("Unknown scheduler type: {}".format(scheduler))

################################