# Development Guide

Guide for developers contributing to Bosty Radio.

## Development Environment Setup

### Prerequisites

- **Python 3.12+**
- **UV package manager**
- **Git**
- **Text editor/IDE** (VS Code, PyCharm, etc.)

### Local Development (Non-Pi Systems)

On macOS or Linux development machines:

```bash
# Clone repository
git clone <repository-url>
cd bosty-radio

# Install UV (if not installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Sync dependencies (RPi.GPIO will be skipped on non-Pi)
uv sync

# Run TUI (will show import warnings for RPi.GPIO, that's OK)
uv run python -m bosty_radio.tui
```

!!! note "RPi.GPIO on Non-Pi Systems"
RPi.GPIO is platform-specific and won't install on macOS/Windows. The code handles this gracefully with try/except blocks. The TUI can be developed and tested without a Pi.

### Raspberry Pi Development

On a Raspberry Pi:

```bash
# Clone repository
git clone <repository-url>
cd bosty-radio

# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Sync dependencies (RPi.GPIO will install)
uv sync --system

# Run full system
uv run python -m bosty_radio.radio_controller
```

## Project Structure

```
bosty-radio/
├── bosty_radio/              # Main Python package
│   ├── __init__.py           # Package initialization
│   ├── config.py             # Configuration management
│   ├── gpio_controller.py     # GPIO input handling
│   ├── morse_led.py          # Morse code LED control
│   ├── audio_controller.py   # MPD/MPC integration
│   ├── bluetooth_controller.py # Bluetooth A2DP sink
│   ├── radio_controller.py   # Main daemon
│   └── tui.py                # Textual configuration TUI
├── systemd/
│   └── bosty-radio.service   # Systemd service file
├── config/
│   └── config.json.example   # Example configuration
├── docs/                      # Documentation (MkDocs)
├── Makefile                   # Build and installation
├── pyproject.toml             # Python project config
└── README.md                  # Project readme
```

## Code Organization

### Module Responsibilities

**`config.py`**

- Configuration data models (Pydantic)
- Configuration file loading/saving
- Validation and defaults

**`gpio_controller.py`**

- GPIO pin setup and reading
- Rotary switch position detection
- Callback handling for position changes

**`morse_led.py`**

- Morse code encoding
- LED blinking patterns
- Thread management for continuous blinking

**`audio_controller.py`**

- MPD/MPC command execution
- Stream playback management
- Error tone generation
- Volume control

**`bluetooth_controller.py`**

- Bluetooth pairing mode
- Connection status monitoring
- Audio sink switching
- Ding sound playback

**`radio_controller.py`**

- Main daemon loop
- Component coordination
- State management
- Signal handling

**`tui.py`**

- Textual UI implementation
- Configuration editing interface
- Validation and saving

## Development Workflow

### Making Changes

1. **Create a branch:**

   ```bash
   git checkout -b feature/my-feature
   ```

2. **Make changes:**

   - Follow code style (see below)
   - Add tests if applicable
   - Update documentation

3. **Test locally:**

   ```bash
   # Run TUI
   uv run python -m bosty_radio.tui

   # Run controller (on Pi only)
   uv run python -m bosty_radio.radio_controller
   ```

4. **Commit changes:**

   ```bash
   git add .
   git commit -m "Description of changes"
   ```

5. **Test on Pi:**
   - Deploy to Raspberry Pi
   - Test with actual hardware
   - Verify service starts correctly

### Code Style

Follow PEP 8 with these specifics:

- **Line length**: 100 characters
- **Type hints**: Use for all function parameters and returns
- **Docstrings**: Google style for classes and functions
- **Imports**: Grouped (stdlib, third-party, local)

Example:

```python
"""Module docstring."""

import logging
from typing import Optional

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class MyClass(BaseModel):
    """Class docstring."""

    def my_method(self, param: str) -> Optional[int]:
        """
        Method docstring.

        Args:
            param: Parameter description

        Returns:
            Return value description
        """
        pass
```

### Formatting

Use Black and Ruff:

```bash
# Format code
uv run black bosty_radio/

# Lint code
uv run ruff check bosty_radio/
```

## Testing

### Manual Testing

**TUI Testing:**

```bash
uv run python -m bosty_radio.tui
```

