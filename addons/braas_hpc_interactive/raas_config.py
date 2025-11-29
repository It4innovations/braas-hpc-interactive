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

"""RaaS config."""

import bpy
import braas_hpc

##################################################################

async def CreateJob(context, token):
        blender_job_info_new = context.scene.raas_blender_job_info_new
        job_type = blender_job_info_new.job_type

        if blender_job_info_new.cluster_type == 'BARBORA':
            if 'JOB_CPU' in job_type:
                await braas_hpc.raas_jobs.CreateJobTask3Dep(context, token, braas_hpc.raas_jobs.JobTaskInfo(36, 11, 10), braas_hpc.raas_jobs.JobTaskInfo(36, 11, 18), braas_hpc.raas_jobs.JobTaskInfo(36, 11, 12), 2, 1)
        
            elif 'JOB_GPU' in job_type:
                await braas_hpc.raas_jobs.CreateJobTask3Dep(context, token, braas_hpc.raas_jobs.JobTaskInfo(24, 12, 13), braas_hpc.raas_jobs.JobTaskInfo(24, 12, 19), braas_hpc.raas_jobs.JobTaskInfo(24, 12, 15), 2, 1)            

        elif blender_job_info_new.cluster_type == 'KAROLINA':
            if 'JOB_CPU' in job_type:
                await braas_hpc.raas_jobs.CreateJobTask3Dep(context, token, braas_hpc.raas_jobs.JobTaskInfo(128, 21, 20), braas_hpc.raas_jobs.JobTaskInfo(128, 21, 28), braas_hpc.raas_jobs.JobTaskInfo(128, 21, 22), 2, 2)                
        
            elif 'JOB_GPU' in job_type:
                await braas_hpc.raas_jobs.CreateJobTask3Dep(context, token, braas_hpc.raas_jobs.JobTaskInfo(128, 22, 23), braas_hpc.raas_jobs.JobTaskInfo(128, 22, 29), braas_hpc.raas_jobs.JobTaskInfo(128, 22, 25), 2, 2)            

        elif blender_job_info_new.cluster_type == 'LUMI':
            if 'JOB_CPU' in job_type:
                # context, token, jobNodes, clusterNodeTypeId, CommandTemplateId, ..., FileTranferMethodId, ClusterId 
                await braas_hpc.raas_jobs.CreateJobTask3Dep(context, token, braas_hpc.raas_jobs.JobTaskInfo(128, 31, 30), braas_hpc.raas_jobs.JobTaskInfo(128, 31, 38), braas_hpc.raas_jobs.JobTaskInfo(128, 31, 32), 2, 3)                
        
            elif 'JOB_GPU' in job_type:
                await braas_hpc.raas_jobs.CreateJobTask3Dep(context, token, braas_hpc.raas_jobs.JobTaskInfo(128, 32, 33), braas_hpc.raas_jobs.JobTaskInfo(128, 32, 39), braas_hpc.raas_jobs.JobTaskInfo(128, 32, 35), 2, 3)            


        elif blender_job_info_new.cluster_type == 'LEONARDO':
            if 'JOB_CPU' in job_type:
                # context, token, jobNodes, clusterNodeTypeId, CommandTemplateId, ..., FileTranferMethodId, ClusterId 
                await braas_hpc.raas_jobs.CreateJobTask3Dep(context, token, braas_hpc.raas_jobs.JobTaskInfo(32, 41, 40), braas_hpc.raas_jobs.JobTaskInfo(32, 41, 48), braas_hpc.raas_jobs.JobTaskInfo(32, 41, 42), 2, 4)
        
            elif 'JOB_GPU' in job_type:
                await braas_hpc.raas_jobs.CreateJobTask3Dep(context, token, braas_hpc.raas_jobs.JobTaskInfo(32, 41, 43), braas_hpc.raas_jobs.JobTaskInfo(32, 41, 49), braas_hpc.raas_jobs.JobTaskInfo(32, 41, 45), 2, 4)            

        elif blender_job_info_new.cluster_type == 'MARENOSTRUM5GPP':
            if 'JOB_CPU' in job_type:
                # context, token, jobNodes, clusterNodeTypeId, CommandTemplateId, ..., FileTranferMethodId, ClusterId 
                await braas_hpc.raas_jobs.CreateJobTask3Dep(context, token, braas_hpc.raas_jobs.JobTaskInfo(32, 51, 50), braas_hpc.raas_jobs.JobTaskInfo(32, 51, 58), braas_hpc.raas_jobs.JobTaskInfo(32, 51, 52), 2, 5)
        
            elif 'JOB_GPU' in job_type:
                await braas_hpc.raas_jobs.CreateJobTask3Dep(context, token, braas_hpc.raas_jobs.JobTaskInfo(32, 51, 53), braas_hpc.raas_jobs.JobTaskInfo(32, 51, 59), braas_hpc.raas_jobs.JobTaskInfo(32, 51, 55), 2, 5)            

        elif blender_job_info_new.cluster_type == 'MARENOSTRUM5ACC':
            if 'JOB_CPU' in job_type:
                # context, token, jobNodes, clusterNodeTypeId, CommandTemplateId, ..., FileTranferMethodId, ClusterId 
                await braas_hpc.raas_jobs.CreateJobTask3Dep(context, token, braas_hpc.raas_jobs.JobTaskInfo(32, 61, 60), braas_hpc.raas_jobs.JobTaskInfo(32, 61, 68), braas_hpc.raas_jobs.JobTaskInfo(32, 61, 62), 2, 6)
        
            elif 'JOB_GPU' in job_type:
                await braas_hpc.raas_jobs.CreateJobTask3Dep(context, token, braas_hpc.raas_jobs.JobTaskInfo(32, 61, 63), braas_hpc.raas_jobs.JobTaskInfo(32, 61, 69), braas_hpc.raas_jobs.JobTaskInfo(32, 61, 65), 2, 6)             

        elif blender_job_info_new.cluster_type == 'POLARIS':
            if 'JOB_CPU' in job_type:
                # context, token, jobNodes, clusterNodeTypeId, CommandTemplateId, ..., FileTranferMethodId, ClusterId 
                await braas_hpc.raas_jobs.CreateJobTask3Dep(context, token, braas_hpc.raas_jobs.JobTaskInfo(64, 71, 70), braas_hpc.raas_jobs.JobTaskInfo(64, 71, 78), braas_hpc.raas_jobs.JobTaskInfo(64, 71, 72), 2, 7)
        
            elif 'JOB_GPU' in job_type:
                await braas_hpc.raas_jobs.CreateJobTask3Dep(context, token, braas_hpc.raas_jobs.JobTaskInfo(64, 71, 73), braas_hpc.raas_jobs.JobTaskInfo(64, 71, 79), braas_hpc.raas_jobs.JobTaskInfo(64, 71, 75), 2, 7)            

        elif blender_job_info_new.cluster_type == 'AURORA':
            if 'JOB_CPU' in job_type:
                # context, token, jobNodes, clusterNodeTypeId, CommandTemplateId, ..., FileTranferMethodId, ClusterId 
                await braas_hpc.raas_jobs.CreateJobTask3Dep(context, token, braas_hpc.raas_jobs.JobTaskInfo(32, 81, 80), braas_hpc.raas_jobs.JobTaskInfo(32, 81, 88), braas_hpc.raas_jobs.JobTaskInfo(32, 81, 82), 2, 8)
        
            elif 'JOB_GPU' in job_type:
                await braas_hpc.raas_jobs.CreateJobTask3Dep(context, token, braas_hpc.raas_jobs.JobTaskInfo(32, 81, 83), braas_hpc.raas_jobs.JobTaskInfo(32, 81, 89), braas_hpc.raas_jobs.JobTaskInfo(32, 81, 85), 2, 8)            

        elif blender_job_info_new.cluster_type == 'VISTA':
            if 'JOB_CPU' in job_type:
                # context, token, jobNodes, clusterNodeTypeId, CommandTemplateId, ..., FileTranferMethodId, ClusterId 
                await braas_hpc.raas_jobs.CreateJobTask3Dep(context, token, braas_hpc.raas_jobs.JobTaskInfo(72, 91, 90), braas_hpc.raas_jobs.JobTaskInfo(72, 91, 98), braas_hpc.raas_jobs.JobTaskInfo(72, 91, 92), 2, 9)
        
            elif 'JOB_GPU' in job_type:
                await braas_hpc.raas_jobs.CreateJobTask3Dep(context, token, braas_hpc.raas_jobs.JobTaskInfo(72, 91, 93), braas_hpc.raas_jobs.JobTaskInfo(72, 91, 99), braas_hpc.raas_jobs.JobTaskInfo(72, 91, 95), 2, 9)            


        elif blender_job_info_new.cluster_type == 'FRONTERA':
            if 'JOB_CPU' in job_type:
                # context, token, jobNodes, clusterNodeTypeId, CommandTemplateId, ..., FileTranferMethodId, ClusterId 
                await braas_hpc.raas_jobs.CreateJobTask3Dep(context, token, braas_hpc.raas_jobs.JobTaskInfo(32, 101, 100), braas_hpc.raas_jobs.JobTaskInfo(32, 101, 108), braas_hpc.raas_jobs.JobTaskInfo(32, 101, 102), 2, 10)
        
            elif 'JOB_GPU' in job_type:
                await braas_hpc.raas_jobs.CreateJobTask3Dep(context, token, braas_hpc.raas_jobs.JobTaskInfo(32, 101, 103), braas_hpc.raas_jobs.JobTaskInfo(32, 101, 109), braas_hpc.raas_jobs.JobTaskInfo(32, 101, 105), 2, 10)


        elif blender_job_info_new.cluster_type == 'CS':
            if 'JOB_CPU' in job_type:
                # context, token, jobNodes, clusterNodeTypeId, CommandTemplateId, ..., FileTranferMethodId, ClusterId 
                await braas_hpc.raas_jobs.CreateJobTask3Dep(context, token, braas_hpc.raas_jobs.JobTaskInfo(32, 111, 110), braas_hpc.raas_jobs.JobTaskInfo(32, 111, 118), braas_hpc.raas_jobs.JobTaskInfo(32, 111, 112), 2, 11)
        
            elif 'JOB_GPU' in job_type:
                await braas_hpc.raas_jobs.CreateJobTask3Dep(context, token, braas_hpc.raas_jobs.JobTaskInfo(32, 111, 113), braas_hpc.raas_jobs.JobTaskInfo(32, 111, 119), braas_hpc.raas_jobs.JobTaskInfo(32, 111, 115), 2, 11)

        else:
            await braas_hpc.raas_config.CreateJob(context, token)

