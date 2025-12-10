# BRaaS-HPC-Interactive 
### (Blender Rendering-as-a-Service for HPC with Interactive Support)

## Overview

BRaaS-HPC-Interactive is a Blender addon that enables interactive rendering and computational work on High-Performance Computing (HPC) clusters. This addon extends the base [BRaaS-HPC](https://github.com/It4innovations/braas-hpc) functionality by providing real-time, interactive sessions with HPC resources, allowing users to run custom commands and scripts directly on HPC nodes while working within Blender.

Developed by [IT4Innovations National Supercomputing Center](https://www.it4i.cz/), this addon is designed for users who need to leverage HPC computational power for:
- Interactive Blender rendering ([BlenderPhi](https://github.com/It4innovations/blenderphi))
- Real-time visualization and processing
- Remote computational tasks with live feedback

## Features

### Interactive Session Management
- **Live HPC Sessions**: Establish interactive SSH connections to HPC compute nodes
- **Interactive Types**: Currently only supports [BlenderPhi](https://github.com/It4innovations/blenderphi)
- **Real-time Command Execution**: Run commands and scripts on HPC resources with live output
- **Automatic SSH Tunneling**: Secure port forwarding between local machine and HPC nodes

### Supported HPC Clusters
This add-on currently supports one HPC system (more systems will be added):
- **KAROLINA** (IT4Innovations)

### Job Management
- Submit interactive jobs to HPC clusters
- Monitor job status and execution
- File transfer between local machine and HPC storage
- Automatic resource allocation (CPU/GPU)

### Script Management
- Automatic installation of required scripts on HPC clusters
- [BlenderPhi](https://github.com/It4innovations/blenderphi) installation and configuration
- Git-based script repository management
- Cluster-specific script configurations

## Requirements

### Local Machine
- **Blender**: 4.5.0 or higher
- **Operating System**: Windows, Linux, or macOS
- **Python**: 3.x (bundled with Blender)
- **SSH Client**: OpenSSH or compatible SSH client
- **Dependencies**: 
  - [BRaaS-HPC](https://github.com/It4innovations/braas-hpc) (first, install the `braas_hpc` addon)

### HPC Cluster Requirements
- SSH access with key-based authentication
- SLURM or PBS job scheduler
- Shared storage accessible from compute nodes
- Git installed (for script installation)
- [BlenderPhi](https://github.com/It4innovations/blenderphi) installed (or can be installed via addon)

## Installation

### Step 1: Download the Addon

1. Download the add-on in zip format: https://github.com/It4innovations/braas-hpc/releases
   - more information at https://github.com/It4innovations/braas-hpc/blob/main/README.md
2. Download the add-on in zip format: https://github.com/It4innovations/braas-hpc-interactive/releases

### Step 2: Install in Blender
1. Open Blender (version 4.5.0 or higher)
2. Go to `Edit > Preferences > Add-ons`
3. Click `Install...` button
4. Navigate to the `braas_hpc_interactive.zip` file and install it
5. Enable the add-on by checking the checkbox next to "System: BRaaS-HPC-Interactive".

### Step 3: Install Scripts on HPC Cluster
1. In Blender, go to `Edit > Preferences > Add-ons`
2. Find "BRaaS-HPC-Interactive" addon
3. Expand the addon preferences
4. Configure the following:
   - **Git Repository (Scripts)**: Default is `https://github.com/It4innovations/braas-hpc-interactive.git`
   - **Branch**: Default is `main`
   - **Link (BlenderPhi)**: URL to BlenderPhi download for HPC (e.g., `https://github.com/it4innovations/blenderphi/releases`)
5. Click `Install scripts on the cluster(s)` button
6. Wait for confirmation that scripts are installed

## Usage

### Initial Setup

1. **Configure Cluster Settings** (in base BRaaS-HPC addon):
   - Open addon preferences for the base `braas_hpc` addon
   - Add cluster configurations (hostname, username, SSH key path, project/allocation)
   - Enable the clusters you want to use

2. **Select Configuration** (in Blender scene):
   - Go to the Blender's Render Properties panel
   - Look for the "BRaaS-HPC" panel
   - Select your cluster, partition, and allocation

### Submitting an Interactive Job

1. **Open Interactive Panel**:
   - In the Blender's Render Properties panel, find the "BRaaS-HPC Interactive" section under "BRaaS-HPC"

2. **Select Interactive Type**:
   - Choose from dropdown: `BlenderPhi` (default)
   - (More interactive types will be added)

3. **Submit Job**:
   - Click `Submit Interactive Job`
   - The addon will:
     - Package your Blender file
     - Upload it to the HPC cluster
     - Submit a job to the scheduler
     - Wait for resources to be allocated

4. **Monitor Job Status**:
   - Refresh the job list to see when your job is running
   - Once in "RUNNING" state, you can connect to it

### Running Interactive Commands

1. **Execute Command**:
   - Click `Run Interactive Command`
   - The addon will:
     - Establish SSH tunnel to the compute node
     - Execute the command in the background
     - Keep the connection alive for monitoring

2. **Stop Command**:
   - Click `Stop Interactive Command` to terminate the running process
   - This closes the SSH tunnel and stops remote execution

### File Management

- **Local Storage**: Files are stored in the path configured in BRaaS-HPC preferences
- **Remote Storage**: Files are uploaded to your cluster's shared storage
- **Automatic Transfer**: The addon handles file transfers automatically
- **Job Structure**:
  ```
  <job_name>/
  ├── in/                 # Input files (Blender file, assets)
  ├── out/                # Output files (renders, logs)
  └── interactive/        # Interactive session files
      ├── blendfile       # Path to Blender file
      ├── hostname.txt    # Compute node hostname
      ├── jobid.txt       # Job ID
      ├── command.sh      # Commands to execute
      ├── command.log     # Standard output
      └── command.err     # Error output
  ```


### Workflow in the GUI

```
1. Configure Cluster (Preferences)
   ↓
2. Select Cluster/Partition/Allocation (Viewport Panel)
   ↓
3. Choose Interactive Type (Interactive Panel)
   ↓
4. Submit Interactive Job (Button)
   ↓
5. Wait for Job to Start (Monitor in Job List)
   ↓
6. Run Interactive Command (Button)
   ↓
7. Work Interactively / Monitor Output
   ↓
8. Stop Command When Done (Button)
   ↓
9. Download Results (if needed)
```

## Technical Details

### Security

- **SSH Key Authentication**: Secure key-based authentication (no passwords stored)
- **Strict Host Checking**: Can be configured per security requirements
- **Encrypted Tunnels**: All data transfers through encrypted SSH connections

## Troubleshooting

### Common Issues

1. **SSH Connection Fails**:
   - Verify SSH key is correctly installed on HPC cluster
   - Check firewall settings allow SSH (port 22)
   - Ensure correct username and hostname in cluster configuration
   - Test manual SSH connection: `ssh -i /path/to/key user@host`

2. **Script Installation Fails**:
   - Check internet connectivity from HPC cluster
   - Verify Git is installed on cluster
   - Ensure write permissions in home directory
   - Check repository URL and branch name

3. **Job Submission Fails**:
   - Verify project/allocation is active and has resources
   - Check job parameters (nodes, walltime, partition)
   - Review cluster-specific requirements
   - Check HPC scheduler status

4. **Interactive Command Doesn't Start**:
   - Ensure job is in "RUNNING" state
   - Check if BlenderPhi is installed on cluster
   - Verify port forwarding settings
   - Review command logs on cluster (`command.log`, `command.err`)

5. **File Transfer Issues**:
   - Check storage path permissions
   - Verify sufficient disk space on both local and remote
   - Ensure network connectivity is stable
   - Check file paths don't contain special characters


# License
This software is licensed under the terms of the [GNU General Public License](https://github.com/It4innovations/braas-hpc/blob/main/LICENSE).


# Acknowledgement
This work was supported by the Ministry of Education, Youth and Sports of the Czech Republic through the e-INFRA CZ (ID:90254).

This work was supported by the SPACE project. This project has received funding from the European High- Performance Computing Joint Undertaking (JU) under grant agreement No 101093441. This project has received funding from the Ministry of Education, Youth and Sports of the Czech Republic (ID: MC2304).
