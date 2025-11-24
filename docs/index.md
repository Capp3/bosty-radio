# Bosty Radio

**Headless GPIO Rotary Internet Radio for Raspberry Pi**

A dedicated, headless internet radio controlled exclusively by a 6-position rotary switch with Morse code LED feedback. All configuration is managed via a Textual TUI over SSH.

## Overview

Bosty Radio transforms a Raspberry Pi into a simple, elegant internet radio that requires no display or complex controls. Just rotate a switch to select your station, and a single LED provides visual feedback through Morse code.

## Key Features

- **6-Position Rotary Switch Control**: Switch between 4 internet radio stations, 1 local file, and Bluetooth mode
- **Morse Code LED Feedback**: Visual feedback showing current mode via repeating Morse code patterns
- **Bluetooth A2DP Sink**: Position 6 enables Bluetooth pairing and audio reception from mobile devices
- **Error Handling**: 500Hz tone plays on stream failures
- **Textual TUI Configuration**: Easy configuration via SSH with helpful source format guidance
- **Volume Control**: Software volume control via TUI (no hardware volume knob needed)
- **Systemd Service**: Runs automatically at boot

## Quick Start

1. **Hardware Setup**: Wire a 6-position rotary switch and LED to your Raspberry Pi GPIO pins
2. **Installation**: Run `make install` on a fresh Raspberry Pi OS installation
3. **Configuration**: Run `make configure` to set up your stations via the TUI
4. **Start**: The service starts automatically at boot, or run `sudo systemctl start bosty-radio`

## Documentation Sections

### For Users

- **[Getting Started](getting-started.md)** - Project overview, requirements, and quick start
- **[Hardware Setup](hardware-setup.md)** - GPIO wiring diagrams and component requirements
- **[Installation](installation.md)** - Step-by-step installation instructions
- **[Configuration](configuration.md)** - Using the TUI and configuring stations
- **[Usage Guide](usage.md)** - Daily operation and features
- **[Troubleshooting](troubleshooting.md)** - Common issues and solutions

### For Developers

- **[Development Guide](development.md)** - Setting up development environment
- **[Architecture](architecture.md)** - System design and component interactions
- **[API Reference](api/config.md)** - Complete API documentation for all modules

## Hardware Requirements

- Raspberry Pi 3B (or compatible)
- 6-position rotary switch
- Single LED for Morse code feedback
- Audio output (3.5mm jack, HDMI, or USB DAC)

## Software Stack

- **Python 3.12+** with UV package management
- **MPD/MPC** for audio playback
- **BlueZ** for Bluetooth A2DP sink
- **Textual** for configuration TUI
- **RPi.GPIO** for hardware control

## Project Philosophy

Bosty Radio follows a philosophy of simplicity and focus:

- **No feature creep**: Core functionality only
- **Modular design**: Clean separation of concerns
- **Error recovery**: Graceful handling of failures
- **User-friendly**: Simple configuration via TUI

## License

See LICENSE file for details.

## Contributing

This is a focused project with minimal feature scope. Contributions should maintain simplicity and avoid feature creep.
