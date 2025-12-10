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
import asyncio

################################
import time
################################

import bpy
from bpy.types import AddonPreferences, Operator, WindowManager, Scene, PropertyGroup, Panel
from bpy.props import StringProperty, EnumProperty, PointerProperty, BoolProperty, IntProperty

from bpy.types import Header, Menu

from . import raas_pref
from . import raas_config
from . import raas_connection
from . import raas_jobs

import braas_hpc

log = logging.getLogger(__name__)

################################
# class RAASINTERACTIVE_PT_simplify(braas_hpc.raas_render.RAAS_PT_simplify, Panel):
#     bl_label = "BRaaS-HPC-Interactive"
#     bl_options = {'DEFAULT_CLOSED'}

##################################################################################
class RAASINTERACTIVE_OT_run_interactive_command(
                        braas_hpc.async_loop.AsyncModalOperatorMixin,
                        braas_hpc.raas_render.AuthenticatedRaasOperatorMixin,                         
                        Operator):
    """run_interactive_command"""
    bl_idname = 'raas_interactive.run_interactive_command'
    bl_label = 'Run Interactive Command'

    log = logging.getLogger('%s.RAASINTERACTIVE_OT_run_interactive_command' % __name__)

    async def async_execute(self, context):  
        try:
            #update_job_info_preset(context)

            if not await self.authenticate(context):
                self.quit()
                return            

            prefs = braas_hpc.raas_pref.preferences()

            idx = context.scene.raas_list_jobs_index

            if idx == -1:
                self.report({'ERROR'}, 'No job selected.')
                context.window_manager.raas_status = "ERROR"
                context.window_manager.raas_status_txt = "There is an error! Check Info Editor!"

                self.quit()
                return

            item = context.scene.raas_list_jobs[idx]

            raas_interactive_type = context.scene.raas_interactive_type

            ##########################Download#####################################
            fileTransfer = await braas_hpc.raas_connection.start_transfer_files(context, item.Id, self.token)
                
            remote_storage_interactive = braas_hpc.raas_connection.convert_path_to_linux(item.Name) + '/interactive'
            local_storage_interactive = braas_hpc.raas_connection.get_job_local_storage(item.Name)

            await braas_hpc.raas_connection.transfer_files_from_cluster(context, fileTransfer, remote_storage_interactive, str(local_storage_interactive), item.Id, self.token)            
            ###############################################################

            # command_file_name = 'command.sh'
            if raas_interactive_type == 'PYNARI':
                command_file_name = 'command.py'                

                remote_storage_interactive = str(braas_hpc.raas_connection.convert_path_to_linux(item.Name))
                local_storage_interactive = braas_hpc.raas_connection.get_job_local_storage(item.Name) / 'interactive'

                #local_storage_interactive = str(raas_connection.get_job_local_storage_interactive(blender_job_info_new.job_name))
                text_content = context.scene.raas_interactive_command.as_string()

                self.report({'INFO'}, f'Writing command \"{context.scene.raas_interactive_command.name}\" to \"{local_storage_interactive}/{command_file_name}\".')
                
                # Write to file
                file_path = str(local_storage_interactive / command_file_name)  # or your desired path
                with open(file_path, 'w') as f:
                    f.write(text_content)

                #remote_storage_interactive = raas_connection.convert_path_to_linux(raas_connection.get_job_remote_storage_interactive(blender_job_info_new.job_name))

                # submitted_job_info_ext_new = context.scene.raas_submitted_job_info_ext_new

                # fileTransfer = await braas_hpc.raas_connection.start_transfer_files(context, submitted_job_info_ext_new.Id, self.token)
                await braas_hpc.raas_connection.transfer_files_to_cluster(context, fileTransfer, str(local_storage_interactive), remote_storage_interactive, item.Id, self.token)
                await braas_hpc.raas_connection.end_transfer_files(context, fileTransfer, item.Id, self.token)

            else:
                await braas_hpc.raas_connection.end_transfer_files(context, fileTransfer, item.Id, self.token)

            #prefs = raas_pref.preferences()
            preset = prefs.cluster_presets[context.scene.raas_cluster_presets_index]
           
            # serverHostname = raas_config.GetDAServer(context)
            serverHostname = context.scene.raas_config_functions.call_get_da_server(context)       
            
            #cmd = raas_jobs.CmdCreateJob(context)
            #cmd = f'{raas_config.GetDAInteractiveScript(context)} {remote_storage_interactive}/{command_file_name} > {remote_storage_interactive}/command.log 2> {remote_storage_interactive}/command.err &'

            cmd, node, jobid, server_port = raas_jobs.CmdCreateJob(context)

            #await raas_connection.ssh_command_jump(server, node, cmd, preset)
            # prefs = raas_pref.preferences()
            # preset = prefs.cluster_presets[context.scene.raas_cluster_presets_index]

            #serverHostname = raas_config.GetDAServer(context) 
            
            # username = preset.raas_da_username
            key_file = preset.raas_private_key_path
            destination = serverHostname #f"{username}@{serverHostname}"

            #create_ssh_command_jump(self, key_file, jump_host, destination, command)
            local_port = server_port
            remote_port = server_port

            # if hasattr(context.scene, "braas_hpc_renderengine"):
            #     server_settings = context.scene.braas_hpc_renderengine.server_settings
            #     local_port = server_settings.braas_hpc_renderengine_port                
            #     remote_port = server_settings.braas_hpc_renderengine_port

            #TODO: MJ !!!
            # if raas_config.GetDASupportSSHProxyJump(context):
            # if context.scene.raas_config_functions.call_get_da_support_ssh_proxy_jump(context):
            #     context.scene.raas_session.create_ssh_command_jump(key_file, destination, node, local_port, remote_port, cmd)
            # else:
            context.scene.raas_session.create_ssh_command(key_file, destination, local_port, node, remote_port, cmd)

            # item = context.scene.raas_submitted_job_info_ext_new
            # asyncio.gather(ListSchedulerJobsForCurrentUser(context, self.token))
            
            # await asyncio.gather(SubmitJob(context, self.token))
            
            # await ListSchedulerJobsForCurrentUser(context, self.token)
            # 
            self.report({'INFO'}, f'Command submitted to interactive session on node {node}.')

        except Exception as e:
            import traceback
            traceback.print_exc()

            self.report({'ERROR'}, "Problem with run interactive command: %s: %s" % (e.__class__, e))
            context.window_manager.raas_status = "ERROR"
            context.window_manager.raas_status_txt = "There is an error! Check Info Editor!"

        self.quit()     

