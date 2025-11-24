# Troubleshooting

Common issues and solutions for Bosty Radio.

## Service Won't Start

### Symptoms

- `systemctl status bosty-radio` shows failed
- Service doesn't appear in process list
- Logs show startup errors

### Solutions

**Check service logs:**

```bash
sudo journalctl -u bosty-radio -n 50
```

**Verify dependencies:**

```bash
# Check MPD is running
systemctl status mpd

# Check Bluetooth is running
systemctl status bluetooth

# Check Python/UV
uv --version
python3 --version
```

**Check configuration file:**

```bash
# Verify config exists
ls -l /etc/bosty-radio/config.json
# or
ls -l ~/.config/bosty-radio/config.json

# Test JSON syntax
python3 -m json.tool /etc/bosty-radio/config.json
```

**Check GPIO permissions:**

- Service may need to run as root for GPIO access
- Verify service file user/group settings

**Reinstall service:**

```bash
make install-service
sudo systemctl daemon-reload
sudo systemctl start bosty-radio
```

## No Audio Output

### Symptoms

- Service running but no sound
- LED blinking but no audio
- Stream appears to play but silent

### Solutions

**Check MPD status:**

```bash
mpc status
```

**Verify audio device:**

```bash
# List audio devices
aplay -l

# Test audio directly
aplay /usr/share/sounds/alsa/Front_Left.wav
```

**Check MPD configuration:**

```bash
sudo nano /etc/mpd.conf
```

Verify `audio_output` section matches your hardware:

- **3.5mm jack**: Use ALSA with `hw:0,0`
- **HDMI**: Use ALSA with `hw:1,0` or `hw:1,7`
- **USB DAC**: Use ALSA with appropriate device

**Test MPD directly:**

```bash
# Add and play a test stream
mpc add http://stream.example.com:8000/radio
mpc play
mpc volume 80
```

**Check volume:**

```bash
# Check current volume
mpc volume

# Set volume
mpc volume 80

# Check system volume (if using ALSA)
alsamixer
```

**Restart MPD:**

```bash
sudo systemctl restart mpd
```

## GPIO Not Detecting Switch

### Symptoms

- Switch rotation doesn't change stations
- Service logs show no position changes
- LED doesn't respond to switch

### Solutions

**Verify wiring:**

- Check common terminal connected to 3.3V
- Verify each position terminal to correct GPIO pin
- Check for loose connections
- Test continuity with multimeter

**Check GPIO pins:**

```bash
# If wiringpi installed
gpio readall

# Check pin states
gpio read 2
gpio read 3
# ... etc
```

**Verify configuration:**

```bash
# Check GPIO pin assignments
make configure
# Navigate to "GPIO Pins (Advanced)" section
```

**Test GPIO manually:**

```bash
# Python test script
python3 << EOF
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
print(f"GPIO 2: {GPIO.input(2)}")
GPIO.cleanup()
EOF
```

**Check for pin conflicts:**

- Some GPIO pins have special functions (I2C, SPI, UART)
- Avoid using GPIO 0, 1, 7-11, 14, 15 if possible
- Check `/boot/config.txt` for pin usage

**Verify pull-down resistors:**

- Software configures internal pull-downs
- If using external resistors, ensure correct values
- Check for short circuits

## Bluetooth Not Working

### Symptoms

- Position 6 doesn't enable pairing
- Device can't find Pi
- Audio doesn't route through Pi

### Solutions

**Check Bluetooth service:**

```bash
systemctl status bluetooth
sudo systemctl start bluetooth
```

**Verify Bluetooth hardware:**

```bash
# Check if Bluetooth adapter is present
hciconfig

# Check adapter status
bluetoothctl show
```

**Enable pairing manually:**

```bash
bluetoothctl
power on
discoverable on
pairable on
```

**Check audio routing:**

```bash
# List audio sinks
pactl list sinks

# Set default sink to Bluetooth
pactl set-default-sink bluez_sink.XX_XX_XX_XX_XX_XX
```

**Check PulseAudio:**

```bash
# Restart PulseAudio
pulseaudio -k
pulseaudio --start

# Check modules
pactl list modules | grep bluetooth
```

**Verify user permissions:**

```bash
# Add user to bluetooth group
sudo usermod -a -G bluetooth $USER
# Log out and back in
```

## Stream Fails to Play

### Symptoms

- 500Hz error tone plays
- Service logs show stream errors
- Station configured but no audio

### Solutions

**Test stream URL manually:**

```bash
mpc add http://stream.example.com:8000/radio
mpc play
mpc status
```

**Check network connection:**

