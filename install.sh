#!/bin/bash
# install.sh - Quick installer for A5000mine
set -e

echo "=== A5000mine Quick Installer ==="

if [ "$EUID" -ne 0 ]; then
    echo "Run with sudo: sudo ./install.sh"
    exit 1
fi

# Detect environment
HAS_GPU=false
HAS_SYSTEMD=false
IS_VIRTUAL=false
lspci 2>/dev/null | grep -i nvidia > /dev/null && HAS_GPU=true
[ -d /run/systemd/system ] && HAS_SYSTEMD=true

# Detect virtualization
if systemd-detect-virt --vm >/dev/null 2>&1 || systemd-detect-virt --container >/dev/null 2>&1; then
    IS_VIRTUAL=true
    VIRT_TYPE=$(systemd-detect-virt 2>/dev/null || echo "unknown")
    echo "Virtual environment detected: $VIRT_TYPE"
fi

echo "[1/5] Updating package lists..."
apt-get update

echo "[2/5] Installing dependencies..."
apt-get install -y jq curl wget python3 python3-pip

if [ "$HAS_GPU" = true ]; then
    echo "[3/5] Installing NVIDIA drivers..."

    # Clean up conflicting versions
    apt-get remove -y nvidia-* 2>/dev/null || true
    apt-get autoremove -y 2>/dev/null || true

    # Install single driver version
    DRIVER_VERSION="550"
    if ! apt-get install -y nvidia-driver-${DRIVER_VERSION} nvidia-utils-${DRIVER_VERSION}; then
        echo "WARNING: NVIDIA driver installation failed"
        if [ "$IS_VIRTUAL" = true ]; then
            echo "Note: NVIDIA drivers may not work in VMs without GPU passthrough"
        fi
    fi
else
    echo "[3/5] No NVIDIA GPU detected - skipping drivers"
fi

echo "[4/5] Installing lolMiner..."
mkdir -p /opt/ae-miner/scripts /opt/ae-miner/logs
cd /opt/ae-miner
if [ ! -f lolMiner ]; then
    wget -q https://github.com/Lolliedieb/lolMiner-releases/releases/download/1.88/lolMiner_v1.88_Lin64.tar.gz
    tar -xzf lolMiner_v1.88_Lin64.tar.gz
    mv 1.88/lolMiner .
    rm -rf 1.88 *.tar.gz
fi
chmod +x lolMiner

echo "[5/5] Creating configuration files..."

# Create config.json
cat > /opt/ae-miner/config.json << 'CONF'
{
    "wallet": "ak_CONFIGURE_ME",
    "worker_name": "rig-01",
    "pool": {
        "url": "stratum+tcp://ae.2miners.com:4040",
        "backup_url": "stratum+tcp://ae.f2pool.com:4040"
    },
    "gpu": {
        "device_id": 0,
        "power_limit": 230,
        "core_offset": 0,
        "mem_offset": 0
    },
    "dashboard": {
        "enabled": true,
        "port": 8080
    }
}
CONF

# Create pre-start script
cat > /opt/ae-miner/scripts/pre-start.sh << 'PRESTART'
#!/bin/bash
# pre-start.sh - Pre-flight checks before starting miner

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}

CONFIG_FILE="/opt/ae-miner/config.json"
POWER_LIMIT=$(jq -r '.gpu.power_limit' "$CONFIG_FILE")

# Check if nvidia-smi is available
if command -v nvidia-smi &> /dev/null; then
    log "Setting GPU power limit to ${POWER_LIMIT}W"
    nvidia-smi -pl "$POWER_LIMIT" || log "WARNING: Failed to set power limit"
else
    log "WARNING: nvidia-smi not found, skipping GPU configuration"
fi

exit 0
PRESTART
chmod +x /opt/ae-miner/scripts/pre-start.sh

# Create miner start script
cat > /opt/ae-miner/scripts/start-miner.sh << 'START'
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
log "Launching lolMiner..."
exec "$MINER_BIN" \
    --coin AE \
    --pool "$POOL_URL" \
    --user "$WALLET.$WORKER" \
    --devices $GPU_ID \
    --watchdog exit \
    --apiport 0
START
chmod +x /opt/ae-miner/scripts/start-miner.sh

