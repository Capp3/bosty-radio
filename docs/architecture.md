# Architecture

System architecture and design decisions for Bosty Radio.

## System Overview

Bosty Radio is a modular, event-driven system that coordinates hardware input (rotary switch), audio playback (MPD), and visual feedback (LED) into a cohesive radio experience.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Rotary Switch                         │
│                  (Hardware Input)                        │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│              GPIO Controller                             │
│         (Position Detection)                             │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│            Radio Controller                              │
│         (Main Coordinator)                               │
└──────┬──────────┬──────────┬──────────┬────────────────┘
       │          │          │          │
       ▼          ▼          ▼          ▼
┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│   Audio  │ │  Morse   │ │Bluetooth │ │  Config  │
│Controller│ │   LED    │ │Controller│ │ Manager  │
└────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘
     │           │            │            │
     ▼           ▼            ▼            ▼
┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│   MPD    │ │   GPIO   │ │  BlueZ   │ │   JSON   │
│   MPC    │ │   LED    │ │ PulseAudio│ │   File  │
└──────────┘ └──────────┘ └──────────┘ └──────────┘
```

## Component Architecture

### Radio Controller (Main Daemon)

**Purpose**: Central coordinator for all components

**Responsibilities**:

- Monitor GPIO for position changes
- Coordinate audio, LED, and Bluetooth
- Manage state transitions
- Handle shutdown gracefully

**Key Design Decisions**:

- **Event-driven**: Responds to GPIO callbacks
- **State machine**: Tracks current position
- **Signal handling**: Graceful shutdown on SIGTERM/SIGINT
- **Error recovery**: Continues operation on component errors

### GPIO Controller

**Purpose**: Read rotary switch position

**Responsibilities**:

- Configure GPIO pins with pull-down resistors
- Poll or detect position changes
- Trigger callbacks on position change
- Clean up resources on shutdown

**Key Design Decisions**:

- **Pull-down resistors**: Internal (software-configured)
- **Callback pattern**: Notifies controller of changes
- **Context manager**: Automatic cleanup
- **Error handling**: Raises if RPi.GPIO unavailable

### Morse LED Controller

**Purpose**: Provide visual feedback via Morse code

**Responsibilities**:

- Encode text to Morse code patterns
- Blink LED according to timing
- Repeat messages continuously
- Show connection status (Bluetooth)

**Key Design Decisions**:

- **Thread-based**: Non-blocking continuous blinking
- **Standard timing**: Follows ITU-R Morse code ratios
- **Repeat mode**: Messages loop until changed
- **State management**: Can switch between blinking and solid

### Audio Controller

**Purpose**: Manage audio playback via MPD

**Responsibilities**:

- Execute MPD/MPC commands
- Play streams and local files
- Control volume
- Play error tones

**Key Design Decisions**:

- **Subprocess-based**: Uses MPC command-line tool
- **Error feedback**: 500Hz tone on failures
- **Status checking**: Verifies playback actually started
- **Volume control**: Software-based via MPC

### Bluetooth Controller

**Purpose**: Manage Bluetooth A2DP sink mode

**Responsibilities**:

- Enable/disable pairing mode
- Monitor connection status
- Switch audio routing
- Play pairing indicators

**Key Design Decisions**:

- **BlueZ-based**: Uses bluetoothctl commands
- **PulseAudio integration**: Routes audio through PulseAudio
- **Status monitoring**: Periodic connection checks
- **No state persistence**: Resets on mode exit

### Configuration Manager

**Purpose**: Load and save configuration

**Responsibilities**:

- Parse JSON configuration files
- Validate configuration data
- Provide defaults
- Handle file I/O errors

**Key Design Decisions**:

- **Pydantic models**: Type-safe configuration
- **Multiple locations**: System and user configs
- **Validation**: Runtime type checking
- **Defaults**: Sensible fallbacks

### TUI (Textual Interface)

**Purpose**: User-friendly configuration interface

**Responsibilities**:

- Display current configuration
- Allow editing of all settings
- Validate input
- Save to JSON file

**Key Design Decisions**:

- **Textual framework**: Modern terminal UI
- **Form-based**: Clear input fields
- **Real-time validation**: Immediate feedback
- **Help text**: Built-in guidance

## Data Flow

### Position Change Flow

```
1. User rotates switch
   ↓
2. GPIO pin goes HIGH
   ↓
3. GPIO Controller detects change
   ↓
4. Callback triggered → Radio Controller
   ↓
5. Radio Controller determines new mode
   ↓
6a. If station (1-5):
    - Stop Bluetooth
    - Start Morse message
    - Play stream/file
   ↓
6b. If Bluetooth (6):
    - Stop audio
    - Start Bluetooth pairing
    - Show Morse/status LED
```

### Audio Playback Flow

```
1. Radio Controller calls Audio Controller
   ↓
2. Audio Controller executes: mpc stop
   ↓
3. Audio Controller executes: mpc clear
   ↓
4. Audio Controller executes: mpc add <url>
   ↓
5. Audio Controller executes: mpc play
   ↓
6. Audio Controller checks: mpc status
   ↓
7a. If playing: Success
   ↓
