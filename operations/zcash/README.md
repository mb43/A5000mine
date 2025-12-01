# Zcash Mining Operation (Z15 Pro)

**Status:** 🔜 Coming Soon

This operation is planned for Zcash (ZEC) mining using Antminer Z15 Pro ASIC miners.

## Specifications

| Spec | Value |
|------|-------|
| **Miner Model** | Antminer Z15 Pro |
| **Hashrate** | 420 KSol/s |
| **Power Consumption** | 1,510W |
| **Algorithm** | Equihash |
| **Expected Daily Income** | ~£45 per miner (est.) |

## Setup Guide

When you're ready to add Z15 Pro miners:

1. Update `config.json` with your ZEC wallet address
2. Add miner details to the `miners` array
3. Follow similar setup process as Kaspa miners:
   - Configure DHCP reservations
   - Set up nginx proxy
   - Configure pool settings
   - Enable remote access via Tailscale

## Recommended Pools

- **2miners**: `stratum+tcp://zec.2miners.com:1010` (1% fee)
- **F2Pool**: `stratum+tcp://zec.f2pool.com:3357` (2.5% fee)

## Wallet Setup

Use a shielded Zcash address (starting with `zs_`) for privacy, or a transparent address (starting with `t1_`) for simplicity.

Recommended wallets:
- **Ywallet** (iOS/Android) - supports shielded addresses
- **Zecwallet Lite** (Desktop) - full-featured
- **Trust Wallet** (Mobile) - simple, transparent addresses only

## Integration Notes

Once configured, the Z15 Pro operation will:
- Appear in the unified dashboard
- Contribute to total income projections
- Be remotely accessible via Tailscale
- Support the same monitoring and automation features as other operations

**Documentation will be added when Z15 Pro miners arrive.**