class RAASINTERACTIVE_OT_stop_interactive_command(
                        braas_hpc.async_loop.AsyncModalOperatorMixin,
                        braas_hpc.raas_render.AuthenticatedRaasOperatorMixin,                         
                        Operator):
    """stop_interactive_command"""
    bl_idname = 'raas_interactive.stop_interactive_command'
    bl_label = 'Stop Interactive Command'

    #stop_upon_exception = True
    log = logging.getLogger('%s.RAAS_OT_stop_interactive_command' % __name__)

    async def async_execute(self, context):

        if not await self.authenticate(context):
            self.quit()
            return

        try:
            #TODO: MJ !!!
            # if raas_config.GetDASupportSSHProxyJump(context):
            # if context.scene.raas_config_functions.call_get_da_support_ssh_proxy_jump(context):
            #     context.scene.raas_session.close_ssh_command_jump() 
            # else:
            context.scene.raas_session.close_ssh_command()

        except Exception as e:
            #print('Problem with downloading files:')
            #print(e)
            import traceback
            traceback.print_exc()

            self.report({'ERROR'}, "Problem with closing process for ssh command: %s: %s" % (e.__class__, e))
            context.window_manager.raas_status = "ERROR"
            context.window_manager.raas_status_txt = "There is an error! Check Info Editor!"


        self.quit()


