# Installation

Complete step-by-step installation guide for Bosty Radio on Raspberry Pi OS.

## Prerequisites

Before starting, ensure you have:

- **Fresh Raspberry Pi OS installation** (recommended: latest Raspberry Pi OS Lite or Desktop)
- **SSH access** enabled
- **Internet connection** on the Pi
- **Root/sudo access** for installation

## Quick Installation

The fastest way to install:

```bash
git clone <repository-url>
cd bosty-radio
make install
```

This single command installs everything needed. Continue reading for detailed steps.

## Detailed Installation Steps

### Step 1: Prepare Raspberry Pi

1. **Flash Raspberry Pi OS** to microSD card using Raspberry Pi Imager
2. **Enable SSH**: Create empty `ssh` file in boot partition (or use Imager's advanced options)
3. **Boot the Pi** and connect via SSH
4. **Update system**:
   ```bash
   sudo apt-get update
   sudo apt-get upgrade -y
   ```

### Step 2: Clone Repository

```bash
cd ~
git clone <repository-url>
cd bosty-radio
```

### Step 3: Install System Dependencies

The installation process handles this automatically, but you can run individually:

```bash
make install-deps
```

This installs:

- `mpd` - Music Player Daemon
- `mpc` - Music Player Client
- `bluez` - Bluetooth stack
- `bluez-tools` - Bluetooth utilities
- `pulseaudio` - Audio system
- `pulseaudio-module-bluetooth` - Bluetooth audio support
- `sox` - Audio utilities (for error tones)
- `python3` - Python interpreter
- `python3-pip` - Python package manager
- `curl` - For downloading UV

### Step 4: Configure MPD

```bash
make install-mpd
```

This creates necessary directories and sets permissions. You may need to configure audio output:

```bash
sudo nano /etc/mpd.conf
```

Common audio output configurations:

**ALSA (3.5mm jack)**:

```conf
audio_output {
    type "alsa"
    name "My ALSA Device"
    device "hw:0,0"
}
```

**PulseAudio**:

```conf
audio_output {
    type "pulse"
    name "My Pulse Device"
}
```

**HDMI**:

```conf
audio_output {
    type "alsa"
    name "My HDMI Device"
    device "hw:1,0"
}
```

After editing, restart MPD:

```bash
sudo systemctl restart mpd
```

### Step 5: Configure Bluetooth

```bash
make install-bluetooth
```

This enables the Bluetooth service and adds your user to the bluetooth group.

### Step 6: Install Python Package

```bash
make install-python
```

This:

1. Installs UV package manager (if not already installed)
2. Syncs Python dependencies using UV
3. Installs the `bosty-radio` package

### Step 7: Install Systemd Service

```bash
make install-service
```

This:

1. Copies the systemd service file to `/etc/systemd/system/`
2. Reloads systemd daemon
3. Creates log directory at `/var/log/bosty-radio/`

## Post-Installation Configuration

### 1. Configure Stations

Run the configuration TUI:

```bash
make configure
```

Or directly:

```bash
uv run python -m bosty_radio.tui
```

See [Configuration](configuration.md) for detailed instructions.

### 2. Start and Enable Service

```bash
# Start the service
sudo systemctl start bosty-radio

# Enable on boot
sudo systemctl enable bosty-radio

# Check status
sudo systemctl status bosty-radio
```

### 3. Verify Installation

Check that everything is working:

```bash
# Check service status
sudo systemctl status bosty-radio

# Check logs
sudo journalctl -u bosty-radio -f

# Check application logs
tail -f /var/log/bosty-radio/controller.log

# Test MPD
mpc status
mpc play <test-url>
```

## Installation Verification Checklist

- [ ] System dependencies installed
- [ ] MPD configured and running (`systemctl status mpd`)
- [ ] Bluetooth service running (`systemctl status bluetooth`)
- [ ] Python package installed (`uv run python -m bosty_radio.tui` works)
- [ ] Systemd service installed (`systemctl status bosty-radio`)
- [ ] Configuration file created (via TUI)
- [ ] Service starts without errors
- [ ] Logs show no errors

## Manual Installation (Alternative)

If you prefer to install components manually:

### Install UV

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Install Python Dependencies

```bash
uv sync --system
```

### Create Service File

```bash
sudo mkdir -p /etc/bosty-radio
sudo mkdir -p /var/log/bosty-radio
sudo cp systemd/bosty-radio.service /etc/systemd/system/
sudo systemctl daemon-reload
```

## Troubleshooting Installation

### UV Installation Fails

If UV installation fails:

```bash
# Try manual installation
curl -LsSf https://astral.sh/uv/install.sh | sh
# Add to PATH if needed
export PATH="$HOME/.cargo/bin:$PATH"
```

### MPD Won't Start

Check MPD configuration:

```bash
# Test configuration
sudo mpd --no-daemon --stdout /etc/mpd.conf

# Check for errors
sudo journalctl -u mpd
```

### Service Fails to Start

Check service logs:

```bash
sudo journalctl -u bosty-radio -n 50
```

Common issues:

- **GPIO permissions**: Service may need to run as root
- **MPD not running**: Ensure MPD service is active
- **Config file missing**: Run `make configure` first
- **UV not found**: Check PATH in service file

### Python Import Errors

If you see import errors for RPi.GPIO:

- This is **normal on non-Pi systems** (macOS, etc.)
- On Raspberry Pi, ensure RPi.GPIO installed: `uv sync --system`
- Check Python version: `python3 --version` (needs 3.12+)

## Uninstallation

To remove Bosty Radio:

```bash
make uninstall
```

This removes:

- Systemd service
- System directories (`/etc/bosty-radio`, `/var/log/bosty-radio`)

It does **not** remove:

- Python package (can be removed with `uv pip uninstall bosty-radio`)
- User configuration files (`~/.config/bosty-radio/`)
- MPD or Bluetooth (system packages)

## Next Steps

After installation:

1. **[Configure your stations](configuration.md)** - Set up your radio stations
2. **[Wire your hardware](hardware-setup.md)** - Connect rotary switch and LED
3. **[Start using your radio](usage.md)** - Enjoy your headless radio!

## System Requirements

### Minimum Requirements

- **Raspberry Pi 3B** or newer
- **512MB RAM** (1GB recommended)
- **8GB microSD card** (16GB recommended)
- **Stable internet connection** for streaming

### Recommended Setup

- **Raspberry Pi 4** (better performance)
- **2GB+ RAM**
- **32GB+ microSD card** (Class 10 or better)
- **Wired ethernet** for stable streaming
- **USB DAC** for better audio quality

## Performance Considerations

- **SD card speed**: Use Class 10 or better for smooth operation
- **Network**: Wired ethernet recommended for stable streaming
- **Audio**: USB DAC provides better quality than 3.5mm jack
- **Power**: Use official Pi power supply for stability
