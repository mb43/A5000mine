# Multi-Operation Mining Guide

A5000mine now supports multiple discrete mining operations running simultaneously:

- **Aeternity (AE)** - GPU mining with NVIDIA A5000
- **Kaspa (KAS)** - ASIC mining with KS5M miners
- **Zcash (ZEC)** - ASIC mining with Z15 Pro (coming soon)

## Architecture

```
A5000mine/
├── operations/              # Discrete mining operations
│   ├── aeternity/          # GPU: NVIDIA A5000
│   │   ├── config.json
│   │   ├── guides/
│   │   └── scripts/
│   ├── kaspa/              # ASIC: KS5M
│   │   ├── config.json
│   │   ├── guides/
│   │   │   ├── wallet-setup.md
│   │   │   ├── remote-access.md
│   │   │   └── quick-deploy.md
│   │   └── scripts/
│   │       └── setup-pi.sh
│   └── zcash/              # ASIC: Z15 Pro (planned)
│       ├── config.json
│       └── README.md
├── dashboard/              # Unified monitoring
│   ├── unified-server.py   # Multi-operation API
│   └── unified-dashboard.html
└── docs/
    └── multi-operation-guide.md (this file)
```

## Quick Start

### 1. Aeternity (GPU Mining)

**Hardware:** NVIDIA A5000 GPU(s)

**Setup:**
```bash
# Install on Ubuntu system
sudo ./install-standalone.sh

# Configure wallet
sudo ae-config

# Mining starts automatically
```

**Expected Performance:**
- Hashrate: 4-6 G/s per GPU
- Power: 230W per GPU
- Income: ~£8.50 per GPU per day

**Guides:** See existing README.md

---

### 2. Kaspa (ASIC Mining)

**Hardware:** IceRiver KS5M ASIC miners

**Quick Deploy:**
```bash
# One-time Pi setup
cd operations/kaspa/scripts
sudo ./setup-pi.sh

# For each miner, see:
operations/kaspa/guides/quick-deploy.md
```

**Expected Performance:**
- Hashrate: 15 TH/s per miner
- Power: 3,400W per miner
- Income: ~£82 per miner per day

**Guides:**
- [Wallet & Pool Setup](../operations/kaspa/guides/wallet-setup.md)
- [Remote Access via Tailscale](../operations/kaspa/guides/remote-access.md)
- [Quick Deployment](../operations/kaspa/guides/quick-deploy.md)

---

### 3. Zcash (Coming Soon)

**Hardware:** Antminer Z15 Pro

**Status:** Placeholder ready - see `operations/zcash/README.md`

**Expected Performance:**
- Hashrate: 420 KSol/s per miner
- Power: 1,510W per miner
- Income: ~£45 per miner per day (estimated)

---

## Unified Dashboard

View all operations in one place with real-time stats and income projections.

### Access the Dashboard

```bash
# Start unified dashboard server
cd dashboard
python3 unified-server.py

# Access at:
http://localhost:8090/unified
```

### Features

- **Real-time monitoring** of all mining operations
- **Income projections**: Daily, Monthly, Yearly in GBP
- **GPU stats**: Temperature, power, utilization (Aeternity)
- **ASIC status**: Per-miner hashrate and health (Kaspa/Zcash)
- **Auto-refresh**: Updates every 5 seconds

### Dashboard Views

| Section | What It Shows |
|---------|---------------|
| Income Projections | Total earnings across all operations |
| Income Breakdown | Per-operation daily/monthly/yearly income |
| Aeternity Card | GPU stats, hashrate, shares |
| Kaspa Card | Miner status, total hashrate, online/offline miners |
| Zcash Card | Placeholder (when configured) |

---

## Configuration

### Operation Configs

Each operation has its own `config.json`:

**Aeternity:** `operations/aeternity/config.json`
```json
{
    "operation": "aeternity",
    "wallet": "ak_YOUR_WALLET",
    "gpu": {
        "power_limit": 230
    },
    "income": {
        "daily_per_gpu_gbp": 8.5
    }
}
```

**Kaspa:** `operations/kaspa/config.json`
```json
{
    "operation": "kaspa",
    "wallet": "kaspa:YOUR_WALLET",
    "miners": [
        {
            "name": "Miner01",
            "ip": "192.168.1.100",
            "proxy_port": 8080
        }
    ],
    "income": {
        "daily_per_miner_gbp": 82
    }
}
```

