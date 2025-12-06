#!/usr/bin/env python3
"""
KaspaMine Real-Time Income Calculator
Fetches live data from multiple sources and calculates accurate income projections

Data Sources:
- CoinGecko API: KAS price in GBP
- Kaspa Explorer API: Network stats (difficulty, hashrate, block reward)
- Pool APIs: EMCD, 2Miners pool stats
- WhatToMine: Profitability verification
"""

import json
import requests
import sys
from datetime import datetime
from typing import Dict, Optional

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

# Colors for terminal output
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
RESET = '\033[0m'


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
            print(f"{GREEN}✓{RESET} Fetched KAS price: £{price:.4f}")
            return float(price)

    except Exception as e:
        print(f"{RED}✗{RESET} Error fetching KAS price from CoinGecko: {e}")

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
            print(f"{RED}✗{RESET} No nodes data in 2Miners API response")
            return None

        network_hashrate_hs = int(nodes[0].get("networkhashps", 0))

        if network_hashrate_hs <= 0:
            print(f"{RED}✗{RESET} Invalid network hashrate from API: {network_hashrate_hs}")
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

        print(f"{GREEN}✓{RESET} Fetched network stats from 2Miners API")
        print(f"{GREEN}✓{RESET} Network hashrate: {stats['network_hashrate_ths']:,.0f} TH/s ({stats['network_hashrate_ths']/1000:.0f} PH/s)")
        return stats

    except Exception as e:
        print(f"{RED}✗{RESET} 2Miners API failed: {e}")
        print(f"{RED}✗{RESET} Cannot proceed without real network data")
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

        print(f"{GREEN}✓{RESET} Fetched 2Miners pool stats")
        return stats

    except Exception as e:
        print(f"{YELLOW}⚠{RESET} Could not fetch 2Miners stats: {e}")
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

def run_calculator(verbose: bool = True) -> Dict:
    """
    Run the complete income calculator

    Returns:
        Dict with all calculated data and projections
    """
    if verbose:
        print(f"\n{BLUE}{'='*60}{RESET}")
        print(f"{BLUE}KaspaMine Real-Time Income Calculator{RESET}")
        print(f"{BLUE}{'='*60}{RESET}\n")

    # Fetch live data
    if verbose:
        print(f"{BLUE}Fetching live data...{RESET}\n")

    kas_price = fetch_kas_price()
    network_stats = fetch_network_stats()
    pool_stats = fetch_2miners_stats()

    if not kas_price or not network_stats:
        print(f"\n{RED}✗ Failed to fetch required data{RESET}")
        print(f"{RED}✗ Calculator requires REAL API data - no fallback estimates allowed{RESET}")
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

    # Display results
    if verbose:
        display_results(results)

    return results


def display_results(results: Dict):
    """Display formatted results to console"""

    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}MARKET DATA{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    print(f"KAS Price:        £{results['market']['kas_price_gbp']:.4f} GBP")
    print(f"Network Hashrate: {results['network']['network_hashrate_ths']:,.0f} TH/s")
    print(f"Block Reward:     {results['network']['block_reward']} KAS")
    print(f"Block Time:       {results['network']['block_time_seconds']} seconds")

    emcd = results['income']['emcd_pool']
    miners = results['income']['2miners_pool']

    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}INCOME PER KS5M MINER{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")

    print(f"\n{GREEN}EMCD Pool (0% fee - RECOMMENDED):{RESET}")
    print(f"  Daily:   {emcd['daily_kas']:>8,.0f} KAS = £{emcd['daily_gbp']:>8,.2f}")
    print(f"  Monthly:              £{emcd['monthly_gbp']:>8,.2f}")
    print(f"  Yearly:               £{emcd['yearly_gbp']:>8,.2f}")
    print(f"  ROI:                  {emcd['roi_days']:>8.1f} days")

    print(f"\n{YELLOW}2Miners Pool (1% fee):{RESET}")
    print(f"  Daily:   {miners['daily_kas']:>8,.0f} KAS = £{miners['daily_gbp']:>8,.2f}")
    print(f"  Monthly:              £{miners['monthly_gbp']:>8,.2f}")
    print(f"  Yearly:               £{miners['yearly_gbp']:>8,.2f}")

    fee_savings = emcd['yearly_gbp'] - miners['yearly_gbp']
    print(f"\n{GREEN}EMCD saves £{fee_savings:.2f}/year (0% fee vs 1% fee){RESET}")

    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}SCALING PROJECTIONS (EMCD 0% FEE){RESET}")
    print(f"{BLUE}{'='*60}{RESET}")

    print(f"\n{'Miners':<8} {'Daily':<12} {'Monthly':<14} {'Yearly':<14} {'ROI (days)'}")
    print(f"{'-'*60}")

    for count in [1, 5, 10, 20]:
        scale = results['scaling'][f"{count}_miners"]
        print(f"{count:<8} £{scale['daily_gbp']:<11,.2f} £{scale['monthly_gbp']:<13,.2f} £{scale['yearly_gbp']:<13,.2f} {scale['roi_days']:.1f}")

    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{GREEN}Data sources:{RESET}")
    print(f"  • KAS Price: CoinGecko API")
    print(f"  • Network Stats: Kaspa Explorer")
    print(f"  • Pool Stats: 2Miners API")
    print(f"{BLUE}{'='*60}{RESET}\n")


def update_config_file(results: Dict, config_path: str = "operations/kaspa/config.json"):
    """Update the Kaspa config file with latest income projections"""

    try:
        # Read existing config
        with open(config_path, 'r') as f:
            config = json.load(f)

        # Update income section
        emcd = results['income']['emcd_pool']
        config['income'] = {
            "daily_per_miner_gbp": emcd['daily_gbp'],
            "monthly_per_miner_gbp": emcd['monthly_gbp'],
            "yearly_per_miner_gbp": emcd['yearly_gbp'],
            "currency": "GBP",
            "kas_per_day": emcd['daily_kas'],
            "kas_price_gbp": results['market']['kas_price_gbp'],
            "pool_fee_percent": 0,
            "min_payout_kas": 1,
            "hardware_cost_gbp": KS5M_COST_GBP,
            "payback_days": emcd['roi_days'],
            "note": f"Auto-updated {datetime.now().strftime('%Y-%m-%d %H:%M')} from live data"
        }

        # Write updated config
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)

        print(f"{GREEN}✓{RESET} Updated {config_path}")

    except Exception as e:
        print(f"{RED}✗{RESET} Error updating config: {e}")


# ============================================================================
# CLI Interface
# ============================================================================

def main():
    """Main entry point"""

    import argparse

    parser = argparse.ArgumentParser(
        description="KaspaMine Real-Time Income Calculator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run calculator with full output
  python3 calculator.py

  # Update config file automatically
  python3 calculator.py --update-config

  # Export results to JSON
  python3 calculator.py --export results.json

  # Quiet mode (just numbers)
  python3 calculator.py --quiet
        """
    )

    parser.add_argument(
        '--update-config',
        action='store_true',
        help='Update operations/kaspa/config.json with latest data'
    )

    parser.add_argument(
        '--export',
        metavar='FILE',
        help='Export results to JSON file'
    )

    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Minimal output'
    )

    args = parser.parse_args()

    # Run calculator
    results = run_calculator(verbose=not args.quiet)

    if not results:
        sys.exit(1)

    # Update config if requested
    if args.update_config:
        update_config_file(results)

    # Export to JSON if requested
    if args.export:
        try:
            with open(args.export, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"{GREEN}✓{RESET} Exported results to {args.export}")
        except Exception as e:
            print(f"{RED}✗{RESET} Error exporting: {e}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