**Component Testing (on Pi):**

```python
# Test GPIO
from bosty_radio.gpio_controller import GPIOController
controller = GPIOController([2, 3, 4, 17, 27, 22])
controller.setup()
position = controller.read_position()
```

**Integration Testing:**

- Test on actual Raspberry Pi
- Verify all rotary switch positions
- Test Morse code patterns
- Verify audio playback
- Test Bluetooth pairing

### Test Checklist

Before submitting changes:

- [ ] Code follows style guidelines
- [ ] Type hints added
- [ ] Docstrings updated
- [ ] TUI tested locally
- [ ] Hardware tested on Pi (if applicable)
- [ ] Service starts without errors
- [ ] Logs show no errors
- [ ] Documentation updated

## Debugging

### Enable Debug Logging

Edit `radio_controller.py`:

```python
logging.basicConfig(
    level=logging.DEBUG,  # Change from INFO
    ...
)
```

### Common Debugging Tasks

**Check GPIO state:**

```python
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
print(f"GPIO 2: {GPIO.input(2)}")
```

**Test MPD commands:**

```bash
mpc status
mpc play <url>
mpc volume 80
```

**Monitor service:**

```bash
sudo journalctl -u bosty-radio -f
```

## Contributing Guidelines

### Scope

This project maintains a focused scope:

- **Core functionality only**
- **No feature creep**
- **Simplicity over complexity**
- **Modular and maintainable**

### What to Contribute

**Welcome:**

- Bug fixes
- Documentation improvements
- Code quality improvements
- Performance optimizations
- Better error handling

**Please Discuss First:**

- New features
- Major architectural changes
- Additional dependencies
- UI/UX changes

### Pull Request Process

1. **Fork repository**
2. **Create feature branch**
3. **Make changes** (follow style guide)
4. **Test thoroughly**
5. **Update documentation**
6. **Submit PR** with clear description

### Code Review

PRs will be reviewed for:

- Code quality and style
- Functionality and testing
- Documentation updates
- Impact on project scope

## Architecture Decisions

### Why MPD/MPC?

- **Stable**: Mature, well-tested audio system
- **Reliable**: Handles streaming and local files
- **Simple**: Command-line interface via subprocess
- **Standard**: Common on Linux systems

### Why Textual TUI?

- **Modern**: Rich terminal UI framework
- **User-friendly**: Better than editing JSON
- **Cross-platform**: Works on any terminal
- **Maintainable**: Python-based, easy to extend

### Why Pydantic?

- **Type safety**: Runtime validation
- **JSON integration**: Easy serialization
- **Documentation**: Auto-generated from models
- **Modern**: Industry standard for config

### Why UV?

- **Fast**: Much faster than pip
- **Modern**: Built for modern Python
- **Reliable**: Better dependency resolution
- **Simple**: Single tool for package management

## Advanced Development

### Adding New Features

1. **Discuss first**: Open an issue
2. **Design**: Plan the implementation
3. **Implement**: Follow existing patterns
4. **Test**: Thoroughly test on Pi
5. **Document**: Update all relevant docs

### Extending Configuration

To add new config options:

1. **Update `RadioConfig`** in `config.py`
2. **Add to TUI** in `tui.py`
3. **Use in controller** in `radio_controller.py`
4. **Update documentation**

### Adding New Components

To add a new hardware component:

1. **Create new module** (e.g., `new_component.py`)
2. **Follow existing patterns** (setup, cleanup, context manager)
3. **Integrate in `radio_controller.py`**
4. **Add to configuration** if needed
5. **Document in API reference**

## Resources

- **Python 3.12 Docs**: https://docs.python.org/3.12/
- **Textual Docs**: https://textual.textualize.io/
- **Pydantic Docs**: https://docs.pydantic.dev/
- **UV Docs**: https://github.com/astral-sh/uv
- **MPD Docs**: https://www.musicpd.org/doc/html/

## Getting Help

- **Issues**: Open a GitHub issue
- **Discussions**: Use GitHub Discussions
- **Code**: Review existing code for examples

## Next Steps

- **[Architecture](architecture.md)**: Understand system design
- **[API Reference](api/config.md)**: Detailed API documentation
- **Start coding**: Pick an issue or feature
