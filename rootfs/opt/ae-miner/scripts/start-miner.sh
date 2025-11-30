#!/bin/bash
# start-miner.sh - Main miner launcher
set -e

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}

MINER_DIR="/opt/ae-miner"
CONFIG_FILE="$MINER_DIR/config.json"
MINER_BIN="$MINER_DIR/lolMiner"

cd "$MINER_DIR"

log "Starting lolMiner for Aeternity"

# Verify config exists
if [ ! -f "$CONFIG_FILE" ]; then
    log "ERROR: Configuration file not found: $CONFIG_FILE"
    log "Please run: ae-config"
    exit 1
fi

# Read configuration
WALLET=$(jq -r '.wallet' "$CONFIG_FILE")
WORKER=$(jq -r '.worker_name' "$CONFIG_FILE")
POOL_URL=$(jq -r '.pool.url' "$CONFIG_FILE")
GPU_ID=$(jq -r '.gpu.device_id' "$CONFIG_FILE")

# Validate wallet
if [ "$WALLET" = "ak_CONFIGURE_ME" ] || [ "$WALLET" = "null" ] || [ -z "$WALLET" ]; then
    log "ERROR: Wallet address not configured"
    log "Please run: ae-config"
    exit 1
fi

# Validate pool URL
if [ "$POOL_URL" = "null" ] || [ -z "$POOL_URL" ]; then
    log "ERROR: Pool URL not configured"
    exit 1
fi

log "Configuration:"
log "  Wallet: ${WALLET:0:10}...${WALLET: -10}"
log "  Worker: $WORKER"
log "  Pool: $POOL_URL"
log "  GPU: $GPU_ID"

# Verify miner binary exists
if [ ! -f "$MINER_BIN" ]; then
    log "ERROR: lolMiner binary not found: $MINER_BIN"
    exit 1
fi

# Start lolMiner
# Algorithm: C29AE (Cuckoo Cycle for Aeternity)
log "Launching lolMiner..."
exec "$MINER_BIN" \
    --coin AE \
    --pool "$POOL_URL" \
    --user "$WALLET.$WORKER" \
    --devices $GPU_ID \
    --watchdog exit \
    --apiport 0
