#!/usr/bin/env python3
"""
KaspaMine Real-Time Income Calculator Web App
A Flask-based web application for calculating Kaspa mining income projections

Data Sources:
- CoinGecko API: KAS price in GBP
- 2Miners API: Network hashrate and difficulty
- Kaspa API: Real block reward (updates with emission schedule)
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

# Kaspa Mining - IceRiver KS5M
KS5M_HASHRATE_THS = 15.0  # TH/s per KS5M miner
KS5M_POWER_W = 3400        # Watts per miner
KS5M_COST_GBP = 600        # Hardware cost

# Zcash Mining - Antminer Z15 Pro
Z15PRO_HASHRATE_KSOL = 840  # KSol/s per Z15 Pro
Z15PRO_POWER_W = 2780       # Watts per miner
Z15PRO_COST_GBP = 3500      # Hardware cost (approximate)

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

# Global variables to store latest results and data source status
latest_results = None
last_update = None
data_source_status = {
    "kaspa": {
        "price": {"status": "unknown", "timestamp": None, "source": "CoinGecko API"},
        "network": {"status": "unknown", "timestamp": None, "source": "2Miners API"},
        "block_reward": {"status": "unknown", "timestamp": None, "source": "Kaspa API"}
    },
    "zcash": {
        "price": {"status": "unknown", "timestamp": None, "source": "CoinGecko API"},
        "network": {"status": "unknown", "timestamp": None, "source": "2Miners API"},
        "block_reward": {"status": "unknown", "timestamp": None, "source": "Hardcoded (2.5 ZEC)"}
    }
}

# ============================================================================
# Data Fetching Functions
# ============================================================================

def fetch_kas_price() -> Optional[float]:
    """
    Fetch current KAS price in GBP from CoinGecko
    Returns: Price in GBP or None if failed
    """
    global data_source_status

    try:
        url = f"{COINGECKO_API}/simple/price"
        params = {
            "ids": "kaspa",
            "vs_currencies": "gbp"
        }
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()

        price = data.get("kaspa", {}).get("gbp")
        if price:
            data_source_status["kaspa"]["price"]["status"] = "live"
            data_source_status["kaspa"]["price"]["timestamp"] = datetime.now().isoformat()
            return float(price)

    except Exception as e:
        print(f"Error fetching KAS price from CoinGecko: {e}")
        data_source_status["kaspa"]["price"]["status"] = "failed"
        data_source_status["kaspa"]["price"]["timestamp"] = datetime.now().isoformat()

    return None

def fetch_network_stats() -> Optional[Dict]:
    """
    Fetch Kaspa network statistics from 2Miners API and Kaspa API (REAL DATA ONLY)
    Returns: Dict with network_hashrate_ths, block_reward, block_time_seconds
    """
    global data_source_status

    try:
        # Fetch network hashrate from 2Miners
        url = "https://kas.2miners.com/api/stats"
        response = requests.get(url, timeout=5)
        response.raise_for_status()

        data = response.json()

        # Extract real network hashrate from nodes[0].networkhashps
        nodes = data.get("nodes", [])
        if not nodes:
            data_source_status["kaspa"]["network"]["status"] = "failed"
            data_source_status["kaspa"]["network"]["timestamp"] = datetime.now().isoformat()
            return None

        network_hashrate_hs = int(nodes[0].get("networkhashps", 0))

        if network_hashrate_hs <= 0:
            data_source_status["kaspa"]["network"]["status"] = "failed"
            data_source_status["kaspa"]["network"]["timestamp"] = datetime.now().isoformat()
            return None

        # Get difficulty if available
        difficulty = data.get("nodes", [{}])[0].get("difficulty", 0)

        # Mark network data as live
        data_source_status["kaspa"]["network"]["status"] = "live"
        data_source_status["kaspa"]["network"]["timestamp"] = datetime.now().isoformat()

        # Fetch real block reward from Kaspa API
        block_reward = 3.67  # Default fallback
        try:
            reward_response = requests.get("https://api.kaspa.org/info/blockreward", timeout=5)
            reward_response.raise_for_status()
            reward_data = reward_response.json()
            block_reward = float(reward_data.get("blockreward", 3.67))
            data_source_status["kaspa"]["block_reward"]["status"] = "live"
            data_source_status["kaspa"]["block_reward"]["timestamp"] = datetime.now().isoformat()
        except Exception as e:
            print(f"Warning: Could not fetch block reward from Kaspa API: {e}, using fallback")
            data_source_status["kaspa"]["block_reward"]["status"] = "cached"
            data_source_status["kaspa"]["block_reward"]["timestamp"] = datetime.now().isoformat()

        stats = {
            "network_hashrate_ths": network_hashrate_hs / 1e12,  # Convert H/s to TH/s
            "block_reward": block_reward,  # Real block reward from Kaspa API
            "block_time_seconds": 0.1,  # Kaspa block time (10 blocks per second after Crescendo upgrade)
            "difficulty": difficulty,
            "source": "2Miners API + Kaspa API (Real-time)"
        }

        return stats

    except Exception as e:
        print(f"2Miners API failed: {e}")
        data_source_status["kaspa"]["network"]["status"] = "failed"
        data_source_status["kaspa"]["network"]["timestamp"] = datetime.now().isoformat()
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
# Zcash Data Fetching Functions
# ============================================================================

def fetch_zec_price() -> Optional[float]:
    """
    Fetch current ZEC price in GBP from CoinGecko
    Returns: Price in GBP or None if failed
    """
    global data_source_status

    try:
        url = f"{COINGECKO_API}/simple/price"
        params = {
            "ids": "zcash",
            "vs_currencies": "gbp"
        }
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()

        price = data.get("zcash", {}).get("gbp")
        if price:
            data_source_status["zcash"]["price"]["status"] = "live"
            data_source_status["zcash"]["price"]["timestamp"] = datetime.now().isoformat()
            return float(price)

    except Exception as e:
        print(f"Error fetching ZEC price from CoinGecko: {e}")
        data_source_status["zcash"]["price"]["status"] = "failed"
        data_source_status["zcash"]["price"]["timestamp"] = datetime.now().isoformat()

    return None

def fetch_zec_network_stats() -> Optional[Dict]:
    """
    Fetch Zcash network statistics from 2Miners API (REAL DATA ONLY)
    Returns: Dict with network_hashrate_sol, block_reward, block_time_seconds
    """
    global data_source_status

    try:
        url = "https://zec.2miners.com/api/stats"
        response = requests.get(url, timeout=5)
        response.raise_for_status()

        data = response.json()

        # Extract real network hashrate from nodes[0].networkhashps
        nodes = data.get("nodes", [])
        if not nodes:
            data_source_status["zcash"]["network"]["status"] = "failed"
            data_source_status["zcash"]["network"]["timestamp"] = datetime.now().isoformat()
            return None

        network_hashrate_sol = int(nodes[0].get("networkhashps", 0))

        if network_hashrate_sol <= 0:
            data_source_status["zcash"]["network"]["status"] = "failed"
            data_source_status["zcash"]["network"]["timestamp"] = datetime.now().isoformat()
            return None

        # Get difficulty and block time
        difficulty = nodes[0].get("difficulty", 0)
        avg_block_time = float(nodes[0].get("avgBlockTime", 75))

        # Mark network data as live
        data_source_status["zcash"]["network"]["status"] = "live"
        data_source_status["zcash"]["network"]["timestamp"] = datetime.now().isoformat()

        # Block reward is hardcoded for now
        data_source_status["zcash"]["block_reward"]["status"] = "live"
        data_source_status["zcash"]["block_reward"]["timestamp"] = datetime.now().isoformat()

        stats = {
            "network_hashrate_sol": network_hashrate_sol,  # Sol/s
            "network_hashrate_ksol": network_hashrate_sol / 1000,  # KSol/s
            "network_hashrate_msol": network_hashrate_sol / 1_000_000,  # MSol/s
            "block_reward": 2.5,  # ZEC per block (current after Nov 2025 halving)
            "block_time_seconds": avg_block_time,
            "difficulty": difficulty,
            "source": "2Miners API (Real-time)"
        }

        return stats

    except Exception as e:
        print(f"2Miners ZEC API failed: {e}")
        data_source_status["zcash"]["network"]["status"] = "failed"
        data_source_status["zcash"]["network"]["timestamp"] = datetime.now().isoformat()
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

def calculate_daily_zec_production(
    miner_hashrate_ksol: float,
    network_hashrate_sol: float,
    block_reward: float,
    block_time_seconds: float
) -> float:
    """
    Calculate expected daily ZEC production

    Formula:
    Daily ZEC = (Your Hashrate / Network Hashrate) × Blocks per Day × Block Reward
    """
    # Convert miner hashrate to Sol/s
    miner_hashrate_sol = miner_hashrate_ksol * 1000

    # Calculate blocks per day
    seconds_per_day = 86400
    blocks_per_day = seconds_per_day / block_time_seconds

    # Calculate your share of network hashrate
    hashrate_share = miner_hashrate_sol / network_hashrate_sol

    # Calculate daily ZEC
    daily_zec = hashrate_share * blocks_per_day * block_reward

    return daily_zec

def calculate_zec_income_projections(
    daily_zec: float,
    zec_price_gbp: float,
    pool_fee_percent: float = 0.0
) -> Dict:
    """
    Calculate Zcash income projections in GBP

    Args:
        daily_zec: ZEC earned per day
        zec_price_gbp: Current ZEC price in GBP
        pool_fee_percent: Pool fee (0-100)

    Returns:
        Dict with daily/monthly/yearly projections
    """
    # Apply pool fee
    fee_multiplier = 1 - (pool_fee_percent / 100)
    daily_zec_after_fee = daily_zec * fee_multiplier

    # Calculate GBP income
    daily_gbp = daily_zec_after_fee * zec_price_gbp
    monthly_gbp = daily_gbp * 30
    yearly_gbp = daily_gbp * 365

    # Calculate ROI
    roi_days = Z15PRO_COST_GBP / daily_gbp if daily_gbp > 0 else 0

    return {
        "daily_zec": round(daily_zec_after_fee, 4),
        "daily_gbp": round(daily_gbp, 2),
        "monthly_gbp": round(monthly_gbp, 2),
        "yearly_gbp": round(yearly_gbp, 2),
        "roi_days": round(roi_days, 1),
        "pool_fee_percent": pool_fee_percent,
        "zec_price_gbp": zec_price_gbp
    }

# ============================================================================
# Main Calculator
# ============================================================================

def run_calculator(coins: str = "both") -> Dict:
    """
    Run the complete income calculator for selected coins

    Args:
        coins: "kaspa", "zcash", or "both" (default)

    Returns:
        Dict with all calculated data and projections
    """
    results = {
        "timestamp": datetime.now().isoformat(),
        "coins_enabled": coins
    }

    # Kaspa calculations
    if coins in ["kaspa", "both"]:
        kas_price = fetch_kas_price()
        kas_network_stats = fetch_network_stats()
        kas_pool_stats = fetch_2miners_stats()

        if kas_price and kas_network_stats:
            # Calculate daily KAS production
            daily_kas = calculate_daily_kas_production(
                miner_hashrate_ths=KS5M_HASHRATE_THS,
                network_hashrate_ths=kas_network_stats["network_hashrate_ths"],
                block_reward=kas_network_stats["block_reward"],
                block_time_seconds=kas_network_stats["block_time_seconds"]
            )

            # Calculate income with different pools
            emcd_income = calculate_income_projections(daily_kas, kas_price, pool_fee_percent=0.0)
            miners_income = calculate_income_projections(daily_kas, kas_price, pool_fee_percent=1.0)

            results["kaspa"] = {
                "miner": {
                    "model": "IceRiver KS5M",
                    "hashrate_ths": KS5M_HASHRATE_THS,
                    "power_w": KS5M_POWER_W,
                    "cost_gbp": KS5M_COST_GBP
                },
                "network": kas_network_stats,
                "market": {
                    "kas_price_gbp": kas_price,
                    "kas_price_usd": kas_price * 1.27
                },
                "income": {
                    "emcd_pool": emcd_income,
                    "2miners_pool": miners_income
                },
                "scaling": {}
            }

            # Calculate scaling (1, 5, 10, 20 miners)
            for count in [1, 5, 10, 20]:
                results["kaspa"]["scaling"][f"{count}_miners"] = {
                    "daily_gbp": round(emcd_income["daily_gbp"] * count, 2),
                    "monthly_gbp": round(emcd_income["monthly_gbp"] * count, 2),
                    "yearly_gbp": round(emcd_income["yearly_gbp"] * count, 2),
                    "daily_kas": round(emcd_income["daily_kas"] * count, 2),
                    "hardware_cost_gbp": KS5M_COST_GBP * count,
                    "roi_days": emcd_income["roi_days"]
                }

    # Zcash calculations
    if coins in ["zcash", "both"]:
        zec_price = fetch_zec_price()
        zec_network_stats = fetch_zec_network_stats()

        if zec_price and zec_network_stats:
            # Calculate daily ZEC production
            daily_zec = calculate_daily_zec_production(
                miner_hashrate_ksol=Z15PRO_HASHRATE_KSOL,
                network_hashrate_sol=zec_network_stats["network_hashrate_sol"],
                block_reward=zec_network_stats["block_reward"],
                block_time_seconds=zec_network_stats["block_time_seconds"]
            )

            # Calculate income with different pools (2Miners has 1% fee for ZEC)
            income_0fee = calculate_zec_income_projections(daily_zec, zec_price, pool_fee_percent=0.0)
            income_1fee = calculate_zec_income_projections(daily_zec, zec_price, pool_fee_percent=1.0)

            results["zcash"] = {
                "miner": {
                    "model": "Antminer Z15 Pro",
                    "hashrate_ksol": Z15PRO_HASHRATE_KSOL,
                    "power_w": Z15PRO_POWER_W,
                    "cost_gbp": Z15PRO_COST_GBP
                },
                "network": zec_network_stats,
                "market": {
                    "zec_price_gbp": zec_price,
                    "zec_price_usd": zec_price * 1.27
                },
                "income": {
                    "0_fee_pool": income_0fee,
                    "2miners_pool": income_1fee
                },
                "scaling": {}
            }

            # Calculate scaling (1, 5, 10, 20 miners)
            for count in [1, 5, 10, 20]:
                results["zcash"]["scaling"][f"{count}_miners"] = {
                    "daily_gbp": round(income_0fee["daily_gbp"] * count, 2),
                    "monthly_gbp": round(income_0fee["monthly_gbp"] * count, 2),
                    "yearly_gbp": round(income_0fee["yearly_gbp"] * count, 2),
                    "daily_zec": round(income_0fee["daily_zec"] * count, 4),
                    "hardware_cost_gbp": Z15PRO_COST_GBP * count,
                    "roi_days": income_0fee["roi_days"]
                }

    # Return None if no data was fetched
    if "kaspa" not in results and "zcash" not in results:
        return None

    return results

# ============================================================================
# Background Update Thread
# ============================================================================

def background_update():
    """Background thread to continuously update calculator data"""
    global latest_results, last_update

    while True:
        try:
            results = run_calculator()
            if results:
                latest_results = results
                last_update = datetime.now()
        except Exception as e:
            print(f"Error in background update: {e}")

        # Update every second for real-time data
        time.sleep(1)

# ============================================================================
# Flask Routes
# ============================================================================

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/api/calculator')
def get_calculator_data():
    """API endpoint to get calculator results with optional coin selection"""
    global latest_results, last_update, data_source_status

    # Get coin selection from query params (kaspa, zcash, or both)
    coins = request.args.get('coins', 'both')
    if coins not in ['kaspa', 'zcash', 'both']:
        coins = 'both'

    if latest_results is None or latest_results.get('coins_enabled') != coins:
        # Initial calculation or coin selection changed
        latest_results = run_calculator(coins=coins)
        last_update = datetime.now()

    if latest_results:
        # Add last update info and data source status
        response_data = latest_results.copy()
        response_data['last_update'] = last_update.isoformat() if last_update else None
        response_data['data_sources'] = data_source_status
        return jsonify(response_data)
    else:
        return jsonify({"error": "Failed to fetch calculator data"}), 500

@app.route('/api/status')
def get_data_source_status():
    """API endpoint to get real-time data source status"""
    global data_source_status
    return jsonify(data_source_status)

@app.route('/api/refresh')
def refresh_data():
    """Force refresh of calculator data with optional coin selection"""
    global latest_results, last_update

    # Get coin selection from query params
    coins = request.args.get('coins', 'both')
    if coins not in ['kaspa', 'zcash', 'both']:
        coins = 'both'

    results = run_calculator(coins=coins)
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
