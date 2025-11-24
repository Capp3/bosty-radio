"""Menu-driven TUI for Bosty Radio configuration."""

import logging
from pathlib import Path
from typing import Optional, cast

from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.screen import Screen
from textual.widgets import Footer, Header, Input, Label, OptionList, Static
from textual.widgets.option_list import Option

from bosty_radio.config import ConfigManager, RadioConfig, StationConfig
from bosty_radio.stations import get_all_stations, get_stations_by_category

logger = logging.getLogger(__name__)


class MainMenuScreen(Screen):
    """Main configuration menu."""

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("escape", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        """Compose main menu UI."""
        yield Header()
        yield Container(
            Static("Bosty Radio Configuration", classes="title"),
            Static("", id="status-message"),
            OptionList(
                Option("Configure Stations", id="stations"),
                Option("Bluetooth Settings", id="bluetooth"),
                Option("Audio Settings", id="audio"),
                Option("Advanced (GPIO Pins)", id="advanced"),
                Option("Save & Exit", id="save_exit"),
                id="main-menu",
            ),
            classes="menu-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Set focus when mounted."""
        self.query_one("#main-menu", OptionList).focus()

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        """Handle menu selection."""
        option_id = event.option.id

        if option_id == "stations":
            self.app.push_screen(StationListScreen())
        elif option_id == "bluetooth":
            self.app.push_screen(BluetoothSettingsScreen())
        elif option_id == "audio":
            self.app.push_screen(AudioSettingsScreen())
        elif option_id == "advanced":
            self.app.push_screen(AdvancedSettingsScreen())
        elif option_id == "save_exit":
            # Call the custom save_and_exit action
            app = cast("ConfigApp", self.app)
            app.action_save_and_exit()

    async def action_quit(self) -> None:
        """Quit with confirmation if changes made."""
        await self.app.action_quit()


class StationListScreen(Screen):
    """List of stations to configure."""

    BINDINGS = [
        ("escape", "back", "Back"),
        ("q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        """Compose station list UI."""
        yield Header()
        yield Container(
            Static("Configure Stations", classes="title"),
            Static("Select a station to configure:", classes="help-text"),
            OptionList(
                Option("Station 1", id="station-0"),
                Option("Station 2", id="station-1"),
                Option("Station 3", id="station-2"),
                Option("Station 4", id="station-3"),
                Option("Station 5", id="station-4"),
                Option("< Back to Main Menu", id="back"),
                id="station-list",
            ),
            classes="menu-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Set focus when mounted."""
        self.query_one("#station-list", OptionList).focus()

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        """Handle station selection."""
        option_id = event.option.id

        if option_id == "back":
            self.app.pop_screen()
        elif option_id and option_id.startswith("station-"):
            station_index = int(option_id.split("-")[1])
            self.app.push_screen(StationEditorScreen(station_index))

    def action_back(self) -> None:
        """Go back to main menu."""
        self.app.pop_screen()

    async def action_quit(self) -> None:
        """Quit application."""
        await self.app.action_quit()


class StationEditorScreen(Screen):
    """Editor for a single station."""

    BINDINGS = [
        ("escape", "back", "Back"),
        ("ctrl+s", "save", "Save"),
        ("q", "quit", "Quit"),
    ]

    def __init__(self, station_index: int, *args, **kwargs):
        """Initialize station editor."""
        super().__init__(*args, **kwargs)
        self.station_index = station_index
        self.mode = "manual"  # Start in manual mode
        self.available_stations = get_all_stations()
        self.stations_by_category = get_stations_by_category()

    def compose(self) -> ComposeResult:
        """Compose station editor UI."""
        app = cast("ConfigApp", self.app)
        station = app.config.stations[self.station_index]

        yield Header()
        yield Container(
            Static(f"Configure Station {self.station_index + 1}", classes="title"),
            Static("", id="status-message"),

            # Mode selection
            Static("Input Mode:", classes="section-label"),
            OptionList(
                Option("Manual Entry", id="mode-manual"),
                Option("Select from Database", id="mode-database"),
                id="mode-selector",
            ),

            # Database selection (hidden initially)
            Static("Select Station:", classes="section-label hidden", id="db-label"),
            OptionList(id="station-database", classes="hidden"),

            # Manual entry fields
            Static("Stream URL or File Path:", classes="section-label", id="url-label"),
            Input(
                value=station.url,
                placeholder="http://stream.example.com/radio or /path/to/file.mp3",
                id="url-input",
            ),

            Static("Morse Code Message:", classes="section-label"),
            Input(
                value=station.morse_message,
                placeholder=f"S{self.station_index + 1}",
                id="morse-input",
            ),

            Static("Station Name (Optional):", classes="section-label"),
            Input(
                value=station.name or "",
                placeholder="Station name",
                id="name-input",
            ),

            # Action buttons
            OptionList(
                Option("Save Station", id="save"),
                Option("< Back to Station List", id="back"),
                id="action-menu",
            ),

            classes="menu-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Set focus and populate database if available."""
        # Populate database list
        if self.available_stations:
            db_list = self.query_one("#station-database", OptionList)

            # Add stations grouped by category
            for category, stations in sorted(self.stations_by_category.items()):
                # Add category header (disabled option)
                db_list.add_option(Option(f"--- {category} ---", id=f"cat-{category}", disabled=True))
                # Add stations in category
                for station in stations:
                    db_list.add_option(Option(station.name, id=f"db-{station.name}"))

        # Set initial focus
        self.query_one("#mode-selector", OptionList).focus()

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        """Handle option selection."""
        option_id = event.option.id

        if option_id == "mode-manual":
            self._switch_to_manual_mode()
        elif option_id == "mode-database":
            self._switch_to_database_mode()
        elif option_id and option_id.startswith("db-"):
            # Station selected from database
            station_name = option_id[3:]  # Remove "db-" prefix
            self._populate_from_database(station_name)
        elif option_id == "save":
            self._save_station()
        elif option_id == "back":
            self.app.pop_screen()

    def _switch_to_manual_mode(self) -> None:
        """Switch to manual entry mode."""
        self.mode = "manual"

        # Hide database widgets
        self.query_one("#db-label").add_class("hidden")
        self.query_one("#station-database").add_class("hidden")

        # Show manual widgets
        self.query_one("#url-label").remove_class("hidden")
        self.query_one("#url-input").remove_class("hidden")

        # Focus on URL input
        self.query_one("#url-input").focus()

    def _switch_to_database_mode(self) -> None:
        """Switch to database selection mode."""
        self.mode = "database"

        # Show database widgets
        self.query_one("#db-label").remove_class("hidden")
        self.query_one("#station-database").remove_class("hidden")

        # Keep URL input visible (shows selected URL)
        self.query_one("#url-label").remove_class("hidden")
        self.query_one("#url-input").remove_class("hidden")

        # Focus on database list
        self.query_one("#station-database").focus()

    def _populate_from_database(self, station_name: str) -> None:
        """Populate fields from selected database station."""
        for station in self.available_stations:
            if station.name == station_name:
                self.query_one("#url-input", Input).value = station.url
                self.query_one("#name-input", Input).value = station.name

                # Show success message
                status = self.query_one("#status-message", Static)
                status.update(f"✓ Loaded: {station.name}")
                status.styles.color = "green"

                # Focus on morse input for user to verify/edit
                self.query_one("#morse-input").focus()
                break

    def _save_station(self) -> None:
        """Save station configuration."""
        try:
            # Collect values
            url = self.query_one("#url-input", Input).value.strip()
            morse = self.query_one("#morse-input", Input).value.strip()
            name = self.query_one("#name-input", Input).value.strip()

            # Validate
            if not url:
                raise ValueError("URL cannot be empty")
            if not morse:
                morse = f"S{self.station_index + 1}"

            # Update config
            app = cast("ConfigApp", self.app)
            app.config.stations[self.station_index] = StationConfig(
                url=url,
                morse_message=morse,
                name=name or None,
            )
            app.config_dirty = True

            # Show success and go back
            status = self.query_one("#status-message", Static)
            status.update("✓ Station saved!")
            status.styles.color = "green"

            # Return to station list after brief delay
            self.set_timer(0.5, lambda: self.app.pop_screen())

        except Exception as e:
            status = self.query_one("#status-message", Static)
            status.update(f"✗ Error: {e}")
            status.styles.color = "red"

    def action_save(self) -> None:
        """Save station (keyboard shortcut)."""
        self._save_station()

    def action_back(self) -> None:
        """Go back without saving."""
        self.app.pop_screen()

    async def action_quit(self) -> None:
        """Quit application."""
        await self.app.action_quit()


class BluetoothSettingsScreen(Screen):
    """Bluetooth settings editor."""

    BINDINGS = [
        ("escape", "back", "Back"),
        ("ctrl+s", "save", "Save"),
        ("q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        """Compose bluetooth settings UI."""
        app = cast("ConfigApp", self.app)

        yield Header()
        yield Container(
            Static("Bluetooth Settings", classes="title"),
            Static("", id="status-message"),

            Static("Bluetooth Morse Code Message:", classes="section-label"),
            Static("This message will blink when in Bluetooth mode (position 6)", classes="help-text"),
            Input(
                value=app.config.bluetooth_morse,
                placeholder="BT",
                id="bluetooth-morse",
            ),

            OptionList(
                Option("Save Settings", id="save"),
                Option("< Back to Main Menu", id="back"),
                id="action-menu",
            ),

            classes="menu-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Set focus when mounted."""
        self.query_one("#bluetooth-morse", Input).focus()

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        """Handle option selection."""
        option_id = event.option.id

        if option_id == "save":
            self._save_settings()
        elif option_id == "back":
            self.app.pop_screen()

    def _save_settings(self) -> None:
        """Save bluetooth settings."""
        try:
            morse = self.query_one("#bluetooth-morse", Input).value.strip()

            if not morse:
                morse = "BT"

            app = cast("ConfigApp", self.app)
            app.config.bluetooth_morse = morse
            app.config_dirty = True

            status = self.query_one("#status-message", Static)
            status.update("✓ Bluetooth settings saved!")
            status.styles.color = "green"

            self.set_timer(0.5, lambda: self.app.pop_screen())

        except Exception as e:
            status = self.query_one("#status-message", Static)
            status.update(f"✗ Error: {e}")
            status.styles.color = "red"

    def action_save(self) -> None:
        """Save settings (keyboard shortcut)."""
        self._save_settings()

    def action_back(self) -> None:
        """Go back without saving."""
        self.app.pop_screen()

    async def action_quit(self) -> None:
        """Quit application."""
        await self.app.action_quit()


class AudioSettingsScreen(Screen):
    """Audio settings editor."""

    BINDINGS = [
        ("escape", "back", "Back"),
        ("ctrl+s", "save", "Save"),
        ("q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        """Compose audio settings UI."""
        app = cast("ConfigApp", self.app)

        yield Header()
        yield Container(
            Static("Audio Settings", classes="title"),
            Static("", id="status-message"),

            Static("Volume (0-100):", classes="section-label"),
            Input(
                value=str(app.config.volume),
                placeholder="80",
                id="volume",
            ),

            Static("Morse Code Dot Duration (ms):", classes="section-label"),
            Static("Duration of a single dot in milliseconds (50-500)", classes="help-text"),
            Input(
                value=str(app.config.morse_dot_duration_ms),
                placeholder="100",
                id="morse-dot",
            ),

            OptionList(
                Option("Save Settings", id="save"),
                Option("< Back to Main Menu", id="back"),
                id="action-menu",
            ),

            classes="menu-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Set focus when mounted."""
        self.query_one("#volume", Input).focus()

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        """Handle option selection."""
        option_id = event.option.id

        if option_id == "save":
            self._save_settings()
        elif option_id == "back":
            self.app.pop_screen()

    def _save_settings(self) -> None:
        """Save audio settings."""
        try:
            volume_str = self.query_one("#volume", Input).value.strip()
            morse_str = self.query_one("#morse-dot", Input).value.strip()

            volume = int(volume_str) if volume_str else 80
            morse_dot = int(morse_str) if morse_str else 100

            # Validate
            if not 0 <= volume <= 100:
                raise ValueError("Volume must be between 0 and 100")
            if not 50 <= morse_dot <= 500:
                raise ValueError("Morse dot duration must be between 50 and 500 ms")

            app = cast("ConfigApp", self.app)
            app.config.volume = volume
            app.config.morse_dot_duration_ms = morse_dot
            app.config_dirty = True

            status = self.query_one("#status-message", Static)
            status.update("✓ Audio settings saved!")
            status.styles.color = "green"

            self.set_timer(0.5, lambda: self.app.pop_screen())

        except ValueError as e:
            status = self.query_one("#status-message", Static)
            status.update(f"✗ Error: {e}")
            status.styles.color = "red"

    def action_save(self) -> None:
        """Save settings (keyboard shortcut)."""
        self._save_settings()

    def action_back(self) -> None:
        """Go back without saving."""
        self.app.pop_screen()

    async def action_quit(self) -> None:
        """Quit application."""
        await self.app.action_quit()


class AdvancedSettingsScreen(Screen):
    """Advanced settings (GPIO pins)."""

    BINDINGS = [
        ("escape", "back", "Back"),
        ("ctrl+s", "save", "Save"),
        ("q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        """Compose advanced settings UI."""
        app = cast("ConfigApp", self.app)
        gpio = app.config.gpio

        yield Header()
        yield Container(
            Static("Advanced Settings (GPIO Pins)", classes="title"),
            Static("", id="status-message"),
            Static("Only change these if you know what you're doing!", classes="warning-text"),

            Static("GPIO Pin Assignments:", classes="section-label"),

            Static("Position 1 Pin:", classes="field-label"),
            Input(value=str(gpio.position_1), id="gpio-pos1"),

            Static("Position 2 Pin:", classes="field-label"),
            Input(value=str(gpio.position_2), id="gpio-pos2"),

            Static("Position 3 Pin:", classes="field-label"),
            Input(value=str(gpio.position_3), id="gpio-pos3"),

            Static("Position 4 Pin:", classes="field-label"),
            Input(value=str(gpio.position_4), id="gpio-pos4"),

            Static("Position 5 Pin:", classes="field-label"),
            Input(value=str(gpio.position_5), id="gpio-pos5"),

            Static("Position 6 Pin:", classes="field-label"),
            Input(value=str(gpio.position_6), id="gpio-pos6"),

            Static("LED Pin:", classes="field-label"),
            Input(value=str(gpio.led), id="gpio-led"),

            OptionList(
                Option("Save Settings", id="save"),
                Option("< Back to Main Menu", id="back"),
                id="action-menu",
            ),

            classes="menu-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Set focus when mounted."""
        self.query_one("#action-menu", OptionList).focus()

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        """Handle option selection."""
        option_id = event.option.id

        if option_id == "save":
            self._save_settings()
        elif option_id == "back":
            self.app.pop_screen()

    def _save_settings(self) -> None:
        """Save GPIO settings."""
        try:
            # Collect values
            pos1 = int(self.query_one("#gpio-pos1", Input).value.strip())
            pos2 = int(self.query_one("#gpio-pos2", Input).value.strip())
            pos3 = int(self.query_one("#gpio-pos3", Input).value.strip())
            pos4 = int(self.query_one("#gpio-pos4", Input).value.strip())
            pos5 = int(self.query_one("#gpio-pos5", Input).value.strip())
            pos6 = int(self.query_one("#gpio-pos6", Input).value.strip())
            led = int(self.query_one("#gpio-led", Input).value.strip())

            # Validate (basic check for valid GPIO range)
            pins = [pos1, pos2, pos3, pos4, pos5, pos6, led]
            for pin in pins:
                if not 2 <= pin <= 27:
                    raise ValueError(f"GPIO pin {pin} is out of valid range (2-27)")

            # Check for duplicates
            if len(pins) != len(set(pins)):
                raise ValueError("GPIO pins must be unique")

            # Update config - create new GPIO config using existing type
            app = cast("ConfigApp", self.app)
            gpio_type = type(app.config.gpio)
            app.config.gpio = gpio_type(
                position_1=pos1,
                position_2=pos2,
                position_3=pos3,
                position_4=pos4,
                position_5=pos5,
                position_6=pos6,
                led=led,
            )
            app.config_dirty = True

            status = self.query_one("#status-message", Static)
            status.update("✓ GPIO settings saved!")
            status.styles.color = "green"

            self.set_timer(0.5, lambda: self.app.pop_screen())

        except ValueError as e:
            status = self.query_one("#status-message", Static)
            status.update(f"✗ Error: {e}")
            status.styles.color = "red"

    def action_save(self) -> None:
        """Save settings (keyboard shortcut)."""
        self._save_settings()

    def action_back(self) -> None:
        """Go back without saving."""
        self.app.pop_screen()

    async def action_quit(self) -> None:
        """Quit application."""
        await self.app.action_quit()


class ConfigApp(App):
    """Main configuration application."""

    CSS = """
    Screen {
        background: $surface;
    }

    .menu-container {
        padding: 1;
        margin: 1;
        width: 100%;
        height: 100%;
    }

    .title {
        text-style: bold;
        background: $primary;
        color: $text;
        padding: 1;
        margin-bottom: 1;
        text-align: center;
    }

    .section-label {
        text-style: bold;
        margin-top: 1;
        margin-bottom: 0;
    }

    .field-label {
        margin-top: 1;
        margin-bottom: 0;
        color: $text-muted;
    }

    .help-text {
        color: $text-muted;
        margin-bottom: 1;
    }

    .warning-text {
        color: $warning;
        margin-bottom: 1;
        text-style: bold;
    }

    #status-message {
        margin-bottom: 1;
        min-height: 1;
    }

    OptionList {
        margin-top: 1;
        margin-bottom: 1;
        height: auto;
    }

    Input {
        margin-bottom: 1;
    }

    .hidden {
        display: none;
    }

    #station-database {
        height: 20;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("ctrl+s", "save", "Save"),
    ]

    def __init__(self, config_path: Optional[Path] = None, *args, **kwargs):
        """Initialize config app."""
        super().__init__(*args, **kwargs)
        self.config_manager = ConfigManager(config_path)
        self.config: RadioConfig = self.config_manager.load()
        self.config_dirty = False

    def on_mount(self) -> None:
        """Push main menu when app starts."""
        self.push_screen(MainMenuScreen())

    def action_save(self) -> None:
        """Save configuration."""
        if self._save_config():
            self.notify("✓ Configuration saved successfully!", severity="information")
        else:
            self.notify("✗ Failed to save configuration", severity="error")

    def action_save_and_exit(self) -> None:
        """Save configuration and exit."""
        if self._save_config():
            self.exit()
        else:
            self.notify("✗ Failed to save configuration", severity="error")

    async def action_quit(self) -> None:
        """Quit with confirmation if unsaved changes."""
        if self.config_dirty:
            self.notify("Warning: You have unsaved changes! Use 'Save & Exit' or Ctrl+S to save.", severity="warning")
            return
        self.exit()

    def _save_config(self) -> bool:
        """Save configuration to file."""
        try:
            # Validate config
            self.config.model_validate(self.config.model_dump())

            # Save to file
            self.config_manager.save(self.config)
            self.config_dirty = False

            logger.info("Configuration saved successfully")
            return True

        except Exception as e:
            logger.error(f"Error saving config: {e}")
            return False


def main():
    """Main entry point for TUI."""
    import sys

    logging.basicConfig(level=logging.WARNING)  # Reduce noise for TUI

    config_path = None
    if len(sys.argv) > 1:
        config_path = Path(sys.argv[1])

    app = ConfigApp(config_path)
    app.run()


if __name__ == "__main__":
    main()
