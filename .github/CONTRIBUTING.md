# Contributing to Bosty Radio

Thank you for your interest in contributing to Bosty Radio! This document provides guidelines and instructions for contributing.

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

## Project Philosophy

Bosty Radio follows a philosophy of simplicity and focus:

- **No feature creep**: Core functionality only
- **Simplicity over complexity**: Prefer simple, maintainable solutions
- **Modular design**: Clean separation of concerns
- **User-friendly**: Simple configuration, clear feedback

When contributing, please keep these principles in mind.

## How to Contribute

### Reporting Bugs

Before reporting a bug:

1. Check if the issue already exists
2. Verify it's not a configuration issue
3. Test on a Raspberry Pi (if hardware-related)

When reporting:

- Use a clear, descriptive title
- Describe the steps to reproduce
- Include relevant logs
- Specify your hardware (Pi model, OS version)
- Include Python version: `python3 --version`

### Suggesting Features

Before suggesting a feature:

1. Check if it aligns with project scope
2. Consider if it adds unnecessary complexity
3. Think about maintainability

Feature requests should:

- Clearly describe the use case
- Explain why it's needed
- Consider alternatives
- Keep scope focused

### Pull Requests

#### Before Submitting

1. **Fork the repository**
2. **Create a branch**: `git checkout -b feature/my-feature` or `fix/my-bug`
3. **Follow code style**: Use Black and Ruff
4. **Add tests**: If applicable
5. **Update documentation**: If needed
6. **Test on Raspberry Pi**: For hardware-related changes

#### Code Style

- **Python**: Follow PEP 8, 100 character line length
- **Type hints**: Use for all functions
- **Docstrings**: Google style for classes and functions
- **Formatting**: Use Black
- **Linting**: Use Ruff

```bash
# Format code
uv run black bosty_radio/

# Lint code
uv run ruff check bosty_radio/
```

#### Commit Messages

Use clear, descriptive commit messages:

```
Short summary (50 chars or less)

More detailed explanation if needed. Wrap to 72 characters.
Explain what and why, not how.

- Bullet points are okay
- Use present tense: "Add feature" not "Added feature"
```

#### Pull Request Process

1. **Update documentation** if needed
2. **Add tests** if applicable
3. **Ensure all checks pass**
4. **Request review** from maintainers
5. **Address feedback** promptly

#### What to Include

- Clear description of changes
- Reference to related issues
- Testing instructions
- Screenshots (for UI changes)
- Documentation updates

## Development Setup

### Prerequisites

- Python 3.12+
- UV package manager
- Git
- Raspberry Pi (for hardware testing)

### Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/bosty-radio.git
cd bosty-radio

# Install UV (if not installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Sync dependencies
uv sync

# Run TUI (for testing)
uv run python -m bosty_radio.tui
```

### Testing

Test your changes:

- **TUI**: Test configuration interface
- **Hardware**: Test on Raspberry Pi if applicable
- **Service**: Test systemd service startup
- **Integration**: Test full system operation

## Development Guidelines

### Adding Features

1. **Discuss first**: Open an issue before major changes
2. **Keep it simple**: Prefer simple solutions
3. **Stay focused**: Don't expand scope
4. **Document**: Update relevant documentation
5. **Test**: Test thoroughly on Pi

### Modifying Configuration

If adding new config options:

1. Update `RadioConfig` in `config.py`
2. Add to TUI in `tui.py`
3. Use in controller if needed
4. Update documentation
5. Add to example config

### Adding Components

If adding new hardware components:

1. Create new module (e.g., `new_component.py`)
2. Follow existing patterns
3. Integrate in `radio_controller.py`
4. Add to configuration if needed
5. Document in API reference

### Code Organization

- **One module per component**: Keep modules focused
- **Clear interfaces**: Well-defined APIs
- **Error handling**: Graceful degradation
- **Logging**: Appropriate log levels
- **Type hints**: All functions

## Documentation

### User Documentation

Located in `docs/`:

- Update relevant pages when adding features
- Add examples for new functionality
- Update troubleshooting if needed

### API Documentation

Located in `docs/api/`:

- Update API docs when changing interfaces
- Include examples
- Document parameters and returns

### Code Comments

- Use docstrings for all public functions/classes
- Add inline comments for complex logic
- Keep comments up-to-date

## Review Process

### What Reviewers Look For

- **Code quality**: Style, clarity, maintainability
- **Functionality**: Works as intended
- **Testing**: Adequate test coverage
- **Documentation**: Updated and clear
- **Scope**: Aligns with project goals

### Responding to Feedback

- **Be open**: Accept constructive criticism
- **Be responsive**: Address feedback promptly
- **Be collaborative**: Work together to improve

## Questions?

- **Open an issue**: For questions or discussions
- **Check documentation**: May already have answers
- **Review existing code**: Learn from examples

## Recognition

Contributors will be:

- Listed in project documentation
- Credited in release notes
- Appreciated by the community

Thank you for contributing to Bosty Radio!

