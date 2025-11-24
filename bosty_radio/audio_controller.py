"""Audio controller using MPD/MPC."""

import logging
import subprocess
import time
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class AudioController:
    """Manages audio playback via MPD/MPC."""

    def __init__(self, error_tone_frequency_hz: int = 500):
        """
        Initialize audio controller.

        Args:
            error_tone_frequency_hz: Frequency for error tone
        """
        self.error_tone_frequency = error_tone_frequency_hz
        self._current_url: Optional[str] = None

    def _run_mpc(self, *args: str, check: bool = False) -> subprocess.CompletedProcess:
        """Run MPC command and return result."""
        cmd = ["mpc"] + list(args)
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, check=check, timeout=10
            )
            return result
        except subprocess.TimeoutExpired:
            logger.error(f"MPC command timed out: {' '.join(cmd)}")
            raise
        except subprocess.CalledProcessError as e:
            logger.error(f"MPC command failed: {' '.join(cmd)}, error: {e.stderr}")
            raise

    def _play_error_tone(self, duration_seconds: float = 0.5) -> None:
        """Play error tone using sox or aplay."""
        # Try sox first, then aplay with a simple tone
        tone_cmd = [
            "sox",
            "-n",
            "-t",
            "alsa",
            "default",
            "synth",
            str(duration_seconds),
            "sine",
            str(self.error_tone_frequency),
        ]

        try:
            subprocess.run(tone_cmd, capture_output=True, timeout=2, check=False)
        except (subprocess.TimeoutExpired, FileNotFoundError):
            # Fallback: try aplay with a generated tone file
            logger.warning("sox not available, skipping error tone")
            # Could generate a WAV file here if needed

    def play_stream(self, url: str) -> bool:
        """
        Play an internet radio stream or local file.

        Args:
            url: Stream URL or file path

        Returns:
            True if successful, False otherwise
        """
        try:
            # Stop current playback
            self._run_mpc("stop", check=False)

            # Clear playlist
            self._run_mpc("clear", check=False)

            # Add URL to playlist
            result = self._run_mpc("add", url, check=False)
            if result.returncode != 0:
                logger.error(f"Failed to add URL to playlist: {result.stderr}")
                self._play_error_tone()
                return False

            # Play
            result = self._run_mpc("play", check=False)
            if result.returncode != 0:
                logger.error(f"Failed to start playback: {result.stderr}")
                self._play_error_tone()
                return False

            # Wait a moment and check if actually playing
            time.sleep(1)
            status = self.get_status()
            if status and "playing" in status.lower():
                self._current_url = url
                logger.info(f"Playing: {url}")
                return True
            else:
                logger.error("Playback started but not actually playing")
                self._play_error_tone()
                return False

        except Exception as e:
            logger.error(f"Error playing stream: {e}")
            self._play_error_tone()
            return False

    def stop(self) -> None:
        """Stop audio playback."""
        try:
            self._run_mpc("stop", check=False)
            self._current_url = None
            logger.info("Audio stopped")
        except Exception as e:
            logger.error(f"Error stopping audio: {e}")

    def set_volume(self, volume: int) -> bool:
        """
        Set volume level (0-100).

        Args:
            volume: Volume level 0-100

        Returns:
            True if successful
        """
        try:
            result = self._run_mpc("volume", str(volume), check=False)
            if result.returncode == 0:
                logger.info(f"Volume set to {volume}%")
                return True
            return False
        except Exception as e:
            logger.error(f"Error setting volume: {e}")
            return False

    def get_status(self) -> Optional[str]:
        """Get current playback status."""
        try:
            result = self._run_mpc("status", check=False)
            if result.returncode == 0:
                return result.stdout
            return None
        except Exception as e:
            logger.error(f"Error getting status: {e}")
            return None

    def is_playing(self) -> bool:
        """Check if audio is currently playing."""
        status = self.get_status()
        if status:
            return "playing" in status.lower()
        return False

