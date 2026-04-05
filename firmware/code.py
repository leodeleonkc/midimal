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

button = digitalio.DigitalInOut(board.D2)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP

last_state = True

while True:
    current_state = button.value

    if last_state and not current_state:
        midi.send(NoteOn(60, 100))
        print("NOTE ON")

    elif not last_state and current_state:
        midi.send(NoteOff(60, 0))
        print("NOTE OFF")

    last_state = current_state
    time.sleep(0.01)