# TUI API

API reference for the `bosty_radio.tui` module.

## Overview

The TUI module provides a menu-driven terminal user interface for configuring Bosty Radio. It uses a hierarchical navigation system similar to raspi-config, making it simple and intuitive to configure all settings.

## Module: `bosty_radio.tui`

## Architecture

The TUI uses a screen-based architecture with the following hierarchy:

```
MainMenuScreen (root)
├── StationListScreen
│   └── StationEditorScreen (for each station)
├── BluetoothSettingsScreen
├── AudioSettingsScreen
└── AdvancedSettingsScreen
```

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
# Standard way
make configure

# Direct Python
python -m bosty_radio.tui

# With custom config path
python -m bosty_radio.tui /path/to/config.json
```

## Classes

### `ConfigApp`

Main configuration application (extends Textual's App).

```python
class ConfigApp(App):
    def __init__(self, config_path: Optional[Path] = None)
    def on_mount(self) -> None
    def action_save(self) -> None
    def action_save_and_exit(self) -> None
    async def action_quit(self) -> None
```

#### Constructor

**`__init__(config_path: Optional[Path] = None)`**

Initialize config app.

**Parameters:**

- **`config_path`** (`Optional[Path]`): Optional path to config file

**Behavior:**

- Creates ConfigManager with optional path
- Loads configuration
- Initializes config_dirty flag for tracking unsaved changes

#### Attributes

- **`config`** (`RadioConfig`): Current configuration
- **`config_manager`** (`ConfigManager`): Configuration file manager
- **`config_dirty`** (`bool`): True if there are unsaved changes

#### Methods

**`on_mount() -> None`**

Push main menu when app starts.

**`action_save() -> None`**

Save configuration to file (keyboard shortcut: Ctrl+S).

**`action_save_and_exit() -> None`**

Save configuration and exit application.

**`async action_quit() -> None`**

Quit application with warning if there are unsaved changes (keyboard shortcut: Q).

#### Keyboard Bindings

- **Q**: Quit (warns if unsaved changes)
- **Ctrl+S**: Save configuration

### `MainMenuScreen`

Root menu screen with main configuration categories.

```python
class MainMenuScreen(Screen):
    def compose(self) -> ComposeResult
    def on_mount(self) -> None
    def on_option_list_option_selected(self, event) -> None
    async def action_quit(self) -> None
```

**Menu Options:**

1. Configure Stations
2. Bluetooth Settings
3. Audio Settings
4. Advanced (GPIO Pins)
5. Save & Exit

**Keyboard Bindings:**

- **Q/Escape**: Quit application
- **↑/↓**: Navigate menu
- **Enter**: Select option

### `StationListScreen`

List of stations (1-5) to configure.

```python
class StationListScreen(Screen):
    def compose(self) -> ComposeResult
    def on_mount(self) -> None
    def on_option_list_option_selected(self, event) -> None
    def action_back(self) -> None
    async def action_quit(self) -> None
```

**Menu Options:**

- Station 1
- Station 2
- Station 3
- Station 4
- Station 5
- < Back to Main Menu

**Keyboard Bindings:**

- **Escape**: Back to main menu
- **Q**: Quit application
- **↑/↓**: Navigate stations
- **Enter**: Edit station

### `StationEditorScreen`

Editor for configuring an individual station.

```python
class StationEditorScreen(Screen):
    def __init__(self, station_index: int)
    def compose(self) -> ComposeResult
    def on_mount(self) -> None
    def on_option_list_option_selected(self, event) -> None
    def action_save(self) -> None
    def action_back(self) -> None
    async def action_quit(self) -> None
```

#### Constructor

**`__init__(station_index: int)`**

Initialize station editor.

**Parameters:**

- **`station_index`** (`int`): Station index (0-4 for stations 1-5)

**Attributes:**

- **`station_index`** (`int`): Index of station being edited
- **`mode`** (`str`): Current mode ("manual" or "database")
- **`available_stations`** (`List[Station]`): Stations from database
- **`stations_by_category`** (`Dict[str, List[Station]]`): Stations grouped by category

#### UI Components

**Input Mode Selection:**
- Manual Entry
- Select from Database

**Database Mode:**
- Searchable list of stations grouped by category
- Selecting a station auto-populates URL and name

**Manual Mode:**
- Stream URL or file path input
- Direct URL entry

**Common Fields:**
- Morse Code Message
- Station Name (optional)

**Actions:**
- Save Station
- Back to Station List

**Keyboard Bindings:**

- **Escape**: Back without saving
- **Ctrl+S**: Save station
- **Q**: Quit application
- **↑/↓**: Navigate options
- **Tab**: Move between input fields

#### Methods

**`on_mount() -> None`**

Populates database list with stations grouped by category.

**`_switch_to_manual_mode() -> None`**

Switch to manual URL entry mode.

**`_switch_to_database_mode() -> None`**

Switch to database selection mode.

**`_populate_from_database(station_name: str) -> None`**

Auto-populate fields when a database station is selected.

**`_save_station() -> None`**

Validate and save station configuration.

### `BluetoothSettingsScreen`

Configure Bluetooth mode settings.

```python
class BluetoothSettingsScreen(Screen):
    def compose(self) -> ComposeResult
    def on_mount(self) -> None
    def on_option_list_option_selected(self, event) -> None
    def action_save(self) -> None
    def action_back(self) -> None
    async def action_quit(self) -> None
