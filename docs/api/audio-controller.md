# Audio Controller API

API reference for the `bosty_radio.audio_controller` module.

## Overview

The audio controller module manages audio playback via MPD (Music Player Daemon) and MPC (Music Player Client). It handles streaming internet radio, playing local files, controlling volume, and playing error tones.

## Module: `bosty_radio.audio_controller`

## Classes

### `AudioController`

Manages audio playback via MPD/MPC.

```python
class AudioController:
    def __init__(self, error_tone_frequency_hz: int = 500)
    def play_stream(self, url: str) -> bool
    def stop(self) -> None
    def set_volume(self, volume: int) -> bool
    def get_status(self) -> Optional[str]
    def is_playing(self) -> bool
```

#### Constructor

**`__init__(error_tone_frequency_hz: int = 500)`**

Initialize audio controller.

**Parameters:**

- **`error_tone_frequency_hz`** (`int`, default: 500): Frequency for error tone in Hz

**Example:**

```python
audio = AudioController(error_tone_frequency_hz=500)
```

#### Methods

**`play_stream(url: str) -> bool`**

Play an internet radio stream or local file.

**Parameters:**

- **`url`** (`str`): Stream URL or file path

**Returns:**

- **`bool`**: True if successful, False otherwise

**Behavior:**

1. Stops current playback
2. Clears playlist
3. Adds URL to playlist
4. Starts playback
5. Verifies playback actually started
6. Plays error tone if failed

**Example:**

```python
success = audio.play_stream("http://stream.example.com:8000/radio")
if success:
    print("Playing")
else:
    print("Failed to play")
```

**`stop() -> None`**

Stop audio playback.

**Behavior:**

- Stops MPD playback
- Clears current URL tracking

**Example:**

```python
audio.stop()
```

**`set_volume(volume: int) -> bool`**

Set volume level (0-100).

**Parameters:**

- **`volume`** (`int`): Volume level 0-100

**Returns:**

- **`bool`**: True if successful

**Example:**

```python
audio.set_volume(80)  # 80% volume
```

**`get_status() -> Optional[str]`**

Get current playback status.

**Returns:**

- **`Optional[str]`**: MPD status output, or None on error

**Example:**

```python
status = audio.get_status()
if status:
    print(status)
```

**`is_playing() -> bool`**

Check if audio is currently playing.

**Returns:**

- **`bool`**: True if playing, False otherwise

**Example:**

```python
if audio.is_playing():
    print("Audio is playing")
```

#### Private Methods

**`_run_mpc(*args: str, check: bool = False) -> subprocess.CompletedProcess`**

Run MPC command and return result.

**Parameters:**

- **`*args`** (`str`): MPC command arguments
- **`check`** (`bool`): Whether to raise on non-zero exit

**Returns:**

- **`subprocess.CompletedProcess`**: Command result

**Raises:**

- **`subprocess.TimeoutExpired`**: If command times out (>10s)
- **`subprocess.CalledProcessError`**: If check=True and command fails

**`_play_error_tone(duration_seconds: float = 0.5) -> None`**

Play error tone using sox or aplay.

**Parameters:**

- **`duration_seconds`** (`float`, default: 0.5): Tone duration

**Behavior:**

- Tries to use `sox` to generate tone
- Falls back silently if sox not available
- Uses configured error tone frequency

## Usage Examples

### Basic Playback

```python
from bosty_radio.audio_controller import AudioController

audio = AudioController()

# Play a stream
success = audio.play_stream("http://stream.example.com:8000/radio")
if success:
    print("Stream started")
else:
    print("Failed to start stream")

# Stop
audio.stop()
```

### Volume Control

```python
from bosty_radio.audio_controller import AudioController

audio = AudioController()

# Set volume
audio.set_volume(80)

# Play stream
audio.play_stream("http://stream.example.com:8000/radio")
```

### Status Monitoring

```python
from bosty_radio.audio_controller import AudioController
import time

audio = AudioController()
audio.play_stream("http://stream.example.com:8000/radio")

# Check status periodically
for _ in range(10):
    if audio.is_playing():
        status = audio.get_status()
        print(f"Status: {status}")
    else:
        print("Not playing")
    time.sleep(1)
```

### Error Handling

```python
from bosty_radio.audio_controller import AudioController

audio = AudioController()

# Try to play invalid URL
success = audio.play_stream("http://invalid-url.example.com")
if not success:
    print("Playback failed, error tone played")
```

### Local File Playback

```python
from bosty_radio.audio_controller import AudioController

audio = AudioController()

# Play local file
success = audio.play_stream("/home/pi/music/song.mp3")
```

## MPD/MPC Commands

The controller uses these MPC commands:

- **`mpc stop`**: Stop playback
- **`mpc clear`**: Clear playlist
- **`mpc add <url>`**: Add URL to playlist
- **`mpc play`**: Start playback
- **`mpc status`**: Get playback status
- **`mpc volume <level>`**: Set volume (0-100)

## Error Handling

### Stream Failures

When a stream fails to play:

1. Error is logged
2. 500Hz tone is played (if sox available)
3. Method returns `False`
4. Previous playback state is cleared

### MPD Not Running

If MPD is not running:

- Commands will fail
- Error tone may not play (depends on audio system)
- Errors are logged

### Network Issues

Network-related failures:

- Timeout after 10 seconds
- Error logged
- Error tone played
- Returns `False`

## Performance

- **`play_stream()`**: Typically 1-3 seconds (includes verification)
- **`stop()`**: Fast (<100ms)
- **`set_volume()`**: Fast (<100ms)
- **`get_status()`**: Fast (<100ms)
- **`is_playing()`**: Fast (<100ms)

## Dependencies

- **MPD**: Must be installed and running
- **MPC**: Must be installed and in PATH
- **sox**: Optional, for error tones

## Related Modules

- **[Radio Controller](radio-controller.md)**: Uses audio controller for playback
- **[Configuration](config.md)**: Provides volume and error tone settings
