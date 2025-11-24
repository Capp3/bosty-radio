# Usage Guide

How to use your Bosty Radio in daily operation.

## Basic Operation

### Starting the Radio

The service starts automatically at boot. To start manually:

```bash
sudo systemctl start bosty-radio
```

### Normal Operation

1. **Power on** your Raspberry Pi
2. **Wait for boot** (service starts automatically)
3. **Rotate the switch** to select a position:
   - Positions 1-4: Internet radio stations
   - Position 5: Local audio file
   - Position 6: Bluetooth mode

### Stopping the Radio

```bash
sudo systemctl stop bosty-radio
```

## Rotary Switch Positions

### Positions 1-4: Internet Radio Stations

These positions play the configured internet radio streams:

1. Rotate switch to desired position (1-4)
2. LED begins blinking Morse code message (e.g., "S1", "S2")
3. Audio starts playing after a brief delay
4. If stream fails, a 500Hz error tone plays
5. LED continues blinking the station message

### Position 5: Local File

Plays a local audio file configured in settings:

1. Rotate switch to position 5
2. LED blinks the configured message (e.g., "F1")
3. Local file starts playing
4. File path must be accessible and valid

### Position 6: Bluetooth Mode

Enables Bluetooth A2DP sink to receive audio from mobile devices:

1. Rotate switch to position 6
2. MPD playback stops
3. Bluetooth enters pairing mode (discoverable)
4. A "ding" sound plays to indicate pairing needed
5. LED behavior:
   - **Blinking "BT"**: Not connected, waiting for pairing
   - **Solid ON**: Connected, receiving audio

## Morse Code Feedback

The LED provides visual feedback through Morse code patterns.

### Station Messages

Each station has a configurable Morse code message:

- **Station 1**: Typically "S1" (··· ·----)
- **Station 2**: Typically "S2" (··· ··---)
- **Station 3**: Typically "S3" (··· ···--)
- **Station 4**: Typically "S4" (··· ····-)
- **Local File**: Typically "F1" (··-. ·----)
- **Bluetooth**: Typically "BT" (-... -)

### Message Timing

Messages repeat continuously with timing based on dot duration:

- **Default**: 100ms per dot
- **Faster**: Lower values (50-80ms)
- **Slower**: Higher values (150-200ms)

### Reading Morse Code

Common patterns you'll see:

- **S** (···): Three short blinks
- **1** (·----): One short, four long
- **B** (-...): One long, three short
- **T** (-): One long blink
- **F** (..-.): Two short, one long, one short

## Bluetooth Mode

### Pairing a Device

1. Rotate switch to position 6
2. Wait for "ding" sound
3. On your phone/device:
   - Open Bluetooth settings
   - Look for "raspberrypi" or your Pi's hostname
   - Tap to pair
4. LED will turn solid when connected
5. Start playing audio on your device
6. Audio routes through Pi's audio output

### Bluetooth Connection Status

- **Blinking "BT"**: Not connected, in pairing mode
- **Solid ON**: Connected and receiving audio
- **Back to blinking**: Connection lost, re-pairing needed

### Leaving Bluetooth Mode

Rotate switch to any other position (1-5):

- Bluetooth pairing mode disabled
- MPD resumes control
- Selected station/file starts playing

## Configuration Interface

Bosty Radio includes a menu-driven TUI (Text User Interface) for easy configuration:

### Launching the TUI

```bash
# Standard way
make configure

# Direct invocation
python -m bosty_radio.tui
```

### Navigation

The TUI uses a simple menu system similar to raspi-config:

**Keyboard Controls:**
- **↑/↓ Arrow Keys**: Navigate menus
- **Enter**: Select option
- **Tab**: Move between input fields
- **Escape**: Go back
- **Q**: Quit
- **Ctrl+S**: Save configuration

### Main Menu Options

1. **Configure Stations**: Set up radio stations (1-5)
2. **Bluetooth Settings**: Configure Bluetooth mode message
3. **Audio Settings**: Adjust volume and morse timing
4. **Advanced (GPIO Pins)**: Modify GPIO pin assignments
5. **Save & Exit**: Save configuration and quit

### Configuring Stations

1. Select "Configure Stations" from main menu
2. Choose a station (1-5) to configure
3. Select input mode:
   - **Manual Entry**: Enter URL directly
   - **Select from Database**: Choose from pre-configured stations
