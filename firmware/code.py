import time
import board
import digitalio
import usb_midi
import adafruit_midi
from adafruit_midi.note_on import NoteOn
from adafruit_midi.note_off import NoteOff

midi = adafruit_midi.MIDI(
    midi_out=usb_midi.ports[1],
    out_channel=0
)

# Four direct input pins
pins = [board.D2, board.D3, board.D4, board.D5]
notes = [60, 62, 64, 65]  # C, D, E, F

buttons = []
last_states = []

for pin in pins:
    btn = digitalio.DigitalInOut(pin)
    btn.direction = digitalio.Direction.INPUT
    btn.pull = digitalio.Pull.UP
    buttons.append(btn)
    last_states.append(True)

while True:
    for i, button in enumerate(buttons):
        current_state = button.value

        if last_states[i] and not current_state:
            midi.send(NoteOn(notes[i], 100))
            print(f"NOTE ON {notes[i]}")

        elif not last_states[i] and current_state:
            midi.send(NoteOff(notes[i], 0))
            print(f"NOTE OFF {notes[i]}")

        last_states[i] = current_state

    time.sleep(0.01)