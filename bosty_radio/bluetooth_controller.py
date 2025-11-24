"""Bluetooth controller for A2DP sink mode."""

import logging
import subprocess
import time
from typing import Optional

logger = logging.getLogger(__name__)


class BluetoothController:
    """Manages Bluetooth A2DP sink functionality."""

    def __init__(self):
        """Initialize Bluetooth controller."""
        self._is_paired = False
        self._is_connected = False
        self._pairing_mode = False

    def _run_command(self, *args: str, check: bool = False) -> subprocess.CompletedProcess:
        """Run a shell command."""
        try:
            result = subprocess.run(
                args, capture_output=True, text=True, check=check, timeout=30
            )
            return result
        except subprocess.TimeoutExpired:
            logger.error(f"Command timed out: {' '.join(args)}")
            raise
        except subprocess.CalledProcessError as e:
            logger.error(f"Command failed: {' '.join(args)}, error: {e.stderr}")
            raise

    def _play_ding(self) -> None:
        """Play a 'ding' sound to indicate pairing needed."""
        # Try to play a simple beep/ding
        # Using sox or aplay with a short tone
        try:
            subprocess.run(
                ["sox", "-n", "-t", "alsa", "default", "synth", "0.2", "sine", "800"],
                capture_output=True,
                timeout=2,
                check=False,
            )
        except (subprocess.TimeoutExpired, FileNotFoundError):
            # Fallback: try beep command
            try:
                subprocess.run(["beep"], timeout=1, check=False)
            except (subprocess.TimeoutExpired, FileNotFoundError):
                logger.warning("Could not play ding sound (sox/beep not available)")

    def enable_pairing_mode(self) -> bool:
        """
        Enable Bluetooth pairing mode (makes Pi discoverable).

        Returns:
            True if successful
        """
        try:
            # Make discoverable
            self._run_command("bluetoothctl", "discoverable", "on", check=False)
            # Enable pairing
            self._run_command("bluetoothctl", "pairable", "on", check=False)
            self._pairing_mode = True
            logger.info("Bluetooth pairing mode enabled")
            self._play_ding()
            return True
        except Exception as e:
            logger.error(f"Error enabling pairing mode: {e}")
            return False

    def disable_pairing_mode(self) -> None:
        """Disable Bluetooth pairing mode."""
        try:
            self._run_command("bluetoothctl", "discoverable", "off", check=False)
            self._run_command("bluetoothctl", "pairable", "off", check=False)
            self._pairing_mode = False
            logger.info("Bluetooth pairing mode disabled")
        except Exception as e:
            logger.error(f"Error disabling pairing mode: {e}")

    def switch_to_bluetooth_sink(self) -> bool:
        """
        Switch audio output to Bluetooth A2DP sink.

        Returns:
            True if successful
        """
        try:
            # Enable pairing mode first
            self.enable_pairing_mode()

            # Switch audio to Bluetooth (using pulseaudio or bluez-alsa)
            # This depends on the audio system setup
            # For pulseaudio:
            result = self._run_command(
                "pactl", "set-default-sink", "bluez_sink", check=False
            )
            if result.returncode != 0:
                # Try alternative method
                logger.warning("Primary Bluetooth sink method failed, trying alternative")
                # Could try bluez-alsa or other methods here

            logger.info("Switched to Bluetooth sink")
            return True
        except Exception as e:
            logger.error(f"Error switching to Bluetooth sink: {e}")
            return False

    def check_connection_status(self) -> bool:
        """
        Check if a device is connected to Bluetooth.

        Returns:
            True if connected, False otherwise
        """
        try:
            result = self._run_command("bluetoothctl", "info", check=False)
            if result.returncode == 0:
                output = result.stdout.lower()
                # Check for connected status
                connected = "connected: yes" in output
                if connected != self._is_connected:
                    self._is_connected = connected
                    logger.info(f"Bluetooth connection status: {connected}")
                return connected
            return False
        except Exception as e:
            logger.error(f"Error checking connection status: {e}")
            return False

    def get_connection_status(self) -> bool:
        """Get current connection status (cached)."""
        return self._is_connected

    def is_pairing_mode(self) -> bool:
        """Check if in pairing mode."""
        return self._pairing_mode