# return cores,queue,script
def GetDAQueueScript(ClusterId, CommandTemplateId):
    # BARBORA
    if ClusterId == 1:
        if CommandTemplateId == 10 * ClusterId + 8:
            return 36,'~/braas-hpc-interactive/scripts/barbora-slurm/run_interactive_cpu.sh'
        
        elif CommandTemplateId == 10 * ClusterId + 9:
            return 24,'~/braas-hpc-interactive/scripts/barbora-slurm/run_interactive_gpu.sh'

    # KAROLINA
    elif ClusterId == 2:     
        if CommandTemplateId == 10 * ClusterId + 8:
            return 128,'~/braas-hpc-interactive/scripts/karolina-slurm/run_interactive_cpu.sh'
        
        elif CommandTemplateId == 10 * ClusterId + 9:
            return 128,'~/braas-hpc-interactive/scripts/karolina-slurm/run_interactive_gpu.sh'

                               
    # LUMI
    elif ClusterId == 3:     
        if CommandTemplateId == 10 * ClusterId + 8:
            return 128,'~/braas-hpc-interactive/scripts/lumi-slurm/run_interactive_cpu.sh'
        
        elif CommandTemplateId == 10 * ClusterId + 9:
            return 128,'~/braas-hpc-interactive/scripts/lumi-slurm/run_interactive_gpu.sh'


    # LEONARDO
    elif ClusterId == 4:
        if CommandTemplateId == 10 * ClusterId + 8:
            return 32,'~/braas-hpc-interactive/scripts/leonardo-slurm/run_interactive_cpu.sh'
        
        elif CommandTemplateId == 10 * ClusterId + 9:
            return 32,'~/braas-hpc-interactive/scripts/leonardo-slurm/run_interactive_gpu.sh'
        
    # "MARENOSTRUM5GPP": "MareNostrum 5 GPP",
    elif ClusterId == 5:
        if CommandTemplateId == 10 * ClusterId + 8:
            return 32,'~/braas-hpc-interactive/scripts/marenostrum5gpp-slurm/run_interactive_cpu.sh'
        
        elif CommandTemplateId == 10 * ClusterId + 9:
            return 32,'~/braas-hpc-interactive/scripts/marenostrum5gpp-slurm/run_interactive_gpu.sh'

    # "MARENOSTRUM5ACC": "MareNostrum 5 ACC",
    elif ClusterId == 6:
        if CommandTemplateId == 10 * ClusterId + 8:
            return 32,'~/braas-hpc-interactive/scripts/marenostrum5acc-slurm/run_interactive_cpu.sh'
        
        elif CommandTemplateId == 10 * ClusterId + 9:
            return 32,'~/braas-hpc-interactive/scripts/marenostrum5acc-slurm/run_interactive_gpu.sh'

    # "POLARIS": "Polaris",
    elif ClusterId == 7:
        if CommandTemplateId == 10 * ClusterId + 8:
            return 64,'~/braas-hpc-interactive/scripts/polaris-pbs/run_interactive_cpu.sh'
        
        elif CommandTemplateId == 10 * ClusterId + 9:
            return 64,'~/braas-hpc-interactive/scripts/polaris-pbs/run_interactive_gpu.sh'

    # "AURORA": "Aurora",
    elif ClusterId == 8:
        if CommandTemplateId == 10 * ClusterId + 8:
            return 32,'~/braas-hpc-interactive/scripts/aurora-pbs/run_interactive_cpu.sh'
        
        elif CommandTemplateId == 10 * ClusterId + 9:
            return 32,'~/braas-hpc-interactive/scripts/aurora-pbs/run_interactive_gpu.sh'

    # "VISTA": "Vista",
    elif ClusterId == 9:
        if CommandTemplateId == 10 * ClusterId + 8:
            return 72,'~/braas-hpc-interactive/scripts/vista-slurm/run_interactive_cpu.sh'
        
        elif CommandTemplateId == 10 * ClusterId + 9:
            return 72,'~/braas-hpc-interactive/scripts/vista-slurm/run_interactive_gpu.sh' 
        
    # "FRONTERA": "Frontera",
    elif ClusterId == 10:
        if CommandTemplateId == 10 * ClusterId + 8:
            return 32,'~/braas-hpc-interactive/scripts/frontera-slurm/run_interactive_cpu.sh'
        
        elif CommandTemplateId == 10 * ClusterId + 9:
            return 32,'~/braas-hpc-interactive/scripts/frontera-slurm/run_interactive_gpu.sh'
        
    # "CS": "CS",
    elif ClusterId == 11:
        if CommandTemplateId == 10 * ClusterId + 8:
            return 32,'~/braas-hpc-interactive/scripts/cs-slurm/run_interactive_cpu.sh'
        
        elif CommandTemplateId == 10 * ClusterId + 9:
            return 32,'~/braas-hpc-interactive/scripts/cs-slurm/run_interactive_gpu.sh'    

    return braas_hpc.raas_config.GetDAQueueScript(ClusterId, CommandTemplateId)    

