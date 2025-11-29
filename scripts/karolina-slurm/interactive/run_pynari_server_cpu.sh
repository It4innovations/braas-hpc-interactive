#!/bin/bash

ml GCC/14.2.0
ml CUDA/12.8.0

export LD_LIBRARY_PATH=/home/milanjaros/.local/lib/python3.12/site-packages/braas_hpc_renderengine_dll:/mnt/proj3/open-28-64/blender/salomon/projects/ingo/install/barney_kar/lib64:/mnt/proj3/open-28-64/blender/salomon/projects/ingo/install/pynari_kar/lib64:/mnt/proj3/open-28-64/blender/salomon/projects/ingo/install/anari-sdk/lib64:$LD_LIBRARY_PATH

/bin/python3.12 command.py > command.log 2>&1
