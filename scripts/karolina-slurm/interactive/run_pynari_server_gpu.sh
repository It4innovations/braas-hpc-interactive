#!/bin/bash

# TODO: Update this script

ml Python/3.12.3-GCCcore-14.2.0
ml tbb/2021.11.0-GCCcore-12.3.0
ml Mesa/24.1.3-GCCcore-13.3.0

ml CMake/3.31.3-GCCcore-14.2.0
ml OpenMPI/5.0.5-NVHPC-24.3-CUDA-12.3.0
ml CUDA/12.8.0
ml GCC/14.2.0

export SITEPKG=$(python -c "import site; print(site.getusersitepackages())")
echo ${SITEPKG}
export LD_LIBRARY_PATH=${SITEPKG}/braas_hpc_renderengine_dll:${SITEPKG}:$LD_LIBRARY_PATH

python command.py > command.log 2>&1
