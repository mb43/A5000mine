#!/usr/bin/env python3
"""
KaspaMine Real-Time Income Calculator Web App
A Flask-based web application for calculating Kaspa mining income projections
"""

import json
import requests
import sys
from datetime import datetime
from typing import Dict, Optional
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import threading
import time

# ============================================================================
# Configuration
# ============================================================================

KS5M_HASHRATE_THS = 15.0  # TH/s per KS5M miner
KS5M_POWER_W = 3400        # Watts per miner
KS5M_COST_GBP = 600        # Hardware cost

# API Endpoints
COINGECKO_API = "https://api.coingecko.com/api/v3"
KASPA_EXPLORER_API = "https://api.kaspa.org"  # Primary
KASPA_EXPLORER_BACKUP = "https://explorer.kaspa.org/api"  # Backup

# Colors for terminal output (keeping for any CLI usage)
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
RESET = '\033[0m'

# ============================================================================
# Flask App Setup
# ============================================================================

app = Flask(__name__,
            template_folder='templates',
            static_folder='static')
CORS(app)

# Global variable to store latest results
latest_results = None
last_update = None

# ============================================================================
# Data Fetching Functions
# ============================================================================

def fetch_kas_price() -> Optional[float]:
    """
    Fetch current KAS price in GBP from CoinGecko
    Returns: Price in GBP or None if failed
    """
    try:
        url = f"{COINGECKO_API}/simple/price"
        params = {
            "ids": "kaspa",
            "vs_currencies": "gbp"
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        price = data.get("kaspa", {}).get("gbp")
        if price:
            return float(price)

    except Exception as e:
        print(f"Error fetching KAS price from CoinGecko: {e}")

    return None

def fetch_network_stats() -> Optional[Dict]:
    """
    Fetch Kaspa network statistics from 2Miners API (REAL DATA ONLY)
    Returns: Dict with network_hashrate_ths, block_reward, block_time_seconds
    """
    try:
        url = "https://kas.2miners.com/api/stats"
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()

        # Extract real network hashrate from nodes[0].networkhashps
        nodes = data.get("nodes", [])
        if not nodes:
            return None

        network_hashrate_hs = int(nodes[0].get("networkhashps", 0))

        if network_hashrate_hs <= 0:
            return None

        # Get difficulty if available
        difficulty = data.get("nodes", [{}])[0].get("difficulty", 0)

        stats = {
            "network_hashrate_ths": network_hashrate_hs / 1e12,  # Convert H/s to TH/s
            "block_reward": 500,  # KAS per block (decreases slowly over time)
            "block_time_seconds": 1,  # Kaspa block time
            "difficulty": difficulty,
            "source": "2Miners API (Real-time)"
        }

        return stats

    except Exception as e:
        print(f"2Miners API failed: {e}")
        return None

def fetch_2miners_stats() -> Optional[Dict]:
    """
    Fetch stats from 2Miners pool API
    Returns: Dict with pool hashrate, miners, fee
    """
    try:
        url = "https://kas.2miners.com/api/stats"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        stats = {
            "pool_hashrate": data.get("hashrate", 0),
            "pool_miners": data.get("workers", 0),
            "pool_fee": data.get("fee", 1.0),
        }

        return stats

    except Exception as e:
        print(f"Could not fetch 2Miners stats: {e}")
        return None

# ============================================================================
# Income Calculation Functions
# ============================================================================

def calculate_daily_kas_production(
    miner_hashrate_ths: float,
    network_hashrate_ths: float,
    block_reward: float,
    block_time_seconds: float
) -> float:
    """
    Calculate expected daily KAS production

    Formula:
    Daily KAS = (Your Hashrate / Network Hashrate) × Blocks per Day × Block Reward
    """
    # Calculate blocks per day
    seconds_per_day = 86400
    blocks_per_day = seconds_per_day / block_time_seconds

    # Calculate your share of network hashrate
    hashrate_share = miner_hashrate_ths / network_hashrate_ths

    # Calculate daily KAS
    daily_kas = hashrate_share * blocks_per_day * block_reward

    return daily_kas

def calculate_income_projections(
    daily_kas: float,
    kas_price_gbp: float,
    pool_fee_percent: float = 0.0
) -> Dict:
    """
    Calculate income projections in GBP

    Args:
        daily_kas: KAS earned per day
        kas_price_gbp: Current KAS price in GBP
        pool_fee_percent: Pool fee (0-100)

    Returns:
        Dict with daily/monthly/yearly projections
    """
    # Apply pool fee
    fee_multiplier = 1 - (pool_fee_percent / 100)
    daily_kas_after_fee = daily_kas * fee_multiplier

    # Calculate GBP income
    daily_gbp = daily_kas_after_fee * kas_price_gbp
    monthly_gbp = daily_gbp * 30
    yearly_gbp = daily_gbp * 365

    # Calculate ROI
    roi_days = KS5M_COST_GBP / daily_gbp if daily_gbp > 0 else 0

    return {
        "daily_kas": round(daily_kas_after_fee, 2),
        "daily_gbp": round(daily_gbp, 2),
        "monthly_gbp": round(monthly_gbp, 2),
        "yearly_gbp": round(yearly_gbp, 2),
        "roi_days": round(roi_days, 1),
        "pool_fee_percent": pool_fee_percent,
        "kas_price_gbp": kas_price_gbp
    }

# ============================================================================
# Main Calculator
# ============================================================================

def run_calculator() -> Dict:
    """
    Run the complete income calculator

    Returns:
        Dict with all calculated data and projections
    """
    # Fetch live data
    kas_price = fetch_kas_price()
    network_stats = fetch_network_stats()
    pool_stats = fetch_2miners_stats()

    if not kas_price or not network_stats:
        return None

    # Calculate daily KAS production
    daily_kas = calculate_daily_kas_production(
        miner_hashrate_ths=KS5M_HASHRATE_THS,
        network_hashrate_ths=network_stats["network_hashrate_ths"],
        block_reward=network_stats["block_reward"],
        block_time_seconds=network_stats["block_time_seconds"]
    )

    # Calculate income with different pools
    emcd_income = calculate_income_projections(daily_kas, kas_price, pool_fee_percent=0.0)
    miners_income = calculate_income_projections(daily_kas, kas_price, pool_fee_percent=1.0)

    # Compile results
    results = {
        "timestamp": datetime.now().isoformat(),
        "miner": {
            "model": "IceRiver KS5M",
            "hashrate_ths": KS5M_HASHRATE_THS,
            "power_w": KS5M_POWER_W,
            "cost_gbp": KS5M_COST_GBP
        },
        "network": network_stats,
        "market": {
            "kas_price_gbp": kas_price,
            "kas_price_usd": kas_price * 1.27  # Approx conversion
        },
        "income": {
            "emcd_pool": emcd_income,
            "2miners_pool": miners_income
        },
        "scaling": {}
    }

    # Calculate scaling (1, 5, 10, 20 miners)
    for count in [1, 5, 10, 20]:
        results["scaling"][f"{count}_miners"] = {
            "daily_gbp": round(emcd_income["daily_gbp"] * count, 2),
            "monthly_gbp": round(emcd_income["monthly_gbp"] * count, 2),
            "yearly_gbp": round(emcd_income["yearly_gbp"] * count, 2),
            "daily_kas": round(emcd_income["daily_kas"] * count, 2),
            "hardware_cost_gbp": KS5M_COST_GBP * count,
            "roi_days": emcd_income["roi_days"]
        }

    return results

# ============================================================================
# Background Update Thread
# ============================================================================

def background_update():
    """Background thread to periodically update calculator data"""
    global latest_results, last_update

    while True:
        try:
            print("Updating calculator data...")
            results = run_calculator()
            if results:
                latest_results = results
                last_update = datetime.now()
                print("✓ Calculator data updated successfully")
            else:
                print("✗ Failed to update calculator data")
        except Exception as e:
            print(f"Error in background update: {e}")

        # Update every 5 minutes
        time.sleep(300)

# ============================================================================
# Flask Routes
# ============================================================================

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/api/calculator')
def get_calculator_data():
    """API endpoint to get calculator results"""
    global latest_results, last_update

    if latest_results is None:
        # Initial calculation if no cached data
        latest_results = run_calculator()
        last_update = datetime.now()

    if latest_results:
        # Add last update info
        response_data = latest_results.copy()
        response_data['last_update'] = last_update.isoformat() if last_update else None
        return jsonify(response_data)
    else:
        return jsonify({"error": "Failed to fetch calculator data"}), 500

@app.route('/api/refresh')
def refresh_data():
    """Force refresh of calculator data"""
    global latest_results, last_update

    results = run_calculator()
    if results:
        latest_results = results
        last_update = datetime.now()
        response_data = results.copy()
        response_data['last_update'] = last_update.isoformat()
        return jsonify(response_data)
    else:
        return jsonify({"error": "Failed to refresh calculator data"}), 500

# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    # Start background update thread
    update_thread = threading.Thread(target=background_update, daemon=True)
    update_thread.start()

    print("Starting KaspaMine Income Calculator Web App...")
    print("Open your browser to http://localhost:5001")
    print("Press Ctrl+C to stop")

    # Run Flask app
    app.run(host='0.0.0.0', port=5001, debug=False)
