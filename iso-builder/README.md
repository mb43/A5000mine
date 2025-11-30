# A5000mine ISO Builder

A web-based interface for creating custom bootable ISOs for A5000 Aeternity mining rigs.

## Features

- **Easy Configuration**: Web interface for configuring wallet, worker name, mining pool, and GPU settings
- **Pool Selection**: Choose from popular pools (2Miners, F2Pool) or enter custom pool URL
- **GPU Optimization**: Configure power limits and clock offsets for optimal performance
- **Real-time Progress**: Monitor build progress with live logs and status updates
- **One-click Download**: Download completed ISOs directly from the browser

## Requirements

- Linux system with root access
- Python 3.6+
- Internet connection (for downloading Ubuntu base ISO)
- Sufficient disk space (minimum 10GB free)

## Installation

1. Clone or download the A5000mine repository
2. Navigate to the iso-builder directory
3. Run the startup script with sudo:

```bash
cd iso-builder
sudo ./start-builder.sh
```

## Usage

1. **Access the Web Interface**
   - Open your browser and go to `http://localhost:3000` (with sudo) or `http://localhost:8000` (without sudo)

2. **Configure Your Mining Setup**
   - **Wallet Address**: Enter your Aeternity wallet address (must start with `ak_`)
   - **Worker Name**: Unique identifier for this mining rig
   - **Mining Pool**: Select from popular pools or enter custom stratum URL
   - **GPU Settings**: Configure power limit and clock offsets

3. **Build the ISO**
   - Click "🚀 Build Custom ISO"
   - Monitor progress in real-time
   - Wait for completion (typically 15-30 minutes)

4. **Download and Install**
   - Download the completed ISO file
   - Write to USB drive: `sudo dd if=a5000mine.iso of=/dev/sdX bs=4M status=progress`
   - Boot from USB and start mining

## Configuration Options

### Wallet
- **Address**: Your Aeternity wallet address (required)
- Must start with `ak_`

### Worker
- **Name**: Unique identifier for your mining rig
- Default: `rig-01`

### Mining Pool
- **2Miners**: `stratum+tcp://ae.2miners.com:4040` (1% fee, recommended)
- **F2Pool**: `stratum+tcp://ae.f2pool.com:4040` (2% fee)
- **Custom**: Enter your own stratum URL

### GPU Settings
- **Power Limit**: GPU power consumption in watts (100-300W, default: 230W)
- **Core Clock Offset**: GPU core clock adjustment in MHz (-500 to +500, default: 0)
- **Memory Clock Offset**: GPU memory clock adjustment in MHz (-500 to +500, default: 0)

## API Endpoints

The ISO builder provides a REST API for integration:

- `POST /api/build-iso`: Start ISO build with configuration
- `GET /api/build-status?id={build_id}`: Get build progress
- `GET /api/download/{filename}`: Download completed ISO

## Troubleshooting

### Build Fails
- Ensure you're running with `sudo` (root privileges required)
- Check available disk space (minimum 10GB)
- Verify internet connection for Ubuntu ISO download

### Web Interface Won't Load
- Check if port 3000 is available
- Ensure Python 3 is installed
- Try running: `python3 server.py` directly

### Mining Issues After Installation
- Verify wallet address format
- Check pool URL is correct
- Ensure GPU drivers are properly installed (automatic in ISO)

## Security Notes

- The web interface runs locally only (localhost:3000)
- No external access required or enabled
- Configuration data is processed locally
- Downloaded ISOs contain your wallet information

## Technical Details

- **Base OS**: Ubuntu 22.04 Server
- **Miner**: lolMiner v1.88 (latest Aeternity-compatible version)
- **GPU Support**: NVIDIA A5000 with optimized drivers
- **Build Process**: Customizes Ubuntu live ISO with mining software and configuration

## Support

For issues or questions:
1. Check the build logs for error messages
2. Verify configuration settings are correct
3. Ensure system meets requirements
4. Review troubleshooting section above
