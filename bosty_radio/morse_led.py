"""Morse code LED controller."""

import logging
import time
from threading import Event, Thread
from typing import Optional

try:
    import RPi.GPIO as GPIO
except ImportError:
    GPIO = None  # type: ignore

logger = logging.getLogger(__name__)

# Morse code dictionary
MORSE_CODE = {
    "A": ".-",
    "B": "-...",
    "C": "-.-.",
    "D": "-..",
    "E": ".",
    "F": "..-.",
    "G": "--.",
    "H": "....",
    "I": "..",
    "J": ".---",
    "K": "-.-",
    "L": ".-..",
    "M": "--",
    "N": "-.",
    "O": "---",
    "P": ".--.",
    "Q": "--.-",
    "R": ".-.",
    "S": "...",
    "T": "-",
    "U": "..-",
    "V": "...-",
    "W": ".--",
    "X": "-..-",
    "Y": "-.--",
    "Z": "--..",
    "0": "-----",
    "1": ".----",
    "2": "..---",
    "3": "...--",
    "4": "....-",
    "5": ".....",
    "6": "-....",
    "7": "--...",
    "8": "---..",
    "9": "----.",
    ".": ".-.-.-",
    ",": "--..--",
    "?": "..--..",
    " ": " ",  # Space between words
}


class MorseLED:
    """Controls LED for Morse code output with repeat functionality."""

    def __init__(self, pin: int, dot_duration_ms: int = 100):
        """
        Initialize Morse LED controller.

        Args:
            pin: GPIO pin number (BCM) for LED
            dot_duration_ms: Duration of a dot in milliseconds
        """
        if GPIO is None:
            raise RuntimeError("RPi.GPIO not available. This must run on a Raspberry Pi.")

        self.pin = pin
        self.dot_duration = dot_duration_ms / 1000.0  # Convert to seconds
        self.dash_duration = self.dot_duration * 3
        self.element_gap = self.dot_duration  # Gap between dots/dashes
        self.letter_gap = self.dot_duration * 3  # Gap between letters
        self.word_gap = self.dot_duration * 7  # Gap between words

        self._setup_complete = False
        self._stop_event = Event()
        self._thread: Optional[Thread] = None
        self._current_message = ""

    def setup(self) -> None:
        """Configure LED GPIO pin as output."""
        if self._setup_complete:
            return

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(self.pin, GPIO.LOW)
        self._setup_complete = True
        logger.info(f"LED setup complete on GPIO {self.pin}")

    def _text_to_morse(self, text: str) -> str:
        """Convert text to Morse code pattern."""
        morse = []
        for char in text.upper():
            if char in MORSE_CODE:
                morse.append(MORSE_CODE[char])
            elif char == " ":
                morse.append(" ")
        return " ".join(morse)

    def _blink_pattern(self, pattern: str) -> None:
        """Blink LED according to Morse pattern."""
        for element in pattern:
            if element == ".":
                GPIO.output(self.pin, GPIO.HIGH)
                time.sleep(self.dot_duration)
                GPIO.output(self.pin, GPIO.LOW)
                time.sleep(self.element_gap)
            elif element == "-":
                GPIO.output(self.pin, GPIO.HIGH)
                time.sleep(self.dash_duration)
                GPIO.output(self.pin, GPIO.LOW)
                time.sleep(self.element_gap)
            elif element == " ":
                # Letter gap (already have element gap, add more)
                time.sleep(self.letter_gap - self.element_gap)
            else:
                # Word gap
                time.sleep(self.word_gap - self.letter_gap)

    def _blink_loop(self) -> None:
        """Main loop for continuous blinking with repeat."""
        while not self._stop_event.is_set():
            if self._current_message:
                morse_pattern = self._text_to_morse(self._current_message)
                logger.debug(f"Blinking Morse: {self._current_message} -> {morse_pattern}")
                self._blink_pattern(morse_pattern)
                # Gap between message repeats
                time.sleep(self.word_gap)
            else:
                # No message, wait a bit before checking again
                time.sleep(0.1)

    def start_message(self, message: str) -> None:
        """
        Start blinking a Morse code message (repeats continuously).

        Args:
            message: Text message to encode (e.g., "S1", "BT")
        """
        if not self._setup_complete:
            self.setup()

        self._current_message = message
        logger.info(f"Starting Morse message: {message}")

        # Stop any existing thread
        self.stop()

        # Start new thread
        self._stop_event.clear()
        self._thread = Thread(target=self._blink_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stop blinking and turn off LED."""
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)

        if self._setup_complete:
            GPIO.output(self.pin, GPIO.LOW)
        self._current_message = ""
        logger.debug("Morse LED stopped")

    def set_state(self, state: bool) -> None:
        """
        Set LED to on or off (for simple status indication).

        Args:
            state: True for on, False for off
        """
        if not self._setup_complete:
            self.setup()
        GPIO.output(self.pin, GPIO.HIGH if state else GPIO.LOW)

    def cleanup(self) -> None:
        """Clean up GPIO resources."""
        self.stop()
        if self._setup_complete and GPIO:
            GPIO.cleanup(self.pin)
            self._setup_complete = False
            logger.info("Morse LED cleanup complete")

    def __enter__(self):
        """Context manager entry."""
        self.setup()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.cleanup()

