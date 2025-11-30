# CLAUDE.md - a5000mine Project

## Project Overview

This repository contains a bootable live Linux OS for mining Aeternity (AE) cryptocurrency on NVIDIA A5000 GPUs. The goal is a plug-and-play mining appliance that boots from USB and immediately starts mining with minimal configuration.

## Key Components

| Component | Purpose |
|-----------|---------|
| `build-iso.sh` | Builds bootable live USB ISO (Ubuntu 22.04 base) |
| `install-standalone.sh` | Alternative installer for existing Ubuntu systems |
| `rootfs/` | Filesystem overlay with mining software and configs |
| `dashboard/` | Web-based monitoring dashboard (port 8080) |
| `config/` | Default configuration templates |

## Technical Stack

- **Base OS**: Ubuntu 22.04 LTS (minimal live image)
- **GPU Driver**: NVIDIA 550 series
- **Mining Software**: lolMiner (Cuckoo Cycle C29AE algorithm)
- **Dashboard**: Lightweight HTML/JS served via Python or Node
- **Init System**: systemd with auto-start mining service

## Target Hardware

- **GPU**: NVIDIA A5000 (24GB VRAM)
- **Expected Hashrate**: 4-6 G/s (graphs/second)
- **Power**: 180-230W (configurable)
- **Algorithm**: Cuckoo Cycle C29AE

## Mining Pools

| Pool | URL | Fee |
|------|-----|-----|
| 2miners (default) | `stratum+tcp://ae.2miners.com:4040` | 1% |
| F2Pool (backup) | `stratum+tcp://ae.f2pool.com:4040` | 2% |

## File Structure Convention

```
a5000mine/
├── CLAUDE.md              # This file
├── README.md              # User documentation
├── build-iso.sh           # ISO builder script
├── install-standalone.sh  # Standalone installer
├── build/                 # Build artifacts (gitignored)
├── config/
│   └── config.json        # Default miner config template
├── rootfs/
│   ├── etc/
│   │   └── systemd/system/
│   │       ├── ae-miner.service
│   │       └── ae-dashboard.service
│   ├── opt/ae-miner/
│   │   ├── config.json
│   │   ├── scripts/
│   │   │   ├── pre-start.sh    # GPU setup (power limits, etc.)
│   │   │   └── start-miner.sh  # Main miner launcher
│   │   └── lolMiner            # Binary (downloaded at build)
│   └── usr/local/bin/
│       ├── ae-config           # First-boot wizard
│       ├── ae-status           # Status checker
│       ├── ae-logs             # Log viewer
│       ├── ae-start            # Start mining
│       └── ae-stop             # Stop mining
└── dashboard/
    ├── index.html
    ├── app.js
    └── server.py
```

## Commands for Claude Code

When working in this repo, these are useful commands:

```bash
# Build the ISO (requires root)
sudo ./build-iso.sh

# Test the standalone installer in a VM
sudo ./install-standalone.sh

# Check syntax of shell scripts
shellcheck build-iso.sh install-standalone.sh

# Validate JSON configs
jq . config/config.json
```

## Development Guidelines

1. **Shell Scripts**: Use bash, include `set -e` for safety, add logging with timestamps
2. **Config Format**: JSON with sensible defaults, validated with jq
3. **Service Files**: systemd units with proper dependencies and restart policies
4. **User Experience**: Minimize required config - wallet address should be the only mandatory input
5. **Error Handling**: Scripts should fail gracefully with helpful error messages

## Config Schema

The main config file (`/opt/ae-miner/config.json`) structure:

```json
{
    "wallet": "ak_...",           // Required: AE wallet address
    "worker_name": "rig-01",      // Optional: identifier for pool
    "pool": {
        "url": "stratum+tcp://ae.2miners.com:4040",
        "backup_url": "stratum+tcp://ae.f2pool.com:4040"
    },
    "gpu": {
        "device_id": 0,
        "power_limit": 230,       // Watts (A5000 TDP)
        "core_offset": 0,         // MHz
        "mem_offset": 0           // MHz
    },
    "dashboard": {
        "enabled": true,
        "port": 8080
    }
}
```

## Current Status / TODO

- [x] Core build system
- [x] lolMiner integration
- [x] NVIDIA driver installation
- [x] Auto-start systemd service
- [x] Configuration wizard (ae-config)
- [x] Web dashboard
- [ ] Multi-GPU support
- [ ] Remote management API
- [ ] OTA updates
- [ ] Temperature-based throttling
- [ ] Pool failover monitoring

## Notes for Claude

- Always preserve existing wallet addresses when modifying configs
- The A5000 has 230W TDP - don't set power limits above this
- lolMiner is the preferred miner for Cuckoo Cycle on NVIDIA
- Dashboard runs on port 8080 - keep this configurable
- Boot process: GRUB → systemd → ae-miner.service → mining starts
- User should only need to run `ae-config` once after first boot
