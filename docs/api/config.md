# Configuration API

API reference for the `bosty_radio.config` module.

## Overview

The configuration module provides type-safe configuration management using Pydantic models. It handles loading, saving, and validating configuration files in JSON format.

## Module: `bosty_radio.config`

### Constants

#### `DEFAULT_CONFIG_PATH`

```python
Path("/etc/bosty-radio/config.json")
```

System-wide configuration file path.

#### `USER_CONFIG_PATH`

```python
Path.home() / ".config" / "bosty-radio" / "config.json"
```

User-specific configuration file path.

## Classes

### `StationConfig`

Configuration for a single station/position.

```python
class StationConfig(BaseModel):
    url: str
    morse_message: str
    name: Optional[str] = None
```

#### Fields

- **`url`** (`str`): Stream URL or file path
- **`morse_message`** (`str`): Morse code message (e.g., 'S1', 'BT')
- **`name`** (`Optional[str]`): Human-readable station name

#### Example

```python
station = StationConfig(
    url="http://stream.example.com:8000/radio",
    morse_message="S1",
    name="Example Radio"
)
```

### `GPIOConfig`

GPIO pin configuration.

```python
class GPIOConfig(BaseModel):
    position_1: int = 2
    position_2: int = 3
    position_3: int = 4
    position_4: int = 17
    position_5: int = 27
    position_6: int = 22
    led: int = 18
```

#### Fields

- **`position_1`** (`int`, default: 2): GPIO pin for position 1 (BCM)
- **`position_2`** (`int`, default: 3): GPIO pin for position 2 (BCM)
- **`position_3`** (`int`, default: 4): GPIO pin for position 3 (BCM)
- **`position_4`** (`int`, default: 17): GPIO pin for position 4 (BCM)
- **`position_5`** (`int`, default: 27): GPIO pin for position 5 (BCM)
- **`position_6`** (`int`, default: 22): GPIO pin for position 6 (BCM)
- **`led`** (`int`, default: 18): GPIO pin for LED (BCM)

#### Validation

All pin numbers are validated to be in range 2-27 (valid GPIO pins).

#### Example

```python
gpio = GPIOConfig(
    position_1=2,
    position_2=3,
    led=18
)
```

### `RadioConfig`

Main configuration model for Bosty Radio.

```python
class RadioConfig(BaseModel):
    stations: List[StationConfig]
    bluetooth_morse: str = "BT"
    morse_dot_duration_ms: int = 100
    gpio: GPIOConfig = GPIOConfig()
    volume: int = 80
    error_tone_frequency_hz: int = 500
```

#### Fields

- **`stations`** (`List[StationConfig]`): Station configurations for positions 1-5 (must be exactly 5)
- **`bluetooth_morse`** (`str`, default: "BT"): Morse code message for Bluetooth mode
- **`morse_dot_duration_ms`** (`int`, default: 100): Morse code dot duration in milliseconds (50-500)
- **`gpio`** (`GPIOConfig`, default: `GPIOConfig()`): GPIO pin configuration
- **`volume`** (`int`, default: 80): Default volume level (0-100)
- **`error_tone_frequency_hz`** (`int`, default: 500): Error tone frequency in Hz (200-2000)

#### Validation

- **`stations`**: Must contain exactly 5 stations
- **`morse_dot_duration_ms`**: Must be between 50 and 500
- **`volume`**: Must be between 0 and 100
- **`error_tone_frequency_hz`**: Must be between 200 and 2000

#### Example

```python
config = RadioConfig(
    stations=[
        StationConfig(url="http://stream.example.com", morse_message="S1"),
        StationConfig(url="http://stream2.example.com", morse_message="S2"),
        StationConfig(url="http://stream3.example.com", morse_message="S3"),
        StationConfig(url="http://stream4.example.com", morse_message="S4"),
        StationConfig(url="/home/pi/music/file.mp3", morse_message="F1"),
    ],
    bluetooth_morse="BT",
    morse_dot_duration_ms=100,
    volume=80
)
```

### `ConfigManager`

Manages loading and saving configuration.

```python
class ConfigManager:
    def __init__(self, config_path: Optional[Path] = None)
    def load(self) -> RadioConfig
    def save(self, config: RadioConfig) -> None
    def get_config(self) -> RadioConfig
    def reload(self) -> RadioConfig
```

#### Constructor

**`__init__(config_path: Optional[Path] = None)`**

Initialize config manager with optional custom path.

**Parameters:**

- **`config_path`** (`Optional[Path]`): Custom config file path. If None, uses `_find_config_file()`.

**Example:**

```python
manager = ConfigManager()
# or
manager = ConfigManager(Path("/custom/path/config.json"))
```

#### Methods

**`load() -> RadioConfig`**

Load configuration from file.

**Returns:**

- **`RadioConfig`**: Loaded configuration or defaults if file doesn't exist

**Raises:**

- **`ValueError`**: If JSON is invalid or validation fails

**Example:**

```python
config = manager.load()
```

**`save(config: RadioConfig) -> None`**

Save configuration to file.

**Parameters:**

- **`config`** (`RadioConfig`): Configuration to save

**Raises:**

- **`IOError`**: If file cannot be written
- **`OSError`**: If directory cannot be created

**Example:**

```python
manager.save(config)
```

**`get_config() -> RadioConfig`**

Get current configuration, loading if necessary.

**Returns:**

- **`RadioConfig`**: Current configuration (cached if already loaded)

**Example:**

```python
config = manager.get_config()
```

**`reload() -> RadioConfig`**

Force reload configuration from file.

**Returns:**

- **`RadioConfig`**: Reloaded configuration

**Example:**

```python
config = manager.reload()  # Forces reload even if cached
```

#### Private Methods

**`_find_config_file() -> Path`**

Find the configuration file, checking system and user locations.

**Returns:**

- **`Path`**: Path to config file (system location if exists, else user location)

**Logic:**

1. Check `/etc/bosty-radio/config.json`
2. Check `~/.config/bosty-radio/config.json`
3. Return user location as default

## Usage Examples

### Loading Configuration

```python
from bosty_radio.config import ConfigManager

manager = ConfigManager()
config = manager.load()

print(f"Volume: {config.volume}")
print(f"Station 1: {config.stations[0].url}")
```

### Saving Configuration

```python
from bosty_radio.config import ConfigManager, RadioConfig, StationConfig, GPIOConfig

manager = ConfigManager()
config = manager.load()

# Modify configuration
config.volume = 90
config.stations[0].url = "http://new-stream.example.com"

# Save
manager.save(config)
```

### Creating Default Configuration

```python
from bosty_radio.config import RadioConfig, StationConfig

# Create with defaults
config = RadioConfig()

# Customize
config.stations[0].url = "http://stream.example.com"
config.stations[0].morse_message = "S1"
config.volume = 80
```

### Custom Config Path

```python
from pathlib import Path
from bosty_radio.config import ConfigManager

# Use custom path
manager = ConfigManager(Path("/tmp/test-config.json"))
config = manager.load()
```

## JSON Format

Configuration is stored as JSON with this structure:

```json
{
  "stations": [
    {
      "url": "http://stream.example.com:8000/radio",
      "morse_message": "S1",
      "name": "Station 1"
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

## Related Modules

- **[GPIO Controller](gpio-controller.md)**: Uses GPIO configuration
- **[Radio Controller](radio-controller.md)**: Uses full configuration
- **[TUI](tui.md)**: Provides UI for configuration
