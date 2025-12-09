#!/bin/bash

set +e
###############################################
ROOT_DIR=${PWD}/../

LOG_DIR=${ROOT_DIR}/log
IN_DIR=${ROOT_DIR}/in
OUT_DIR=${ROOT_DIR}/out
CACHE_DIR=${ROOT_DIR}/cache

LOG=${ROOT_DIR}/interactive/command.log
###############################################

mkdir -p ${LOG_DIR}
mkdir -p ${IN_DIR}
mkdir -p ${OUT_DIR}
mkdir -p ${CACHE_DIR}

###############################################
# ml CUDA
# ml Mesa
# ml GCC
###############################################
BLEND_FILE=`cat ${ROOT_DIR}/interactive/blendfile`
FRAME_CMD="--render-frame 1"
CYCLES_DEVICE_CMD="--cycles-device CPU"
###############################################
export CYCLES_BRAAS_HPC_INTERACTIVE_MODE=1
export CYCLES_BRAAS_HPC_SERVER_PORT=$1

echo "Using port: ${CYCLES_BRAAS_HPC_SERVER_PORT}"

killall blender

~/blenderphi/blender --factory-startup --enable-autoexec -noaudio --background ${ROOT_DIR}/${BLEND_FILE} -E CYCLES --render-output ${OUT_DIR}/###### ${FRAME_CMD} -- ${CYCLES_DEVICE_CMD} >> ${LOG} 2>&1