7b. If failed: Play error tone
```

### Morse Code Flow

```
1. Radio Controller sets message
   ↓
2. Morse LED Controller encodes text
   ↓
3. Background thread starts
   ↓
4. Thread blinks LED according to pattern
   ↓
5. Pattern repeats continuously
   ↓
6. On new message: Stop thread, start new
```

## State Management

### Radio Controller State

```python
current_position: int | None  # 0-5 or None
running: bool                  # Service active
_shutdown_requested: bool      # Graceful shutdown flag
```

### Position States

- **0-4**: Station positions (internet radio)
- **5**: Bluetooth mode
- **None**: No position detected (error state)

### Component States

Each component manages its own state:

- **GPIO**: Current position, setup status
- **Morse LED**: Current message, thread status
- **Audio**: Current URL, playback status
- **Bluetooth**: Pairing mode, connection status

## Error Handling Strategy

### Component-Level Errors

Each component handles its own errors:

- **GPIO**: Raises if hardware unavailable
- **Audio**: Returns False on failure, plays error tone
- **Bluetooth**: Logs errors, continues operation
- **Morse LED**: Gracefully handles thread errors

### System-Level Recovery

Radio Controller:

- **Continues operation** if one component fails
- **Logs all errors** for debugging
- **Attempts recovery** where possible
- **Graceful degradation** (e.g., audio fails but LED works)

### Error Feedback

- **Audio errors**: 500Hz tone
- **Bluetooth**: Ding sound for pairing
- **All errors**: Logged to file and journald

## Concurrency Model

### Threading

- **Main thread**: Radio controller loop
- **Morse LED thread**: Continuous blinking (daemon thread)
- **No other threads**: All other operations are synchronous

### Blocking Operations

- **GPIO reading**: Fast, non-blocking
- **MPC commands**: Blocking but fast (<1s)
- **Bluetooth commands**: Blocking but timeout-protected
- **Sleep**: 0.1s in main loop to prevent busy-waiting

## Configuration System

### Configuration Hierarchy

1. **System config**: `/etc/bosty-radio/config.json` (root)
2. **User config**: `~/.config/bosty-radio/config.json` (user)
3. **Defaults**: Hardcoded in `RadioConfig` model

### Configuration Validation

- **Pydantic models**: Type checking at runtime
- **Field validators**: Range checks, format validation
- **TUI validation**: Pre-save validation
- **Error messages**: Clear feedback on invalid config

## Design Patterns

### Observer Pattern

GPIO Controller uses callbacks to notify Radio Controller of position changes.

### Strategy Pattern

Different audio sources (streams, files, Bluetooth) handled by different strategies.

### Context Manager Pattern

GPIO and LED components support `with` statements for automatic cleanup.

### Factory Pattern

ConfigManager creates RadioConfig instances from JSON or defaults.

## Technology Choices

### Why Python?

- **GPIO libraries**: Excellent RPi.GPIO support
- **Rapid development**: Fast iteration
- **Rich ecosystem**: Many libraries available
- **Cross-platform**: Can develop on non-Pi systems

### Why MPD/MPC?

- **Mature**: Stable, well-tested
- **Reliable**: Handles streaming well
- **Simple**: Command-line interface
- **Standard**: Common on Linux

### Why Textual?

- **Modern**: Rich terminal UI
- **User-friendly**: Better than JSON editing
- **Maintainable**: Python-based
- **Cross-platform**: Works anywhere

### Why Pydantic?

- **Type safety**: Runtime validation
- **JSON**: Easy serialization
- **Documentation**: Auto-generated
- **Modern**: Industry standard

### Why UV?

- **Fast**: Much faster than pip
- **Modern**: Built for Python 3.12+
- **Reliable**: Better dependency resolution
- **Simple**: Single tool

## Performance Considerations

### CPU Usage

- **Minimal**: Main loop sleeps 0.1s
- **Morse LED**: Separate thread, minimal CPU
- **MPC commands**: Fast, non-blocking

### Memory Usage

- **Low**: No large data structures
- **Threads**: Only one background thread
- **Config**: Small JSON file

### Network

- **Streaming**: Depends on stream bitrate
- **MPD**: Efficient streaming
- **Bluetooth**: Minimal network usage

## Security Considerations

### Service Permissions

- **Root required**: For GPIO access (may change with gpio group)
- **File permissions**: Config files readable by service user
- **Network**: No exposed network services

### Input Validation

- **Config validation**: Pydantic ensures type safety
- **URL validation**: Basic format checking
- **File paths**: Relative to Pi filesystem

## Future Considerations

### Potential Improvements

- **Non-root GPIO**: Use gpio group permissions
- **Web interface**: Optional web-based config
- **Stream metadata**: Display song/station info
- **Presets**: Save/load station presets

### Design Constraints

- **No feature creep**: Keep scope focused
- **Simplicity**: Prefer simple solutions
- **Modularity**: Easy to extend
- **Maintainability**: Clear code structure

## Related Documentation

- **[Development Guide](development.md)**: How to contribute
- **[API Reference](api/config.md)**: Detailed API docs
- **[Configuration](configuration.md)**: User configuration guide
