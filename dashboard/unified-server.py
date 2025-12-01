#!/usr/bin/env python3
"""
A5000mine Unified Multi-Operation Dashboard Server
Monitors multiple mining operations: Aeternity (GPU), Kaspa (ASIC), Zcash (ASIC)
"""

import json
import os
import subprocess
import time
import glob
from datetime import datetime, timedelta
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import re

# Configuration
OPERATIONS_DIR = "/home/user/A5000mine/operations"
DASHBOARD_DIR = os.path.dirname(os.path.abspath(__file__))

# Global state
start_time = time.time()


def load_operation_config(operation_name):
    """Load configuration for a specific operation"""
    try:
        config_file = f"{OPERATIONS_DIR}/{operation_name}/config.json"
        with open(config_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Could not load {operation_name} config: {e}")
        return None


def get_all_operations():
    """Discover all configured mining operations"""
    operations = []
    try:
        if os.path.exists(OPERATIONS_DIR):
            for op_dir in os.listdir(OPERATIONS_DIR):
                op_path = os.path.join(OPERATIONS_DIR, op_dir)
                if os.path.isdir(op_path):
                    config = load_operation_config(op_dir)
                    if config:
                        operations.append({
                            "name": op_dir,
                            "config": config
                        })
    except Exception as e:
        print(f"Error discovering operations: {e}")

    return operations


def get_gpu_stats():
    """Get GPU statistics using nvidia-smi for Aeternity operation"""
    gpus = []
    try:
        cmd = [
            "nvidia-smi",
            "--query-gpu=index,name,temperature.gpu,power.draw,utilization.gpu,memory.used",
            "--format=csv,noheader,nounits"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)

        if result.returncode == 0:
            for line in result.stdout.strip().split('\n'):
                parts = [p.strip() for p in line.split(',')]
                if len(parts) >= 6:
                    gpus.append({
                        "index": int(parts[0]),
                        "name": parts[1],
                        "temperature": int(float(parts[2])),
                        "power_draw": int(float(parts[3])),
                        "utilization": int(float(parts[4])),
                        "memory_used": int(float(parts[5]))
                    })
    except Exception as e:
        print(f"Error getting GPU stats: {e}")

    return gpus


def check_aeternity_mining():
    """Check Aeternity mining status"""
    try:
        result = subprocess.run(
            ["systemctl", "is-active", "ae-miner"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except Exception:
        return False


def parse_aeternity_logs():
    """Parse Aeternity miner log file for statistics"""
    log_file = "/opt/ae-miner/logs/miner.log"
    stats = {
        "hashrate": 0.0,
        "shares_accepted": 0,
        "shares_rejected": 0,
        "recent_logs": []
    }

    try:
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                lines = f.readlines()[-100:]

                for line in lines:
                    line = line.strip()

                    # Extract hashrate
                    hashrate_match = re.search(r'Speed[:\s]+(\d+\.?\d*)\s*G', line, re.IGNORECASE)
                    if hashrate_match:
                        stats["hashrate"] = float(hashrate_match.group(1))

                    # Count shares
                    if re.search(r'accepted|share.+accepted', line, re.IGNORECASE):
                        stats["shares_accepted"] += 1
                    if re.search(r'rejected|share.+rejected', line, re.IGNORECASE):
                        stats["shares_rejected"] += 1

                    # Collect relevant logs
                    if any(keyword in line.lower() for keyword in
                           ['speed', 'accepted', 'rejected', 'share', 'gpu', 'temp']):
                        stats["recent_logs"].append(line[-200:])

                stats["recent_logs"] = stats["recent_logs"][-10:]
    except Exception as e:
        print(f"Error parsing Aeternity logs: {e}")

    return stats


def check_kaspa_miners(config):
    """Check Kaspa miners status"""
    miners_status = []

    if not config or "miners" not in config:
        return miners_status

    for miner in config.get("miners", []):
        ip = miner.get("ip")
        name = miner.get("name", "Unknown")

        status = {
            "name": name,
            "ip": ip,
            "online": False,
            "hashrate": 0.0,
            "temperature": 0,
            "power": 0
        }

        # Check if miner is reachable
        try:
            result = subprocess.run(
                ["ping", "-c", "1", "-W", "2", ip],
                capture_output=True,
                timeout=3
            )
            status["online"] = (result.returncode == 0)

            # If online, estimate hashrate from config
            if status["online"]:
                status["hashrate"] = config.get("performance", {}).get("hashrate_per_miner", 15.0)
                status["power"] = config.get("performance", {}).get("power_per_miner", 3400)
        except Exception as e:
            print(f"Error checking miner {name}: {e}")

        miners_status.append(status)

    return miners_status


def calculate_income_projections(operations_data):
    """Calculate income projections across all operations"""
    total_daily_gbp = 0.0
    total_monthly_gbp = 0.0
    total_yearly_gbp = 0.0

    projections = []

    for op in operations_data:
        op_name = op["name"]
        config = op["config"]

        if op_name == "aeternity":
            # GPU mining
            gpu_count = len(op.get("gpu_stats", []))
            daily_per_gpu = config.get("income", {}).get("daily_per_gpu_gbp", 8.5)
            daily = gpu_count * daily_per_gpu

            projections.append({
                "operation": "Aeternity (GPU)",
                "units": f"{gpu_count} GPU(s)",
                "daily_gbp": daily,
                "monthly_gbp": daily * 30,
                "yearly_gbp": daily * 365,
                "active": op.get("mining_active", False)
            })

            if op.get("mining_active", False):
                total_daily_gbp += daily

        elif op_name == "kaspa":
            # ASIC mining
            miners = op.get("miners_status", [])
            online_count = sum(1 for m in miners if m.get("online", False))
            daily_per_miner = config.get("income", {}).get("daily_per_miner_gbp", 82)
            daily = online_count * daily_per_miner

            projections.append({
                "operation": "Kaspa (ASIC)",
                "units": f"{online_count}/{len(miners)} miner(s)",
                "daily_gbp": daily,
                "monthly_gbp": daily * 30,
                "yearly_gbp": daily * 365,
                "active": online_count > 0
            })

            if online_count > 0:
                total_daily_gbp += daily

        elif op_name == "zcash":
            # Future ASIC mining
            # Placeholder - will be populated when configured
            miners = op.get("miners_status", [])
            online_count = sum(1 for m in miners if m.get("online", False))
            daily_per_miner = config.get("income", {}).get("daily_per_miner_gbp", 45)
            daily = online_count * daily_per_miner

            projections.append({
                "operation": "Zcash (ASIC)",
                "units": f"{online_count}/{len(miners)} miner(s)",
                "daily_gbp": daily,
                "monthly_gbp": daily * 30,
                "yearly_gbp": daily * 365,
                "active": online_count > 0
            })

            if online_count > 0:
                total_daily_gbp += daily

    total_monthly_gbp = total_daily_gbp * 30
    total_yearly_gbp = total_daily_gbp * 365

    return {
        "by_operation": projections,
        "total": {
            "daily_gbp": round(total_daily_gbp, 2),
            "monthly_gbp": round(total_monthly_gbp, 2),
            "yearly_gbp": round(total_yearly_gbp, 2),
            "currency": "GBP"
        }
    }


def get_unified_status():
    """Compile unified status data for all operations"""
    operations = get_all_operations()
    operations_data = []

    for op in operations:
        op_name = op["name"]
        config = op["config"]

        op_data = {
            "name": op_name,
            "config": config,
            "hardware": config.get("hardware", "Unknown"),
            "enabled": True
        }

        # Get operation-specific data
        if op_name == "aeternity":
            op_data["mining_active"] = check_aeternity_mining()
            op_data["gpu_stats"] = get_gpu_stats()
            op_data["miner_stats"] = parse_aeternity_logs()

        elif op_name == "kaspa":
            miners_status = check_kaspa_miners(config)
            op_data["miners_status"] = miners_status
            op_data["mining_active"] = any(m.get("online", False) for m in miners_status)

        elif op_name == "zcash":
            # Placeholder for future implementation
            op_data["miners_status"] = []
            op_data["mining_active"] = False

        operations_data.append(op_data)

    # Calculate income projections
    income_projections = calculate_income_projections(operations_data)

    return {
        "operations": operations_data,
        "income_projections": income_projections,
        "system": {
            "uptime": int(time.time() - start_time),
            "hostname": subprocess.run(["hostname"], capture_output=True, text=True).stdout.strip()
        },
        "timestamp": datetime.now().isoformat()
    }


class UnifiedDashboardHandler(SimpleHTTPRequestHandler):
    """Custom HTTP request handler for unified dashboard"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DASHBOARD_DIR, **kwargs)

    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/api/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            data = get_unified_status()
            self.wfile.write(json.dumps(data, indent=2).encode())

        elif self.path == '/unified' or self.path == '/unified.html':
            # Serve unified dashboard
            self.path = '/unified-dashboard.html'
            super().do_GET()
        else:
            # Serve static files
            super().do_GET()

    def log_message(self, format, *args):
        """Override to reduce logging noise"""
        if args[1] != '200':
            super().log_message(format, *args)


def main():
    """Start unified dashboard server"""
    port = 8090  # Use different port to not conflict with existing dashboard

    server_address = ('', port)
    httpd = HTTPServer(server_address, UnifiedDashboardHandler)

    print("=" * 60)
    print("  A5000mine Unified Multi-Operation Dashboard")
    print("=" * 60)
    print(f"Listening on port {port}")
    print(f"Access at: http://localhost:{port}/unified")
    print("API endpoint: http://localhost:{port}/api/status")
    print("")
    print("Monitoring operations:")

    ops = get_all_operations()
    for op in ops:
        print(f"  - {op['name'].title()}: {op['config'].get('hardware', 'Unknown')} mining")

    print("")
    print("Press Ctrl+C to stop")
    print("=" * 60)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        httpd.shutdown()


if __name__ == "__main__":
    main()
