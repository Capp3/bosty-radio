# Configuration

Complete guide to configuring Bosty Radio using the Textual TUI interface.

## Overview

All configuration is done through a Terminal User Interface (TUI) accessible via SSH. The TUI provides a user-friendly way to configure stations, Morse code messages, volume, and GPIO pins without editing JSON files manually.

## Starting the Configuration TUI

Run the configuration interface:

```bash
make configure
```

Or directly:

```bash
uv run python -m bosty_radio.tui
```

You can also specify a custom config file path:

```bash
uv run python -m bosty_radio.tui /path/to/config.json
```

## TUI Navigation

The TUI uses a menu-driven interface similar to raspi-config for simple, intuitive navigation.

### Main Menu

When you start the TUI, you'll see the main menu with these options:

1. **Configure Stations** - Set up radio stations 1-5
2. **Bluetooth Settings** - Configure Bluetooth mode
3. **Audio Settings** - Volume and morse timing
4. **Advanced (GPIO Pins)** - Pin assignments
5. **Save & Exit** - Save all changes and quit

### Keyboard Shortcuts

**Navigation:**
- **↑/↓ Arrow Keys**: Navigate menu items
- **Enter**: Select menu option
- **Tab**: Move between input fields
- **Escape**: Go back to previous menu
- **Q**: Quit (warns if unsaved changes)

**Actions:**
- **Ctrl+S**: Save configuration from any screen
- **Escape**: Return to previous menu without saving

### Navigation Flow

1. Start at Main Menu
2. Select a category (e.g., "Configure Stations")
3. Choose specific item to edit (e.g., "Station 1")
4. Make changes
5. Save (auto-returns to previous screen)
6. Navigate back with Escape to return to Main Menu
7. Select "Save & Exit" when done

### Mouse Support

The TUI also supports mouse interaction:

- Click to select menu items
- Click to activate buttons
- Scroll to view long lists

## Configuration Sections

### Stations (Positions 1-5)

Configure each of the 5 stations that correspond to rotary switch positions 1-5.

**To configure a station:**

1. Select "Configure Stations" from main menu
2. Choose a station (1-5)
3. Select input mode:
   - **Manual Entry**: Enter URL directly
   - **Select from Database**: Choose from pre-configured stations
4. Enter or verify fields:
   - **URL/Path**: Stream URL or local file path
   - **Morse Code Message**: Text to display via LED (e.g., "S1", "S2", "F1")
   - **Name** (optional): Human-readable station name
5. Select "Save Station"

**Using the Station Database:**

If you choose "Select from Database":
- Stations are grouped by category (e.g., "BBC", "NPR")
- Navigate with arrow keys
- Press Enter to select
- URL and name will auto-populate
- You can still edit fields after selection

#### Allowed Source Formats

**Internet Radio Streams:**

- Direct MP3 streams: `http://stream.example.com:8000/stream.mp3`
- HTTPS streams: `https://example.com/stream.m3u`
- Playlist files: `http://example.com/playlist.pls`
- M3U playlists: `http://example.com/playlist.m3u`

**Local Files:**

- MP3 files: `/home/pi/music/station.mp3`
- M3U playlists: `/home/pi/music/playlist.m3u`
- Any audio format supported by MPD

#### Examples

```
Station 1:
  URL: http://stream.example.com:8000/radio
  Morse: S1
  Name: Example Radio

Station 5 (Local File):
  URL: /home/pi/music/recording.mp3
  Morse: F1
  Name: My Recording
```

### Bluetooth Mode

Configure the Morse code message displayed when rotary switch is in position 6 (Bluetooth mode).

- **Morse Code Message**: Default is "BT"
- The LED will blink this message when not connected
- LED stays solid ON when a device is connected

### Morse Code Settings

Control the timing of Morse code messages:

- **Dot Duration (ms)**: Base timing unit (default: 100ms)
  - Range: 50-500ms
  - Smaller values = faster blinking
  - Larger values = slower, more readable

The timing follows standard Morse code ratios:

- Dot = 1 unit
- Dash = 3 units
- Element gap = 1 unit
- Letter gap = 3 units
- Word gap = 7 units

### Volume

Set the default volume level:

- **Volume**: 0-100 (default: 80)
- This is the software volume control
- No hardware volume knob is provided
- Change requires service restart

### GPIO Pins (Advanced)

Modify GPIO pin assignments if needed (defaults usually work):

- **Position 1-6**: GPIO pins for rotary switch positions
- **LED**: GPIO pin for Morse code LED

!!! warning "Pin Changes"
Only change GPIO pins if you have a specific reason (pin conflicts, custom wiring). Default pins are tested and recommended.

## Configuration File Structure

The configuration is stored as JSON. Here's the structure:

