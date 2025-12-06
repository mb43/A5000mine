# GPU Mining Deprecation Notice

**⚠️ GPU cryptocurrency mining is NO LONGER PROFITABLE as of December 2025.**

## Reality Check (Verified Dec 1, 2025)

### NVIDIA A5000 Mining Profitability:

| Coin | Daily Income | Monthly Income | Yearly Income |
|------|--------------|----------------|---------------|
| Aeternity (AE) | £0.068 | £2.04 | £24.82 |
| Ethereum Classic | £0.47 | £14.10 | £169 |
| Ravencoin | £0.25 | £7.66 | £92 |
| Ergo | £0.39 | £11.70 | £140 |

**Best case: £169/year**

### Compare to KS5M ASIC:

| Hardware | Daily | Monthly | Yearly | ROI |
|----------|-------|---------|--------|-----|
| **KS5M ASIC** | **£83.50** | **£2,507.50** | **£30,500** | **7.2 days** |
| A5000 GPU | £0.47 | £14.10 | £169 | Never |

**KS5M is 180x more profitable than the best GPU option!**

---

## Why GPU Mining Died

1. **ASIC dominance**: Purpose-built hardware 100-1000x more efficient
2. **Low coin prices**: 2025 crypto bear market
3. **High difficulty**: Network hashrate increased while prices dropped
4. **Electricity costs**: Even with FREE power, barely breaks even

---

## What Happened to £30-40/Day?

You may have seen estimates of £30-40/day for A5000 mining. **This was wrong!**

**Root cause:** Calculator had wrong hashrate input:
- Entered: 10,076 Gps (= 2,015 A5000 GPUs!)
- Reality: 5 Gps (= 1 A5000 GPU)

That £30-40/day was for a **2,000-GPU farm**, not a single card!

---

## GPU Mining Alternatives

If you have an A5000, consider:

### Option 1: GPU Rental (Slightly Better)
- Rent on Vast.ai or RunPod
- Income: £5-12/day (30-50% utilization)
- Requires 24/7 uptime, stable network
- **Still 7-17x less than KS5M!**

### Option 2: Sell the GPU
- Sell A5000, buy 3-4 more KS5M miners
- **Much better ROI!**

### Option 3: Keep for AI/ML
- Use for AI inference, training, rendering
- More valuable than mining

---

## Legacy Documentation

GPU mining code and guides preserved for reference:

- `operations/aeternity/` - Aeternity GPU configs
- `install-standalone.sh` - GPU miner installer
- `build-iso.sh` - Bootable USB builder
- `rootfs/` - GPU miner system files

**DO NOT use for production mining in 2025!**

---

## Recommendation

**Focus 100% on ASIC mining:**

- ✅ Kaspa (KS5M): £83.50/day, 7.2 day ROI
- ✅ Zcash (Z15 Pro): £45/day (when available)
- ❌ GPU mining: £0.47/day, waste of time

**One £600 KS5M makes more than 177 A5000 GPUs!**

---

## Sources

All data verified from:
- [WhatToMine A5000 Calculator](https://whattomine.com/gpus/71-nvidia-rtx-a5000)
- [2Miners Aeternity Calculator](https://2miners.com/ae-mining-calculator)
- [Kryptex A5000 Profitability](https://www.kryptex.com/en/hardware/nvidia-rtx-a5000)
- [Hashrate.no A5000 Estimates](https://hashrate.no/gpus/a5000)

Updated: December 1, 2025