class RAASINTERACTIVE_OT_submit_job(
                        braas_hpc.async_loop.AsyncModalOperatorMixin,
                        braas_hpc.raas_render.AuthenticatedRaasOperatorMixin,                         
                        Operator):
    """submit_job"""
    bl_idname = 'raas_interactive.submit_job'
    bl_label = 'Submit job'

    #stop_upon_exception = True
    log = logging.getLogger('%s.RAASINTERACTIVE_OT_submit_job' % __name__)

    # quit_after_submit = BoolProperty()

    async def async_execute(self, context):  
        try:
            braas_hpc.raas_render.update_job_info_preset(context)

            if not await self.authenticate(context):
                self.quit()
                return         

            #scene = context.scene
            raas_interactive_type = context.scene.raas_interactive_type
            prefs = braas_hpc.raas_pref.preferences()

            if prefs.cluster_presets[context.scene.raas_cluster_presets_index].is_enabled == False:
                self.report({'ERROR'}, 'Selected configuration is not active.')
                context.window_manager.raas_status = "ERROR"
                context.window_manager.raas_status_txt = "There is an error! Check Info Editor!"

                self.quit()
                return

            # Check the configuration was selected
            if context.scene.raas_blender_job_info_new.cluster_type == "" or \
                context.scene.raas_blender_job_info_new.job_partition == "" or \
                    context.scene.raas_blender_job_info_new.job_allocation == "":                
                self.report({'ERROR'}, 'Select a configuration (cluster, partition, allocation).')
                context.window_manager.raas_status = "ERROR"
                context.window_manager.raas_status_txt = "There is an error! Check Info Editor!"

                self.quit()
                return

            # Check or create a project name (task)
            if context.scene.raas_blender_job_info_new.job_project is None or \
                len(context.scene.raas_blender_job_info_new.job_project) == 0:
                context.scene.raas_blender_job_info_new.job_project = Path(context.blend_data.filepath).stem

            context.scene.raas_blender_job_info_new.job_project = context.scene.raas_blender_job_info_new.job_project.replace(" ","_").replace("\\","_").replace("/","_").replace("'","_").replace('"','_')

            # Name directories
            from datetime import datetime
            dt = datetime.now().isoformat('-').replace(':', '').replace('.', '')
            unique_dir = '%s-%s' % (dt[0:19], context.scene.raas_blender_job_info_new.job_project)
            outdir = Path(prefs.raas_job_storage_path) / unique_dir / 'in'
            outdir.mkdir(parents=True)

            # missing_sources = None

            engine_old = context.scene.render.engine
            context.scene.render.engine = 'CYCLES'
            
            # Prepare blend file
            if raas_interactive_type == 'BLENDERPHI':
                if context.scene.raas_blender_job_info_new.file_type == 'DEFAULT':
                    # Save to a different file, specifically for Raas.
                    context.window_manager.raas_status = 'SAVING'
                    filepath = await braas_hpc.raas_render.submit_job_save_blendfile(context, outdir)
                    context.scene.raas_blender_job_info_new.blendfile = filepath.name

                else: #OTHER
                    filepath = Path(raas_connection.get_blendfile_fullpath(context)).with_suffix('.blend')        

                if context.scene.raas_blender_job_info_new.file_type == 'DEFAULT':
                    # BAT-pack the files to the destination directory.
                    missing_sources = await braas_hpc.raas_render.submit_job_bat_pack(filepath, context.scene.raas_blender_job_info_new.job_project, outdir)

                    # remove files
                    self.log.info("Removing temporary file %s", filepath)
                    filepath.unlink()                
                else:                  

                    from distutils.dir_util import copy_tree
                    copy_tree(bpy.path.abspath(context.scene.raas_blender_job_info_new.blendfile_dir), str(outdir))

                outdir_interactive = Path(prefs.raas_job_storage_path) / unique_dir / 'interactive'
                outdir_interactive.mkdir(parents=True)

                # Write to file
                file_path_interactive = str(outdir_interactive / 'blendfile')  # or your desired path
                with open(file_path_interactive, 'w') as f:
                    f.write(f'in/{filepath.name}') # TODO: context.scene.raas_blender_job_info_new.file_type != 'DEFAULT'

            context.scene.render.engine = engine_old

            # Image/animation info
            #context.scene.raas_blender_job_info_new.frame_step = context.scene.frame_step
            context.scene.raas_blender_job_info_new.frame_start = context.scene.frame_start
            context.scene.raas_blender_job_info_new.frame_end = context.scene.frame_end
            context.scene.raas_blender_job_info_new.frame_current = context.scene.frame_current

            context.scene.raas_blender_job_info_new.job_name = unique_dir  

            # Do a final report.
            # if missing_sources:
            #     names = (ms.name for ms in missing_sources)
            #     self.report({'WARNING'}, 'Raas job created with missing files: %s' %
            #                 '; '.join(names
            #                 ))

            # await raas_config.CreateJob(context, self.token)  
            await context.scene.raas_config_functions.call_create_job_interactive(context, self.token)
            
            blender_job_info_new = context.scene.raas_blender_job_info_new

            local_storage_in = str(braas_hpc.raas_connection.get_job_local_storage(blender_job_info_new.job_name))
            remote_storage_in = braas_hpc.raas_connection.convert_path_to_linux(braas_hpc.raas_connection.get_job_remote_storage(blender_job_info_new.job_name))

            submitted_job_info_ext_new = context.scene.raas_submitted_job_info_ext_new

            fileTransfer = await braas_hpc.raas_connection.start_transfer_files(context, submitted_job_info_ext_new.Id, self.token)
            await braas_hpc.raas_connection.transfer_files_to_cluster(context, fileTransfer, local_storage_in, remote_storage_in, submitted_job_info_ext_new.Id, self.token)
            await braas_hpc.raas_connection.end_transfer_files(context, fileTransfer, submitted_job_info_ext_new.Id, self.token)

            item = context.scene.raas_submitted_job_info_ext_new
            asyncio.gather(braas_hpc.raas_render.ListSchedulerJobsForCurrentUser(context, self.token))
            
            await asyncio.gather(braas_hpc.raas_render.SubmitJob(context, self.token))
            
            await braas_hpc.raas_render.ListSchedulerJobsForCurrentUser(context, self.token)

            self.report({'INFO'}, 'Please refresh the list of tasks.')

        except Exception as e:
            import traceback
            traceback.print_exc()

            self.report({'ERROR'}, "Problem with submitting of job: %s: %s" % (e.__class__, e))
            context.window_manager.raas_status = "ERROR"
            context.window_manager.raas_status_txt = "There is an error! Check Info Editor!"

        self.quit()

