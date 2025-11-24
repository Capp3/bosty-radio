# TUI API

API reference for the `bosty_radio.tui` module.

## Overview

The TUI module provides a Textual-based terminal user interface for configuring Bosty Radio. It allows users to edit all configuration settings through a user-friendly interface without manually editing JSON files.

## Module: `bosty_radio.tui`

## Functions

### `main()`

Main entry point for the TUI application.

**Behavior:**

- Sets up logging (WARNING level to reduce noise)
- Parses command-line arguments for config path
- Creates and runs ConfigApp

**Command-line arguments:**

- Optional: Config file path

**Example:**

```bash
python -m bosty_radio.tui
# or
python -m bosty_radio.tui /path/to/config.json
```

## Classes

### `StationEditor`

Editor for a single station configuration.

```python
class StationEditor(Container):
    def __init__(self, station: StationConfig, index: int, *args, **kwargs)
    def compose(self) -> ComposeResult
    def get_station(self) -> StationConfig
```

#### Constructor

**`**init**(station: StationConfig, index: int, \*args, **kwargs)`\*\*

Initialize station editor.

**Parameters:**

- **`station`** (`StationConfig`): Station configuration to edit
- **`index`** (`int`): Station index (0-4)
- **`\*args, **kwargs`\*\*: Passed to Container

#### Methods

**`compose() -> ComposeResult`**

Compose station editor UI.

**Returns:**

- **`ComposeResult`**: UI widgets

**Widgets:**

- Label with station number
- Input for URL/path
- Input for Morse code message
- Input for station name (optional)

**`get_station() -> StationConfig`**

Get updated station configuration from UI.

**Returns:**

- **`StationConfig`**: Updated station configuration

**Behavior:**

- Reads values from input widgets
- Creates new StationConfig
- Uses default Morse message if empty

### `ConfigApp`

Main configuration TUI application.

```python
class ConfigApp(App):
    def __init__(self, config_path: Optional[Path] = None, *args, **kwargs)
    def compose(self) -> ComposeResult
    def action_save(self) -> None
    def action_help(self) -> None
    def action_quit(self) -> None
    def on_button_pressed(self, event: Button.Pressed) -> None
```

#### Constructor

**`**init**(config_path: Optional[Path] = None, \*args, **kwargs)`\*\*

Initialize config app.

**Parameters:**

- **`config_path`** (`Optional[Path]`): Optional path to config file
- **`\*args, **kwargs`\*\*: Passed to App

**Behavior:**

- Creates ConfigManager with optional path
- Loads configuration

#### Methods

**`compose() -> ComposeResult`**

Compose main UI.

**Returns:**

- **`ComposeResult`**: UI widgets

**UI Structure:**

- Header with clock
- Scrollable container with:
  - Title
  - Status label
  - Help section (allowed sources)
  - Station editors (5 stations)
  - Bluetooth Morse input
  - Morse timing input
  - Volume input
  - GPIO pin inputs (advanced)
- Button bar (Save, Cancel)
- Footer

**`action_save() -> None`**

Save configuration.

**Behavior:**

1. Collects data from all UI fields
2. Validates configuration
3. Saves to file
4. Updates status message (success/error)

**Status Messages:**

- Green: "✓ Configuration saved successfully!"
- Red: Error message with details

**`action_help() -> None`**

Show help information.

**Behavior:**

- Updates status label with help text
- Help is also visible in UI above

**`action_quit() -> None`**

Quit application.

**Behavior:**

- Exits the TUI application

**`on_button_pressed(event: Button.Pressed) -> None`**

Handle button presses.

**Parameters:**

- **`event`** (`Button.Pressed`): Button press event

**Behavior:**

- "Save" button: Calls `action_save()`
- "Cancel" button: Exits application

#### Keyboard Bindings

- **Q**: Quit
- **S**: Save
- **H**: Help

#### CSS Styling

The app includes custom CSS for:

- Screen background
- Config container padding
- Station label styling
- Help text panel
- Button margins

## Usage Examples

### Running the TUI

```bash
# Standard way
make configure

# Direct Python
uv run python -m bosty_radio.tui

# With custom config path
uv run python -m bosty_radio.tui /path/to/config.json
```

### Programmatic Usage

```python
from pathlib import Path
from bosty_radio.tui import ConfigApp

# Create and run app
app = ConfigApp(Path("/custom/config.json"))
app.run()
```

### Customization

The TUI can be customized by:

1. **Modifying CSS**: Edit the `CSS` class variable
2. **Adding fields**: Extend `compose()` method
3. **Custom validation**: Modify `action_save()`
4. **Additional bindings**: Add to `BINDINGS` list

## UI Navigation

### Keyboard Navigation

- **Tab**: Move to next field
- **Shift+Tab**: Move to previous field
- **Enter**: Edit selected field
- **Esc**: Cancel editing
- **Arrow keys**: Navigate within fields
- **S**: Save configuration
- **Q**: Quit
- **H**: Show help

### Mouse Support

- Click to select fields
- Click buttons to activate
- Scroll to navigate long forms

## Configuration Sections

### Help Section

Shows allowed source formats:

- Internet Radio URLs (http/https)
- Local file paths
- Example formats

### Stations Section

Five station editors, one for each position (1-5):

- URL/Path input
- Morse code message input
- Station name input (optional)

### Bluetooth Mode

- Morse code message input (default: "BT")

### Morse Code Settings

- Dot duration in milliseconds (50-500)

### Volume

- Volume level (0-100)

### GPIO Pins (Advanced)

- Individual pin inputs for all 7 GPIO pins
- Only change if needed

## Validation

### Pre-Save Validation

Before saving:

- Station URLs: Must be valid format
- Morse messages: Must be non-empty
- Volume: Must be 0-100
- GPIO pins: Must be valid numbers (2-27)
- Dot duration: Must be 50-500ms

### Pydantic Validation

After collecting data:

- Creates RadioConfig instance
- Pydantic validates all fields
- Raises ValueError on validation failure

## Error Handling

### Save Errors

If save fails:

- Error message displayed in red
- Configuration not saved
- User can correct and retry

### Validation Errors

If validation fails:

- Error message shows specific issue
- Invalid fields highlighted
- User can correct and retry

### File Errors

If file cannot be written:

- Error logged
- Error message displayed
- User notified

## Status Messages

The status label shows:

- **Green**: Success messages
- **Red**: Error messages
- **Default**: Help/info messages

## Related Modules

- **[Configuration](config.md)**: Provides configuration models
- **[Radio Controller](radio-controller.md)**: Uses configuration