**Zcash:** `operations/zcash/config.json`
```json
{
    "operation": "zcash",
    "wallet": "t1_YOUR_WALLET",
    "miners": [],
    "income": {
        "daily_per_miner_gbp": 45
    }
}
```

### Updating Income Estimates

Crypto prices fluctuate. Update income estimates regularly:

1. Edit operation config files
2. Update `daily_per_gpu_gbp` or `daily_per_miner_gbp`
3. Restart dashboard: `python3 unified-server.py`

---

## Adding a New Operation

Want to add Bitcoin, Ethereum, or another coin? Here's how:

### 1. Create Operation Directory

```bash
mkdir -p operations/mycoin/{guides,docs,scripts}
```

### 2. Create Config File

`operations/mycoin/config.json`:
```json
{
    "operation": "mycoin",
    "hardware": "ASIC",
    "wallet": "CONFIGURE_ME",
    "miners": [],
    "income": {
        "daily_per_miner_gbp": 100
    }
}
```

### 3. Update Dashboard

The unified dashboard auto-discovers operations from the `operations/` directory. Just restart:

```bash
cd dashboard
python3 unified-server.py
```

Your new operation will appear automatically!

### 4. Add Guides

Create operation-specific guides in `operations/mycoin/guides/`:
- `wallet-setup.md`
- `pool-setup.md`
- `quick-deploy.md`

---

## Remote Access

All operations can be accessed remotely via **Tailscale**.

### Aeternity Dashboard
```
http://kaspa-site-01:8090/unified
```

### Kaspa Miners
```
http://kaspa-site-01:8080  (Miner 1)
http://kaspa-site-01:8081  (Miner 2)
http://kaspa-site-01:8082  (Miner 3)
```

### SSH Access
```bash
ssh pi@kaspa-site-01
```

---

## Income Projections

### Current Setup Example

| Operation | Units | Daily | Monthly | Yearly |
|-----------|-------|-------|---------|--------|
| Aeternity | 2 GPUs | £17.00 | £510 | £6,205 |
| Kaspa | 5 Miners | £410.00 | £12,300 | £149,650 |
| Zcash | 0 Miners | £0.00 | £0 | £0 |
| **TOTAL** | - | **£427.00** | **£12,810** | **£155,855** |

### Scaling Example (10 KS5M Miners)

| Operation | Units | Daily | Monthly | Yearly |
|-----------|-------|-------|---------|--------|
| Aeternity | 2 GPUs | £17.00 | £510 | £6,205 |
| Kaspa | 10 Miners | £820.00 | £24,600 | £299,300 |
| **TOTAL** | - | **£837.00** | **£25,110** | **£305,505** |

*Note: Income estimates based on November 2025 prices and difficulty. Update regularly.*

---

## Troubleshooting

### Dashboard Not Showing Operation

**Check config file exists:**
```bash
ls operations/*/config.json
```

**Check config is valid JSON:**
```bash
jq . operations/kaspa/config.json
```

**Restart dashboard:**
```bash
pkill -f unified-server.py
python3 dashboard/unified-server.py
```

### Kaspa Miners Showing Offline

**Check network:**
```bash
# From Pi
ping 192.168.1.100
```

**Check nginx:**
```bash
sudo systemctl status nginx
sudo systemctl restart nginx
```

**Check Tailscale:**
```bash
tailscale status
```

### GPU Not Showing in Dashboard

**Check NVIDIA driver:**
```bash
nvidia-smi
```

**Check ae-miner service:**
```bash
sudo systemctl status ae-miner
```

---

## Best Practices

1. **Update income estimates monthly** based on current crypto prices
2. **Monitor all operations** via unified dashboard daily
3. **Keep configs backed up** in git repository
4. **Use Tailscale** for secure remote access (no port forwarding)
5. **Enable auto-reboot** for ASIC miners (watchdog scripts)
6. **Separate wallets** for each operation (easier accounting)

---

## Next Steps

- [ ] Configure Kaspa wallet and add first KS5M
- [ ] Update income estimates for current market conditions
- [ ] Set up Tailscale remote access
- [ ] Add Zcash operation when Z15 Pro arrives
- [ ] Consider adding automation for crypto conversions

For automation (daily crypto→stablecoin, weekly→GBP), see upcoming automation guides.
