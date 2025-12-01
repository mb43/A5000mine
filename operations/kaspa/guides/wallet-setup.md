# Kaspa Wallet Setup Guide

## Step 1: Install Kaspium Wallet (5 minutes)

### Download Kaspium
**Best mobile wallet for Kaspa:**

- **iOS**: App Store → search "Kaspium"
- **Android**: Play Store → search "Kaspium"

### Initial Setup

1. Open app → "Create New Wallet"
2. **CRITICAL**: Write down your 12-word seed phrase on paper
   - Store in 2+ physical locations
   - Never screenshot or digital copy
   - **This is your ONLY backup**
3. Set PIN/biometric authentication
4. Tap "Receive" → copy your Kaspa address
   - Starts with `kaspa:qq...` (about 61 characters)
   - **This is YOUR_KASPA_ADDRESS for pool config**

## Step 2: Pool Account Setup (10 minutes)

### Primary Pool: EMCD (Recommended)

1. Go to https://pool.emcd.io
2. Click "Sign Up" (top right)
3. Enter email + create password
4. Verify email
5. Dashboard → "Add Worker"
   - Worker name: `Miner01` (or any name you want)
   - Your Kaspa address from Step 1

**Pool Settings:**
```
Primary: stratum+tcp://kas.emcd.io:3333
Backup:  stratum+tcp://kas.emcd.io:7777
```

### Backup Pool: 2Miners (No Account Needed)

- **URL**: `stratum+tcp://eu-kas.2miners.com:2020`
- No registration required
- Stats available at: https://2miners.com/kas-network-hashrate?address=YOUR_KASPA_ADDRESS

## Step 3: Payment Settings

### On EMCD Dashboard:

1. Settings → Payouts
2. Set minimum payout: **100 KAS** (pays out ~daily with 1 KS5M)
3. Payment method: Already set (your Kaspa address)
4. Auto-pays when you hit threshold

## Step 4: Pool Configuration for Miner

When you login to KS5M web UI, enter exactly:

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

**Replace `YOUR_KASPA_ADDRESS` with the address from Kaspium (the `kaspa:qq...` one)**

## Step 5: Monitoring Your Earnings

### EMCD Dashboard
- Login → see real-time hashrate
- Current unpaid balance
- Payment history
- Worker status

### 2Miners (Backup Check)
- Go to https://2miners.com/kas-network-hashrate
- Paste your address → see stats (no login needed)

## Expected Earnings Timeline

| Time | Expected Result |
|------|----------------|
| 10 minutes | Hashrate shows 15 TH/s on pool |
| 1 hour | First shares accepted, balance starts |
| 24 hours | 630 KAS earned (£82) |
| Daily payout | Every 24h once you hit 100 KAS minimum |

## Security Checklist

- ✅ Seed phrase written on paper (not digital)
- ✅ Seed phrase stored in 2+ locations
- ✅ Never share seed phrase with anyone
- ✅ Kaspa address copied correctly (starts with `kaspa:qq`)
- ✅ Pool password is just `x` (not a real password)

**Done!** Once miner is running, check EMCD dashboard in 10 minutes to confirm hashrate.
