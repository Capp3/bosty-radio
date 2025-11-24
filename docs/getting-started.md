# Getting Started

Welcome to Bosty Radio! This guide will help you understand what the project is, what you need to get started, and how to quickly set up your headless internet radio.

## What is Bosty Radio?

Bosty Radio is a headless internet radio system for Raspberry Pi that uses a simple 6-position rotary switch for control and a single LED for feedback. No display, no complex menus—just rotate the switch to change stations.

## Project Overview

The system consists of:

- **Hardware**: 6-position rotary switch, single LED, Raspberry Pi
- **Software**: Python daemon monitoring GPIO and controlling audio
- **Audio Backend**: MPD (Music Player Daemon) for streaming and playback
- **Configuration**: Textual TUI accessible via SSH
- **Service**: Systemd service running at boot

## Features

- **6-Position Rotary Switch**: Select between 4 internet radio stations, 1 local file, or Bluetooth mode
- **Morse Code LED Feedback**: Visual indication of current mode (e.g., "S1" for Station 1, "BT" for Bluetooth)
- **Bluetooth A2DP Sink**: Receive audio from your phone or other Bluetooth devices
- **Error Handling**: Audio feedback (500Hz tone) when streams fail
- **Volume Control**: Software-based volume control via configuration
- **Auto-start**: Runs automatically at boot

## Requirements

### Hardware

- **Raspberry Pi 3B** (or compatible model with GPIO)
- **6-position rotary switch** (SP6T or similar)
- **Single LED** (any color, with appropriate resistor)
- **Audio output**: 3.5mm jack, HDMI, or USB DAC
- **Power supply** for Raspberry Pi
- **MicroSD card** (8GB minimum, 16GB recommended)

### Software

- **Raspberry Pi OS** (fresh installation recommended)
- **SSH access** enabled
- **Internet connection** for installation and streaming

### Optional

- **Breadboard and jumper wires** for prototyping
- **Resistors** (220Ω for LED, pull-down resistors if needed)
- **Enclosure** for final installation

## Quick Start

If you're ready to get started immediately:

1. **Prepare your Raspberry Pi**:

   ```bash
   # Flash Raspberry Pi OS to SD card
   # Enable SSH
   # Boot and connect via SSH
   ```

2. **Clone and install**:

   ```bash
   git clone <repository-url>
   cd bosty-radio
   make install
   ```

3. **Configure**:

   ```bash
   make configure
   # Follow the TUI to set up your stations
   ```

4. **Start the service**:

   ```bash
   sudo systemctl start bosty-radio
   sudo systemctl enable bosty-radio
   ```

5. **Wire your hardware** (see [Hardware Setup](hardware-setup.md))

6. **Test**: Rotate the switch and listen!

## What's Next?

- **[Hardware Setup](hardware-setup.md)**: Detailed wiring instructions
- **[Installation](installation.md)**: Complete installation guide
- **[Configuration](configuration.md)**: Setting up your stations
- **[Usage Guide](usage.md)**: How to use your radio

## Understanding the System

### Rotary Switch Positions

| Position | Function       | Description                               |
| -------- | -------------- | ----------------------------------------- |
| 1-4      | Internet Radio | Four configurable internet radio stations |
| 5        | Local File     | Play a local audio file                   |
| 6        | Bluetooth      | Bluetooth A2DP sink mode                  |

### Morse Code Feedback

The LED provides visual feedback through Morse code:

- **Stations 1-5**: Blinks the configured message (e.g., "S1", "S2", "F1")
- **Bluetooth Mode**:
  - Blinks "BT" when not connected
  - Solid ON when connected
- **Continuous**: Messages repeat until position changes

### Configuration

All configuration is done via a Textual TUI over SSH. No need to edit files manually—the TUI guides you through:

- Station URLs or file paths
- Morse code messages
- Volume settings
- GPIO pin mapping (advanced)

## Support

If you encounter issues:

1. Check the [Troubleshooting](troubleshooting.md) guide
2. Review service logs: `sudo journalctl -u bosty-radio -f`
3. Check application logs: `/var/log/bosty-radio/controller.log`

## Project Philosophy

Bosty Radio is designed with simplicity in mind:

- **Focused scope**: Core functionality only, no feature creep
- **Modular design**: Easy to understand and maintain
- **User-friendly**: Simple configuration, clear feedback
- **Reliable**: Error handling and recovery built-in

Ready to build your radio? Continue to [Hardware Setup](hardware-setup.md)!
