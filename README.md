# KaspaMine Income Calculator Web App

A modern web application for calculating real-time Kaspa mining income projections for IceRiver KS5M miners.

## Features

- **Real-time Data**: Fetches live KAS price from CoinGecko and network stats from 2Miners API
- **Income Projections**: Calculates daily, monthly, and yearly income for different mining pools
- **Pool Comparison**: Compare EMCD (0% fee) vs 2Miners (1% fee) pools
- **Scaling Calculator**: See income projections for 1, 5, 10, and 20 miners
- **ROI Calculator**: Calculate hardware payback period
- **Auto-refresh**: Data updates every 5 minutes automatically

## Quick Start

### Prerequisites
- Python 3.8 or higher
- Internet connection for API data

### Installation

1. **Clone or download** this repository

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python app.py
   ```

4. **Open your browser** and go to: `http://localhost:5000`

### Alternative Startup Script

You can also use the provided startup script:
```bash
./start.sh
```

## Usage

### Web Interface
- **Market Data**: Current KAS price and network hashrate
- **Miner Specs**: IceRiver KS5M specifications and ROI
- **Income Comparison**: Side-by-side comparison of mining pools
- **Scaling Table**: Projections for multiple miners

### Manual Refresh
Click the "Refresh" button to manually update all data from APIs.

### Auto-Refresh
The application automatically refreshes data every 5 minutes in the background.

## API Endpoints

- `GET /`: Main dashboard
- `GET /api/calculator`: Get current calculator data
- `GET /api/refresh`: Force refresh of calculator data

## Data Sources

- **KAS Price**: CoinGecko API (GBP)
- **Network Stats**: 2Miners Pool API (real-time network hashrate, difficulty)
- **Pool Stats**: 2Miners Pool API

## Configuration

The application is pre-configured for IceRiver KS5M miners with:
- Hashrate: 15 TH/s
- Power: 3400 W
- Cost: £600

To modify these values, edit the constants at the top of `app.py`.

## Troubleshooting

### Common Issues

1. **"Failed to fetch calculator data"**
   - Check your internet connection
   - APIs might be temporarily unavailable
   - Try refreshing the page

2. **Port 5000 already in use**
   - Change the port in `app.py`: `app.run(port=5001)`

3. **Import errors**
   - Make sure all requirements are installed: `pip install -r requirements.txt`

### Logs
Check the terminal output for detailed error messages and API status.

## Development

### Project Structure
```
├── app.py              # Flask application
├── requirements.txt    # Python dependencies
├── templates/
│   └── index.html      # Web interface
├── static/             # Static files (CSS, JS)
├── start.sh           # Startup script
└── README.md          # This file
```

### Adding New Features
- Modify calculator logic in `app.py`
- Update the web interface in `templates/index.html`
- Add new API endpoints as needed

## License

This project is provided as-is for educational and personal use.