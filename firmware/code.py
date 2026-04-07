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

row_pins = [board.D2, board.D3, board.D4, board.D5]
col_pins = [board.D6, board.D7, board.D8, board.D9]

# Rows = INPUT_PULLUP
rows = []
for pin in row_pins:
    r = digitalio.DigitalInOut(pin)
    r.direction = digitalio.Direction.INPUT
    r.pull = digitalio.Pull.UP
    rows.append(r)

# Columns = OUTPUT
cols = []
for pin in col_pins:
    c = digitalio.DigitalInOut(pin)
    c.direction = digitalio.Direction.OUTPUT
    c.value = True  # idle HIGH
    cols.append(c)

notes = [
    [60, 62, 64, 65],
    [67, 69, 71, 72],
    [74, 76, 77, 79],
    [81, 83, 84, 86],
]

last_states = [
    [False]*4,
    [False]*4,
    [False]*4,
    [False]*4,
]

while True:
    for col_index, col in enumerate(cols):
        col.value = False  # drive column LOW
        time.sleep(0.001)

        for row_index, row in enumerate(rows):
            pressed = not row.value
            note = notes[row_index][col_index]

            if pressed and not last_states[row_index][col_index]:
                midi.send(NoteOn(note, 100))
                print("NOTE ON", note)

            elif not pressed and last_states[row_index][col_index]:
                midi.send(NoteOff(note, 0))
                print("NOTE OFF", note)

            last_states[row_index][col_index] = pressed

        col.value = True  # reset HIGH

    time.sleep(0.001)