class RAASINTERACTIVE_PT_ListJobs(braas_hpc.raas_render.RaasButtonsPanel, Panel):
    bl_label = "BRaaS-HPC Interactive"
    bl_parent_id = "RAAS_PT_simplify"

    def draw(self, context):
        layout = self.layout

        if context.window_manager.raas_status in {'IDLE', 'ERROR', 'DONE'}:
            layout.enabled = True
        else:
            layout.enabled = False        

        #header
        # box = layout.box()

        # row = box.row()   

        # col = row.column()        
        # col.label(text="Id")
        # col = row.column()
        # col.label(text="Project")        
        # col = row.column()
        # col.label(text="Cluster")        
        # col = row.column()
        # col.label(text="State")        
        
        # #table
        # row = layout.row()
        # row.template_list("RAAS_UL_SubmittedJobInfoExt", "", context.scene, "raas_list_jobs", context.scene, "raas_list_jobs_index")

        # #button
        # row = layout.row()
        # row.operator(RAAS_OT_ListJobsForCurrentUser.bl_idname, text='Refresh')
        # row.operator(RAAS_OT_CancelJob.bl_idname, text='Cancel')

        # idx = context.scene.raas_list_jobs_index        

        # if idx != -1 and len(context.scene.raas_list_jobs) > 0:

        #     item = context.scene.raas_list_jobs[idx]   
        box = layout.box()
        # box.enabled = False

        # box.label(text=('Job: %d' % item.Id))
        # box.prop(item, "Name")
        # box.prop(item, "Project")
        # box.prop(item, "SubmitTime")
        # box.prop(item, "StartTime")
        # box.prop(item, "EndTime")

        # #row = box.column()            
        # box.prop(item, "State")

        # box = layout.box()

        # local_storage = str(raas_connection.get_job_local_storage(item.Name))
        # paths_layout = box.column(align=True)
        # labeled_row = paths_layout.split(**raas_pref.factor(0.25), align=True)
        # labeled_row.label(text='Storage Path:')
        # prop_btn_row = labeled_row.row(align=True)
        # prop_btn_row.label(text=local_storage)
        # props = prop_btn_row.operator(RAAS_OT_explore_file_path.bl_idname,
        #                             text='', icon='DISK_DRIVE')
        # props.path = local_storage

        col = box.column()
        col.prop(context.scene, "raas_interactive_type")
        col.operator(RAASINTERACTIVE_OT_submit_job.bl_idname, text='Submit Interactive Job')
        # col.operator(RAASINTERACTIVE_OT_download_files.bl_idname, text='Download information')

        # if item.InteractiveMode:                
        # if context.scene.raas_session.ssh_tunnel_proc is None or not context.scene.raas_session.ssh_tunnel_proc.is_running():
        #     row = box.row()
        #     row.operator(RAAS_OT_connect_to_client.bl_idname, text='Connect to Client')
        # else:
        #     row = box.row()
        #     row.operator(RAAS_OT_disconnect_from_client.bl_idname, text='Disconnect from Client')

        # if raas_config.GetDASupportSSHProxyJump(context):
        # if context.scene.raas_config_functions.call_get_da_support_ssh_proxy_jump(context):
        #     show_raas_interactive_command = context.scene.raas_session.ssh_command_jump_proc is None or not context.scene.raas_session.ssh_command_jump_proc.is_running()
        # else:
        show_raas_interactive_command = context.scene.raas_session.ssh_command_proc is None or not context.scene.raas_session.ssh_command_proc.is_running()


        if show_raas_interactive_command:
            col = box.column()
            
            if context.scene.raas_interactive_type == 'PYNARI':
                col.prop(context.scene, "raas_interactive_command")

            col.operator(RAASINTERACTIVE_OT_run_interactive_command.bl_idname, text='Run Interactive Command')
        else:
            row = box.row()
            row.operator(RAASINTERACTIVE_OT_stop_interactive_command.bl_idname, text='Stop Interactive Command')


