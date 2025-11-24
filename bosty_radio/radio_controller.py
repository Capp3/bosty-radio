"""Main radio controller daemon."""

import logging
import signal
import sys
import time
from pathlib import Path

from bosty_radio.audio_controller import AudioController
from bosty_radio.bluetooth_controller import BluetoothController
from bosty_radio.config import ConfigManager, RadioConfig
from bosty_radio.gpio_controller import GPIOController
from bosty_radio.morse_led import MorseLED

logger = logging.getLogger(__name__)


class RadioController:
    """Main controller coordinating all components."""

    def __init__(self, config_path: Path | None = None):
        """Initialize radio controller."""
        self.config_manager = ConfigManager(config_path)
        self.config: RadioConfig = self.config_manager.load()

        # Components
        self.gpio: GPIOController | None = None
        self.morse_led: MorseLED | None = None
        self.audio: AudioController | None = None
        self.bluetooth: BluetoothController | None = None

        # State
        self.current_position: int | None = None
        self.running = False
        self._shutdown_requested = False

        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.info(f"Received signal {signum}, shutting down...")
        self._shutdown_requested = True

    def _position_changed(self, position: int) -> None:
        """Handle position change callback from GPIO."""
        logger.info(f"Position changed to {position + 1}")
        self._switch_to_position(position)

    def _switch_to_position(self, position: int) -> None:
        """Switch to a new position."""
        if position == self.current_position:
            return  # No change

        self.current_position = position

        if position < 5:
            # Positions 1-5: Internet radio or local file
            self._switch_to_station(position)
        elif position == 5:
            # Position 6: Bluetooth mode
            self._switch_to_bluetooth()

    def _switch_to_station(self, station_index: int) -> None:
        """Switch to a station (position 1-5)."""
        if station_index >= len(self.config.stations):
            logger.error(f"Invalid station index: {station_index}")
            return

        station = self.config.stations[station_index]
        logger.info(f"Switching to station {station_index + 1}: {station.morse_message}")

        # Stop Bluetooth if active
        if self.bluetooth:
            self.bluetooth.disable_pairing_mode()

        # Start Morse code message
        if self.morse_led:
            self.morse_led.start_message(station.morse_message)

        # Play station
        if self.audio:
            success = self.audio.play_stream(station.url)
            if not success:
                logger.error(f"Failed to play station {station_index + 1}")
                # Morse code will continue showing the message
            else:
                logger.info(f"Successfully playing station {station_index + 1}")

    def _switch_to_bluetooth(self) -> None:
        """Switch to Bluetooth mode (position 6)."""
        logger.info("Switching to Bluetooth mode")

        # Stop audio playback
        if self.audio:
            self.audio.stop()

        # Start Bluetooth Morse code
        if self.morse_led:
            self.morse_led.start_message(self.config.bluetooth_morse)

        # Enable Bluetooth pairing
        if self.bluetooth:
            self.bluetooth.switch_to_bluetooth_sink()

    def _update_bluetooth_led(self) -> None:
        """Update LED based on Bluetooth connection status."""
        if not self.bluetooth or self.current_position != 5:
            return

        connected = self.bluetooth.check_connection_status()
        # For Bluetooth mode, LED shows connection status
        # If connected, solid on; if not, continue Morse code
        if connected:
            if self.morse_led:
                self.morse_led.stop()
                self.morse_led.set_state(True)
        else:
            # Not connected, show Morse code
            if self.morse_led:
                self.morse_led.set_state(False)
                self.morse_led.start_message(self.config.bluetooth_morse)

    def setup(self) -> None:
        """Initialize all components."""
        try:
            # GPIO setup
            gpio_pins = [
                self.config.gpio.position_1,
                self.config.gpio.position_2,
                self.config.gpio.position_3,
                self.config.gpio.position_4,
                self.config.gpio.position_5,
                self.config.gpio.position_6,
            ]
            self.gpio = GPIOController(gpio_pins, callback=self._position_changed)
            self.gpio.setup()

            # Morse LED setup
            self.morse_led = MorseLED(self.config.gpio.led, self.config.morse_dot_duration_ms)
            self.morse_led.setup()

            # Audio controller
            self.audio = AudioController(self.config.error_tone_frequency_hz)
            # Set initial volume
            self.audio.set_volume(self.config.volume)

            # Bluetooth controller
            self.bluetooth = BluetoothController()

            logger.info("All components initialized")
        except Exception as e:
            logger.error(f"Error during setup: {e}")
            raise

    def run(self) -> None:
        """Main run loop."""
        self.running = True
        logger.info("Radio controller started")

        last_bluetooth_check = 0
        bluetooth_check_interval = 2.0  # Check every 2 seconds

        try:
            while not self._shutdown_requested:
                # Read GPIO position
                position = self.gpio.read_position() if self.gpio else None

                if position is not None and position != self.current_position:
                    self._switch_to_position(position)

                # Update Bluetooth LED status periodically
                if self.current_position == 5:  # Bluetooth mode
                    now = time.time()
                    if now - last_bluetooth_check >= bluetooth_check_interval:
                        self._update_bluetooth_led()
                        last_bluetooth_check = now

                # Small sleep to avoid busy-waiting
                time.sleep(0.1)

        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received")
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
        finally:
            self.shutdown()

    def shutdown(self) -> None:
        """Clean shutdown of all components."""
        logger.info("Shutting down...")
        self.running = False

        if self.audio:
            self.audio.stop()

        if self.bluetooth:
            self.bluetooth.disable_pairing_mode()

        if self.morse_led:
            self.morse_led.stop()
            self.morse_led.cleanup()

        if self.gpio:
            self.gpio.cleanup()

        logger.info("Shutdown complete")

    def reload_config(self) -> None:
        """Reload configuration from file."""
        logger.info("Reloading configuration...")
        self.config = self.config_manager.reload()
        # Update volume if changed
        if self.audio:
            self.audio.set_volume(self.config.volume)
        logger.info("Configuration reloaded")


def main():
    """Main entry point."""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("/var/log/bosty-radio/controller.log"),
            logging.StreamHandler(sys.stdout),
        ],
    )

    try:
        controller = RadioController()
        controller.setup()
        controller.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
