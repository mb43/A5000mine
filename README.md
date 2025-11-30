# A5000mine - Aeternity Mining Live USB

A plug-and-play bootable Linux OS for mining Aeternity (AE) cryptocurrency on NVIDIA A5000 GPUs.

## Features

- **Bootable Live USB**: Based on Ubuntu 22.04 LTS
- **Zero Configuration**: Just add your wallet address and start mining
- **Optimized for A5000**: Achieves 4-6 G/s hashrate at 180-230W
- **Web Dashboard**: Monitor mining stats at http://localhost:8080
- **Auto-start Mining**: Begins mining immediately after boot

## Quick Start

### Method 1: Bootable USB (Recommended)

1. **Build the ISO**:
   ```bash
   sudo ./build-iso.sh
   ```

2. **Flash to USB** (8GB+ required):
   ```bash
   sudo dd if=build/a5000mine.iso of=/dev/sdX bs=4M status=progress
   ```

3. **Boot from USB** and run the configuration wizard:
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
