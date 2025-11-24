"""Textual TUI for configuration."""

import logging
from pathlib import Path
from typing import Optional

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, ScrollableContainer, Vertical
from textual.widgets import Button, Footer, Header, Input, Label, Select

from bosty_radio.config import ConfigManager, RadioConfig, StationConfig
from bosty_radio.stations import get_all_stations

logger = logging.getLogger(__name__)


class StationEditor(Container):
    """Editor for a single station configuration."""

    def __init__(self, station: StationConfig, index: int, *args, **kwargs):
        """Initialize station editor."""
        super().__init__(*args, **kwargs)
        self.station = station
        self.index = index
        self.mode = "manual"  # Start in manual mode
        self.available_stations = get_all_stations()

    def compose(self) -> ComposeResult:
        """Compose station editor UI."""
        with Vertical():
            yield Label(f"Station {self.index + 1}", classes="station-label")

            # Toggle button for mode selection
            with Horizontal(classes="mode-toggle"):
                yield Button(
                    "Database",
                    id=f"station-{self.index}-mode-database",
                    variant="default",
                )
                yield Button(
                    "Manual",
                    id=f"station-{self.index}-mode-manual",
                    variant="primary",
                )

            # Database selection (initially hidden)
            if self.available_stations:
                # Build options for Select widget: (display_text, value)
                station_options = [("-- Select a station --", "")] + [
                    (f"{s.name} ({s.category})", s.name) for s in self.available_stations
                ]
                yield Select(
                    station_options,
                    id=f"station-{self.index}-select",
                    classes="station-select hidden",
                )

            # Manual input fields
            yield Input(
                self.station.url,
                placeholder="Stream URL or file path",
                id=f"station-{self.index}-url",
                classes="manual-input",
            )
            yield Input(
                self.station.morse_message,
                placeholder="Morse code (e.g., S1, S2)",
                id=f"station-{self.index}-morse",
            )
            yield Input(
                self.station.name or "",
                placeholder="Station name (optional)",
                id=f"station-{self.index}-name",
            )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle mode toggle button presses."""
        button_id = event.button.id

        if button_id == f"station-{self.index}-mode-database":
            self._switch_to_database_mode()
        elif button_id == f"station-{self.index}-mode-manual":
            self._switch_to_manual_mode()

    def _switch_to_database_mode(self) -> None:
        """Switch to database selection mode."""
        self.mode = "database"

        # Update button styles
        db_button = self.query_one(f"#station-{self.index}-mode-database", Button)
        manual_button = self.query_one(f"#station-{self.index}-mode-manual", Button)
        db_button.variant = "primary"
        manual_button.variant = "default"

        # Show select, keep URL input visible but de-emphasize
        try:
            select_widget = self.query_one(f"#station-{self.index}-select", Select)
            select_widget.remove_class("hidden")
        except Exception:
            pass  # Select widget might not exist if no stations loaded

    def _switch_to_manual_mode(self) -> None:
        """Switch to manual entry mode."""
        self.mode = "manual"

        # Update button styles
        db_button = self.query_one(f"#station-{self.index}-mode-database", Button)
        manual_button = self.query_one(f"#station-{self.index}-mode-manual", Button)
        db_button.variant = "default"
        manual_button.variant = "primary"

        # Hide select
        try:
            select_widget = self.query_one(f"#station-{self.index}-select", Select)
            select_widget.add_class("hidden")
        except Exception:
            pass

    def on_select_changed(self, event: Select.Changed) -> None:
        """Handle station selection from database."""
        if event.select.id == f"station-{self.index}-select":
            selected_name = event.value

            if selected_name:
                # Find the selected station
                for station in self.available_stations:
                    if station.name == selected_name:
                        # Auto-populate URL and name fields
                        url_input = self.query_one(f"#station-{self.index}-url", Input)
                        name_input = self.query_one(f"#station-{self.index}-name", Input)

                        url_input.value = station.url
                        name_input.value = station.name
                        break

    def get_station(self) -> StationConfig:
        """Get updated station configuration from UI."""
        url_input = self.query_one(f"#station-{self.index}-url", Input)
        morse_input = self.query_one(f"#station-{self.index}-morse", Input)
        name_input = self.query_one(f"#station-{self.index}-name", Input)

        return StationConfig(
            url=url_input.value,
            morse_message=morse_input.value or f"S{self.index + 1}",
            name=name_input.value or None,
        )


class ConfigApp(App):
    """Main configuration TUI application."""

    CSS = """
    Screen {
        background: $surface;
    }
    .config-container {
        padding: 1;
        margin: 1;
    }
    .station-label {
        text-style: bold;
        margin-top: 1;
    }
    .help-text {
        background: $panel;
        padding: 1;
        margin: 1;
        border: solid $primary;
    }
    Button {
        margin: 1;
    }
    .mode-toggle {
        height: auto;
        margin-bottom: 1;
    }
    .mode-toggle Button {
        margin: 0 1 0 0;
        min-width: 12;
    }
    .station-select {
        margin-bottom: 1;
    }
    .hidden {
        display: none;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("s", "save", "Save"),
        ("h", "help", "Help"),
    ]

    def __init__(self, config_path: Optional[Path] = None, *args, **kwargs):
        """Initialize config app."""
        super().__init__(*args, **kwargs)
        self.config_manager = ConfigManager(config_path)
        self.config: RadioConfig = self.config_manager.load()

    def compose(self) -> ComposeResult:
        """Compose main UI."""
        yield Header(show_clock=True)
        with ScrollableContainer(classes="config-container"):
            yield Label("Bosty Radio Configuration", classes="title")
            yield Label("", id="status")

            # Help section
            with Container(classes="help-text"):
                yield Label("Allowed Sources:", classes="help-label")
                yield Label("• Internet Radio: http:// or https:// URLs (M3U, PLS, direct stream)")
                yield Label("• Local Files: /path/to/file.mp3 or /path/to/file.m3u")
                yield Label("• Examples:")
                yield Label("  - http://stream.example.com:8000/stream.mp3")
                yield Label("  - /home/pi/music/station.m3u")
                yield Label("  - https://example.com/playlist.pls")

            # Stations
            yield Label("Stations (Positions 1-5):", classes="section-label")
            for i, station in enumerate(self.config.stations):
                yield StationEditor(station, i, id=f"station-editor-{i}")

            # Bluetooth Morse
            yield Label("Bluetooth Mode:", classes="section-label")
            yield Input(
                self.config.bluetooth_morse,
                placeholder="Morse code for Bluetooth (e.g., BT)",
                id="bluetooth-morse",
            )

            # Morse timing
            yield Label("Morse Code Settings:", classes="section-label")
            yield Input(
                str(self.config.morse_dot_duration_ms),
                placeholder="Dot duration (ms)",
                id="morse-dot-duration",
            )

            # Volume
            yield Label("Volume:", classes="section-label")
            yield Input(
                str(self.config.volume),
                placeholder="Volume (0-100)",
                id="volume",
            )

            # GPIO pins (advanced)
            yield Label("GPIO Pins (Advanced):", classes="section-label")
            yield Label("Position 1:")
            yield Input(str(self.config.gpio.position_1), id="gpio-pos1")
            yield Label("Position 2:")
            yield Input(str(self.config.gpio.position_2), id="gpio-pos2")
            yield Label("Position 3:")
            yield Input(str(self.config.gpio.position_3), id="gpio-pos3")
            yield Label("Position 4:")
            yield Input(str(self.config.gpio.position_4), id="gpio-pos4")
            yield Label("Position 5:")
            yield Input(str(self.config.gpio.position_5), id="gpio-pos5")
            yield Label("Position 6:")
            yield Input(str(self.config.gpio.position_6), id="gpio-pos6")
            yield Label("LED:")
            yield Input(str(self.config.gpio.led), id="gpio-led")

        with Horizontal():
            yield Button("Save", id="save-button", variant="primary")
            yield Button("Cancel", id="cancel-button")

        yield Footer()

    def action_save(self) -> None:
        """Save configuration."""
        try:
            # Collect station data
            stations = []
            for i in range(5):
                editor = self.query_one(f"#station-editor-{i}", StationEditor)
                stations.append(editor.get_station())

            # Collect other settings
            bluetooth_morse = self.query_one("#bluetooth-morse", Input).value
            morse_dot = int(self.query_one("#morse-dot-duration", Input).value or "100")
            volume = int(self.query_one("#volume", Input).value or "80")

            # GPIO pins
            gpio_config = {
                "position_1": int(self.query_one("#gpio-pos1", Input).value or "2"),
                "position_2": int(self.query_one("#gpio-pos2", Input).value or "3"),
                "position_3": int(self.query_one("#gpio-pos3", Input).value or "4"),
                "position_4": int(self.query_one("#gpio-pos4", Input).value or "17"),
                "position_5": int(self.query_one("#gpio-pos5", Input).value or "27"),
                "position_6": int(self.query_one("#gpio-pos6", Input).value or "22"),
                "led": int(self.query_one("#gpio-led", Input).value or "18"),
            }

            # Create new config
            new_config = RadioConfig(
                stations=stations,
                bluetooth_morse=bluetooth_morse or "BT",
                morse_dot_duration_ms=morse_dot,
                volume=volume,
                gpio=self.config.gpio.__class__(**gpio_config),
                error_tone_frequency_hz=self.config.error_tone_frequency_hz,
            )

            # Validate
            new_config.model_validate(new_config.model_dump())

            # Save
            self.config_manager.save(new_config)
            self.config = new_config

            status = self.query_one("#status", Label)
            status.update("✓ Configuration saved successfully!")
            status.styles.color = "green"

        except ValueError as e:
            status = self.query_one("#status", Label)
            status.update(f"✗ Validation error: {e}")
            status.styles.color = "red"
        except Exception as e:
            logger.error(f"Error saving config: {e}")
            status = self.query_one("#status", Label)
            status.update(f"✗ Error saving: {e}")
            status.styles.color = "red"

    def action_help(self) -> None:
        """Show help information."""
        # Help is already visible in the UI
        status = self.query_one("#status", Label)
        status.update("Help information is shown above. Use Tab to navigate, Enter to edit.")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "save-button":
            self.action_save()
        elif event.button.id == "cancel-button":
            self.exit()

    async def action_quit(self) -> None:
        """Quit application."""
        self.exit()


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
