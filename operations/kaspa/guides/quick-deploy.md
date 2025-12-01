# KS5M Quick Deployment Guide

Complete copy-paste deployment process for each new KS5M miner.

## Prerequisites (One-Time Per Site)

### Hardware Needed:

| Item | Model | Price (GBP) |
|------|-------|-------------|
| 5G Router | Zyxel NR5103E + Poynting XPOL-1-5G antenna | £245-£265 |
| 5G SIM | Three / Smarty / Voxi unlimited data | £25-£40/mo |
| Raspberry Pi | Pi 5 8GB kit | £105 |
| Switch | TP-Link TL-SG108 (8-port Gigabit) | £18 |
| UPS | APC BE425M-UK or TalentCell 12V 30Ah | £55 |
| Cables | Cat6 Ethernet, various lengths | £15 |

**Total one-off cost per site: £490-£530**
**Paid back in <7 days with just one KS5M**

## Part A: One-Time Site Setup

### 1. Network Setup (15 min)

```bash
# Router: Zyxel NR5103E
# - Insert SIM card
# - Connect antenna
# - Power on
# - Default admin: 192.168.1.1
# - Login: admin / (password on sticker)
```

### 2. Raspberry Pi Setup (20 min)

Flash SD card with Raspberry Pi OS Lite 64-bit (Bookworm):

```bash
# Boot Pi, then run:
sudo raspi-config
# → System Options → Hostname → kaspa-control-01
# → Interface Options → SSH → Enable
# → Boot Options → Wait for Network at Boot → Enable
# → Localisation → timezone London
```

Reboot, then:

```bash
sudo apt update && sudo apt full-upgrade -y && sudo reboot

# After reboot, install Tailscale
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up --advertise-exit-node --accept-dns=false

# Install nginx
sudo apt install -y nginx curl wget unzip
sudo systemctl enable nginx
```

Create miner proxy (see [remote-access.md](remote-access.md) for full config).

## Part B: Deploying Each New KS5M (12 Minutes Per Miner)

### Step 1: Physical Connection (2 min)

1. Plug KS5M into mains power
2. Connect KS5M to 8-port switch via Ethernet
3. Power on → wait 2 minutes

### Step 2: Router Configuration (3 min)

On Zyxel admin page (192.168.1.1):

1. **DHCP Reservation**:
   - DHCP → Reservations → Add reservation
   - MAC address = sticker on KS5M
   - Fixed IP:
     - First miner: `192.168.1.100`
     - Second miner: `192.168.1.101`
     - Third miner: `192.168.1.102`
     - etc.

2. **Port Forwarding** (only do once per site):
   - Firewall → Port Forwarding → add rule
   - External port 8080 → internal `192.168.1.10` port 8080

### Step 3: Miner Configuration (7 min)

1. **Access miner web UI**: `http://192.168.1.100` (or .101, .102, etc.)

2. **Login**:
   - Username: `root`
   - Password: `root`
   - **Change password immediately**

3. **Firmware Update**:
   - Firmware → upgrade to latest from iceriver.io
   - Takes ~4 minutes

4. **Pool Configuration**:

```
Pool 1:
URL:      stratum+tcp://kas.emcd.io:3333
Worker:   YOUR_KASPA_ADDRESS.Miner01
Password: x

Pool 2:
URL:      stratum+tcp://kas.emcd.io:7777
Worker:   YOUR_KASPA_ADDRESS.Miner01
Password: x

Pool 3:
URL:      stratum+tcp://eu-kas.2miners.com:2020
Worker:   YOUR_KASPA_ADDRESS.Miner01
Password: x
```

**Replace:**
- `YOUR_KASPA_ADDRESS` with your real Kaspium address
- `Miner01` → `Miner02`, `Miner03`, etc. for each unit

5. **Save & Apply** → watch hashrate hit 15 TH/s within 10 minutes

## Expected Performance Per Miner

| Metric | Value |
|--------|-------|
| Hashrate | 15 TH/s |
| Power Consumption | 3,400W |
| Heat Output | 3.4 kW |
| Daily KAS | 630 KAS |
| Daily Income | £82-£85 |
| Auto-reconnect | Yes |
| Remote Access | Via Tailscale |

## Scaling Table: KS5Ms Per 5G Site

| Miners | Power | Heat | UK 5G Speed | Notes |
|--------|-------|------|-------------|-------|
| 1-6 | 3.4-20 kW | 3-20 kW | 150-600 Mbps | Single socket fine |
| 7-12 | 24-40 kW | 24-40 kW | Same | Need 32A or 3-phase |
| 13-20 | 45-68 kW | 45-68 kW | Same | 3-phase or container |

**Most people stop at 10-12 per site = ~£30,000/month profit on one £500 site kit**

## Post-Deployment Checklist

- ✅ Miner shows 15 TH/s on web UI
- ✅ Pool dashboard shows hashrate (check after 10 min)
- ✅ Tailscale access works: `http://kaspa-site-01:8080`
- ✅ Auto-reboot cron job configured
- ✅ Miner sends shares (check pool stats)
- ✅ Worker name correct in pool dashboard

## Troubleshooting

### Miner not hashing:
```bash
# Check miner web UI
# Verify pool config is correct
# Restart miner from web UI
```

### Can't access miner remotely:
```bash
# SSH to Pi
ssh pi@kaspa-site-01

# Check nginx
sudo systemctl status nginx
sudo systemctl restart nginx
```

### Miner offline:
```bash
# Check physical connections
# Verify router DHCP reservation
# Check miner power supply
# Manual reboot via web UI or power cycle
```

## Next Steps

To add another miner:
1. Repeat Part B only (12 minutes)
2. Increment IP address (.101, .102, etc.)
3. Increment worker name (Miner02, Miner03, etc.)
4. Done!

For wallet and pool setup, see [wallet-setup.md](wallet-setup.md).

For remote access details, see [remote-access.md](remote-access.md).
