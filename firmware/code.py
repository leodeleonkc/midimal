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

# 2x2 matrix pins
row_pins = [board.D2, board.D3]
col_pins = [board.D6, board.D7]

# MIDI notes for each matrix position
# [row][col]
notes = [
    [60, 62],  # row 0: C, D
    [64, 65],  # row 1: E, F
]

rows = []
cols = []

# Set up rows as outputs, idle HIGH
for pin in row_pins:
    row = digitalio.DigitalInOut(pin)
    row.direction = digitalio.Direction.OUTPUT
    row.value = True
    rows.append(row)

# Set up columns as inputs with pull-up
for pin in col_pins:
    col = digitalio.DigitalInOut(pin)
    col.direction = digitalio.Direction.INPUT
    col.pull = digitalio.Pull.UP
    cols.append(col)

# Track pressed state per matrix position
last_states = [
    [False, False],
    [False, False]
]

while True:
    for r, row in enumerate(rows):
        # Set all rows HIGH first
        for rr in rows:
            rr.value = True

        # Activate current row
        row.value = False

        # Tiny settling delay
        time.sleep(0.001)

        for c, col in enumerate(cols):
            pressed = not col.value
            note = notes[r][c]

            if pressed and not last_states[r][c]:
                midi.send(NoteOn(note, 100))
                print(f"NOTE ON row={r} col={c} note={note}")

            elif not pressed and last_states[r][c]:
                midi.send(NoteOff(note, 0))
                print(f"NOTE OFF row={r} col={c} note={note}")

            last_states[r][c] = pressed

    time.sleep(0.005)