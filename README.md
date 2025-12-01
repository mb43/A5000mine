# A5000mine - Multi-Operation Cryptocurrency Mining Platform

A comprehensive mining platform supporting multiple discrete operations:
- **Aeternity (AE)** - GPU mining with NVIDIA A5000
- **Kaspa (KAS)** - ASIC mining with IceRiver KS5M
- **Zcash (ZEC)** - ASIC mining with Antminer Z15 Pro (coming soon)

## Features

- **Multi-Operation Support**: Run GPU and ASIC miners simultaneously
- **Unified Dashboard**: Monitor all operations with real-time stats and income projections
- **Modular Architecture**: Easily add new mining operations
- **Remote Access**: Secure remote monitoring via Tailscale
- **Automated Management**: Watchdog scripts, auto-reboot, health monitoring
- **Income Tracking**: Real-time daily/monthly/yearly projections in GBP

### Aeternity (GPU) Features
- **Bootable Live USB**: Based on Ubuntu 22.04 LTS
- **Zero Configuration**: Just add your wallet address and start mining
- **Optimized for A5000**: Achieves 4-6 G/s hashrate at 180-230W
- **Expected Income**: ~£8.50 per GPU per day

### Kaspa (ASIC) Features
- **Quick Deploy**: 12-minute setup per KS5M miner
- **15 TH/s per miner**: Industrial-scale hashrate
- **Remote Management**: Access miner web UIs via Tailscale
- **Expected Income**: ~£82 per miner per day
- **Auto-recovery**: Watchdog reboots dead miners automatically

## 🚀 Quick Navigation

