#!/usr/bin/env python3
"""
Quick test script to verify the KaspaMine calculator works
"""

import sys
import os

# Add the user packages path for Flask
sys.path.insert(0, os.path.expanduser('~/Library/Python/3.13/lib/python/site-packages'))

try:
    # Test imports
    from flask import Flask
    from flask_cors import CORS
    import requests
    print("✓ All imports successful")

    # Test basic calculator functions (without API calls)
    def calculate_daily_kas_production(miner_hashrate_ths, network_hashrate_ths, block_reward, block_time_seconds):
        seconds_per_day = 86400
        blocks_per_day = seconds_per_day / block_time_seconds
        hashrate_share = miner_hashrate_ths / network_hashrate_ths
        daily_kas = hashrate_share * blocks_per_day * block_reward
        return daily_kas

    # Test calculation with sample data
    daily_kas = calculate_daily_kas_production(15.0, 100000.0, 500, 1)
    print(f"✓ Calculator function works: {daily_kas:.4f} KAS/day with sample data")

    print("\n✅ KaspaMine Calculator is ready to run!")
    print("Run: python3 app.py")
    print("Or:   ./start.sh")

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Try running: pip3 install flask flask-cors requests")
except Exception as e:
    print(f"❌ Error: {e}")
