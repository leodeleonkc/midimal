# import storage
# import supervisor
# import usb_cdc
# import usb_midi

# usb_cdc.disable()   # disable serial / REPL over USB
# usb_midi.enable()   # MIDI is normally already enabled, but explicit is fine

# # Let CircuitPython code write files to CIRCUITPY (commented out for sync_to_board.sh in dev mode)
# #storage.remount("/", readonly=False)

# # Hide CircuitPython overlays on the OLED/console
# supervisor.status_bar.display = False
# supervisor.status_bar.console = False

# # Optional: stop host filesystem touches from auto-reloading code.py
# supervisor.runtime.autoreload = False

import board  # pyright: ignore[reportMissingImports]
import digitalio  # pyright: ignore[reportMissingImports]
import storage  # pyright: ignore[reportMissingImports]
import usb_cdc  # pyright: ignore[reportMissingImports]
import usb_midi  # pyright: ignore[reportMissingImports]
import supervisor  # pyright: ignore[reportMissingImports]

supervisor.set_usb_identification(manufacturer="Leo de Leon", product="MIDIMAL")

enc_sw = digitalio.DigitalInOut(board.A2)
enc_sw.direction = digitalio.Direction.INPUT
enc_sw.pull = digitalio.Pull.UP

maintenance_mode = not enc_sw.value  # hold encoder during boot

usb_midi.enable()

if maintenance_mode:
    usb_cdc.enable()
else:
    usb_cdc.disable()
    storage.disable_usb_drive()
