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

ROOT_NOTE = 60
TRANSPOSE = 0
OCTAVE_SHIFT = 0

# Encoder simulation
sim_left = digitalio.DigitalInOut(board.A0)
sim_left.direction = digitalio.Direction.INPUT
sim_left.pull = digitalio.Pull.UP

sim_right = digitalio.DigitalInOut(board.A1)
sim_right.direction = digitalio.Direction.INPUT
sim_right.pull = digitalio.Pull.UP

sim_hold = digitalio.DigitalInOut(board.A2)
sim_hold.direction = digitalio.Direction.INPUT
sim_hold.pull = digitalio.Pull.UP

# Test note trigger (use D2)
test_button = digitalio.DigitalInOut(board.D2)
test_button.direction = digitalio.Direction.INPUT
test_button.pull = digitalio.Pull.UP

last_button = True

def clamp(value, min_value, max_value):
    return max(min_value, min(max_value, value))

def current_note():
    return ROOT_NOTE + TRANSPOSE + (OCTAVE_SHIFT * 12)

while True:
    hold_active = not sim_hold.value

    if not sim_left.value:
        if hold_active:
            OCTAVE_SHIFT = clamp(OCTAVE_SHIFT - 1, -2, 2)
            print("OCTAVE_SHIFT =", OCTAVE_SHIFT)
        else:
            TRANSPOSE = clamp(TRANSPOSE - 1, -12, 12)
            print("TRANSPOSE =", TRANSPOSE)
        time.sleep(0.25)

    if not sim_right.value:
        if hold_active:
            OCTAVE_SHIFT = clamp(OCTAVE_SHIFT + 1, -2, 2)
            print("OCTAVE_SHIFT =", OCTAVE_SHIFT)
        else:
            TRANSPOSE = clamp(TRANSPOSE + 1, -12, 12)
            print("TRANSPOSE =", TRANSPOSE)
        time.sleep(0.25)

    # Test note trigger
    current_state = test_button.value

    if last_button and not current_state:
        midi.send(NoteOn(current_note(), 100))
        print("NOTE ON", current_note())

    elif not last_button and current_state:
        midi.send(NoteOff(current_note(), 0))
        print("NOTE OFF", current_note())

    last_button = current_state

    time.sleep(0.01)