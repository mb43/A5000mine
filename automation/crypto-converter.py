#!/usr/bin/env python3
"""
A5000mine Automated Crypto Converter
Automatically converts mining rewards to stablecoins and fiat

Features:
- Daily conversion: Mining rewards → USDT/USDC
- Weekly conversion: Stablecoins → GBP
- Multiple exchange support
- Secure API key management
- Transaction logging
"""

import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/crypto-converter.log'),
        logging.StreamHandler()
    ]
)

CONFIG_FILE = "/home/user/A5000mine/automation/config.json"
STATE_FILE = "/home/user/A5000mine/automation/state.json"


class CryptoConverter:
    """Manages automated cryptocurrency conversions"""

    def __init__(self, config_file=CONFIG_FILE):
        self.config = self.load_config(config_file)
        self.state = self.load_state()

    def load_config(self, config_file):
        """Load configuration from file"""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logging.error(f"Config file not found: {config_file}")
            logging.info("Please create config file with your exchange API keys")
            raise
        except Exception as e:
            logging.error(f"Error loading config: {e}")
            raise

    def load_state(self):
        """Load persistent state"""
        try:
            if os.path.exists(STATE_FILE):
                with open(STATE_FILE, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logging.error(f"Error loading state: {e}")

        return {
            "last_daily_conversion": None,
            "last_weekly_conversion": None,
            "total_converted_usd": 0.0,
            "total_converted_gbp": 0.0,
            "conversion_history": []
        }

    def save_state(self):
        """Save persistent state"""
        try:
            with open(STATE_FILE, 'w') as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            logging.error(f"Error saving state: {e}")

    def should_run_daily_conversion(self):
        """Check if daily conversion should run"""
        if not self.config.get("daily_conversion", {}).get("enabled", False):
            return False

        last_run = self.state.get("last_daily_conversion")
        if not last_run:
            return True

        last_run_date = datetime.fromisoformat(last_run).date()
        today = datetime.now().date()

        return today > last_run_date

    def should_run_weekly_conversion(self):
        """Check if weekly conversion should run"""
        if not self.config.get("weekly_conversion", {}).get("enabled", False):
            return False

        last_run = self.state.get("last_weekly_conversion")
        if not last_run:
            return True

        last_run_date = datetime.fromisoformat(last_run)
        days_since = (datetime.now() - last_run_date).days

        return days_since >= 7

    def get_balance(self, operation, wallet_address):
        """
        Get cryptocurrency balance for a wallet
        In production, this would query blockchain APIs
        """
        # TODO: Implement actual blockchain API calls
        # For now, return mock data
        logging.info(f"Checking {operation} balance for {wallet_address}")

        # Mock balances - replace with real API calls
        mock_balances = {
            "aeternity": 150.0,  # AE tokens
            "kaspa": 5000.0,     # KAS tokens
            "zcash": 2.5         # ZEC coins
        }

        return mock_balances.get(operation, 0.0)

    def convert_to_stablecoin(self, crypto, amount, stablecoin="USDT"):
        """
        Convert cryptocurrency to stablecoin
        Uses exchange API (Kraken, Binance, Coinbase, etc.)
        """
        exchange = self.config.get("exchanges", {}).get("primary", "kraken")

        logging.info(f"Converting {amount} {crypto} to {stablecoin} via {exchange}")

        # TODO: Implement actual exchange API calls
        # This is a mock implementation
        if exchange == "kraken":
            return self._convert_via_kraken(crypto, amount, stablecoin)
        elif exchange == "binance":
            return self._convert_via_binance(crypto, amount, stablecoin)
        elif exchange == "coinbase":
            return self._convert_via_coinbase(crypto, amount, stablecoin)
        else:
            logging.error(f"Unknown exchange: {exchange}")
            return None

    def _convert_via_kraken(self, crypto, amount, stablecoin):
        """Convert via Kraken API"""
        # TODO: Implement Kraken API integration
        # https://docs.kraken.com/rest/
        logging.info(f"Kraken: {amount} {crypto} → {stablecoin}")

        # Mock conversion
        mock_rates = {
            "AE": 0.035,   # AE to USD
            "KAS": 0.13,   # KAS to USD
            "ZEC": 42.50   # ZEC to USD
        }

        rate = mock_rates.get(crypto.upper(), 0)
        usd_value = amount * rate

        return {
            "success": True,
            "exchange": "kraken",
            "from_currency": crypto,
            "to_currency": stablecoin,
            "amount": amount,
            "received": usd_value,
            "rate": rate,
            "timestamp": datetime.now().isoformat(),
            "tx_id": f"mock_kraken_{int(time.time())}"
        }

    def _convert_via_binance(self, crypto, amount, stablecoin):
        """Convert via Binance API"""
        # TODO: Implement Binance API integration
        # https://binance-docs.github.io/apidocs/spot/en/
        logging.info(f"Binance: {amount} {crypto} → {stablecoin}")
        return {"success": False, "error": "Not implemented"}

    def _convert_via_coinbase(self, crypto, amount, stablecoin):
        """Convert via Coinbase API"""
        # TODO: Implement Coinbase API integration
        # https://docs.cloud.coinbase.com/
        logging.info(f"Coinbase: {amount} {crypto} → {stablecoin}")
        return {"success": False, "error": "Not implemented"}

    def convert_to_gbp(self, stablecoin_amount, provider="wise"):
        """
        Convert stablecoin to GBP via payment provider
        Supports: Wise (TransferWise), Revolut, PayPal
        """
        logging.info(f"Converting {stablecoin_amount} USDT to GBP via {provider}")

        # TODO: Implement actual payment provider APIs
        if provider == "wise":
            return self._convert_via_wise(stablecoin_amount)
        elif provider == "revolut":
            return self._convert_via_revolut(stablecoin_amount)
        elif provider == "paypal":
            return self._convert_via_paypal(stablecoin_amount)
        else:
            logging.error(f"Unknown provider: {provider}")
            return None

    def _convert_via_wise(self, usd_amount):
        """Convert via Wise (TransferWise) API"""
        # TODO: Implement Wise API integration
        # https://api-docs.wise.com/
        logging.info(f"Wise: {usd_amount} USD → GBP")

        # Mock conversion (current rate ~0.79)
        gbp_rate = 0.79
        gbp_amount = usd_amount * gbp_rate
        fee = usd_amount * 0.005  # 0.5% fee

        return {
            "success": True,
            "provider": "wise",
            "from_amount": usd_amount,
            "from_currency": "USD",
            "to_amount": gbp_amount - (fee * gbp_rate),
            "to_currency": "GBP",
            "rate": gbp_rate,
            "fee": fee,
            "timestamp": datetime.now().isoformat(),
            "tx_id": f"mock_wise_{int(time.time())}"
        }

    def _convert_via_revolut(self, usd_amount):
        """Convert via Revolut API"""
        # TODO: Implement Revolut Business API
        logging.info(f"Revolut: {usd_amount} USD → GBP")
        return {"success": False, "error": "Not implemented"}

    def _convert_via_paypal(self, usd_amount):
        """Convert via PayPal API"""
        # TODO: Implement PayPal API
        logging.info(f"PayPal: {usd_amount} USD → GBP")
        return {"success": False, "error": "Not implemented"}

    def run_daily_conversion(self):
        """Run daily conversion: crypto → stablecoin"""
        if not self.should_run_daily_conversion():
            logging.info("Daily conversion not due yet")
            return

        logging.info("=" * 60)
        logging.info("Starting daily conversion: Crypto → Stablecoin")
        logging.info("=" * 60)

        daily_config = self.config.get("daily_conversion", {})
        operations = daily_config.get("operations", [])
        min_amounts = daily_config.get("min_amounts", {})
        stablecoin = daily_config.get("target_stablecoin", "USDT")

        total_converted = 0.0

        for op in operations:
            op_name = op.get("name")
            wallet = op.get("wallet")
            crypto_symbol = op.get("crypto_symbol")

            if not all([op_name, wallet, crypto_symbol]):
                logging.warning(f"Skipping incomplete operation config: {op}")
                continue

            # Get current balance
            balance = self.get_balance(op_name, wallet)
            min_amount = min_amounts.get(op_name, 0)

            if balance < min_amount:
                logging.info(f"{op_name}: Balance {balance} {crypto_symbol} below minimum {min_amount}")
                continue

            # Convert to stablecoin
            result = self.convert_to_stablecoin(crypto_symbol, balance, stablecoin)

            if result and result.get("success"):
                logging.info(f"✓ Converted {balance} {crypto_symbol} → {result['received']} {stablecoin}")
                total_converted += result['received']

                # Log transaction
                self.state["conversion_history"].append({
                    "type": "daily",
                    "operation": op_name,
                    "result": result
                })
            else:
                logging.error(f"✗ Failed to convert {op_name}: {result}")

        # Update state
        self.state["last_daily_conversion"] = datetime.now().isoformat()
        self.state["total_converted_usd"] += total_converted
        self.save_state()

        logging.info(f"Daily conversion complete. Total: ${total_converted:.2f} {stablecoin}")

    def run_weekly_conversion(self):
        """Run weekly conversion: stablecoin → GBP"""
        if not self.should_run_weekly_conversion():
            logging.info("Weekly conversion not due yet")
            return

        logging.info("=" * 60)
        logging.info("Starting weekly conversion: Stablecoin → GBP")
        logging.info("=" * 60)

        weekly_config = self.config.get("weekly_conversion", {})
        provider = weekly_config.get("provider", "wise")
        min_amount = weekly_config.get("min_amount_usd", 100)

        # TODO: Get actual stablecoin balance from exchange
        # For now, use mock data
        stablecoin_balance = 1000.0  # Mock USDT balance

        if stablecoin_balance < min_amount:
            logging.info(f"Stablecoin balance ${stablecoin_balance} below minimum ${min_amount}")
            return

        # Convert to GBP
        result = self.convert_to_gbp(stablecoin_balance, provider)

        if result and result.get("success"):
            logging.info(f"✓ Converted ${result['from_amount']} → £{result['to_amount']:.2f}")

            # Log transaction
            self.state["conversion_history"].append({
                "type": "weekly",
                "result": result
            })

            # Update state
            self.state["last_weekly_conversion"] = datetime.now().isoformat()
            self.state["total_converted_gbp"] += result['to_amount']
            self.save_state()

            logging.info(f"Weekly conversion complete. Received: £{result['to_amount']:.2f}")
        else:
            logging.error(f"✗ Failed weekly conversion: {result}")

    def run(self):
        """Main run loop - check and execute conversions"""
        logging.info("Crypto Converter Service Starting")

        # Run daily conversion if due
        self.run_daily_conversion()

        # Run weekly conversion if due
        self.run_weekly_conversion()

        logging.info("Crypto Converter Service Complete")


def main():
    """Main entry point"""
    converter = CryptoConverter()
    converter.run()


if __name__ == "__main__":
    main()