def GetDAInteractiveScript(context):

    blender_job_info_new = context.scene.raas_blender_job_info_new
    cluster_type = blender_job_info_new.cluster_type
    job_type = blender_job_info_new.job_type

    # BARBORA
    if cluster_type == 'BARBORA':
        if job_type == 'JOB_GPU':
            return '~/braas-hpc-interactive/scripts/barbora-slurm/interactive/run_pynari_server_gpu.sh'
        
        elif job_type == 'JOB_CPU':
            return '~/braas-hpc-interactive/scripts/barbora-slurm/interactive/run_pynari_server_cpu.sh'    
        
    # KAROLINA
    elif cluster_type == 'KAROLINA':
        if job_type == 'JOB_GPU':
            return '~/braas-hpc-interactive/scripts/karolina-slurm/interactive/run_pynari_server_gpu.sh'
        
        elif job_type == 'JOB_CPU':
            return '~/braas-hpc-interactive/scripts/karolina-slurm/interactive/run_pynari_server_cpu.sh'
                                          
    # LUMI
    elif cluster_type == 'LUMI':     
        if job_type == 'JOB_GPU':
            return '~/braas-hpc-interactive/scripts/lumi-slurm/interactive/run_pynari_server_gpu.sh'
        
        elif job_type == 'JOB_CPU':
            return '~/braas-hpc-interactive/scripts/lumi-slurm/interactive/run_pynari_server_cpu.sh'

    # LEONARDO
    elif cluster_type == 'LEONARDO':
        return '~/braas-hpc-interactive/scripts/leonardo-slurm/interactive/run_pynari_server_gpu.sh'
                
    # "MARENOSTRUM5GPP": "MareNostrum 5 GPP",
    elif cluster_type == 'MARENOSTRUM5GPP':
        return '~/braas-hpc-interactive/scripts/marenostrum5gpp-slurm/interactive/run_pynari_server_cpu.sh'

    # "MARENOSTRUM5ACC": "MareNostrum 5 ACC",
    elif cluster_type == 'MARENOSTRUM5ACC':
        return '~/braas-hpc-interactive/scripts/marenostrum5acc-slurm/interactive/run_pynari_server_gpu.sh'

    # "POLARIS": "Polaris",
    elif cluster_type == 'POLARIS':
        return '~/braas-hpc-interactive/scripts/polaris-pbs/interactive/run_pynari_server_gpu.sh'

    # "AURORA": "Aurora",
    elif cluster_type == 'AURORA':
        return '~/braas-hpc-interactive/scripts/aurora-pbs/interactive/run_pynari_server_gpu.sh'

    # "VISTA": "Vista",
    elif cluster_type == 'VISTA':
        return '~/braas-hpc-interactive/scripts/vista-slurm/interactive/run_pynari_server_gpu.sh'  
        
    # "FRONTERA": "Frontera",
    elif cluster_type == 'FRONTERA':
        return '~/braas-hpc-interactive/scripts/frontera-slurm/interactive/run_pynari_server_gpu.sh'
    
    # CS
    elif cluster_type == 'CS':
        if job_type == 'JOB_GPU':
            return '~/braas-hpc-interactive/scripts/cs-slurm/interactive/run_pynari_server_gpu.sh'
        
        elif job_type == 'JOB_CPU':
            return '~/braas-hpc-interactive/scripts/cs-slurm/interactive/run_pynari_server_cpu.sh'    

    else:
        return None
    
