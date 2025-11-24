# Bluetooth Controller API

API reference for the `bosty_radio.bluetooth_controller` module.

## Overview

The Bluetooth controller module manages Bluetooth A2DP sink functionality, allowing the Raspberry Pi to receive audio from mobile devices. It handles pairing mode, connection status monitoring, and audio routing.

## Module: `bosty_radio.bluetooth_controller`

## Classes

### `BluetoothController`

Manages Bluetooth A2DP sink functionality.

```python
class BluetoothController:
    def __init__(self)
    def enable_pairing_mode(self) -> bool
    def disable_pairing_mode(self) -> None
    def switch_to_bluetooth_sink(self) -> bool
    def check_connection_status(self) -> bool
    def get_connection_status(self) -> bool
    def is_pairing_mode(self) -> bool
```

#### Constructor

**`__init__(self)`**

Initialize Bluetooth controller.

**Example:**

```python
bluetooth = BluetoothController()
```

#### Methods

**`enable_pairing_mode() -> bool`**

Enable Bluetooth pairing mode (makes Pi discoverable).

**Returns:**

- **`bool`**: True if successful

**Behavior:**

- Makes Bluetooth adapter discoverable
- Enables pairing
- Plays "ding" sound to indicate pairing needed
- Sets pairing mode flag

**Example:**

```python
if bluetooth.enable_pairing_mode():
    print("Pairing mode enabled, waiting for device...")
```

**`disable_pairing_mode() -> None`**

Disable Bluetooth pairing mode.

**Behavior:**

- Makes adapter non-discoverable
- Disables pairing
- Clears pairing mode flag

**Example:**

```python
bluetooth.disable_pairing_mode()
```

**`switch_to_bluetooth_sink() -> bool`**

Switch audio output to Bluetooth A2DP sink.

**Returns:**

- **`bool`**: True if successful

**Behavior:**

1. Enables pairing mode
2. Attempts to switch PulseAudio default sink to Bluetooth
3. Logs warnings if primary method fails

**Example:**

```python
if bluetooth.switch_to_bluetooth_sink():
    print("Switched to Bluetooth sink")
```

**`check_connection_status() -> bool`**

Check if a device is connected to Bluetooth.

**Returns:**

- **`bool`**: True if connected, False otherwise

**Behavior:**

- Queries Bluetooth adapter for connection status
- Updates internal connection state
- Logs status changes

**Example:**

```python
connected = bluetooth.check_connection_status()
if connected:
    print("Device connected")
```

**`get_connection_status() -> bool`**

Get current connection status (cached).

**Returns:**

- **`bool`**: Cached connection status

**Note:** This returns the last known status. Use `check_connection_status()` to query current status.

**Example:**

```python
status = bluetooth.get_connection_status()
```

**`is_pairing_mode() -> bool`**

Check if in pairing mode.

**Returns:**

- **`bool`**: True if pairing mode is active

**Example:**

```python
if bluetooth.is_pairing_mode():
    print("Waiting for pairing...")
```

#### Private Methods

**`_run_command(*args: str, check: bool = False) -> subprocess.CompletedProcess`**

Run a shell command.

**Parameters:**

- **`*args`** (`str`): Command and arguments
- **`check`** (`bool`): Whether to raise on non-zero exit

**Returns:**

- **`subprocess.CompletedProcess`**: Command result

**Raises:**

- **`subprocess.TimeoutExpired`**: If command times out (>30s)
- **`subprocess.CalledProcessError`**: If check=True and command fails

**`_play_ding() -> None`**

Play a 'ding' sound to indicate pairing needed.

**Behavior:**

- Tries to use `sox` to generate tone
- Falls back to `beep` command
- Silently fails if neither available

## Usage Examples

### Basic Pairing

```python
from bosty_radio.bluetooth_controller import BluetoothController

bluetooth = BluetoothController()

# Enable pairing mode
if bluetooth.enable_pairing_mode():
    print("Pairing mode enabled")
    print("Pair your device now...")

    # Check connection
    if bluetooth.check_connection_status():
        print("Device connected!")

    # Disable when done
    bluetooth.disable_pairing_mode()
```

### Switching to Bluetooth

```python
from bosty_radio.bluetooth_controller import BluetoothController

bluetooth = BluetoothController()

# Switch to Bluetooth sink (enables pairing automatically)
if bluetooth.switch_to_bluetooth_sink():
    print("Bluetooth sink active")

    # Monitor connection
    while True:
        if bluetooth.check_connection_status():
            print("Connected")
            break
        time.sleep(2)
```

### Connection Monitoring

```python
from bosty_radio.bluetooth_controller import BluetoothController
import time

bluetooth = BluetoothController()
bluetooth.enable_pairing_mode()

# Monitor connection status
while True:
    connected = bluetooth.check_connection_status()
    if connected:
        print("Device connected")
        break
    else:
        print("Waiting for connection...")
    time.sleep(2)
```

### Status Checking

```python
from bosty_radio.bluetooth_controller import BluetoothController

bluetooth = BluetoothController()

# Check current status
if bluetooth.is_pairing_mode():
    print("In pairing mode")

if bluetooth.get_connection_status():
    print("Device is connected")
else:
    print("No device connected")
```

## Bluetooth Commands

The controller uses these commands:

- **`bluetoothctl discoverable on`**: Make adapter discoverable
- **`bluetoothctl discoverable off`**: Make adapter non-discoverable
- **`bluetoothctl pairable on`**: Enable pairing
- **`bluetoothctl pairable off`**: Disable pairing
- **`bluetoothctl info`**: Get adapter/device info
- **`pactl set-default-sink bluez_sink`**: Switch audio to Bluetooth

## Error Handling

### Command Failures

If Bluetooth commands fail:

- Errors are logged
- Methods return `False` or `None`
- System continues operation
- No exceptions raised (graceful degradation)

### Bluetooth Service Not Running

If Bluetooth service is not running:

- Commands will fail
- Errors are logged
- Methods return `False`

### Audio Routing Failures

If PulseAudio routing fails:

- Warning is logged
- Alternative methods may be attempted
- Returns `True` (pairing mode still enabled)

## State Management

### Internal State

- **`_is_paired`**: Pairing status (not currently used)
- **`_is_connected`**: Connection status (cached)
- **`_pairing_mode`**: Pairing mode flag

### State Persistence

**Important:** State is **not persisted**. When switching away from Bluetooth mode:

- Pairing mode is disabled
- Connection status is reset
- State must be re-established on next use

## Performance

- **`enable_pairing_mode()`**: Fast (<1s)
- **`disable_pairing_mode()`**: Fast (<1s)
- **`switch_to_bluetooth_sink()`**: Fast (<2s)
- **`check_connection_status()`**: Moderate (1-2s, queries hardware)

## Dependencies

- **BlueZ**: Bluetooth stack (bluetoothctl)
- **PulseAudio**: Audio routing (pactl)
- **sox/beep**: Optional, for ding sound

## Limitations

### Audio Routing

The current implementation uses PulseAudio. If your system uses a different audio system (ALSA directly, PipeWire, etc.), you may need to modify the `switch_to_bluetooth_sink()` method.

### Pairing Persistence

Pairing state is not saved. Each time you switch to Bluetooth mode, you may need to re-pair devices.

### Connection Detection

Connection detection relies on `bluetoothctl info`, which may not always accurately reflect A2DP connection status.

## Related Modules

- **[Radio Controller](radio-controller.md)**: Uses Bluetooth controller for position 6
- **[Morse LED](morse-led.md)**: Shows Bluetooth connection status via LED
