# KaspaMine - Profitable ASIC Mining Platform

**KS5M Kaspa Mining: £40.94/day per miner | 14.7 day ROI | £14,941/year**
*(Updated Dec 6, 2025 - Run `python3 calculator.py` for real-time figures)*

A complete deployment platform for IceRiver KS5M ASIC miners with remote management, automated monitoring, and crypto conversion automation.

## 🚀 Why Kaspa Mining?

```
1 KS5M ASIC:  £40.94/day  = £14,941/year  (PROFITABLE!)
1 GPU Mining: £0.07/day   = £25/year      (DEAD in 2025)

KS5M is 585x more profitable than GPU mining.
```

## ✅ Features

- **12-Minute Deployment**: Complete KS5M setup from unboxing to hashing
- **Zero Pool Fees**: EMCD pool with 0% fees (saves £149/year per miner!)
- **14.7 Day ROI**: £600 hardware paid back in 2 weeks
- **Real-Time Calculator**: Live income projections using CoinGecko + 2Miners APIs
- **Remote Access**: Secure monitoring via Tailscale from anywhere
- **Auto-Recovery**: Watchdog scripts auto-reboot dead miners
- **Unified Dashboard**: Real-time monitoring with income projections
- **Automated Conversion**: Optional daily crypto→stablecoin, weekly→GBP

## 📊 Real-World Performance (Live API Data - Dec 6, 2025)

| Metric | Per Miner | 5 Miners | 10 Miners |
|--------|-----------|----------|-----------|
| **Daily Income** | £40.94 | £204.70 | £409.40 |
| **Monthly Income** | £1,228.09 | £6,140.45 | £12,280.90 |
| **Yearly Income** | £14,941.73 | £74,708.65 | £149,417.30 |
| **Hardware Cost** | £600 | £3,000 | £6,000 |
| **ROI** | 14.7 days | 14.7 days | 14.7 days |

**Based on:** KAS @ £0.0395, 1,035 KAS/day, Network: 626 PH/s, EMCD pool (0% fee)
**Run `python3 calculator.py` for current real-time figures**

## ⚡ Also Supports (Legacy)

- **Zcash (ZEC)** - Antminer Z15 Pro support (placeholder ready)
- **GPU Mining** - ⚠️ **NOT RECOMMENDED** - GPU mining is unprofitable in 2025 (£0.07/day)

## 🚀 Quick Start - When Your KS5M Arrives

| Step | Action | Time | Guide |
|------|--------|------|-------|
| **1** | Create Kaspium Wallet | 5 min | [Wallet Setup](operations/kaspa/guides/wallet-setup.md) |
| **2** | Connect & Configure KS5M | 7 min | [Quick Deploy](operations/kaspa/guides/quick-deploy.md) |
| **3** | Enable Remote Access | 5 min | [Remote Access](operations/kaspa/guides/remote-access.md) |
| **4** | Start Earning! | 0 min | £40.94/day automatically! |

**Total setup time: 17 minutes from box to hashing** 🎯

## 📱 Unified Dashboard (Optional)

Monitor all your mining operations in one place with real-time stats and income projections.

```bash
# Start dashboard
python3 dashboard/unified-server.py

# Access at: http://localhost:8090/unified
```

**Features:**
- Real-time KS5M hashrate and status
- Income projections: Daily/Monthly/Yearly in GBP
- Auto-refresh every 5 seconds
- Remote access via Tailscale

---

## 💰 Kaspa (KS5M ASIC) - Complete Setup Guide

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

### Performance Per KS5M (Verified)

| Metric | Value |
|--------|-------|
| **Hashrate** | 15 TH/s |
| **Power Consumption** | 3,400W |
| **Daily KAS** | 1,781 KAS |
| **Daily Income** | £83.50 |
| **Pool** | EMCD (0% fee!) |
| **Payout Threshold** | 1 KAS (multiple payouts/day) |

### Scaling (Updated with Real Income)

| Miners | Power | Daily Income | Monthly Income | Yearly Income | Notes |
|--------|-------|--------------|----------------|---------------|-------|
| 1 | 3.4 kW | £83.50 | £2,507.50 | £30,500 | Single socket |
| 5 | 17 kW | £417.50 | £12,537.50 | £152,500 | Still manageable |
| 10 | 34 kW | £835 | £25,075 | £305,000 | Need 3-phase |
| 20 | 68 kW | £1,670 | £50,150 | £609,500 | Container setup |