def GetDASupportSSHProxyJump(context):

    blender_job_info_new = context.scene.raas_blender_job_info_new
    cluster_type = blender_job_info_new.cluster_type
    job_type = blender_job_info_new.job_type

    # BARBORA
    if cluster_type == 'BARBORA':
        return True   
        
    # KAROLINA
    elif cluster_type == 'KAROLINA':
        return True
                                          
    # LUMI
    elif cluster_type == 'LUMI':     
        return True

    # LEONARDO
    elif cluster_type == 'LEONARDO':
        return False
                
    # "MARENOSTRUM5GPP": "MareNostrum 5 GPP",
    elif cluster_type == 'MARENOSTRUM5GPP':
        return False
    
    # "MARENOSTRUM5ACC": "MareNostrum 5 ACC",
    elif cluster_type == 'MARENOSTRUM5ACC':
        return False

    # "POLARIS": "Polaris",
    elif cluster_type == 'POLARIS':
        return False

    # "AURORA": "Aurora",
    elif cluster_type == 'AURORA':
        return False
    
    # "VISTA": "Vista",
    elif cluster_type == 'VISTA':
        return False  
        
    # "FRONTERA": "Frontera",
    elif cluster_type == 'FRONTERA':
        return False
    
    elif cluster_type == 'CS':
        return True    

    else:
        return False        