4. Enter or verify:
   - Stream URL or file path
   - Morse code message (e.g., "S1", "S2")
   - Station name (optional)
5. Select "Save Station"
6. Repeat for other stations
7. Return to main menu with Escape

### Using Station Database

If you select "Select from Database":

1. Browse stations grouped by category (e.g., BBC, NPR)
2. Navigate with arrow keys
3. Press Enter to select
4. URL and name auto-populate
5. Edit if needed
6. Save station

### Volume Control

Volume is controlled via software (no hardware knob):

1. Run configuration: `make configure`
2. Navigate to "Audio Settings"
3. Adjust volume setting (0-100)
4. Save settings
5. Exit TUI
6. Restart service: `sudo systemctl restart bosty-radio`

Volume changes take effect immediately after restart.

### Configuration Tips

- **Unsaved Changes**: TUI warns you if you try to quit with unsaved changes
- **Validation**: Invalid inputs show error messages in red
- **Success Feedback**: Successful saves show green checkmarks
- **Non-Destructive**: Using "Back" doesn't save changes
- **Quick Save**: Use Ctrl+S to save from any screen

## Service Management

### Check Status

```bash
sudo systemctl status bosty-radio
```

### View Logs

Real-time logs:

```bash
sudo journalctl -u bosty-radio -f
```

Application logs:

```bash
tail -f /var/log/bosty-radio/controller.log
```

### Restart Service

```bash
sudo systemctl restart bosty-radio
```

### Stop Service

```bash
sudo systemctl stop bosty-radio
```

### Enable/Disable on Boot

```bash
# Enable auto-start
sudo systemctl enable bosty-radio

# Disable auto-start
sudo systemctl disable bosty-radio
```

## Error Indicators

### 500Hz Tone

A 500Hz tone plays when:

- Stream URL fails to load
- Playback fails to start
- Network connection issues

**What to do:**

1. Check internet connection
2. Verify stream URL is correct
3. Test URL manually: `mpc play <url>`
4. Check logs for details

### LED Not Blinking

If LED doesn't respond:

1. Check wiring connections
2. Verify GPIO pin in configuration
3. Check service logs for errors
4. Test LED manually (if possible)

### No Audio Output

If no sound:

1. Check MPD status: `mpc status`
2. Verify audio device in `/etc/mpd.conf`
3. Test audio: `mpc play <url>`
4. Check volume: `mpc volume`
5. Verify audio output device is connected

## Daily Usage Tips

### Startup Sequence

1. Power on Pi
2. Wait 30-60 seconds for full boot
3. Service starts automatically
4. Rotate switch to desired position
5. Wait for audio to start

### Switching Stations

Simply rotate the switch:

- Previous station stops
- New station starts
- LED updates to new message
- Smooth transition (no manual stop needed)

### Network Considerations

- **Wired ethernet**: Most reliable for streaming
- **WiFi**: Works but may have occasional dropouts
- **Stream quality**: Lower bitrate = more stable on slow connections

### Power Management

- **Safe shutdown**: `sudo shutdown -h now`
- **Reboot**: `sudo reboot`
- **Service only**: `sudo systemctl restart bosty-radio`

## Advanced Usage

### Testing Streams Manually

Before configuring, test streams:

```bash
# Test a stream URL
mpc add http://stream.example.com:8000/radio
mpc play

# Check status
mpc status

# Stop
mpc stop
```

### Monitoring Status

Watch service status in real-time:

```bash
# Systemd status
watch -n 1 'sudo systemctl status bosty-radio'

# MPD status
watch -n 1 'mpc status'
```

### Reloading Configuration

After changing config file manually:

```bash
# Restart service to reload
sudo systemctl restart bosty-radio
```

Note: The service doesn't auto-reload config changes. Restart required.

## Troubleshooting

For detailed troubleshooting, see [Troubleshooting Guide](troubleshooting.md).

Common issues:

- Service won't start
- No audio output
- Bluetooth not working
- GPIO not detecting switch

## Next Steps

- **[Troubleshooting](troubleshooting.md)**: Solve common issues
- **[Configuration](configuration.md)**: Adjust settings
- **[Development](development.md)**: Contribute to the project