```

**UI Components:**

- Bluetooth Morse Code Message input (default: "BT")
- Help text explaining the message usage
- Save Settings
- Back to Main Menu

**Keyboard Bindings:**

- **Escape**: Back without saving
- **Ctrl+S**: Save settings
- **Q**: Quit application
- **Tab**: Navigate fields

### `AudioSettingsScreen`

Configure audio and morse code settings.

```python
class AudioSettingsScreen(Screen):
    def compose(self) -> ComposeResult
    def on_mount(self) -> None
    def on_option_list_option_selected(self, event) -> None
    def action_save(self) -> None
    def action_back(self) -> None
    async def action_quit(self) -> None
```

**UI Components:**

- Volume (0-100)
- Morse Code Dot Duration (50-500 ms)
- Save Settings
- Back to Main Menu

**Validation:**

- Volume must be between 0 and 100
- Morse dot duration must be between 50 and 500 ms

**Keyboard Bindings:**

- **Escape**: Back without saving
- **Ctrl+S**: Save settings
- **Q**: Quit application
- **Tab**: Navigate fields

### `AdvancedSettingsScreen`

Configure GPIO pin assignments (advanced users).

```python
class AdvancedSettingsScreen(Screen):
    def compose(self) -> ComposeResult
    def on_mount(self) -> None
    def on_option_list_option_selected(self, event) -> None
    def action_save(self) -> None
    def action_back(self) -> None
    async def action_quit(self) -> None
```

**UI Components:**

- Warning message
- GPIO Pin inputs for:
  - Position 1 Pin
  - Position 2 Pin
  - Position 3 Pin
  - Position 4 Pin
  - Position 5 Pin
  - Position 6 Pin
  - LED Pin
- Save Settings
- Back to Main Menu

**Validation:**

- All pins must be in valid GPIO range (2-27)
- All pins must be unique (no duplicates)

**Keyboard Bindings:**

- **Escape**: Back without saving
- **Ctrl+S**: Save settings
- **Q**: Quit application
- **Tab**: Navigate fields

## Navigation

### General Navigation

- **↑/↓ Arrow Keys**: Navigate menu items and options
- **Enter**: Select menu item or confirm input
- **Tab**: Move between input fields
- **Escape**: Go back to previous screen
- **Q**: Quit application (warns if unsaved changes)
- **Ctrl+S**: Save configuration from any screen

### Navigation Flow

1. Start at Main Menu
2. Select a category (Stations, Bluetooth, Audio, Advanced)
3. Edit settings in the category screen
4. Save changes (auto-returns to previous screen)
5. Navigate back with Escape if not saving
6. Return to Main Menu
7. Select "Save & Exit" to save all changes and quit

## Status Messages

All screens display status messages:

- **Green "✓"**: Success (e.g., "Station saved!")
- **Red "✗"**: Error with details (e.g., "Volume must be between 0 and 100")
- **Yellow Warning**: Unsaved changes notification

## Notifications

The app uses Textual's notification system:

- **Information**: Configuration saved successfully
- **Warning**: Unsaved changes when quitting
- **Error**: Failed to save configuration

## Error Handling

### Validation Errors

When validation fails:

- Error message displayed in red
- User remains on the edit screen
- Can correct and retry

### Save Errors

If save fails:

- Error notification shown
- Configuration not written to file
- User can retry or cancel

### Input Validation

- Station URL: Cannot be empty
- Morse message: Defaults to "S1", "S2", etc. if empty
- Volume: Must be 0-100
- Morse dot duration: Must be 50-500 ms
- GPIO pins: Must be 2-27 and unique

## Usage Examples

### Running the TUI

```bash
# Standard way
make configure

# Direct invocation
python -m bosty_radio.tui

# With custom config path
python -m bosty_radio.tui /path/to/config.json
```

### Typical Workflow

1. Launch TUI
2. Navigate to "Configure Stations"
3. Select "Station 1"
4. Choose "Manual Entry" or "Select from Database"
5. If database: Select station from list
6. Edit morse message if desired
7. Select "Save Station"
8. Repeat for other stations
9. Return to Main Menu
10. Select "Save & Exit"

### Database Selection

1. In Station Editor, select "Select from Database"
2. Browse stations grouped by category (e.g., "--- BBC ---")
3. Navigate with arrow keys
4. Press Enter to select
5. URL and name auto-populate
6. Edit if needed
7. Save station

## CSS Styling

The TUI includes custom CSS for consistent appearance:

- Primary color highlights for active selections
- Panel backgrounds for help text
- Warning colors for advanced settings
- Proper spacing and margins
- Hidden class for conditional elements

## Related Modules

- **[Configuration](config.md)**: Provides configuration models
- **[Stations](../stations.md)**: Station database for selection
- **[Radio Controller](radio-controller.md)**: Uses saved configuration

## Design Philosophy

The new TUI follows these principles:

1. **Simple Navigation**: Menu-driven like raspi-config
2. **Clear Hierarchy**: Logical grouping of settings
3. **Focus Management**: Proper keyboard navigation
4. **Immediate Feedback**: Status messages and validation
5. **Non-Destructive**: Back button doesn't save changes
6. **Intuitive**: Common keyboard shortcuts (Q, Ctrl+S, Escape)

## Differences from Previous Version

The menu-driven TUI replaces the previous scrollable form:

**Old (Form-Based):**
- All settings on one long scrollable page
- Complex toggle system for each station
- Harder to navigate with keyboard
- Easy to get lost in options

**New (Menu-Driven):**
- Hierarchical menu system
- One task at a time
- Clear navigation path
- Simple keyboard navigation
- Similar to raspi-config or other CLI tools

This makes the TUI more approachable and easier to use, especially for those familiar with traditional console configuration tools.
