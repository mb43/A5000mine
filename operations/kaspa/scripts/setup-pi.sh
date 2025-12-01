#!/bin/bash
#
# Kaspa Mining Pi Setup Script
# Sets up Raspberry Pi for Kaspa miner management
#

set -e

echo "========================================="
echo "  Kaspa Mining Pi Setup"
echo "========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Please run as root (use sudo)${NC}"
    exit 1
fi

echo -e "${GREEN}[1/6] Updating system...${NC}"
apt update && apt upgrade -y

echo -e "${GREEN}[2/6] Installing Tailscale...${NC}"
if ! command -v tailscale &> /dev/null; then
    curl -fsSL https://tailscale.com/install.sh | sh
else
    echo "Tailscale already installed"
fi

echo -e "${GREEN}[3/6] Installing nginx...${NC}"
apt install -y nginx curl wget unzip

echo -e "${GREEN}[4/6] Configuring nginx proxy for miners...${NC}"

# Create nginx config for miner proxies
cat > /etc/nginx/sites-available/kaspa-miners <<'EOF'
# Kaspa Miner Proxy Configuration
# Allows remote access to miner web UIs via Tailscale

# Miner 1
server {
    listen 8080;
    server_name _;
    location / {
        proxy_pass http://192.168.1.100:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_connect_timeout 10s;
        proxy_send_timeout 10s;
        proxy_read_timeout 10s;
    }
}

# Miner 2
server {
    listen 8081;
    server_name _;
    location / {
        proxy_pass http://192.168.1.101:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_connect_timeout 10s;
        proxy_send_timeout 10s;
        proxy_read_timeout 10s;
    }
}

# Miner 3
server {
    listen 8082;
    server_name _;
    location / {
        proxy_pass http://192.168.1.102:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_connect_timeout 10s;
        proxy_send_timeout 10s;
        proxy_read_timeout 10s;
    }
}

# Miner 4
server {
    listen 8083;
    server_name _;
    location / {
        proxy_pass http://192.168.1.103:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_connect_timeout 10s;
        proxy_send_timeout 10s;
        proxy_read_timeout 10s;
    }
}

# Add more miners as needed...
EOF

# Enable the site
ln -sf /etc/nginx/sites-available/kaspa-miners /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test nginx config
nginx -t

# Restart nginx
systemctl restart nginx
systemctl enable nginx

echo -e "${GREEN}[5/6] Setting up miner watchdog (auto-reboot dead miners)...${NC}"

# Create watchdog script
mkdir -p /opt/kaspa-watchdog
cat > /opt/kaspa-watchdog/check-miners.sh <<'EOF'
#!/bin/bash
# Kaspa Miner Watchdog
# Checks miner health and reboots if unresponsive

check_and_reboot() {
    local ip=$1
    local name=$2

    if ! ping -c2 "$ip" >/dev/null 2>&1; then
        logger "Kaspa Watchdog: $name ($ip) is down, attempting reboot"
        curl -m 10 "http://$ip/cgi-bin/reboot.cgi" >/dev/null 2>&1 || true
    fi
}

# Check each miner (add more as needed)
check_and_reboot "192.168.1.100" "Miner01"
check_and_reboot "192.168.1.101" "Miner02"
check_and_reboot "192.168.1.102" "Miner03"
EOF

chmod +x /opt/kaspa-watchdog/check-miners.sh

# Add to crontab (runs every 15 minutes)
(crontab -l 2>/dev/null | grep -v "kaspa-watchdog" ; echo "*/15 * * * * /opt/kaspa-watchdog/check-miners.sh") | crontab -

echo -e "${GREEN}[6/6] Configuring Tailscale...${NC}"

# Prompt for hostname
read -p "Enter hostname for this site (e.g., kaspa-site-01): " HOSTNAME
if [ -z "$HOSTNAME" ]; then
    HOSTNAME="kaspa-site-$(date +%s | tail -c 3)"
fi

hostnamectl set-hostname "$HOSTNAME"

echo ""
echo -e "${YELLOW}Tailscale is installed but not connected.${NC}"
echo "Please run one of the following:"
echo ""
echo "  1. Interactive login (opens browser):"
echo "     sudo tailscale up --accept-dns=false"
echo ""
echo "  2. With auth key:"
echo "     sudo tailscale up --authkey=tskey-auth-xxxxx --accept-dns=false"
echo ""

echo ""
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}  Setup Complete!${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo "Next steps:"
echo "  1. Connect Tailscale (see command above)"
echo "  2. Access miners remotely:"
echo "     - Miner 1: http://$HOSTNAME:8080"
echo "     - Miner 2: http://$HOSTNAME:8081"
echo "     - Miner 3: http://$HOSTNAME:8082"
echo "  3. Miner watchdog runs every 15 minutes"
echo ""
echo "To add more miners:"
echo "  - Edit /etc/nginx/sites-available/kaspa-miners"
echo "  - Edit /opt/kaspa-watchdog/check-miners.sh"
echo "  - Run: sudo systemctl reload nginx"
echo ""
