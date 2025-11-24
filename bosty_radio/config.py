"""Configuration management for Bosty Radio."""

import json
import logging
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger(__name__)

# Default configuration file location
DEFAULT_CONFIG_PATH = Path("/etc/bosty-radio/config.json")
USER_CONFIG_PATH = Path.home() / ".config" / "bosty-radio" / "config.json"


class StationConfig(BaseModel):
    """Configuration for a single station/position."""

    url: str = Field(..., description="Stream URL or file path")
    morse_message: str = Field(..., description="Morse code message (e.g., 'S1', 'BT')")
    name: Optional[str] = Field(None, description="Human-readable station name")


class GPIOConfig(BaseModel):
    """GPIO pin configuration."""

    position_1: int = Field(2, description="GPIO pin for position 1 (BCM)")
    position_2: int = Field(3, description="GPIO pin for position 2 (BCM)")
    position_3: int = Field(4, description="GPIO pin for position 3 (BCM)")
    position_4: int = Field(17, description="GPIO pin for position 4 (BCM)")
    position_5: int = Field(27, description="GPIO pin for position 5 (BCM)")
    position_6: int = Field(22, description="GPIO pin for position 6 (BCM)")
    led: int = Field(18, description="GPIO pin for LED (BCM)")

    @field_validator(
        "position_1", "position_2", "position_3", "position_4", "position_5", "position_6", "led"
    )
    @classmethod
    def validate_pin(cls, v: int) -> int:
        """Validate GPIO pin number is in valid range."""
        if not 2 <= v <= 27:
            raise ValueError(f"GPIO pin {v} is not in valid range (2-27)")
        return v


class RadioConfig(BaseModel):
    """Main configuration model for Bosty Radio."""

    stations: List[StationConfig] = Field(
        default_factory=lambda: [
            StationConfig(url="", morse_message="S1"),
            StationConfig(url="", morse_message="S2"),
            StationConfig(url="", morse_message="S3"),
            StationConfig(url="", morse_message="S4"),
            StationConfig(url="", morse_message="F1"),  # File
        ],
        description="Station configurations for positions 1-5",
    )
    bluetooth_morse: str = Field("BT", description="Morse code message for Bluetooth mode")
    morse_dot_duration_ms: int = Field(
        100, ge=50, le=500, description="Morse code dot duration in milliseconds"
    )
    gpio: GPIOConfig = Field(default_factory=GPIOConfig, description="GPIO pin configuration")
    volume: int = Field(80, ge=0, le=100, description="Default volume level (0-100)")
    error_tone_frequency_hz: int = Field(
        500, ge=200, le=2000, description="Error tone frequency in Hz"
    )

    @field_validator("stations")
    @classmethod
    def validate_stations(cls, v: List[StationConfig]) -> List[StationConfig]:
        """Ensure exactly 5 stations for positions 1-5."""
        if len(v) != 5:
            raise ValueError(f"Must have exactly 5 stations, got {len(v)}")
        return v


class ConfigManager:
    """Manages loading and saving configuration."""

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize config manager with optional custom path."""
        self.config_path = config_path or self._find_config_file()
        self._config: Optional[RadioConfig] = None

    def _find_config_file(self) -> Path:
        """Find the configuration file, checking system and user locations."""
        # Check system location first
        if DEFAULT_CONFIG_PATH.exists():
            return DEFAULT_CONFIG_PATH
        # Fall back to user location
        if USER_CONFIG_PATH.exists():
            return USER_CONFIG_PATH
        # Default to user location for new configs
        return USER_CONFIG_PATH

    def load(self) -> RadioConfig:
        """Load configuration from file."""
        if self._config is not None:
            return self._config

        if not self.config_path.exists():
            logger.info(f"Config file not found at {self.config_path}, using defaults")
            self._config = RadioConfig()
            return self._config

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._config = RadioConfig(**data)
            logger.info(f"Loaded configuration from {self.config_path}")
            return self._config
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Error loading config: {e}, using defaults")
            self._config = RadioConfig()
            return self._config

    def save(self, config: RadioConfig) -> None:
        """Save configuration to file."""
        # Ensure directory exists
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(config.model_dump(mode="json"), f, indent=2, ensure_ascii=False)
            self._config = config
            logger.info(f"Saved configuration to {self.config_path}")
        except (IOError, OSError) as e:
            logger.error(f"Error saving config: {e}")
            raise

    def get_config(self) -> RadioConfig:
        """Get current configuration, loading if necessary."""
        if self._config is None:
            return self.load()
        return self._config

    def reload(self) -> RadioConfig:
        """Force reload configuration from file."""
        self._config = None
        return self.load()
