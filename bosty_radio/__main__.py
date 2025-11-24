"""Main entry point for bosty_radio package."""

import sys

if __name__ == "__main__":
    # Allow running as: python -m bosty_radio
    # Default to running the controller
    from bosty_radio.radio_controller import main

    main()

