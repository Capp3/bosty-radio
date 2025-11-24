"""GPIO controller for rotary switch input."""

import logging
from typing import Callable, Optional

try:
    import RPi.GPIO as GPIO
except ImportError:
    # Mock for development/testing
    GPIO = None  # type: ignore

logger = logging.getLogger(__name__)


class GPIOController:
    """Manages GPIO input reading for rotary switch positions."""

    def __init__(self, pins: list[int], callback: Optional[Callable[[int], None]] = None):
        """
        Initialize GPIO controller.

        Args:
            pins: List of GPIO pin numbers (BCM) for positions 1-6
            callback: Optional callback function(position_index) when position changes
        """
        if GPIO is None:
            raise RuntimeError("RPi.GPIO not available. This must run on a Raspberry Pi.")

        self.pins = pins
        self.callback = callback
        self.current_position: Optional[int] = None
        self._setup_complete = False

    def setup(self) -> None:
        """Configure GPIO pins with pull-down resistors."""
        if self._setup_complete:
            return

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        for pin in self.pins:
            # Configure as input with pull-down resistor
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            logger.debug(f"Configured GPIO {pin} as input with pull-down")

        self._setup_complete = True
        logger.info("GPIO setup complete")

    def read_position(self) -> Optional[int]:
        """
        Read current rotary switch position.

        Returns:
            Position index (0-5) if a position is selected, None if no position is active
        """
        if not self._setup_complete:
            self.setup()

        for index, pin in enumerate(self.pins):
            if GPIO.input(pin) == GPIO.HIGH:
                if self.current_position != index:
                    logger.info(f"Position changed to {index + 1} (GPIO {pin})")
                    self.current_position = index
                    if self.callback:
                        self.callback(index)
                return index

        # No position selected (shouldn't happen with proper hardware, but handle gracefully)
        if self.current_position is not None:
            logger.warning("No GPIO position detected, but previous position was set")
        self.current_position = None
        return None

    def cleanup(self) -> None:
        """Clean up GPIO resources."""
        if self._setup_complete and GPIO:
            GPIO.cleanup()
            self._setup_complete = False
            logger.info("GPIO cleanup complete")

    def __enter__(self):
        """Context manager entry."""
        self.setup()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.cleanup()
