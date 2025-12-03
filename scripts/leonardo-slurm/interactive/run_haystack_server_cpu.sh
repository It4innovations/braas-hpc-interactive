#!/bin/bash

module use /mnt/proj3/open-28-64/blender/salomon/projects/ingo/easybuild_cs_p06/modules/all

ml Python/3.11.3-GCCcore-12.2.0
ml OpenMPI/4.1.6-NVHPC-23.11-CUDA-12.2.0

export SITEPKG=$(python -c "import site; print(site.getusersitepackages())")
echo ${SITEPKG}
export LD_LIBRARY_PATH=${SITEPKG}/braas_hpc_renderengine_dll:${SITEPKG}:$LD_LIBRARY_PATH

python command.py > command.log 2>&1