######################CLEANUP###########################  
@bpy.app.handlers.persistent
def cleanup_on_exit():
    """Cleanup SSH connections and tunnels when Blender exits"""
    try:
        if hasattr(bpy.context.scene, 'raas_interactive_session'):
            session = bpy.context.scene.raas_interactive_session
            if session:
                session.close_ssh_tunnel()
                # session.close_ssh_command()
                # session.close_ssh_command_jump()
                # session.paramiko_close()                

    except Exception as e:
        print(f"Error during cleanup: {e}")

#################################################

# RaasManagerGroup needs to be registered before classes that use it.
_rna_classes = []
_rna_classes.extend(
    cls for cls in locals().values()
    if (isinstance(cls, type)
        and cls.__name__.startswith('RAASINTERACTIVE')
        and cls not in _rna_classes)
)


def register():
    #from ..utils import redraw
    bpy.app.handlers.load_pre.append(cleanup_on_exit)        

    for cls in _rna_classes:
        bpy.utils.register_class(cls)

    scene = bpy.types.Scene
    
    scene.raas_interactive_session = raas_connection.RaasInteractiveSession()

    #################################
    # Delete raas_config_functions
    try:
        del bpy.types.Scene.raas_config_functions
    except AttributeError:
        pass

    scene.raas_config_functions = raas_config.RaasInteractiveConfigFunctions()
    #################################
    scene.raas_interactive_command = bpy.props.PointerProperty(
        type=bpy.types.Text,
        name="Interactive Command",
        description="Selected text object from text editor"
    )

    scene.raas_interactive_type = bpy.props.EnumProperty(
        name='Interactive Type',
        items=raas_config.interactive_type_items
    )

    #################################

def unregister():

    if cleanup_on_exit in bpy.app.handlers.load_pre:
        bpy.app.handlers.load_pre.remove(cleanup_on_exit)
    
    # Also cleanup immediately on addon disable
    cleanup_on_exit()

    for cls in _rna_classes:
        try:
            bpy.utils.unregister_class(cls)
        except RuntimeError:
            log.warning('Unable to unregister class %r, probably already unregistered', cls)

    # try:
    #     del bpy.types.WindowManager.raas_status
    # except AttributeError:
    #     pass