| Mining Operation | Hardware | Setup Guide | Daily Income |
|-----------------|----------|-------------|--------------|
| **Aeternity** | NVIDIA A5000 GPU | [See below](#aeternity-gpu-mining-setup) | ~£8.50 per GPU |
| **Kaspa** | IceRiver KS5M ASIC | [Kaspa Guides](operations/kaspa/guides/) | ~£82 per miner |
| **Zcash** | Antminer Z15 Pro | [Coming Soon](operations/zcash/) | ~£45 per miner (est.) |
| **Unified Dashboard** | Any browser | [Dashboard Setup](#unified-dashboard) | Monitor all operations |

## Unified Dashboard

Monitor all your mining operations in one place with real-time stats and income projections.

### Start the Dashboard

```bash
# Clone the repository
git clone https://github.com/mb43/A5000mine.git
cd A5000mine

# Start unified dashboard
python3 dashboard/unified-server.py

# Access at: http://localhost:8090/unified
```

### Dashboard Features

- **Real-time monitoring** of all mining operations
- **Income projections**: Daily, Monthly, Yearly in GBP
- **GPU stats**: Temperature, power, utilization (Aeternity)
- **ASIC status**: Per-miner hashrate and health (Kaspa/Zcash)
- **Auto-refresh**: Updates every 5 seconds

## Aeternity (GPU Mining) Setup

### Method 1: Download Pre-built ISO (Easiest)

1. **Download the latest ISO** from [GitHub Releases](https://github.com/mb43/A5000mine/releases)

2. **Verify the checksum**:
   ```bash
   sha256sum -c SHA256SUMS
   ```

3. **Flash to USB** (8GB+ required):
   ```bash
   sudo dd if=a5000mine.iso of=/dev/sdX bs=4M status=progress oflag=sync
   ```

4. **Boot from USB** and run the configuration wizard:
   ```bash
   sudo ae-config
   ```

4. **Enter your AE wallet address** when prompted (format: `ak_...`)

5. Mining starts automatically!

### Method 2: Install on Existing Ubuntu System

```bash
sudo ./install-standalone.sh
sudo ae-config
```

### Method 3: Build ISO from Source

If you want to customize the ISO or build it yourself:

```bash
sudo ./build-iso.sh
```

**Note:** Building the ISO requires significant disk space (~15GB) and can take 20-30 minutes. For most users, downloading the pre-built ISO from releases is recommended.

## Hardware Requirements

- **GPU**: NVIDIA A5000 (24GB VRAM)
- **RAM**: 8GB+ recommended
- **Storage**: 8GB+ USB drive or 20GB+ disk space
- **Network**: Internet connection for pool access

## Performance Expectations

| Metric | Value |
|--------|-------|
| Hashrate | 4-6 G/s |
| Power Draw | 180-230W |
| Algorithm | Cuckoo Cycle C29AE |
| Pool Fee | 1% (2miners default) |

## Management Commands

| Command | Description |
|---------|-------------|
| `ae-config` | Configure wallet and pool settings |
| `ae-status` | View current mining status |
| `ae-logs` | View miner logs |
| `ae-start` | Start mining service |
| `ae-stop` | Stop mining service |

## Dashboard Access

The web dashboard is accessible at:
- **Local**: http://localhost:8080
- **Network**: http://<your-ip>:8080

Shows real-time:
- Hashrate and shares
- GPU temperature and power
- Pool connection status
- Earnings estimate

## Configuration

Edit `/opt/ae-miner/config.json` to customize:

```json
{
    "wallet": "ak_YourWalletAddress",
    "worker_name": "rig-01",
    "pool": {
        "url": "stratum+tcp://ae.2miners.com:4040",
        "backup_url": "stratum+tcp://ae.f2pool.com:4040"
    },
    "gpu": {
        "power_limit": 230,
        "core_offset": 0,
        "mem_offset": 0
    }
}
```

After editing, restart mining:
```bash
sudo systemctl restart ae-miner
```

---

## Kaspa (ASIC Mining) Setup

Complete guides for deploying IceRiver KS5M ASIC miners.

### Prerequisites (One-Time Per Site)

| Item | Model | Price (GBP) |
|------|-------|-------------|
| 5G Router | Zyxel NR5103E + Poynting antenna | £245-£265 |
| 5G SIM | Smarty unlimited data | £25-£40/mo |
| Raspberry Pi | Pi 5 8GB kit | £105 |
| Switch | TP-Link TL-SG108 (8-port) | £18 |
| **Total** | **One-off per site** | **~£500** |

**Paid back in <7 days with just one KS5M!**

### Quick Deploy (12 Minutes Per Miner)

1. **Set up Raspberry Pi** (one-time):
   ```bash
   cd operations/kaspa/scripts
   sudo ./setup-pi.sh
   ```

2. **Deploy each KS5M**:
   - See [Quick Deploy Guide](operations/kaspa/guides/quick-deploy.md)
   - Full copy-paste instructions
   - Router config, miner setup, pool configuration

3. **Configure wallet & pools**:
   - See [Wallet Setup Guide](operations/kaspa/guides/wallet-setup.md)
   - Kaspium wallet installation
   - EMCD pool account
   - Pool configuration

4. **Enable remote access**:
   - See [Remote Access Guide](operations/kaspa/guides/remote-access.md)
   - Tailscale setup
   - Nginx proxy configuration
   - Access miners from anywhere

### Performance Per KS5M

| Metric | Value |
|--------|-------|
| Hashrate | 15 TH/s |
| Power Consumption | 3,400W |
| Daily KAS | 630 KAS |
| Daily Income | £82-£85 |
| Pool | EMCD (1% fee) |

### Scaling

| Miners | Power | Monthly Income (£) | Notes |
|--------|-------|-------------------|-------|
| 1 | 3.4 kW | £2,460 | Single socket |
| 5 | 17 kW | £12,300 | Still manageable |
| 10 | 34 kW | £24,600 | Need 3-phase |
| 20 | 68 kW | £49,200 | Container setup |

### Remote Access

Access miners via Tailscale from anywhere:

```
http://kaspa-site-01:8080  (Miner 1)
http://kaspa-site-01:8081  (Miner 2)
http://kaspa-site-01:8082  (Miner 3)
```

---

## Supported Mining Pools

| Pool | URL | Fee |
|------|-----|-----|
| 2miners | stratum+tcp://ae.2miners.com:4040 | 1% |
| F2Pool | stratum+tcp://ae.f2pool.com:4040 | 2% |

## Troubleshooting

### Mining not starting
```bash
# Check service status
sudo systemctl status ae-miner

# View logs
ae-logs
```

### GPU not detected
```bash
# Verify NVIDIA driver
nvidia-smi

# Check GPU power limits
sudo nvidia-smi -pl 230
```

### Dashboard not accessible
```bash
# Check dashboard service
sudo systemctl status ae-dashboard

# Restart dashboard
sudo systemctl restart ae-dashboard
```

### Installation errors on Ubuntu VMs

**Problem**: NVIDIA driver or kernel headers installation fails

**Common Errors**:
- `E: Unable to locate package linux-headers-X.X.X-pve`
- `nvidia-dkms-XXX` package errors
- Multiple NVIDIA driver version conflicts

**Solutions**:

1. **Proxmox VM kernel headers issue**:
   The updated installer scripts now automatically detect Proxmox kernels and install `linux-headers-generic` instead.

2. **NVIDIA drivers in VMs**:
   - NVIDIA drivers require GPU passthrough to work in VMs
   - Without passthrough, driver installation may fail (this is expected)
   - For testing without GPU: The software will install but mining won't work

3. **Multiple driver version conflicts**:
   The installer now removes conflicting NVIDIA packages before installation.

4. **Manual cleanup** (if needed):
   ```bash
   # Remove all NVIDIA packages
   sudo apt-get remove --purge nvidia-*
   sudo apt-get autoremove

   # Reinstall with single version
   sudo apt-get install nvidia-driver-550 nvidia-utils-550
   ```

**Note**: If running in a VM for testing purposes, the installer will detect the virtual environment and continue despite driver installation failures. For actual mining, you need:
- Bare metal installation, OR
- VM with proper GPU passthrough configured

## Development

### Testing Changes

```bash
# Validate shell scripts
shellcheck build-iso.sh install-standalone.sh

# Validate JSON config
jq . config/config.json

# Test in VM before deployment
sudo ./install-standalone.sh
```

## Technical Details

- **Miner**: lolMiner (optimized for Cuckoo Cycle)
- **GPU Driver**: NVIDIA 550 series
- **Init System**: systemd with auto-start services
- **Dashboard**: Lightweight HTML/JS with Python backend

## Safety Features

- Automatic power limiting to prevent GPU damage
- Pool failover for high availability
- Temperature monitoring
- Graceful shutdown handling

## License

MIT License - See repository for details

## Support

For issues and questions, please use the GitHub issue tracker.

## Disclaimer

Cryptocurrency mining involves financial risk. Mine at your own risk. Ensure you comply with local regulations and electricity costs.