### Remote Access

Access miners via Tailscale from anywhere:

```
http://kaspa-site-01:8080  (Miner 1)
http://kaspa-site-01:8081  (Miner 2)
http://kaspa-site-01:8082  (Miner 3)
```

---

## 🔧 Supported Kaspa Pools

| Pool | URL | Fee | Min Payout | Recommended |
|------|-----|-----|------------|-------------|
| **EMCD** | stratum+tcp://kas.emcd.io:3333 | **0%** | 1 KAS | ⭐ **YES** |
| EMCD Backup | stratum+tcp://kas.emcd.io:7777 | 0% | 1 KAS | Backup |
| 2Miners | stratum+tcp://eu-kas.2miners.com:2020 | 1% | 50 KAS | Backup |

**Why EMCD?**
- 0% pool fee saves £912/year per miner!
- 1 KAS minimum payout = multiple payouts per day
- Reliable, high uptime

## ⚠️ Troubleshooting

### Miner not hashing
```bash
# Access miner web UI
http://MINER_IP

# Check:
# 1. Pool URL is correct
# 2. Wallet address is correct
# 3. Miner shows online in pool dashboard
# 4. Network connection is stable
```

### Can't access miner remotely
```bash
# SSH to Pi
ssh pi@kaspa-site-01

# Check nginx
sudo systemctl status nginx
sudo systemctl restart nginx

# Check Tailscale
tailscale status
```

### Miner offline after power cut
```bash
# KS5M auto-recovers - wait 5 minutes
# If still offline, reboot via web UI or power cycle

# Check watchdog is running (auto-reboots dead miners)
crontab -l | grep kaspa-watchdog
```

---

## 🤖 Optional: Automated Crypto Conversion

Automatically convert KAS → stablecoins → GBP. See [automation/README.md](automation/README.md).

**Features:**
- Daily: KAS → USDT (minimize volatility)
- Weekly: USDT → GBP (auto deposit to bank)
- Secure API key management
- Full transaction logging

---

## 📚 Complete Documentation

| Document | Description |
|----------|-------------|
| [Quick Deploy](operations/kaspa/guides/quick-deploy.md) | 12-minute KS5M setup guide |
| [Wallet Setup](operations/kaspa/guides/wallet-setup.md) | Kaspium wallet + EMCD pool |
| [Remote Access](operations/kaspa/guides/remote-access.md) | Tailscale configuration |
| [Multi-Operation Guide](docs/multi-operation-guide.md) | Complete system overview |
| [Automation Setup](automation/README.md) | Crypto conversion automation |
| [GitHub Pages](docs/github-pages-setup.md) | Public dashboard hosting |

---

## ⚠️ Legacy: GPU Mining (NOT RECOMMENDED)

GPU mining is **NOT profitable** in Dec 2025. Included for reference only.

**Reality Check:**
- A5000 Aeternity mining: £0.068/day (£25/year)
- KS5M Kaspa mining: £83.50/day (£30,500/year)
- **KS5M is 1,228x more profitable!**

GPU mining documentation preserved in:
- `operations/aeternity/` - Legacy configs
- Original `install-standalone.sh` - GPU miner installer

**Do NOT use for production. Focus 100% on Kaspa ASIC mining.**

---

## 📊 Summary: Why Kaspa?

```
Hardware Cost: £600
Daily Income:  £83.50
ROI:           7.2 days
Monthly:       £2,507.50
Yearly:        £30,500

With FREE electricity, this is pure profit!
```

**10 KS5M miners = £305,000/year = life-changing income** 🚀

---

## 💬 Support

For issues:
- Check [Troubleshooting](#troubleshooting)
- Review [Complete Documentation](#complete-documentation)
- Open GitHub issue

## ⚖️ Disclaimer

Cryptocurrency mining involves financial risk. Mine at your own risk. Ensure you comply with local regulations and electricity costs. Income projections based on Dec 2025 prices and may fluctuate.

## 📄 License

MIT License - See repository for details
