# GPIO Controller API

API reference for the `bosty_radio.gpio_controller` module.

## Overview

The GPIO controller module manages reading the rotary switch position via GPIO pins. It configures pins with pull-down resistors and provides callbacks when the position changes.

## Module: `bosty_radio.gpio_controller`

## Classes

### `GPIOController`

Manages GPIO input reading for rotary switch positions.

```python
class GPIOController:
    def __init__(self, pins: list[int], callback: Optional[Callable[[int], None]] = None)
    def setup(self) -> None
    def read_position(self) -> Optional[int]
    def cleanup(self) -> None
```

#### Constructor

**`__init__(pins: list[int], callback: Optional[Callable[[int], None]] = None)`**

Initialize GPIO controller.

**Parameters:**

- **`pins`** (`list[int]`): List of GPIO pin numbers (BCM) for positions 1-6
- **`callback`** (`Optional[Callable[[int], None]]`): Optional callback function(position_index) when position changes

**Raises:**

- **`RuntimeError`**: If RPi.GPIO is not available (not running on Raspberry Pi)

**Example:**

```python
def on_position_change(position: int):
    print(f"Position changed to {position + 1}")

controller = GPIOController(
    pins=[2, 3, 4, 17, 27, 22],
    callback=on_position_change
)
```

#### Methods

**`setup() -> None`**

Configure GPIO pins with pull-down resistors.

This method:

- Sets GPIO mode to BCM
- Disables GPIO warnings
- Configures each pin as input with pull-down resistor

**Raises:**

- **`RuntimeError`**: If RPi.GPIO is not available

**Example:**

```python
controller.setup()
```

**`read_position() -> Optional[int]`**

Read current rotary switch position.

**Returns:**

- **`Optional[int]`**: Position index (0-5) if a position is selected, None if no position is active

**Behavior:**

- Checks each GPIO pin in order
- Returns index of first pin that is HIGH
- Triggers callback if position changed
- Returns None if no pin is HIGH

**Example:**

```python
position = controller.read_position()
if position is not None:
    print(f"Position {position + 1} selected")
```

**`cleanup() -> None`**

Clean up GPIO resources.

This method:

- Calls GPIO.cleanup() to reset all pins
- Marks setup as incomplete

**Example:**

```python
controller.cleanup()
```

#### Context Manager

The class supports Python's context manager protocol:

```python
with GPIOController([2, 3, 4, 17, 27, 22]) as controller:
    position = controller.read_position()
    # Automatic cleanup on exit
```

#### Properties

- **`pins`** (`list[int]`): List of GPIO pin numbers
- **`current_position`** (`Optional[int]`): Currently detected position (0-5 or None)
- **`callback`** (`Optional[Callable[[int], None]]`): Callback function

## Usage Examples

### Basic Usage

```python
from bosty_radio.gpio_controller import GPIOController

# Create controller
controller = GPIOController([2, 3, 4, 17, 27, 22])

# Setup GPIO
controller.setup()

# Read position
position = controller.read_position()
if position is not None:
    print(f"Position {position + 1} is selected")

# Cleanup
controller.cleanup()
```

### With Callback

```python
from bosty_radio.gpio_controller import GPIOController

def position_changed(position: int):
    print(f"Switch moved to position {position + 1}")

controller = GPIOController(
    pins=[2, 3, 4, 17, 27, 22],
    callback=position_changed
)

controller.setup()

# Callback will be triggered automatically on position change
while True:
    controller.read_position()
    time.sleep(0.1)
```

### Using Context Manager

```python
from bosty_radio.gpio_controller import GPIOController

with GPIOController([2, 3, 4, 17, 27, 22]) as controller:
    for _ in range(100):
        position = controller.read_position()
        if position is not None:
            print(f"Position: {position + 1}")
        time.sleep(0.1)
# Automatic cleanup
```

### Polling Loop

```python
from bosty_radio.gpio_controller import GPIOController
import time

controller = GPIOController([2, 3, 4, 17, 27, 22])
controller.setup()

try:
    while True:
        position = controller.read_position()
        if position is not None:
            print(f"Current position: {position + 1}")
        time.sleep(0.1)
except KeyboardInterrupt:
    pass
finally:
    controller.cleanup()
```

## GPIO Pin Configuration

### Pull-Down Resistors

The controller uses **internal pull-down resistors** configured in software:

```python
GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
```

This means:

- Pin reads LOW (0) when switch is not connected
- Pin reads HIGH (1) when switch connects to 3.3V
- No external resistors needed

### Pin Numbering

Uses **BCM (Broadcom) numbering**, not physical pin numbers:

- GPIO 2 = Physical Pin 3
- GPIO 3 = Physical Pin 5
- GPIO 4 = Physical Pin 7
- GPIO 17 = Physical Pin 11
- GPIO 27 = Physical Pin 13
- GPIO 22 = Physical Pin 15

### Rotary Switch Wiring

The rotary switch should be wired so:

- **Common terminal** connects to **3.3V**
- **Each position terminal** connects to its GPIO pin
- When a position is selected, that pin goes HIGH

## Error Handling

### RPi.GPIO Not Available

On non-Pi systems, RPi.GPIO will not be available:

```python
try:
    controller = GPIOController([2, 3, 4, 17, 27, 22])
    controller.setup()
except RuntimeError as e:
    print(f"GPIO not available: {e}")
```

### No Position Detected

If no position is detected (all pins LOW):

```python
position = controller.read_position()
if position is None:
    print("No position selected or wiring issue")
```

## Thread Safety

The GPIO controller is **not thread-safe**. Use from a single thread or protect with locks if accessing from multiple threads.

## Performance

- **`read_position()`**: Very fast (<1ms)
- **`setup()`**: Fast, called once at startup
- **`cleanup()`**: Fast, called once at shutdown

## Related Modules

- **[Radio Controller](radio-controller.md)**: Uses GPIO controller for position detection
- **[Configuration](config.md)**: Provides GPIO pin configuration
