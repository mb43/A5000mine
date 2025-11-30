#!/bin/bash
# install-standalone.sh - Install A5000 mining software on existing Ubuntu system
set -e

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}

error() {
    log "ERROR: $*" >&2
    exit 1
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    error "This script must be run as root (use sudo)"
fi

# Check Ubuntu version
log "Checking system compatibility"
if ! grep -q "Ubuntu 22.04" /etc/os-release 2>/dev/null; then
    log "WARNING: This installer is designed for Ubuntu 22.04. Your system may not be compatible."
    read -p "Continue anyway? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check for NVIDIA GPU
log "Checking for NVIDIA GPU"
if ! lspci | grep -i nvidia >/dev/null 2>&1; then
    log "WARNING: No NVIDIA GPU detected. Installation will continue but mining will not work."
    read -p "Continue anyway? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

INSTALL_DIR="/opt/ae-miner"
BIN_DIR="/usr/local/bin"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

log "Starting A5000mine installation"

# Update package lists
log "Updating package lists"
apt-get update || error "Failed to update package lists"

# Install NVIDIA drivers
log "Installing NVIDIA drivers (this may take several minutes)"
apt-get install -y \
    nvidia-driver-550 \
    nvidia-utils-550 \
    || log "WARNING: NVIDIA driver installation failed or partially completed"

# Install dependencies
log "Installing dependencies"
apt-get install -y \
    build-essential \
    linux-headers-$(uname -r) \
    wget \
    curl \
    jq \
    python3 \
    python3-pip \
    htop \
    vim \
    || error "Failed to install dependencies"

# Create installation directory
log "Creating installation directory"
mkdir -p "$INSTALL_DIR"
mkdir -p "$INSTALL_DIR/scripts"
mkdir -p "$INSTALL_DIR/logs"

# Download lolMiner
log "Downloading lolMiner"
cd "$INSTALL_DIR"
LOLMINER_VERSION="1.88"
wget -q "https://github.com/Lolliedieb/lolMiner-releases/releases/download/${LOLMINER_VERSION}/lolMiner_v${LOLMINER_VERSION}_Lin64.tar.gz" \
    -O lolminer.tar.gz || error "Failed to download lolMiner"
tar -xzf lolminer.tar.gz
mv ${LOLMINER_VERSION}/lolMiner .
chmod +x lolMiner
rm -rf ${LOLMINER_VERSION} lolminer.tar.gz

log "lolMiner installed successfully"

# Copy rootfs overlay if it exists
if [ -d "$SCRIPT_DIR/rootfs" ]; then
    log "Installing system files from rootfs overlay"
    rsync -av "$SCRIPT_DIR/rootfs/" / || error "Failed to copy rootfs overlay"
else
    log "No rootfs directory found, creating minimal setup"

    # Create default config if not exists
    if [ ! -f "$INSTALL_DIR/config.json" ]; then
        log "Creating default configuration"
        cat > "$INSTALL_DIR/config.json" << 'EOF'
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
EOF
    fi
fi

# Copy config template if it exists
if [ -f "$SCRIPT_DIR/config/config.json" ] && [ ! -f "$INSTALL_DIR/config.json" ]; then
    log "Installing default configuration"
    cp "$SCRIPT_DIR/config/config.json" "$INSTALL_DIR/config.json"
fi

# Install systemd services if they exist in rootfs
if [ -f "$SCRIPT_DIR/rootfs/etc/systemd/system/ae-miner.service" ]; then
    log "Installing systemd services"
    cp "$SCRIPT_DIR/rootfs/etc/systemd/system/ae-miner.service" /etc/systemd/system/
    [ -f "$SCRIPT_DIR/rootfs/etc/systemd/system/ae-dashboard.service" ] && \
        cp "$SCRIPT_DIR/rootfs/etc/systemd/system/ae-dashboard.service" /etc/systemd/system/

    systemctl daemon-reload
    log "Systemd services installed"
fi

# Install utility scripts if they exist
if [ -d "$SCRIPT_DIR/rootfs/usr/local/bin" ]; then
    log "Installing utility scripts"
    cp "$SCRIPT_DIR/rootfs/usr/local/bin"/ae-* "$BIN_DIR/" 2>/dev/null || true
    chmod +x "$BIN_DIR"/ae-* 2>/dev/null || true
fi

# Create version marker
echo "a5000mine-v1.0-standalone" > "$INSTALL_DIR/.version"
echo "$(date)" >> "$INSTALL_DIR/.install_date"

log "Installation complete!"
log ""
log "Next steps:"
log "1. Reboot to load NVIDIA drivers: sudo reboot"
log "2. After reboot, configure your wallet: sudo ae-config"
log "3. Start mining: sudo systemctl start ae-miner"
log ""
log "For status: ae-status"
log "For logs: ae-logs"
log "Dashboard: http://localhost:8080"
