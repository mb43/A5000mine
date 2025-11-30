#!/usr/bin/env python3
"""
A5000mine Dashboard Server
Simple web server for monitoring mining status
"""

import json
import os
import subprocess
import time
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import re

# Configuration
CONFIG_FILE = "/opt/ae-miner/config.json"
LOG_FILE = "/opt/ae-miner/logs/miner.log"
DASHBOARD_DIR = os.path.dirname(os.path.abspath(__file__))

# Global state
start_time = time.time()
stats = {
    "shares_accepted": 0,
    "shares_rejected": 0,
    "last_hashrate": 0.0
}


def load_config():
    """Load mining configuration"""
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Could not load config: {e}")
        return {}


def get_gpu_stats():
    """Get GPU statistics using nvidia-smi"""
    try:
        cmd = [
            "nvidia-smi",
            "--query-gpu=name,temperature.gpu,power.draw,utilization.gpu",
            "--format=csv,noheader,nounits"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)

        if result.returncode == 0:
            parts = result.stdout.strip().split(',')
            if len(parts) >= 4:
                return {
                    "name": parts[0].strip(),
                    "temperature": int(float(parts[1].strip())),
                    "power_draw": int(float(parts[2].strip())),
                    "utilization": int(float(parts[3].strip()))
                }
    except Exception as e:
        print(f"Error getting GPU stats: {e}")

    return {
        "name": "N/A",
        "temperature": 0,
        "power_draw": 0,
        "utilization": 0
    }


def check_mining_status():
    """Check if mining service is running"""
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


def parse_log_file():
    """Parse miner log file for statistics"""
    logs = []
    hashrate = 0.0

    try:
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'r') as f:
                # Read last 100 lines
                lines = f.readlines()[-100:]

                for line in lines:
                    line = line.strip()

                    # Extract hashrate (example: "Speed: 5.23 G/s")
                    hashrate_match = re.search(r'Speed[:\s]+(\d+\.?\d*)\s*G', line, re.IGNORECASE)
                    if hashrate_match:
                        hashrate = float(hashrate_match.group(1))

                    # Count accepted shares
                    if re.search(r'accepted|share.+accepted', line, re.IGNORECASE):
                        stats["shares_accepted"] += 1

                    # Count rejected shares
                    if re.search(r'rejected|share.+rejected', line, re.IGNORECASE):
                        stats["shares_rejected"] += 1

                    # Add to log display
                    if any(keyword in line.lower() for keyword in
                           ['speed', 'accepted', 'rejected', 'share', 'gpu', 'temp']):
                        logs.append(line[-200:])  # Limit line length

                # Update global hashrate
                if hashrate > 0:
                    stats["last_hashrate"] = hashrate

    except Exception as e:
        print(f"Error parsing log file: {e}")

    return logs[-15:]  # Return last 15 relevant log entries


def get_status_data():
    """Compile all status data for API"""
    config = load_config()
    is_mining = check_mining_status()
    gpu_stats = get_gpu_stats()
    logs = parse_log_file()

    uptime = int(time.time() - start_time) if is_mining else 0

    data = {
        "mining": {
            "active": is_mining,
            "worker": config.get("worker_name", "-"),
            "pool": config.get("pool", {}).get("url", "-"),
            "uptime": uptime
        },
        "performance": {
            "hashrate": stats["last_hashrate"],
            "shares_accepted": stats["shares_accepted"],
            "shares_rejected": stats["shares_rejected"]
        },
        "gpu": gpu_stats,
        "logs": logs,
        "timestamp": datetime.now().isoformat()
    }

    return data


class DashboardHandler(SimpleHTTPRequestHandler):
    """Custom HTTP request handler for dashboard"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DASHBOARD_DIR, **kwargs)

    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/api/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            data = get_status_data()
            self.wfile.write(json.dumps(data).encode())
        else:
            # Serve static files
            super().do_GET()

    def log_message(self, format, *args):
        """Override to reduce logging noise"""
        # Only log errors
        if args[1] != '200':
            super().log_message(format, *args)


def main():
    """Start dashboard server"""
    config = load_config()
    port = config.get("dashboard", {}).get("port", 8080)

    server_address = ('', port)
    httpd = HTTPServer(server_address, DashboardHandler)

    print(f"A5000mine Dashboard Server")
    print(f"Listening on port {port}")
    print(f"Access at: http://localhost:{port}")
    print("Press Ctrl+C to stop")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        httpd.shutdown()


if __name__ == "__main__":
    main()
