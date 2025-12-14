#!/usr/bin/env python3
"""Test the calculator API endpoints"""

import sys
sys.path.insert(0, '/home/user/A5000mine')

from app import run_calculator
import json

print("="*60)
print("Testing Kaspa & Zcash Calculator Backend")
print("="*60)

# Test 1: Kaspa only
print("\n1. Testing KASPA only...")
try:
    result = run_calculator(coins='kaspa')
    if result and 'kaspa' in result:
        kas_data = result['kaspa']
        print(f"   ✓ Kaspa data fetched successfully")
        print(f"   - KAS Price: £{kas_data['market']['kas_price_gbp']}")
        print(f"   - Network Hashrate: {kas_data['network']['network_hashrate_ths']:,.0f} TH/s")
        print(f"   - Block Reward: {kas_data['network']['block_reward']} KAS")
        print(f"   - Daily income (1 miner): £{kas_data['income']['emcd_pool']['daily_gbp']}")
    else:
        print("   ✗ Failed to fetch Kaspa data")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 2: Zcash only
print("\n2. Testing ZCASH only...")
try:
    result = run_calculator(coins='zcash')
    if result and 'zcash' in result:
        zec_data = result['zcash']
        print(f"   ✓ Zcash data fetched successfully")
        print(f"   - ZEC Price: £{zec_data['market']['zec_price_gbp']}")
        print(f"   - Network Hashrate: {zec_data['network']['network_hashrate_ksol']:,.0f} KSol/s")
        print(f"   - Block Reward: {zec_data['network']['block_reward']} ZEC")
        print(f"   - Daily income (1 miner): £{zec_data['income']['0_fee_pool']['daily_gbp']}")
    else:
        print("   ✗ Failed to fetch Zcash data")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 3: Both coins
print("\n3. Testing BOTH coins...")
try:
    result = run_calculator(coins='both')
    if result:
        print(f"   ✓ Both coins data fetched successfully")
        print(f"   - Coins enabled: {result['coins_enabled']}")
        print(f"   - Has Kaspa: {'kaspa' in result}")
        print(f"   - Has Zcash: {'zcash' in result}")

        if 'kaspa' in result:
            print(f"   - Kaspa daily: £{result['kaspa']['income']['emcd_pool']['daily_gbp']}")
        if 'zcash' in result:
            print(f"   - Zcash daily: £{result['zcash']['income']['0_fee_pool']['daily_gbp']}")
    else:
        print("   ✗ Failed to fetch data for both coins")
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n" + "="*60)
print("✓ Backend API tests completed!")
print("="*60)