# Create utility scripts
cat > /usr/local/bin/ae-config << 'AECONFIG'
#!/bin/bash
# ae-config - Configure wallet and mining settings

CONFIG_FILE="/opt/ae-miner/config.json"

if [ ! -f "$CONFIG_FILE" ]; then
    echo "ERROR: Config file not found: $CONFIG_FILE"
    exit 1
fi

echo "=== A5000mine Configuration ==="
echo ""

# Get current wallet
CURRENT_WALLET=$(jq -r '.wallet' "$CONFIG_FILE")
echo "Current wallet: $CURRENT_WALLET"
read -p "Enter AE wallet address (ak_...): " NEW_WALLET

if [[ "$NEW_WALLET" =~ ^ak_ ]]; then
    jq --arg wallet "$NEW_WALLET" '.wallet = $wallet' "$CONFIG_FILE" > "$CONFIG_FILE.tmp"
    mv "$CONFIG_FILE.tmp" "$CONFIG_FILE"
    echo "Wallet updated!"
else
    echo "ERROR: Invalid wallet format (must start with ak_)"
    exit 1
fi

# Get worker name
read -p "Enter worker name [rig-01]: " WORKER_NAME
WORKER_NAME=${WORKER_NAME:-rig-01}
jq --arg worker "$WORKER_NAME" '.worker_name = $worker' "$CONFIG_FILE" > "$CONFIG_FILE.tmp"
mv "$CONFIG_FILE.tmp" "$CONFIG_FILE"

echo ""
echo "Configuration saved!"
echo "Start mining with: sudo systemctl start ae-miner"
AECONFIG
chmod +x /usr/local/bin/ae-config

cat > /usr/local/bin/ae-status << 'AESTATUS'
#!/bin/bash
# ae-status - Show mining status
systemctl status ae-miner --no-pager
AESTATUS
chmod +x /usr/local/bin/ae-status

cat > /usr/local/bin/ae-logs << 'AELOGS'
#!/bin/bash
# ae-logs - Show miner logs
tail -f /opt/ae-miner/logs/miner.log
AELOGS
chmod +x /usr/local/bin/ae-logs

cat > /usr/local/bin/ae-start << 'AESTART'
#!/bin/bash
# ae-start - Start mining service
systemctl start ae-miner
echo "Mining service started"
systemctl status ae-miner --no-pager
AESTART
chmod +x /usr/local/bin/ae-start

cat > /usr/local/bin/ae-stop << 'AESTOP'
#!/bin/bash
# ae-stop - Stop mining service
systemctl stop ae-miner
echo "Mining service stopped"
AESTOP
chmod +x /usr/local/bin/ae-stop

# Setup systemd service
if [ "$HAS_SYSTEMD" = true ]; then
    cat > /etc/systemd/system/ae-miner.service << 'SVC'
[Unit]
Description=Aeternity Mining Service
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/ae-miner
ExecStartPre=/opt/ae-miner/scripts/pre-start.sh
ExecStart=/opt/ae-miner/scripts/start-miner.sh
Restart=always
RestartSec=10
StandardOutput=append:/opt/ae-miner/logs/miner.log
StandardError=append:/opt/ae-miner/logs/miner.error.log

# Resource limits
LimitNOFILE=65536

# Security settings
PrivateTmp=true
NoNewPrivileges=false

[Install]
WantedBy=multi-user.target
SVC
    systemctl daemon-reload
    systemctl enable ae-miner
    echo "Systemd service installed and enabled"
else
    echo "No systemd detected - manual start required"
fi

# Create version marker
echo "a5000mine-v1.0-quick" > /opt/ae-miner/.version
date > /opt/ae-miner/.install_date

echo ""
echo "=== Installation Complete ==="
echo ""
if [ "$HAS_GPU" = false ]; then
    echo "NOTE: No GPU detected - install drivers on real hardware"
    echo ""
fi
echo "Next steps:"
echo "1. Configure wallet: sudo ae-config"
echo "2. Start mining: sudo systemctl start ae-miner"
echo ""
echo "Management commands:"
echo "  ae-config  - Configure wallet/pool"
echo "  ae-status  - View mining status"
echo "  ae-logs    - View miner logs"
echo "  ae-start   - Start mining"
echo "  ae-stop    - Stop mining"
echo ""
