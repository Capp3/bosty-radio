# Bosty Radio Installation Makefile
# For Raspberry Pi OS (bare install)

.PHONY: help install install-deps install-mpd install-bluetooth install-python install-service configure clean uninstall

# Default target
help:
	@echo "Bosty Radio Installation"
	@echo ""
	@echo "Available commands:"
	@echo "  install          - Full installation (deps, MPD, Bluetooth, Python, service)"
	@echo "  install-deps     - Install system dependencies"
	@echo "  install-mpd      - Install and configure MPD"
	@echo "  install-bluetooth - Install and configure Bluetooth"
	@echo "  install-python   - Install Python package with UV"
	@echo "  install-service  - Install systemd service"
	@echo "  configure        - Run configuration TUI"
	@echo "  clean            - Clean build artifacts"
	@echo "  uninstall        - Remove installation"
	@echo "  help             - Show this help message"

# Full installation
install: install-deps install-mpd install-bluetooth install-python install-service
	@echo ""
	@echo "✓ Installation complete!"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Run 'make configure' to set up your stations"
	@echo "  2. Start the service: sudo systemctl start bosty-radio"
	@echo "  3. Enable on boot: sudo systemctl enable bosty-radio"

# Install system dependencies
install-deps:
	@echo "Installing system dependencies..."
	sudo apt-get update
	sudo apt-get install -y \
		mpd \
		mpc \
		bluez \
		bluez-tools \
		pulseaudio \
		pulseaudio-module-bluetooth \
		sox \
		python3 \
		python3-pip \
		curl \
		sed
	@echo "✓ System dependencies installed"

# Install and configure MPD
install-mpd:
	@echo "Configuring MPD..."
	sudo mkdir -p /var/lib/mpd/playlists
	sudo mkdir -p /var/log/mpd
	sudo mkdir -p /home/pi/music
	sudo chown -R mpd:audio /var/lib/mpd
	sudo chown -R mpd:audio /var/log/mpd
	@echo "✓ MPD configured"
	@echo ""
	@echo "Note: You may need to edit /etc/mpd.conf to set your audio output device"

# Install and configure Bluetooth
install-bluetooth:
	@echo "Configuring Bluetooth..."
	sudo usermod -a -G bluetooth $$USER || true
	sudo systemctl enable bluetooth
	sudo systemctl start bluetooth
	@echo "✓ Bluetooth configured"
	@echo ""
	@echo "Note: Bluetooth audio sink will be configured when switching to position 6"

# Install Python package with UV
install-python:
	@echo "Installing UV package manager..."
	@if ! command -v uv > /dev/null 2>&1; then \
		curl -LsSf https://astral.sh/uv/install.sh | sh; \
		echo "✓ UV installed"; \
	else \
		echo "✓ UV already installed"; \
	fi
	@echo "Installing Python package..."
	uv sync --system
	@echo "✓ Python package installed"

# Install systemd service
install-service:
	@echo "Installing systemd service..."
	sudo mkdir -p /etc/bosty-radio
	sudo mkdir -p /var/log/bosty-radio
	@echo "Updating service file with project path..."
	@sed "s|/home/pi/bosty-radio|$$(pwd)|g" systemd/bosty-radio.service > /tmp/bosty-radio.service
	sudo cp /tmp/bosty-radio.service /etc/systemd/system/bosty-radio.service
	rm /tmp/bosty-radio.service
	sudo systemctl daemon-reload
	@echo "✓ Systemd service installed"

# Run configuration TUI
configure:
	@echo "Starting configuration TUI..."
	uv run python -m bosty_radio.tui

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .venv/
	rm -rf __pycache__/
	find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "✓ Clean complete"

# Uninstall
uninstall:
	@echo "Uninstalling Bosty Radio..."
	sudo systemctl stop bosty-radio || true
	sudo systemctl disable bosty-radio || true
	sudo rm -f /etc/systemd/system/bosty-radio.service
	sudo systemctl daemon-reload
	sudo rm -rf /etc/bosty-radio
	sudo rm -rf /var/log/bosty-radio
	@echo "✓ Uninstalled (Python package and config files remain)"
