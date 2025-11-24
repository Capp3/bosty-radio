# Radio Controller API

API reference for the `bosty_radio.radio_controller` module.

## Overview

The radio controller is the main daemon that coordinates all components. It monitors GPIO for position changes, manages audio playback, controls the LED, and handles Bluetooth mode.

## Module: `bosty_radio.radio_controller`

## Functions

### `main()`

Main entry point for the radio controller daemon.

**Behavior:**

- Sets up logging to file and stdout
- Creates RadioController instance
- Calls setup() and run()
- Handles fatal errors

**Example:**

```python
from bosty_radio.radio_controller import main

if __name__ == "__main__":
    main()
```

## Classes

### `RadioController`

Main controller coordinating all components.

```python
class RadioController:
    def __init__(self, config_path: Path | None = None)
    def setup(self) -> None
    def run(self) -> None
    def shutdown(self) -> None
    def reload_config(self) -> None
```

#### Constructor

**`__init__(config_path: Path | None = None)`**

Initialize radio controller.

**Parameters:**

- **`config_path`** (`Path | None`): Optional path to configuration file

**Behavior:**

- Creates ConfigManager
- Loads configuration
- Initializes component references (None initially)
- Sets up signal handlers (SIGINT, SIGTERM)

**Example:**

```python
controller = RadioController()
# or
controller = RadioController(Path("/custom/config.json"))
```

#### Methods

**`setup() -> None`**

Initialize all components.

**Behavior:**

1. Sets up GPIO controller with pins from config
2. Sets up Morse LED with pin and timing from config
3. Creates audio controller with error tone frequency
4. Sets initial volume
5. Creates Bluetooth controller

**Raises:**

- **`Exception`**: If any component setup fails

**Example:**

```python
controller = RadioController()
controller.setup()
```

**`run() -> None`**

Main run loop.

**Behavior:**

- Enters continuous loop
- Reads GPIO position every 0.1s
- Switches modes on position change
- Monitors Bluetooth connection status (if in Bluetooth mode)
- Exits on shutdown signal

**Example:**

```python
controller.setup()
controller.run()  # Blocks until shutdown
```

**`shutdown() -> None`**

Clean shutdown of all components.

**Behavior:**

- Stops audio playback
- Disables Bluetooth pairing
- Stops and cleans up LED
- Cleans up GPIO
- Logs shutdown completion

**Example:**

```python
controller.shutdown()
```

**`reload_config() -> None`**

Reload configuration from file.

**Behavior:**

- Forces config reload
- Updates volume if changed
- Does not restart components

**Example:**

```python
controller.reload_config()
```

#### Private Methods

**`_signal_handler(signum, frame)`**

Handle shutdown signals (SIGINT, SIGTERM).

**Behavior:**

- Sets `_shutdown_requested` flag
- Logs signal received
- Allows graceful shutdown in main loop

**`_position_changed(position: int) -> None`**

Handle position change callback from GPIO.

**Parameters:**

- **`position`** (`int`): New position index (0-5)

**Behavior:**

- Logs position change
- Calls `_switch_to_position()`

**`_switch_to_position(position: int) -> None`**

Switch to a new position.

**Parameters:**

- **`position`** (`int`): Position index (0-5)

**Behavior:**

- Skips if position unchanged
- Updates `current_position`
- Routes to station or Bluetooth handler

**`_switch_to_station(station_index: int) -> None`**

Switch to a station (position 1-5).

**Parameters:**

- **`station_index`** (`int`): Station index (0-4)

**Behavior:**

1. Stops Bluetooth if active
2. Starts Morse code message for station
3. Plays station URL/file
4. Logs success/failure

**`_switch_to_bluetooth() -> None`**

Switch to Bluetooth mode (position 6).

**Behavior:**

1. Stops audio playback
2. Starts Bluetooth Morse code
3. Enables Bluetooth pairing

**`_update_bluetooth_led() -> None`**

Update LED based on Bluetooth connection status.

**Behavior:**

- Checks connection status
- If connected: LED solid ON
- If not connected: LED blinks "BT" Morse code

## Usage Examples

### Basic Usage

```python
from bosty_radio.radio_controller import RadioController

controller = RadioController()
controller.setup()
controller.run()  # Runs until shutdown signal
```

### With Custom Config

```python
from pathlib import Path
from bosty_radio.radio_controller import RadioController

controller = RadioController(Path("/custom/config.json"))
controller.setup()
controller.run()
```

### Graceful Shutdown

```python
import signal
from bosty_radio.radio_controller import RadioController

controller = RadioController()
controller.setup()

try:
    controller.run()
except KeyboardInterrupt:
    pass
finally:
    controller.shutdown()
```

### Manual Control

```python
from bosty_radio.radio_controller import RadioController
import time

controller = RadioController()
controller.setup()

# Run for a limited time
start_time = time.time()
while time.time() - start_time < 60:  # Run for 60 seconds
    controller.run()  # This blocks, so this example is simplified
    time.sleep(0.1)

controller.shutdown()
```

## State Management

### Controller State

- **`current_position`** (`int | None`): Current rotary switch position (0-5 or None)
- **`running`** (`bool`): Whether main loop is running
- **`_shutdown_requested`** (`bool`): Flag for graceful shutdown

### Component References

- **`gpio`**: GPIOController instance
- **`morse_led`**: MorseLED instance
- **`audio`**: AudioController instance
- **`bluetooth`**: BluetoothController instance

## Signal Handling

The controller handles these signals:

- **SIGINT** (Ctrl+C): Graceful shutdown
- **SIGTERM**: Graceful shutdown (from systemd)

On signal:

1. `_shutdown_requested` flag is set
2. Main loop exits on next iteration
3. `shutdown()` is called (in finally block)
4. All components are cleaned up

## Main Loop Behavior

The main loop:

1. Reads GPIO position (every 0.1s)
2. Checks for position changes
3. Switches modes if changed
4. Monitors Bluetooth status (if in Bluetooth mode)
5. Sleeps 0.1s to prevent busy-waiting
6. Exits when `_shutdown_requested` is True

## Error Handling

### Component Errors

If a component fails:

- Error is logged
- Controller continues operation
- Other components remain functional
- Graceful degradation

### Setup Errors

If setup fails:

- Exception is raised
- Controller should not be used
- Caller should handle exception

### Runtime Errors

Runtime errors in main loop:

- Logged but don't stop controller
- Loop continues
- Components attempt recovery

## Logging

The controller logs to:

- **File**: `/var/log/bosty-radio/controller.log`
- **Stdout**: Console output
- **Journald**: Via systemd (when run as service)

Log format:

```
%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

## Performance

- **Setup**: 1-2 seconds (component initialization)
- **Main loop iteration**: ~0.1s (mostly sleep)
- **Position change handling**: <100ms
- **Shutdown**: <1 second

## Threading

The controller runs in a single thread:

- Main thread: Controller loop
- Background thread: Morse LED blinking (managed by MorseLED)

## Related Modules

- **[Configuration](config.md)**: Provides configuration
- **[GPIO Controller](gpio-controller.md)**: Position detection
- **[Morse LED](morse-led.md)**: Visual feedback
- **[Audio Controller](audio-controller.md)**: Playback
- **[Bluetooth Controller](bluetooth-controller.md)**: Bluetooth mode
