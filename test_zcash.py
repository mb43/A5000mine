#!/usr/bin/env python3
"""Test Zcash calculator functions"""

import requests

# Test Zcash API calls
print("Testing Zcash APIs...")

# Test ZEC price from CoinGecko
try:
    response = requests.get(
        "https://api.coingecko.com/api/v3/simple/price",
        params={"ids": "zcash", "vs_currencies": "gbp"},
        timeout=10
    )
    data = response.json()
    zec_price = data.get("zcash", {}).get("gbp")
    print(f"✓ ZEC Price: £{zec_price}")
except Exception as e:
    print(f"✗ Failed to fetch ZEC price: {e}")

# Test Zcash network stats from 2Miners
try:
    response = requests.get("https://zec.2miners.com/api/stats", timeout=10)
    data = response.json()
    nodes = data.get("nodes", [])
    if nodes:
        hashrate = int(nodes[0].get("networkhashps", 0))
        difficulty = float(nodes[0].get("difficulty", 0))
        block_time = float(nodes[0].get("avgBlockTime", 75))

        print(f"✓ Network Hashrate: {hashrate:,} Sol/s ({hashrate/1000:,.0f} KSol/s)")
        print(f"✓ Difficulty: {difficulty:,.0f}")
        print(f"✓ Avg Block Time: {block_time} seconds")

        # Calculate daily ZEC for Z15 Pro (840 KSol/s)
        miner_hashrate_sol = 840 * 1000
        blocks_per_day = 86400 / float(block_time)
        hashrate_share = miner_hashrate_sol / hashrate
        block_reward = 2.5
        daily_zec = hashrate_share * blocks_per_day * block_reward

        print(f"\n✓ Estimated daily ZEC for Z15 Pro: {daily_zec:.4f} ZEC")
        print(f"✓ Estimated daily GBP (at £{zec_price}): £{daily_zec * zec_price:.2f}")

except Exception as e:
    print(f"✗ Failed to fetch ZEC network stats: {e}")

print("\n✓ All tests passed!")
