# Hardware Setup

This guide covers the hardware components, wiring diagrams, and safety considerations for building your Bosty Radio.

## Components Required

### Essential Components

- **Raspberry Pi 3B** (or compatible)
- **6-Position Rotary Switch** (SP6T single-pole, 6-throw)
- **LED** (any color, standard 5mm or 3mm)
- **Resistor for LED** (220Ω recommended)
- **Jumper wires** (male-to-female for Pi, male-to-male for connections)
- **Breadboard** (optional, for prototyping)

### Audio Output Options

Choose one:

- **3.5mm audio jack** (built into Pi)
- **HDMI audio** (if using HDMI display)
- **USB DAC** (external USB audio device)

## GPIO Pin Mapping

The default GPIO pin assignments are:

| Component                | GPIO Pin (BCM) | Physical Pin | Function          |
| ------------------------ | -------------- | ------------ | ----------------- |
| Rotary Switch Position 1 | GPIO 2         | Pin 3        | Station 1         |
| Rotary Switch Position 2 | GPIO 3         | Pin 5        | Station 2         |
| Rotary Switch Position 3 | GPIO 4         | Pin 7        | Station 3         |
| Rotary Switch Position 4 | GPIO 17        | Pin 11       | Station 4         |
| Rotary Switch Position 5 | GPIO 27        | Pin 13       | Local File        |
| Rotary Switch Position 6 | GPIO 22        | Pin 15       | Bluetooth         |
| LED                      | GPIO 18        | Pin 12       | Morse Code Output |

!!! note "Pin Numbers"
GPIO pin numbers use BCM (Broadcom) numbering, not physical pin numbers. The software configures internal pull-down resistors on all input pins.

## Wiring Diagram

### Rotary Switch Wiring

The rotary switch should be wired so that:

1. **Common terminal** connects to **3.3V** (Pin 1 or Pin 17)
2. **Each position terminal** connects to its respective GPIO pin
3. **Software configures pull-down resistors** on all GPIO pins

```
3.3V (Pin 1) ──┐
               │
               ├── Common (Rotary Switch)
               │
               ├── Position 1 ── GPIO 2 (Pin 3)
               ├── Position 2 ── GPIO 3 (Pin 5)
               ├── Position 3 ── GPIO 4 (Pin 7)
               ├── Position 4 ── GPIO 17 (Pin 11)
               ├── Position 5 ── GPIO 27 (Pin 13)
               └── Position 6 ── GPIO 22 (Pin 15)
```

### LED Wiring

The LED connects to GPIO 18 with a current-limiting resistor:

```
GPIO 18 (Pin 12) ── 220Ω Resistor ── LED Anode (+)
                                            │
                                           LED
                                            │
GND (Pin 6, 9, 14, 20, 25, 30, 34, or 39) ─┘
```

!!! warning "LED Polarity"
LEDs are polarized. The longer leg (anode) connects to the resistor, the shorter leg (cathode) connects to ground.

## Step-by-Step Wiring Instructions

### 1. Power Down the Pi

Always power down and disconnect power before wiring:

```bash
sudo shutdown -h now
# Wait for shutdown, then disconnect power
```

### 2. Wire the Rotary Switch

1. Connect the **common terminal** of the rotary switch to **3.3V** (Pin 1)
2. Connect each position terminal to its GPIO pin:
   - Position 1 → GPIO 2 (Pin 3)
   - Position 2 → GPIO 3 (Pin 5)
   - Position 3 → GPIO 4 (Pin 7)
   - Position 4 → GPIO 17 (Pin 11)
   - Position 5 → GPIO 27 (Pin 13)
   - Position 6 → GPIO 22 (Pin 15)

### 3. Wire the LED

1. Connect one end of a 220Ω resistor to **GPIO 18** (Pin 12)
2. Connect the other end of the resistor to the **LED anode** (longer leg)
3. Connect the **LED cathode** (shorter leg) to **GND** (any ground pin, e.g., Pin 6)

### 4. Verify Connections

Double-check all connections before powering on:

- [ ] Rotary switch common to 3.3V
- [ ] All 6 position terminals to correct GPIO pins
- [ ] LED resistor to GPIO 18
- [ ] LED anode to resistor
- [ ] LED cathode to GND
- [ ] No short circuits
- [ ] No loose connections

### 5. Power On and Test

1. Reconnect power to the Pi
2. SSH into the Pi
3. Test GPIO reading (if you have wiringpi installed):
   ```bash
   gpio readall
   ```
4. Start the service and test:
   ```bash
   sudo systemctl start bosty-radio
   sudo systemctl status bosty-radio
   ```

## Safety Considerations

### Electrical Safety

- **Always power down** before making connections
- **Double-check connections** before powering on
- **Use appropriate resistors** for LED (220Ω recommended)
- **Avoid short circuits** between 3.3V and GND
- **Don't exceed GPIO voltage** (3.3V maximum)

### Physical Safety

- **Secure connections** to prevent shorts
- **Use proper wire gauge** (22-24 AWG for jumper wires)
- **Protect from moisture** if used in humid environments
- **Ensure proper ventilation** for the Pi

### GPIO Protection

- The software uses **internal pull-down resistors** (no external resistors needed for inputs)
- GPIO pins are **3.3V tolerant** (do not connect 5V signals)
- **Maximum current per pin**: 16mA (LED with resistor is safe)

## Troubleshooting Hardware Issues

### LED Not Working

- Check LED polarity (anode/cathode)
- Verify resistor value (220Ω recommended)
- Test with multimeter for continuity
- Try a different GPIO pin to isolate issue

### Rotary Switch Not Detected

- Verify common terminal is connected to 3.3V
- Check each position terminal connection
- Test continuity with multimeter
- Verify GPIO pin assignments in configuration

### False Triggers

- Check for loose connections
- Verify no short circuits
- Ensure proper pull-down configuration
- Check for electrical interference

## Advanced: Custom Pin Mapping

If you need to use different GPIO pins (e.g., due to conflicts), you can change them in the configuration TUI:

1. Run `make configure`
2. Navigate to "GPIO Pins (Advanced)" section
3. Change pin numbers as needed
4. Save configuration
5. Restart service: `sudo systemctl restart bosty-radio`

!!! note "Pin Restrictions"
Some GPIO pins have special functions (I2C, SPI, UART). Avoid using: - GPIO 0, 1 (I2C) - GPIO 7-11 (SPI) - GPIO 14, 15 (UART)

## Enclosure Considerations

If building a permanent installation:

- **Ventilation**: Ensure Pi has adequate airflow
- **Access**: Consider access to SD card and power
- **Mounting**: Secure rotary switch and LED
- **Cable management**: Keep wires organized
- **Strain relief**: Protect connections from stress

## Next Steps

Once hardware is wired:

1. Continue to [Installation](installation.md) if not already installed
2. Run [Configuration](configuration.md) to set up stations
3. Test with [Usage Guide](usage.md)
