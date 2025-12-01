# Automated Crypto Conversion System

Automatically convert mining rewards to stablecoins (daily) and GBP (weekly).

## Features

- **Daily Conversion**: Mining rewards (AE, KAS, ZEC) → Stablecoins (USDT/USDC)
- **Weekly Conversion**: Stablecoins → GBP via payment providers
- **Multiple Exchanges**: Kraken, Binance, Coinbase support
- **Payment Providers**: Wise, Revolut, PayPal support
- **Secure**: API key management, 2FA support, transaction logging
- **Automated**: Runs via cron, fully hands-off
- **Notifications**: Email/Telegram alerts for conversions

## How It Works

```
┌─────────────────┐
│  Mining Rewards │  (Daily payouts from pools)
│  AE, KAS, ZEC   │
└────────┬────────┘
         │
         │ Daily (00:00 UTC)
         ▼
┌─────────────────┐
│   Exchange      │  Convert to USDT/USDC
│  (Kraken, etc)  │  (Minimize volatility)
└────────┬────────┘
         │
         │ Weekly (Monday 00:00 UTC)
         ▼
┌─────────────────┐
│ Payment Provider│  Convert to GBP
│  (Wise, etc)    │  (Cash out to bank)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Your Bank      │  GBP in your account
└─────────────────┘
```

## Quick Setup

### 1. Install Dependencies

```bash
cd automation
pip3 install -r requirements.txt
```

### 2. Create Configuration

```bash
# Copy example config
cp config.example.json config.json

# Add to .gitignore (IMPORTANT!)
echo "automation/config.json" >> ../.gitignore

# Edit with your API keys
nano config.json
```

### 3. Configure API Keys

You'll need API keys from:

**Exchanges:**
- [Kraken](https://www.kraken.com/u/security/api) (recommended)
- [Binance](https://www.binance.com/en/my/settings/api-management) (optional)
- [Coinbase](https://www.coinbase.com/settings/api) (optional)

**Payment Providers:**
- [Wise](https://wise.com/help/articles/2958112/wise-api) (recommended)
- [Revolut Business](https://developer.revolut.com/docs/api/business/) (optional)

### 4. Test Manually

```bash
# Test daily conversion (crypto → stablecoin)
python3 crypto-converter.py

# Check logs
tail -f /var/log/crypto-converter.log
```

### 5. Set Up Automation

```bash
# Add to crontab
crontab -e

# Add these lines:
# Daily conversion at midnight UTC
0 0 * * * /usr/bin/python3 /home/user/A5000mine/automation/crypto-converter.py

# Weekly conversion every Monday at midnight UTC
0 0 * * 1 /usr/bin/python3 /home/user/A5000mine/automation/crypto-converter.py
```

## Configuration Guide

### Daily Conversion Settings

```json
{
  "daily_conversion": {
    "enabled": true,
    "target_stablecoin": "USDT",
    "min_amounts": {
      "aeternity": 100,   // Only convert if ≥100 AE
      "kaspa": 500,       // Only convert if ≥500 KAS
      "zcash": 1          // Only convert if ≥1 ZEC
    }
  }
}
```

**Why minimum amounts?**
- Avoid excessive exchange fees on small amounts
- Wait for daily payouts to accumulate
- More efficient conversion

### Weekly Conversion Settings

```json
{
  "weekly_conversion": {
    "enabled": true,
    "provider": "wise",
    "min_amount_usd": 500,  // Only convert if ≥$500 USDT
    "destination": {
      "sort_code": "XX-XX-XX",
      "account_number": "XXXXXXXX"
    }
  }
}
```

### Exchange Configuration

#### Kraken (Recommended)

**Pros:**
- Supports AE, KAS, ZEC
- Low fees (0.16-0.26%)
- Excellent security
- Crypto → Stablecoin support

**Setup:**
1. Go to [Kraken API](https://www.kraken.com/u/security/api)
2. Create API key with permissions:
   - Query Funds
   - Create & Modify Orders
3. Add to `config.json`:

```json
{
  "exchanges": {
    "primary": "kraken",
    "kraken": {
      "api_key": "YOUR_KEY",
      "api_secret": "YOUR_SECRET",
      "enabled": true
    }
  }
}
```

#### Binance (Alternative)

**Pros:**
- Supports KAS, ZEC
- Very low fees (0.1%)
- High liquidity

**Note:** Does not support AE - use Kraken for AE

**Setup:**
1. Go to [Binance API](https://www.binance.com/en/my/settings/api-management)
2. Create API key with permissions:
   - Read Info
   - Enable Spot & Margin Trading
3. Add to `config.json`

### Payment Provider Configuration

#### Wise (Recommended)

**Pros:**
- Low fees (0.5%)
- Real exchange rates
- Fast transfers (1-2 days)
- API support

**Setup:**
1. Create Wise Business account
2. Get API key from [Wise API](https://wise.com/help/articles/2958112/wise-api)
3. Add UK bank account as recipient
4. Add to `config.json`:

```json
{
  "payment_providers": {
    "wise": {
      "api_key": "YOUR_WISE_API_KEY",
      "profile_id": "YOUR_PROFILE_ID",
      "enabled": true
    }
  }
}
```

#### Revolut Business (Alternative)

**Pros:**
- Lower fees (0.2%)
- Instant transfers
- Multi-currency support

**Cons:**
- Requires business account
- More complex setup

**Setup:**
1. Create Revolut Business account
2. Apply for API access
3. Follow [Revolut API docs](https://developer.revolut.com/docs/api/business/)

## Security Best Practices

### API Key Security

1. **Never commit `config.json` to git**
   ```bash
   # Verify it's in .gitignore
   git status
   # Should NOT show config.json
   ```

2. **Use API key restrictions**
   - Limit to specific IPs (Tailscale IPs)
   - Enable withdrawal whitelist
   - Set daily withdrawal limits
   - Require 2FA for API key creation

3. **Encrypt sensitive data**
   ```bash
   # Store config.json encrypted
   gpg -c config.json

   # Decrypt when needed
   gpg -d config.json.gpg > config.json
   ```

### Exchange Security

1. **Enable 2FA** on all exchange accounts
2. **Set withdrawal limits** (e.g., max $10k/day)
3. **Use withdrawal whitelists** (only allow transfers to your Wise account)
4. **Monitor transactions** via notifications

### Transaction Limits

Set maximum conversion amounts to prevent accidents:

```json
{
  "security": {
    "max_daily_conversion_usd": 10000,
    "max_weekly_conversion_usd": 50000
  }
}
```

## Notifications

Get notified of every conversion:

### Email Notifications

```json
{
  "security": {
    "enable_notifications": true,
    "notification_email": "your-email@example.com"
  }
}
```

### Telegram Notifications

1. Create Telegram bot via [@BotFather](https://t.me/botfather)
2. Get your chat ID from [@userinfobot](https://t.me/userinfobot)
3. Add to config:

```json
{
  "security": {
    "notification_methods": ["telegram"],
    "telegram_bot_token": "YOUR_BOT_TOKEN",
    "telegram_chat_id": "YOUR_CHAT_ID"
  }
}
```

## Example Conversion Flow

### Daily (Crypto → USDT)

```
10:00 AM: Kaspa pool pays out 630 KAS
00:00 AM: Automation checks balance = 630 KAS
          ✓ Above minimum (500 KAS)
          ✓ Convert 630 KAS → $81.90 USDT
          ✓ USDT stored in Kraken account
          ✓ Notification sent
```

### Weekly (USDT → GBP)

```
Monday 00:00: Check USDT balance = $574.30
              ✓ Above minimum ($500)
              ✓ Convert $574.30 → £453.70 GBP
              ✓ Transfer to UK bank account
              ✓ Arrive in 1-2 days
              ✓ Notification sent
```

## Transaction History

All conversions are logged to `state.json`:

```json
{
  "conversion_history": [
    {
      "type": "daily",
      "operation": "kaspa",
      "timestamp": "2025-12-01T00:00:00",
      "from_amount": 630,
      "from_currency": "KAS",
      "to_amount": 81.90,
      "to_currency": "USDT",
      "exchange": "kraken",
      "tx_id": "kraken_12345"
    },
    {
      "type": "weekly",
      "timestamp": "2025-12-02T00:00:00",
      "from_amount": 574.30,
      "from_currency": "USDT",
      "to_amount": 453.70,
      "to_currency": "GBP",
      "provider": "wise",
      "tx_id": "wise_67890"
    }
  ]
}
```

## Monitoring

### Check Status

```bash
# View recent conversions
cat automation/state.json | jq .conversion_history[-5:]

# Check logs
tail -f /var/log/crypto-converter.log

# Test configuration
python3 automation/crypto-converter.py --dry-run
```

### Dashboard Integration

The unified dashboard shows conversion stats:
- Total converted to stablecoins
- Total converted to GBP
- Next scheduled conversion
- Conversion history

## Troubleshooting

### Conversion Not Running

```bash
# Check crontab
crontab -l

# Check logs
tail -50 /var/log/crypto-converter.log

# Test manually
python3 automation/crypto-converter.py
```

### API Key Errors

```bash
# Verify API keys
python3 -c "import json; print(json.load(open('automation/config.json'))['exchanges']['kraken']['api_key'])"

# Test exchange connection
# (Add test script to verify API keys work)
```

### Insufficient Balance

The automation checks minimum amounts - make sure:
- Daily payouts are hitting your wallets
- Minimum amounts aren't set too high
- Exchange accounts have sufficient balance

## Cost Analysis

### Daily Conversion (Crypto → USDT)

| Exchange | Fee | Example |
|----------|-----|---------|
| Kraken | 0.16% | £82 → £81.87 (-13p) |
| Binance | 0.10% | £82 → £81.92 (-8p) |

### Weekly Conversion (USDT → GBP)

| Provider | Fee | Example |
|----------|-----|---------|
| Wise | 0.5% | £500 → £497.50 (-£2.50) |
| Revolut | 0.2% | £500 → £499.00 (-£1.00) |

### Monthly Totals (10 KS5M Example)

```
Monthly Income: £24,600

Daily conversions:  30 × £0.40 = £12.00
Weekly conversions: 4 × £12.30 = £49.20

Total fees: £61.20/month (0.25%)
Net income: £24,538.80/month
```

**Fees are minimal compared to value of automation!**

## Advanced Features

### Tax Reporting

Export conversion history for tax purposes:

```bash
python3 automation/export-tax-report.py --year 2025 --format csv
```

### Custom Schedules

Run conversions at different times:

```python
# In config.json
{
  "daily_conversion": {
    "schedule": "daily at 12:00 UTC"  // Noon instead of midnight
  }
}
```

### Partial Conversions

Convert only a percentage of balance:

```json
{
  "daily_conversion": {
    "convert_percentage": 80  // Keep 20% in crypto
  }
}
```

## Support

For issues or questions:
- Check logs: `/var/log/crypto-converter.log`
- Review state: `automation/state.json`
- Test manually before enabling cron
- Start with small amounts to test

## Disclaimer

- Cryptocurrency trading involves risk
- Exchange rates fluctuate
- Transaction fees apply
- Tax implications vary by jurisdiction
- Test thoroughly before automating large amounts
- Keep API keys secure
- Monitor conversions regularly

**Always start with small test amounts!**
