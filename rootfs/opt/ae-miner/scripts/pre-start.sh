#!/bin/bash
# pre-start.sh - GPU setup before mining starts
set -e

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}

log "Running pre-start GPU configuration"

# Check if NVIDIA driver is loaded
if ! nvidia-smi >/dev/null 2>&1; then
    log "ERROR: NVIDIA driver not loaded or GPU not detected"
    exit 1
fi

# Load config
CONFIG_FILE="/opt/ae-miner/config.json"
if [ ! -f "$CONFIG_FILE" ]; then
    log "ERROR: Configuration file not found: $CONFIG_FILE"
    exit 1
fi

# Read power limit from config
POWER_LIMIT=$(jq -r '.gpu.power_limit' "$CONFIG_FILE")
GPU_ID=$(jq -r '.gpu.device_id' "$CONFIG_FILE")
CORE_OFFSET=$(jq -r '.gpu.core_offset' "$CONFIG_FILE")
MEM_OFFSET=$(jq -r '.gpu.mem_offset' "$CONFIG_FILE")

log "Configuring GPU $GPU_ID"

# Set persistence mode
log "Enabling persistence mode"
nvidia-smi -i $GPU_ID -pm 1 || log "WARNING: Could not enable persistence mode"

# Set power limit
if [ "$POWER_LIMIT" != "null" ] && [ "$POWER_LIMIT" -gt 0 ]; then
    log "Setting power limit to ${POWER_LIMIT}W"
    nvidia-smi -i $GPU_ID -pl $POWER_LIMIT || log "WARNING: Could not set power limit"
fi

# Apply GPU offsets if nvidia-settings is available
if command -v nvidia-settings >/dev/null 2>&1; then
    if [ "$CORE_OFFSET" != "0" ] && [ "$CORE_OFFSET" != "null" ]; then
        log "Applying core offset: ${CORE_OFFSET} MHz"
        nvidia-settings -a "[gpu:$GPU_ID]/GPUGraphicsClockOffset[3]=$CORE_OFFSET" >/dev/null 2>&1 || log "WARNING: Could not apply core offset"
    fi

    if [ "$MEM_OFFSET" != "0" ] && [ "$MEM_OFFSET" != "null" ]; then
        log "Applying memory offset: ${MEM_OFFSET} MHz"
        nvidia-settings -a "[gpu:$GPU_ID]/GPUMemoryTransferRateOffset[3]=$MEM_OFFSET" >/dev/null 2>&1 || log "WARNING: Could not apply memory offset"
    fi
fi

# Display GPU info
log "GPU Status:"
nvidia-smi -i $GPU_ID --query-gpu=name,power.limit,temperature.gpu,clocks.gr,clocks.mem --format=csv,noheader

log "Pre-start configuration complete"