```json
{
  "stations": [
    {
      "url": "http://stream.example.com:8000/radio",
      "morse_message": "S1",
      "name": "Station 1"
    },
    {
      "url": "https://example.com/stream.m3u",
      "morse_message": "S2",
      "name": "Station 2"
    },
    {
      "url": "http://example.com/playlist.pls",
      "morse_message": "S3",
      "name": "Station 3"
    },
    {
      "url": "http://stream.example.com:8080/radio",
      "morse_message": "S4",
      "name": "Station 4"
    },
    {
      "url": "/home/pi/music/recording.mp3",
      "morse_message": "F1",
      "name": "Local File"
    }
  ],
  "bluetooth_morse": "BT",
  "morse_dot_duration_ms": 100,
  "volume": 80,
  "error_tone_frequency_hz": 500,
  "gpio": {
    "position_1": 2,
    "position_2": 3,
    "position_3": 4,
    "position_4": 17,
    "position_5": 27,
    "position_6": 22,
    "led": 18
  }
}
```

## Configuration File Locations

The system checks for configuration files in this order:

1. **System config**: `/etc/bosty-radio/config.json` (requires root)
2. **User config**: `~/.config/bosty-radio/config.json` (user directory)

The TUI will create the file in the appropriate location based on permissions.

## Saving Configuration

### Saving Individual Sections

When editing a specific section (Station, Bluetooth, Audio, Advanced):

1. Make your changes
2. Select "Save Settings" or "Save Station"
3. Status message shows success (green ✓) or error (red ✗)
4. Automatically returns to previous menu

### Saving All and Exiting

From the main menu:

1. Select "Save & Exit"
2. All changes are written to the config file
3. TUI closes automatically

### Quick Save

Press **Ctrl+S** from any screen to save immediately.

### Unsaved Changes Warning

If you try to quit with unsaved changes, the TUI will warn you and prevent quitting until you either:
- Save your changes (Ctrl+S or "Save & Exit")
- Acknowledge you want to discard changes

### Applying Changes

After saving configuration, restart the service:

```bash
sudo systemctl restart bosty-radio
```

## Validation

The TUI validates configuration before saving:

- **Station URLs**: Must be valid URLs or file paths
- **Morse messages**: Must be non-empty
- **Volume**: Must be 0-100
- **GPIO pins**: Must be valid GPIO numbers (2-27)
- **Dot duration**: Must be 50-500ms

If validation fails, an error message will be displayed.

## Editing Configuration Manually

While the TUI is recommended, you can edit the JSON file directly:

```bash
sudo nano /etc/bosty-radio/config.json
# or
nano ~/.config/bosty-radio/config.json
```

After editing, validate and restart:

```bash
# Test JSON syntax
python3 -m json.tool /etc/bosty-radio/config.json

# Restart service
sudo systemctl restart bosty-radio
```

## Configuration Tips

### Finding Radio Stream URLs

1. **Check station websites**: Many stations provide direct stream URLs
2. **Use radio directories**: Sites like RadioBrowser, TuneIn
3. **Test URLs**: Use `mpc play <url>` to test before configuring
4. **M3U/PLS playlists**: Often more reliable than direct streams

### Morse Code Messages

Keep messages short and memorable:

- **Good**: "S1", "S2", "BT", "F1"
- **Avoid**: Long messages like "STATIONONE" (hard to read)

### Volume Levels

- **0-30**: Very quiet
- **40-60**: Moderate
- **70-85**: Normal listening (recommended)
- **90-100**: Loud (may cause distortion)

### Testing Configuration

After saving:

1. Check service status: `sudo systemctl status bosty-radio`
2. Check logs: `sudo journalctl -u bosty-radio -f`
3. Test each position on the rotary switch
4. Verify Morse code messages are correct
5. Test audio playback

## Troubleshooting Configuration

### TUI Won't Start

- Check Python version: `python3 --version` (needs 3.12+)
- Check UV installation: `uv --version`
- Try: `uv sync --system` to reinstall dependencies

### Configuration Not Saving

- Check file permissions
- Ensure directory exists: `mkdir -p ~/.config/bosty-radio`
- Check disk space: `df -h`

### Changes Not Applied

- Restart service: `sudo systemctl restart bosty-radio`
- Check logs for errors: `sudo journalctl -u bosty-radio -n 50`
- Verify config file location

### Invalid URLs

- Test URL with: `mpc play <url>`
- Check internet connection
- Verify URL format (must start with http:// or https://)

## Next Steps

After configuration:

1. **[Wire your hardware](hardware-setup.md)** if not already done
2. **[Start using your radio](usage.md)**
3. **[Troubleshoot issues](troubleshooting.md)** if needed
