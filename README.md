# bosty-radio

Headless GPIO Rotary Internet Radio for Raspberry Pi

A dedicated, headless internet radio controlled exclusively by a 6-position rotary switch with Morse code LED feedback. All configuration is managed via a Textual TUI over SSH.

## Features

- **6-Position Rotary Switch Control**: Switch between 4 internet radio stations, 1 local file, and Bluetooth mode
- **Morse Code LED Feedback**: Visual feedback showing current mode via repeating Morse code patterns
- **Bluetooth A2DP Sink**: Position 6 enables Bluetooth pairing and audio reception from mobile devices
- **Error Handling**: 500Hz tone plays on stream failures
- **Textual TUI Configuration**: Easy configuration via SSH with helpful source format guidance
- **Volume Control**: Software volume control via TUI (no hardware volume knob needed)
- **Systemd Service**: Runs automatically at boot

## Hardware Requirements

- Raspberry Pi 3B (or compatible)
- 6-position rotary switch
- Single LED for Morse code feedback
- Audio output (3.5mm jack, HDMI, or USB DAC)

## Hardware Wiring

| Component                | GPIO Pin (BCM) | Function                | Notes                     |
| ------------------------ | -------------- | ----------------------- | ------------------------- |
| Rotary Switch Position 1 | GPIO 2         | Station 1               | Pulled High when selected |
| Rotary Switch Position 2 | GPIO 3         | Station 2               | Pulled High when selected |
| Rotary Switch Position 3 | GPIO 4         | Station 3               | Pulled High when selected |
| Rotary Switch Position 4 | GPIO 17        | Station 4               | Pulled High when selected |
| Rotary Switch Position 5 | GPIO 27        | Recorded Audio File     | Pulled High when selected |
| Rotary Switch Position 6 | GPIO 22        | Bluetooth Receiver Mode | Pulled High when selected |
| LED                      | GPIO 18        | Morse Code              | Status/Feedback Output    |

**Important**: The rotary switch connects the selected pin to 3.3V (pulled high). The software configures internal pull-down resistors on all input pins.

## Installation

### Prerequisites

- Fresh Raspberry Pi OS installation
- SSH access enabled
- Internet connection

### Quick Install

```bash
# Clone the repository
git clone <repository-url>
cd bosty-radio

# Run full installation
make install
```

This will:

1. Install system dependencies (MPD, MPC, Bluetooth tools, etc.)
2. Configure MPD for audio playback
3. Set up Bluetooth
4. Install Python package with UV
5. Install systemd service

### Manual Installation Steps

If you prefer step-by-step:

```bash
# Install system dependencies
make install-deps

# Configure MPD
make install-mpd

# Configure Bluetooth
make install-bluetooth

# Install Python package
make install-python

# Install systemd service
make install-service
```

### Post-Installation Configuration

1. **Configure MPD audio output** (if needed):

   ```bash
   sudo nano /etc/mpd.conf
   # Set your audio_output device (alsa, pulse, etc.)
   ```

2. **Run configuration TUI**:

   ```bash
   make configure
   # or
   uv run python -m bosty_radio.tui
   ```

3. **Start the service**:

   ```bash
   sudo systemctl start bosty-radio
   sudo systemctl enable bosty-radio  # Enable on boot
   ```

4. **Check status**:
   ```bash
   sudo systemctl status bosty-radio
   ```

## Configuration

### Using the TUI

Run the configuration interface:

```bash
make configure
```

The TUI allows you to configure:

- **Stations 1-5**: Stream URLs or local file paths, Morse code messages, optional names
- **Bluetooth Mode**: Morse code message for Bluetooth mode
- **Morse Code Settings**: Dot duration in milliseconds
- **Volume**: Default volume level (0-100)
- **GPIO Pins**: Advanced pin mapping (defaults are usually fine)

### Allowed Sources

The TUI shows help for allowed source formats:

**Internet Radio:**

- Direct stream URLs: `http://stream.example.com:8000/stream.mp3`
- HTTPS streams: `https://example.com/stream.m3u`
- Playlist files: `http://example.com/playlist.pls`

**Local Files:**

- MP3 files: `/home/pi/music/station.mp3`
- Playlist files: `/home/pi/music/playlist.m3u`
- Any audio format supported by MPD

