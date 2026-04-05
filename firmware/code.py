import time
import usb_midi
import adafruit_midi
from adafruit_midi.note_on import NoteOn
from adafruit_midi.note_off import NoteOff

midi = adafruit_midi.MIDI(midi_out=usb_midi.ports[1], out_channel=0)

while True:
    midi.send(NoteOn(60, 100))
    time.sleep(0.5)
    midi.send(NoteOff(60, 0))
    time.sleep(0.5)