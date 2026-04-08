import storage
import supervisor

# Let CircuitPython code write files to CIRCUITPY (commented out for sync_to_board.sh in dev mode)
#storage.remount("/", readonly=False)

# Hide CircuitPython overlays on the OLED/console
supervisor.status_bar.display = False
supervisor.status_bar.console = False

# Optional: stop host filesystem touches from auto-reloading code.py
supervisor.runtime.autoreload = False