def GetGitAddonCommand(repository, branch):    
    return 'if [ -d ~/braas-hpc-interactive ] ; then rm -rf ~/braas-hpc-interactive ; fi ; git clone -q -b ' + branch + ' ' + repository

class RaasInteractiveConfigFunctions:
    """Class that holds pointers to all functions"""
    
    def __init__(self):
        ########################super().__init__()
        # Function pointers
        # self.get_blender_cluster_version = GetBlenderClusterVersion
        self.create_job = braas_hpc.raas_config.CreateJob
        # self.get_server = GetServer
        self.get_server_from_type = braas_hpc.raas_config.GetServerFromType
        self.get_scheduler_from_context = braas_hpc.raas_config.GetSchedulerFromContext
        self.get_da_server = braas_hpc.raas_config.GetDAServer
        self.get_da_cluster_path = braas_hpc.raas_config.GetDAClusterPath
        self.get_da_open_call_project = braas_hpc.raas_config.GetDAOpenCallProject
        self.get_da_queue_mpi_procs = braas_hpc.raas_config.GetDAQueueMPIProcs
        self.get_da_queue_script = GetDAQueueScript
        self.get_git_addon_command = braas_hpc.raas_config.GetGitAddonCommand
        self.get_blender_install_command = braas_hpc.raas_config.GetBlenderInstallCommand
        self.get_blender_patch_command = braas_hpc.raas_config.GetBlenderPatchCommand
        self.get_current_pid_info = braas_hpc.raas_config.GetCurrentPidInfo
        self.set_pid_dir = braas_hpc.raas_config.SetPidDir

        ########################New
        self.get_da_interactive_script = GetDAInteractiveScript
        self.get_da_support_ssh_proxy_jump = GetDASupportSSHProxyJump
        self.create_job_interactive = CreateJob
        self.get_git_addon_command_interactive = GetGitAddonCommand
    
    # Convenience methods that can be called on the instance
    # def call_get_blender_cluster_version(self):
    #     """Returns Blender cluster version string"""
    #     return self.get_blender_cluster_version()
    
    async def call_create_job(self, context, token):
        """Creates a job with the given context and token"""
        return await self.create_job(context, token)
    
    async def call_create_job_interactive(self, context, token):
        """Creates a job with the given context and token"""
        return await self.create_job_interactive(context, token)    
    
    # def call_get_server(self, pid):
    #     """Gets server from PID"""
    #     return self.get_server(pid)
    
    def call_get_server_from_type(self, cluster_type):
        """Gets server from cluster type"""
        return self.get_server_from_type(cluster_type)
    
    def call_get_scheduler_from_context(self, context):
        """Gets scheduler from context"""
        return self.get_scheduler_from_context(context)
    
    def call_get_da_server(self, context):
        """Gets DA server from context"""
        return self.get_da_server(context)
    
    def call_get_da_cluster_path(self, context, project_dir, pid):
        """Gets DA cluster path"""
        return self.get_da_cluster_path(context, project_dir, pid)
    
    def call_get_da_open_call_project(self, pid):
        """Gets DA open call project"""
        return self.get_da_open_call_project(pid)
    
    def call_get_da_queue_mpi_procs(self, command_template_id):
        """Gets DA queue MPI processes count"""
        return self.get_da_queue_mpi_procs(command_template_id)
    
    def call_get_da_queue_script(self, cluster_id, command_template_id):
        """Gets DA queue script"""
        return self.get_da_queue_script(cluster_id, command_template_id)
    
    def call_get_git_addon_command(self, repository, branch):
        """Gets git addon command"""
        return self.get_git_addon_command(repository, branch)
    
    def call_get_git_addon_command_interactive(self, repository, branch):
        """Gets git addon command"""
        return self.get_git_addon_command_interactive(repository, branch)    
    
    def call_get_blender_install_command(self, preset, url_link):
        """Gets Blender install command"""
        return self.get_blender_install_command(preset, url_link)
    
    def call_get_blender_patch_command(self, preset, url_link):
        """Gets Blender patch command"""
        return self.get_blender_patch_command(preset, url_link)
    
    def call_get_current_pid_info(self, context, preferences):
        """Gets current PID info"""
        return self.get_current_pid_info(context, preferences)
    
    def call_set_pid_dir(self, preset):
        """Sets PID directory"""
        return self.set_pid_dir(preset)
    
    def call_get_da_interactive_script(self, context):
        """Gets DA interactive script"""
        return self.get_da_interactive_script(context)
    
    def call_get_da_support_ssh_proxy_jump(self, context):
        """Gets DA support SSH proxy jump"""
        return self.get_da_support_ssh_proxy_jump(context)