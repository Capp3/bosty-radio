# Morse LED API

API reference for the `bosty_radio.morse_led` module.

## Overview

The Morse LED module controls an LED to display Morse code messages. It supports continuous repeating of messages and can also be used for simple on/off status indication.

## Module: `bosty_radio.morse_led`

### Constants

#### `MORSE_CODE`

Dictionary mapping characters to Morse code patterns.

```python
MORSE_CODE = {
    "A": ".-", "B": "-...", "C": "-.-.", ...
    "0": "-----", "1": ".----", ...
}
```

Supports:

- Letters A-Z
- Numbers 0-9
- Punctuation: `.`, `,`, `?`
- Space: `" "` (word separator)

## Classes

### `MorseLED`

Controls LED for Morse code output with repeat functionality.

```python
class MorseLED:
    def __init__(self, pin: int, dot_duration_ms: int = 100)
    def setup(self) -> None
    def start_message(self, message: str) -> None
    def stop(self) -> None
    def set_state(self, state: bool) -> None
    def cleanup(self) -> None
```

#### Constructor

**`__init__(pin: int, dot_duration_ms: int = 100)`**

Initialize Morse LED controller.

**Parameters:**

- **`pin`** (`int`): GPIO pin number (BCM) for LED
- **`dot_duration_ms`** (`int`, default: 100): Duration of a dot in milliseconds

**Raises:**

- **`RuntimeError`**: If RPi.GPIO is not available

**Timing Calculations:**

- Dot duration = `dot_duration_ms / 1000.0` seconds
- Dash duration = dot duration × 3
- Element gap = dot duration
- Letter gap = dot duration × 3
- Word gap = dot duration × 7

**Example:**

```python
led = MorseLED(pin=18, dot_duration_ms=100)
```

#### Methods

**`setup() -> None`**

Configure LED GPIO pin as output.

This method:

- Sets GPIO mode to BCM
- Configures pin as output
- Sets pin to LOW (LED off)

**Raises:**

- **`RuntimeError`**: If RPi.GPIO is not available

**Example:**

```python
led.setup()
```

**`start_message(message: str) -> None`**

Start blinking a Morse code message (repeats continuously).

**Parameters:**

- **`message`** (`str`): Text message to encode (e.g., "S1", "BT")

**Behavior:**

- Stops any existing message
- Encodes text to Morse code
- Starts background thread for continuous blinking
- Message repeats until `stop()` is called

**Example:**

```python
led.start_message("S1")  # Blinks ... .---- continuously
led.start_message("BT")   # Blinks -... - continuously
```

**`stop() -> None`**

Stop blinking and turn off LED.

This method:

- Stops the background thread
- Turns LED off
- Clears current message

**Example:**

```python
led.stop()
```

**`set_state(state: bool) -> None`**

Set LED to on or off (for simple status indication).

**Parameters:**

- **`state`** (`bool`): True for on, False for off

**Use Case:**

- Solid ON for Bluetooth connected status
- Solid OFF for inactive state

**Example:**

```python
led.set_state(True)   # LED on
led.set_state(False)  # LED off
```

**`cleanup() -> None`**

Clean up GPIO resources.

This method:

- Stops blinking
- Cleans up GPIO pin
- Marks setup as incomplete

**Example:**

```python
led.cleanup()
```

#### Private Methods

**`_text_to_morse(text: str) -> str`**

Convert text to Morse code pattern.

**Parameters:**

- **`text`** (`str`): Text to encode

**Returns:**

- **`str`**: Space-separated Morse code patterns

**Example:**

```python
pattern = led._text_to_morse("S1")  # "... .----"
```

**`_blink_pattern(pattern: str) -> None`**

Blink LED according to Morse pattern.

**Parameters:**

- **`pattern`** (`str`): Morse code pattern string

**Behavior:**

- Blinks LED for dots (short)
- Blinks LED for dashes (long)
- Adds appropriate gaps between elements

**`_blink_loop() -> None`**

Main loop for continuous blinking with repeat.

Runs in background thread, continuously blinking the current message.

#### Context Manager

The class supports Python's context manager protocol:

```python
with MorseLED(pin=18, dot_duration_ms=100) as led:
    led.start_message("S1")
    time.sleep(10)
    # Automatic cleanup on exit
```

## Usage Examples

### Basic Morse Code

```python
from bosty_radio.morse_led import MorseLED
import time

led = MorseLED(pin=18, dot_duration_ms=100)
led.setup()

# Start blinking "S1"
led.start_message("S1")

# Let it blink for 10 seconds
time.sleep(10)

# Stop
led.stop()
led.cleanup()
```

### Continuous Repeating

```python
from bosty_radio.morse_led import MorseLED
import time

led = MorseLED(pin=18)
led.setup()

# Message will repeat continuously
led.start_message("BT")

# Run for a while
time.sleep(60)

# Stop when done
led.stop()
led.cleanup()
```

### Status Indication

```python
from bosty_radio.morse_led import MorseLED

led = MorseLED(pin=18)
led.setup()

# Solid ON for connected
led.set_state(True)
time.sleep(5)

# Solid OFF for disconnected
led.set_state(False)

led.cleanup()
```

### Changing Messages

```python
from bosty_radio.morse_led import MorseLED
import time

led = MorseLED(pin=18)
led.setup()

# Start with one message
led.start_message("S1")
time.sleep(5)

# Change to another message (automatically stops previous)
led.start_message("S2")
time.sleep(5)

# Stop
led.stop()
led.cleanup()
```

### Using Context Manager

```python
from bosty_radio.morse_led import MorseLED
import time

with MorseLED(pin=18, dot_duration_ms=100) as led:
    led.start_message("S1")
    time.sleep(10)
    # Automatic cleanup
```

## Morse Code Timing

### Standard Timing (ITU-R)

The implementation follows ITU-R Morse code timing:

- **Dot**: 1 unit
- **Dash**: 3 units
- **Element gap**: 1 unit (between dots/dashes)
- **Letter gap**: 3 units (between letters)
- **Word gap**: 7 units (between words)

### Example: "S1"

- **S** = `...` (3 dots)
- **1** = `.----` (1 dot, 4 dashes)
- **Pattern**: `... .----`
- **Timing**: Dot (100ms) - Gap (100ms) - Dot (100ms) - Gap (100ms) - Dot (100ms) - Letter gap (300ms) - Dot (100ms) - Gap (100ms) - Dash (300ms) - Gap (100ms) - Dash (300ms) - Gap (100ms) - Dash (300ms) - Gap (100ms) - Dash (300ms)

## Threading

The Morse LED uses a **background daemon thread** for blinking:

- Thread runs continuously while message is active
- Thread is stopped when `stop()` is called
- Thread automatically stops on cleanup
- Non-blocking: Main thread continues normally

## Error Handling

### RPi.GPIO Not Available

```python
try:
    led = MorseLED(pin=18)
    led.setup()
except RuntimeError as e:
    print(f"GPIO not available: {e}")
```

### Thread Errors

The background thread handles errors gracefully and logs them. The main thread is not affected.

## Performance

- **Setup**: Fast, called once
- **Message start**: Fast, starts thread immediately
- **Blinking**: Minimal CPU usage (thread sleeps between blinks)
- **Stop**: Fast, thread joins with 1s timeout

## Related Modules

- **[Radio Controller](radio-controller.md)**: Uses Morse LED for feedback
- **[GPIO Controller](gpio-controller.md)**: Uses same GPIO library
- **[Configuration](config.md)**: Provides Morse code settings
