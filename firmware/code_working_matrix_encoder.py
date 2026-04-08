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

# ---------------------------------
# Musical settings
# ---------------------------------
ROOT_NOTE = 60
TRANSPOSE = 0
OCTAVE_SHIFT = 0

# Simple playable layout for now
BASE_NOTES = [
    [0, 2, 4, 5],
    [7, 9, 11, 12],
    [14, 16, 17, 19],
    [21, 23, 24, 26],
]

def clamp(value, min_value, max_value):
    return max(min_value, min(max_value, value))

def current_note(row, col):
    return ROOT_NOTE + BASE_NOTES[row][col] + TRANSPOSE + (OCTAVE_SHIFT * 12)

# ---------------------------------
# Matrix setup
# Current working hardware logic:
# rows = INPUT_PULLUP
# cols = OUTPUT (drive LOW one at a time)
# ---------------------------------
row_pins = [board.D2, board.D3, board.D4, board.D5]
col_pins = [board.D6, board.D7, board.D8, board.D9]

rows = []
for pin in row_pins:
    r = digitalio.DigitalInOut(pin)
    r.direction = digitalio.Direction.INPUT
    r.pull = digitalio.Pull.UP
    rows.append(r)

cols = []
for pin in col_pins:
    c = digitalio.DigitalInOut(pin)
    c.direction = digitalio.Direction.OUTPUT
    c.value = True
    cols.append(c)

last_states = [
    [False, False, False, False],
    [False, False, False, False],
    [False, False, False, False],
    [False, False, False, False],
]

active_notes = [
    [None, None, None, None],
    [None, None, None, None],
    [None, None, None, None],
    [None, None, None, None],
]

# ---------------------------------
# Encoder setup
# ---------------------------------
enc_a = digitalio.DigitalInOut(board.A0)
enc_a.direction = digitalio.Direction.INPUT
enc_a.pull = digitalio.Pull.UP

enc_b = digitalio.DigitalInOut(board.A1)
enc_b.direction = digitalio.Direction.INPUT
enc_b.pull = digitalio.Pull.UP

enc_sw = digitalio.DigitalInOut(board.A2)
enc_sw.direction = digitalio.Direction.INPUT
enc_sw.pull = digitalio.Pull.UP

last_a = enc_a.value

# ---------------------------------
# Main loop
# ---------------------------------
while True:
    # ---- Encoder handling ----
    current_a = enc_a.value
    hold_active = not enc_sw.value

    if last_a and not current_a:  # falling edge
        if enc_b.value:
            direction = -1   # LEFT
        else:
            direction = 1    # RIGHT

        if hold_active:
            OCTAVE_SHIFT = clamp(OCTAVE_SHIFT + direction, -2, 2)
            print("OCTAVE_SHIFT =", OCTAVE_SHIFT)
        else:
            TRANSPOSE = clamp(TRANSPOSE + direction, -12, 12)
            print("TRANSPOSE =", TRANSPOSE)

        time.sleep(0.02)

    last_a = current_a

    # ---- Matrix scan ----
    for col_index, col in enumerate(cols):
        col.value = False
        time.sleep(0.0005)

        for row_index, row in enumerate(rows):
            pressed = not row.value
            note = current_note(row_index, col_index)

            if pressed and not last_states[row_index][col_index]:
                midi.send(NoteOn(note, 100))
                active_notes[row_index][col_index] = note
                print("NOTE ON", note)

            elif not pressed and last_states[row_index][col_index]:
                note_off = active_notes[row_index][col_index]
                if note_off is not None:
                    midi.send(NoteOff(note_off, 0))
                    print("NOTE OFF", note_off)
                active_notes[row_index][col_index] = None

            last_states[row_index][col_index] = pressed

        col.value = True

    time.sleep(0.001)