```bash
# Test internet
ping -c 3 8.8.8.8

# Test DNS
nslookup stream.example.com

# Test stream URL
curl -I http://stream.example.com:8000/radio
```

**Verify URL format:**

- Must start with `http://` or `https://`
- Check for typos in URL
- Some streams require specific user-agent

**Check MPD playlist:**

```bash
# View current playlist
mpc playlist

# Clear and retry
mpc clear
mpc add <url>
mpc play
```

**Check firewall:**

```bash
# If using firewall, allow MPD
sudo ufw allow 6600
```

## LED Not Working

### Symptoms

- LED doesn't blink
- No Morse code feedback
- LED stays off or on constantly

### Solutions

**Check wiring:**

- Verify LED anode (long leg) to resistor to GPIO 18
- Verify LED cathode (short leg) to GND
- Check resistor value (220Ω recommended)
- Test LED polarity (try reversing)

**Test LED manually:**

```bash
# Python test
python3 << EOF
import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.OUT)
GPIO.output(18, GPIO.HIGH)
time.sleep(1)
GPIO.output(18, GPIO.LOW)
GPIO.cleanup()
EOF
```

**Check GPIO pin in configuration:**

```bash
# Verify LED pin assignment
make configure
# Check "GPIO Pins (Advanced)" → "LED"
```

**Check service logs:**

```bash
sudo journalctl -u bosty-radio | grep -i led
```

**Verify LED is not burned out:**

- Test with multimeter
- Try different LED
- Check current limiting resistor

## Configuration Issues

### Symptoms

- TUI won't start
- Configuration not saving
- Changes not applied

### Solutions

**TUI startup errors:**

```bash
# Check Python version
python3 --version  # Needs 3.12+

# Check UV
uv --version

# Reinstall dependencies
uv sync --system
```

**Permission errors:**

```bash
# Check file permissions
ls -l /etc/bosty-radio/config.json
ls -l ~/.config/bosty-radio/config.json

# Fix permissions if needed
sudo chmod 644 /etc/bosty-radio/config.json
sudo chown root:root /etc/bosty-radio/config.json
```

**JSON syntax errors:**

```bash
# Validate JSON
python3 -m json.tool /etc/bosty-radio/config.json
```

**Changes not applying:**

- Restart service after config changes: `sudo systemctl restart bosty-radio`
- Check logs for validation errors
- Verify config file location

## Performance Issues

### Symptoms

- Slow response to switch changes
- Audio stuttering
- High CPU usage

### Solutions

**Check system resources:**

```bash
# CPU and memory
top
htop

# Disk I/O
iostat
```

**Check network:**

```bash
# Network speed
speedtest-cli

# Connection quality
ping -c 10 stream.example.com
```

**Optimize SD card:**

- Use Class 10 or better SD card
- Consider using USB drive for OS
- Enable TRIM if supported

**Reduce stream bitrate:**

- Use lower quality streams
- Prefer 128kbps over 320kbps
- Use local files when possible

## Getting Help

### Log Files

**Service logs:**

```bash
sudo journalctl -u bosty-radio -f
```

**Application logs:**

```bash
tail -f /var/log/bosty-radio/controller.log
```

**MPD logs:**

```bash
sudo journalctl -u mpd -f
```

### Diagnostic Information

Collect system info:

```bash
# System info
uname -a
cat /etc/os-release

# Python version
python3 --version

# Service status
systemctl status bosty-radio mpd bluetooth

# GPIO info
gpio readall  # if wiringpi installed
```

### Common Error Messages

**"RPi.GPIO not available"**

- Normal on non-Pi systems
- On Pi: `uv sync --system` to install

**"MPC command failed"**

- Check MPD is running
- Verify MPD configuration
- Test with `mpc status`

**"Config file not found"**

- Run `make configure` to create
- Check file permissions
- Verify path in logs

## Prevention

### Best Practices

1. **Regular updates**: Keep system and packages updated
2. **Backup config**: Save config file before major changes
3. **Test streams**: Verify URLs before configuring
4. **Monitor logs**: Check logs periodically
5. **Stable power**: Use official Pi power supply
6. **Quality SD card**: Use Class 10 or better
7. **Wired network**: Use ethernet for streaming when possible

### Maintenance

```bash
# Weekly: Check service status
sudo systemctl status bosty-radio

# Monthly: Update system
sudo apt-get update && sudo apt-get upgrade

# As needed: Check logs
sudo journalctl -u bosty-radio --since "1 week ago"
```

## Still Having Issues?

If problems persist:

1. Review all relevant logs
2. Check hardware connections
3. Verify all configurations
4. Test components individually
5. Consult [Development Guide](development.md) for advanced debugging
