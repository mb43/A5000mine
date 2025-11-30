#!/bin/bash
# build-iso.sh - Build bootable live USB ISO for A5000 mining
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

# Configuration
WORK_DIR="$(pwd)/build"
ISO_NAME="a5000mine.iso"
UBUNTU_VERSION="22.04"
UBUNTU_ISO="ubuntu-${UBUNTU_VERSION}-live-server-amd64.iso"
UBUNTU_URL="https://releases.ubuntu.com/${UBUNTU_VERSION}/${UBUNTU_ISO}"

log "Starting A5000mine ISO build process"

# Create work directory
log "Creating build directory"
mkdir -p "$WORK_DIR"
cd "$WORK_DIR"

# Download Ubuntu base ISO if not present
if [ ! -f "$UBUNTU_ISO" ]; then
    log "Downloading Ubuntu ${UBUNTU_VERSION} base ISO"
    wget -c "$UBUNTU_URL" || error "Failed to download Ubuntu ISO"
else
    log "Ubuntu ISO already exists, skipping download"
fi

# Install required packages
log "Installing build dependencies"
apt-get update
apt-get install -y \
    xorriso \
    squashfs-tools \
    genisoimage \
    isolinux \
    syslinux-utils \
    wget \
    curl \
    jq \
    || error "Failed to install dependencies"

# Extract ISO
log "Extracting base ISO"
mkdir -p iso_extract iso_new
mount -o loop "$UBUNTU_ISO" iso_extract || error "Failed to mount ISO"
rsync -a iso_extract/ iso_new/ || error "Failed to copy ISO contents"
umount iso_extract

# Extract squashfs
log "Extracting squashfs filesystem"
mkdir -p squashfs_root
unsquashfs -d squashfs_root iso_new/casper/filesystem.squashfs || error "Failed to extract squashfs"

# Mount required filesystems for chroot
log "Setting up chroot environment"
mount --bind /dev squashfs_root/dev
mount --bind /proc squashfs_root/proc
mount --bind /sys squashfs_root/sys
mount --bind /run squashfs_root/run

# Cleanup function
cleanup() {
    log "Cleaning up mounts"
    umount -l squashfs_root/dev 2>/dev/null || true
    umount -l squashfs_root/proc 2>/dev/null || true
    umount -l squashfs_root/sys 2>/dev/null || true
    umount -l squashfs_root/run 2>/dev/null || true
}
trap cleanup EXIT

# Copy rootfs overlay to chroot
log "Copying rootfs overlay"
if [ -d "$(pwd)/../rootfs" ]; then
    rsync -a $(pwd)/../rootfs/ squashfs_root/
else
    log "WARNING: No rootfs directory found, skipping overlay"
fi

# Chroot and install packages
log "Installing packages in chroot"
cat > squashfs_root/tmp/install.sh << 'EOF'
#!/bin/bash
set -e
export DEBIAN_FRONTEND=noninteractive

# Update package lists
apt-get update

# Install NVIDIA drivers and dependencies
apt-get install -y \
    nvidia-driver-550 \
    nvidia-utils-550 \
    build-essential \
    linux-headers-generic \
    wget \
    curl \
    jq \
    python3 \
    python3-pip \
    systemd \
    network-manager \
    openssh-server \
    htop \
    vim \
    nano

# Download lolMiner
mkdir -p /opt/ae-miner
cd /opt/ae-miner
LOLMINER_VERSION="1.88"
wget "https://github.com/Lolliedieb/lolMiner-releases/releases/download/${LOLMINER_VERSION}/lolMiner_v${LOLMINER_VERSION}_Lin64.tar.gz" \
    -O lolminer.tar.gz
tar -xzf lolminer.tar.gz
mv ${LOLMINER_VERSION}/lolMiner .
chmod +x lolMiner
rm -rf ${LOLMINER_VERSION} lolminer.tar.gz

# Enable services
systemctl enable ae-miner.service || true
systemctl enable ae-dashboard.service || true
systemctl enable NetworkManager
systemctl enable ssh

# Clean up
apt-get clean
rm -rf /var/lib/apt/lists/*
EOF

chmod +x squashfs_root/tmp/install.sh
chroot squashfs_root /tmp/install.sh || error "Failed to install packages in chroot"
rm squashfs_root/tmp/install.sh

# Create build directory marker
mkdir -p squashfs_root/opt/ae-miner
echo "a5000mine-v1.0" > squashfs_root/opt/ae-miner/.version

# Rebuild squashfs
log "Rebuilding squashfs filesystem"
rm -f iso_new/casper/filesystem.squashfs
mksquashfs squashfs_root iso_new/casper/filesystem.squashfs -comp xz -b 1M || error "Failed to create squashfs"

# Update filesystem size
log "Updating filesystem manifest"
printf $(du -sx --block-size=1 squashfs_root | cut -f1) > iso_new/casper/filesystem.size

# Calculate MD5 sums
log "Calculating MD5 checksums"
cd iso_new
find . -type f -print0 | xargs -0 md5sum | grep -v "\./md5sum.txt" > md5sum.txt

# Create bootable ISO
log "Creating bootable ISO"
xorriso -as mkisofs \
    -iso-level 3 \
    -full-iso9660-filenames \
    -volid "A5000MINE" \
    -eltorito-boot isolinux/isolinux.bin \
    -eltorito-catalog isolinux/boot.cat \
    -no-emul-boot -boot-load-size 4 -boot-info-table \
    -isohybrid-mbr /usr/lib/ISOLINUX/isohdpfx.bin \
    -eltorito-alt-boot \
    -e boot/grub/efi.img \
    -no-emul-boot -isohybrid-gpt-basdat \
    -output "../${ISO_NAME}" \
    . || error "Failed to create ISO"

cd ..

# Cleanup
cleanup
trap - EXIT

log "Build complete!"
log "ISO location: ${WORK_DIR}/${ISO_NAME}"
log "To write to USB: sudo dd if=${WORK_DIR}/${ISO_NAME} of=/dev/sdX bs=4M status=progress"