### Configuration File Location

- System config: `/etc/bosty-radio/config.json`
- User config: `~/.config/bosty-radio/config.json`

The system checks system location first, then falls back to user location.

## Usage

### Normal Operation

1. Power on the Raspberry Pi
2. The service starts automatically at boot
3. Rotate the switch to select a position:
   - **Positions 1-4**: Internet radio stations
   - **Position 5**: Local audio file
   - **Position 6**: Bluetooth mode (enters pairing, plays "ding" sound)

### Morse Code Feedback

- **Stations 1-5**: LED blinks the configured Morse code message (e.g., "S1", "S2") continuously
- **Bluetooth Mode**:
  - LED blinks "BT" when not connected
  - LED stays solid ON when connected
- **Error**: 500Hz tone plays if stream fails to start

### Bluetooth Mode

When switching to position 6:

1. MPD playback stops
2. Bluetooth enters pairing mode (discoverable)
3. A "ding" sound plays to indicate pairing is needed
4. LED shows connection status:
   - Blinking "BT" = not connected
   - Solid ON = connected

Pair your phone/device, then audio will route through the Pi's audio output.

### Volume Control

Volume is controlled via the TUI configuration. There is no hardware volume control. To change volume:

1. Run `make configure`
2. Adjust the volume setting (0-100)
3. Save configuration
4. Restart service: `sudo systemctl restart bosty-radio`

## Service Management

```bash
# Start service
sudo systemctl start bosty-radio

# Stop service
sudo systemctl stop bosty-radio

# Restart service
sudo systemctl restart bosty-radio

# Check status
sudo systemctl status bosty-radio

# View logs
sudo journalctl -u bosty-radio -f

# Enable on boot
sudo systemctl enable bosty-radio

# Disable on boot
sudo systemctl disable bosty-radio
```

## Logs

- Service logs: `journalctl -u bosty-radio`
- Application logs: `/var/log/bosty-radio/controller.log`

## Project Structure

```
bosty-radio/
├── bosty_radio/          # Main Python package
│   ├── __init__.py
│   ├── config.py         # Configuration management
│   ├── gpio_controller.py # GPIO input handling
│   ├── morse_led.py      # Morse code LED control
│   ├── audio_controller.py # MPD/MPC audio control
│   ├── bluetooth_controller.py # Bluetooth A2DP sink
│   ├── radio_controller.py # Main daemon
│   └── tui.py            # Textual configuration TUI
├── systemd/
│   └── bosty-radio.service # Systemd service file
├── Makefile              # Installation and management
├── pyproject.toml        # Python project config (UV)
└── README.md
```

## Development

### Setup Development Environment

```bash
# Install UV (if not already installed)
make install

# Sync dependencies
uv sync

# Run TUI locally (will show import errors for RPi.GPIO, that's OK)
uv run python -m bosty_radio.tui
```

### Testing on Raspberry Pi

The code must run on a Raspberry Pi with RPi.GPIO available. For development on non-Pi systems, the GPIO modules will show import warnings but the TUI can still be tested.

## Troubleshooting

### Service won't start

- Check logs: `sudo journalctl -u bosty-radio`
- Verify MPD is running: `systemctl status mpd`
- Verify Bluetooth is running: `systemctl status bluetooth`
- Check GPIO permissions (may need to run as root)

### No audio output

- Verify MPD configuration: `mpc status`
- Check audio device: `aplay -l`
- Test MPD directly: `mpc play <url>`
- Verify volume: `mpc volume`

### Bluetooth not working

- Check Bluetooth service: `systemctl status bluetooth`
- Verify pairing mode: `bluetoothctl show`
- Check audio routing: `pactl list sinks`

### GPIO not detecting switch

- Verify wiring connections
- Check GPIO pins with: `gpio readall` (if wiringpi installed)
- Verify pull-down configuration in code
- Check for pin conflicts

## Uninstallation

```bash
make uninstall
```

This removes the systemd service and system directories but keeps the Python package and user configuration files.

## License

See LICENSE file.

## Contributing

This is a focused project with minimal feature scope. Contributions should maintain simplicity and avoid feature creep.
