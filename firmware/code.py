import time
import json
import board
import neopixel
import digitalio
import usb_midi
import adafruit_midi
import displayio
import terminalio
import os
from fourwire import FourWire
from adafruit_display_text import label
import adafruit_displayio_sh1106
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
IDLE_TIMEOUT = 600  # seconds
chord_mode = False

last_activity_time = time.monotonic()
display_on = True

SCALE_ORDER = ["major", "minor", "pentatonic", "blues"]
SCALES = {
    "major":      [0, 2, 4, 5, 7, 9, 11],
    "minor":      [0, 2, 3, 5, 7, 8, 10],
    "pentatonic": [0, 2, 4, 7, 9],
    "blues":      [0, 3, 5, 6, 7, 10],
}

DISPLAY_SCALE_NAMES = {
    "major": "Major",
    "minor": "Minor",
    "pentatonic": "Pentatonic",
    "blues": "Blues",
}

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

def root_note_name():
    return NOTE_NAMES[ROOT_NOTE % 12]

SETTINGS_FILE = "/midimal_settings.json"
SETTINGS_SAVE_DELAY = 0.4

settings_dirty = False
settings_save_at = 0

def mark_settings_dirty():
    global settings_dirty, settings_save_at
    settings_dirty = True
    settings_save_at = time.monotonic() + SETTINGS_SAVE_DELAY

def save_settings():
    global settings_dirty

    data = {
        "root_note": ROOT_NOTE,
        "scale_index": active_scale_index,
        "transpose": TRANSPOSE,
        "octave_shift": OCTAVE_SHIFT,
        "chord_mode": chord_mode,
    }

    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(data, f)
        settings_dirty = False
    except OSError as e:
        print("SAVE SETTINGS DISABLED:", e)
        settings_dirty = False
    except Exception as e:
        print("SAVE SETTINGS ERROR:", e)
        settings_dirty = False

def load_settings():
    global ROOT_NOTE, active_scale_index, TRANSPOSE, OCTAVE_SHIFT, chord_mode

    try:
        with open(SETTINGS_FILE, "r") as f:
            data = json.load(f)

        ROOT_NOTE = int(data.get("root_note", 60))
        active_scale_index = clamp(int(data.get("scale_index", 2)), 0, len(SCALE_ORDER) - 1)
        TRANSPOSE = clamp(int(data.get("transpose", 0)), -12, 12)
        OCTAVE_SHIFT = clamp(int(data.get("octave_shift", 0)), -2, 2)
        chord_mode = bool(data.get("chord_mode", False))

        print("SETTINGS LOADED")
    except OSError:
        print("No saved settings found, using defaults")
    except Exception as e:
        print("LOAD SETTINGS ERROR:", e)

def shift_root(direction):
    global ROOT_NOTE
    ROOT_NOTE = 60 + ((ROOT_NOTE - 60 + direction) % 12)
    print("ROOT_NOTE =", root_note_name(), ROOT_NOTE)
    mark_settings_dirty()
    update_display()

def reset_to_defaults():
    global ROOT_NOTE, active_scale_index, TRANSPOSE, OCTAVE_SHIFT, chord_mode

    ROOT_NOTE = 60
    active_scale_index = 2   # pentatonic
    TRANSPOSE = 0
    OCTAVE_SHIFT = 0
    chord_mode = False

    print("RESET TO DEFAULTS")
    mark_settings_dirty()
    update_display()

def toggle_chord_mode():
    global chord_mode
    chord_mode = not chord_mode
    print("CHORD_MODE =", chord_mode)
    mark_settings_dirty()
    update_display()

active_scale_index = 2  # pentatonic default
LONG_PRESS_TIME = 0.45

def active_scale_name():
    return SCALE_ORDER[active_scale_index]

def clamp(value, min_value, max_value):
    return max(min_value, min(max_value, value))

def get_scale_note(index):
    scale = SCALES[active_scale_name()]
    scale_len = len(scale)
    octave = index // scale_len
    degree = index % scale_len
    return ROOT_NOTE + scale[degree] + (octave * 12) + TRANSPOSE + (OCTAVE_SHIFT * 12)

def get_chord_notes(index):
    return [
        get_scale_note(index),
        get_scale_note(index + 2),
        get_scale_note(index + 4),
    ]

def current_notes(row, col):
    note_index = (row * 4) + col
    if chord_mode:
        return get_chord_notes(note_index)
    return [get_scale_note(note_index)]

def mark_activity():
    global last_activity_time, display_on
    last_activity_time = time.monotonic()

    if not display_on:
        display.root_group = splash
        display_on = True

def check_idle():
    global display_on

    if display_on and (time.monotonic() - last_activity_time > IDLE_TIMEOUT):
        display.root_group = None
        display_on = False

# ---------------------------------
# OLED setup
# ---------------------------------
displayio.release_displays()

spi = board.SPI()

display_bus = FourWire(
    spi,
    command=board.D0,      # DC
    chip_select=board.D1,  # CS
    reset=board.D10,       # RES
    baudrate=1000000
)

display = adafruit_displayio_sh1106.SH1106(
    display_bus,
    width=132,
    height=64,
    rotation=0
)

def show_startup_splash():
    if not ("midimal_splash_a.bmp" in os.listdir("/") and "midimal_splash_b.bmp" in os.listdir("/")):
        print("Splash BMP files not found")
        return

    print("Showing startup splash")

    splash_group = displayio.Group()

    bmp_a = displayio.OnDiskBitmap("/midimal_splash_a.bmp")
    tile_a = displayio.TileGrid(bmp_a, pixel_shader=bmp_a.pixel_shader)

    bmp_b = displayio.OnDiskBitmap("/midimal_splash_b.bmp")
    tile_b = displayio.TileGrid(bmp_b, pixel_shader=bmp_b.pixel_shader)

    splash_group.append(tile_a)
    display.root_group = splash_group
    time.sleep(0.40)

    splash_group.pop()
    splash_group.append(tile_b)
    display.root_group = splash_group
    time.sleep(0.28)

    splash_group.pop()
    splash_group.append(tile_a)
    display.root_group = splash_group
    time.sleep(0.28)

    splash_group.pop()
    splash_group.append(tile_b)
    display.root_group = splash_group
    time.sleep(0.28)

    splash_group.pop()
    splash_group.append(tile_a)
    display.root_group = splash_group
    time.sleep(0.28)

    splash_group.pop()
    splash_group.append(tile_b)
    display.root_group = splash_group
    time.sleep(0.28)

    splash_group.pop()
    splash_group.append(tile_a)
    display.root_group = splash_group
    time.sleep(0.55)

DISPLAY_X_OFFSET = 0
VISIBLE_W = 128
VISIBLE_H = 64

# HUD drawing surface
hud_bitmap = displayio.Bitmap(132, 64, 2)
hud_palette = displayio.Palette(2)
hud_palette[0] = 0x000000  # black
hud_palette[1] = 0xFFFFFF  # white

hud_bg = displayio.TileGrid(hud_bitmap, pixel_shader=hud_palette)
splash = displayio.Group(x=DISPLAY_X_OFFSET, y=0)
splash.append(hud_bg)

def draw_rect(bitmap, x, y, w, h, color):
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            if 0 <= xx < 132 and 0 <= yy < 64:
                bitmap[xx, yy] = color

def draw_hline(bitmap, x, y, w, color, dotted=False):
    for xx in range(x, x + w):
        if 0 <= xx < 132 and 0 <= y < 64:
            if not dotted or (xx % 3 != 1):
                bitmap[xx, y] = color

def draw_vline(bitmap, x, y, h, color, dotted=False):
    for yy in range(y, y + h):
        if 0 <= x < 132 and 0 <= yy < 64:
            if not dotted or (yy % 3 != 1):
                bitmap[x, yy] = color

def draw_static_hud():
    draw_rect(hud_bitmap, 0, 0, 132, 64, 0)

    # Draw only inside visible 128px area
    left = 2
    top = 2
    right = 125
    bottom = 61

    # Outer border
    draw_hline(hud_bitmap, left, top, right - left + 1, 1)
    draw_hline(hud_bitmap, left, bottom, right - left + 1, 1)
    draw_vline(hud_bitmap, left, top, bottom - top + 1, 1)
    draw_vline(hud_bitmap, right, top, bottom - top + 1, 1)

    # Divider lines
    draw_hline(hud_bitmap, 10, 24, 108, 1, dotted=True)

    # Center divider with balanced spacing
    draw_vline(hud_bitmap, 57, 30, 24, 1, dotted=True)

draw_static_hud()

# Top scale text
scale_label = label.Label(
    terminalio.FONT,
    text="PENTATONIC",
    color=0xFFFFFF
)
splash.append(scale_label)

scale_arrow = label.Label(
    terminalio.FONT,
    text="",
    color=0xFFFFFF,
    x=12,
    y=14
)
splash.append(scale_arrow)

chord_label = label.Label(
    terminalio.FONT,
    text=" c ",
    color=0x000000,
    x=0,
    y=12,
    background_color=0xFFFFFF
)
splash.append(chord_label)

# Section labels
octave_title = label.Label(
    terminalio.FONT,
    text="OCTAVE",
    color=0xFFFFFF,
    x=14,
    y=35
)
splash.append(octave_title)

transpose_title = label.Label(
    terminalio.FONT,
    text="TRANSPOSE",
    color=0xFFFFFF,
    x=65,
    y=35
)
splash.append(transpose_title)

# Values
octave_value = label.Label(
    terminalio.FONT,
    text="+0",
    color=0xFFFFFF,
    x=20,
    y=49
)
splash.append(octave_value)

octave_arrow = label.Label(
    terminalio.FONT,
    text="",
    color=0xFFFFFF,
    x=10,
    y=49
)
splash.append(octave_arrow)

transpose_value = label.Label(
    terminalio.FONT,
    text="+0",
    color=0xFFFFFF,
    x=72,
    y=49
)
splash.append(transpose_value)

transpose_arrow = label.Label(
    terminalio.FONT,
    text="",
    color=0xFFFFFF,
    x=60,
    y=49
)
splash.append(transpose_arrow)

show_startup_splash()
display.root_group = splash

last_display_scale = None
last_display_transpose = None
last_display_octave = None
last_display_scale_mode = None
last_display_octave_active = None
last_display_transpose_active = None
last_display_chord_mode = None

scale_mode = False
octave_adjust_active = False
transpose_indicator_until = 0

def update_display(force=False):
    global last_display_scale
    global last_display_transpose
    global last_display_octave
    global last_display_scale_mode
    global last_display_octave_active
    global last_display_transpose_active
    global last_display_chord_mode
    global chord_mode

    base_scale_name = DISPLAY_SCALE_NAMES[active_scale_name()].upper()
    scale_text = f"{root_note_name()} {base_scale_name}"
    transpose_text = f"{TRANSPOSE:+d}"
    octave_text = f"{OCTAVE_SHIFT:+d}"

    # Normal rotate changes octave, so the timed indicator belongs to octave.
    octave_active = time.monotonic() < transpose_indicator_until

    # Click + rotate changes transpose, so the held-session indicator belongs to transpose.
    transpose_active = octave_adjust_active

    if (
        force
        or scale_text != last_display_scale
        or TRANSPOSE != last_display_transpose
        or OCTAVE_SHIFT != last_display_octave
        or scale_mode != last_display_scale_mode
        or octave_active != last_display_octave_active
        or transpose_active != last_display_transpose_active
        or chord_mode != last_display_chord_mode
    ):
        scale_label.text = scale_text
        scale_label.x = (VISIBLE_W - (len(scale_text) * 6)) // 2
        scale_label.y = 14

        scale_arrow.text = ">" if scale_mode else ""
        scale_arrow.x = scale_label.x - 10
        scale_arrow.y = 14

        if chord_mode:
            chord_label.hidden = False
            chord_label.x = scale_label.x + (len(scale_label.text) * 6) + 4
            chord_label.y = 14
        else:
            chord_label.hidden = True

        # Left side = OCTAVE
        octave_value.text = octave_text
        octave_value.x = 25
        octave_value.y = 49

        if octave_active:
            octave_arrow.text = ">"
            octave_arrow.x = octave_value.x - 10
            octave_arrow.y = octave_value.y
        else:
            octave_arrow.text = ""

        # Right side = TRANSPOSE
        transpose_value.text = transpose_text
        transpose_value.x = 82
        transpose_value.y = 49

        if transpose_active:
            transpose_arrow.text = ">"
            transpose_arrow.x = transpose_value.x - 10
            transpose_arrow.y = transpose_value.y
        else:
            transpose_arrow.text = ""

        last_display_scale = scale_text
        last_display_transpose = TRANSPOSE
        last_display_octave = OCTAVE_SHIFT
        last_display_scale_mode = scale_mode
        last_display_octave_active = octave_active
        last_display_transpose_active = transpose_active
        last_display_chord_mode = chord_mode

load_settings()
update_display(force=True)

# ---------------------------------
# LED setup
# ---------------------------------
LED_PIN = board.A3
NUM_PIXELS = 6
LED_BRIGHTNESS = 0.12

pixels = neopixel.NeoPixel(
    LED_PIN,
    NUM_PIXELS,
    brightness=LED_BRIGHTNESS,
    auto_write=True,
    pixel_order=neopixel.GRB,
)

pixels.fill((0, 0, 0))

def led_on(index):
    if index < NUM_PIXELS:
        pixels[index] = (255, 255, 255)

def led_off(index):
    if index < NUM_PIXELS:
        pixels[index] = (0, 0, 0)

# ---------------------------------
# Matrix setup
# Current hardware logic:
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
    [[], [], [], []],
    [[], [], [], []],
    [[], [], [], []],
    [[], [], [], []],
]

# ---------------------------------
# Encoder setup (also used for scale selection)
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

last_sw = enc_sw.value

last_ab = (int(enc_a.value) << 1) | int(enc_b.value)
encoder_accum = 0

button_press_time = None
encoder_rotated_while_pressed = False
button_used_with_key = False
root_down_latched = False
root_up_latched = False
reset_latched = False
chord_latched = False

mark_activity()

print("MIDIMAL boot")
print("ACTIVE_SCALE =", active_scale_name())

# ---------------------------------
# Main loop
# ---------------------------------
SESSION_HOLD_TIME = 0.5

while True:
    now = time.monotonic()

    # ---- Button state tracking ----
    sw_pressed = not enc_sw.value

    if sw_pressed and last_sw:
        button_press_time = now
        scale_mode = False
        octave_adjust_active = False
        encoder_rotated_while_pressed = False
        button_used_with_key = False
        root_down_latched = False
        root_up_latched = False
        reset_latched = False
        chord_latched = False
        mark_activity()

    elif not sw_pressed and not last_sw:
        if scale_mode:
            print("SCALE/ROOT SESSION CONFIRMED")

        button_press_time = None
        scale_mode = False
        octave_adjust_active = False
        encoder_rotated_while_pressed = False
        button_used_with_key = False
        root_down_latched = False
        root_up_latched = False
        reset_latched = False
        chord_latched = False

        if settings_dirty:
            save_settings()

        update_display()

    last_sw = enc_sw.value

    # ---- Session activation ----
    if (
        sw_pressed
        and button_press_time is not None
        and not scale_mode
        and not octave_adjust_active
        and not encoder_rotated_while_pressed
        and (now - button_press_time) >= SESSION_HOLD_TIME
    ):
        scale_mode = True
        print("SCALE/ROOT SESSION:", active_scale_name(), root_note_name())
        update_display()

    # ---- Encoder handling ----
    current_ab = (int(enc_a.value) << 1) | int(enc_b.value)

    if current_ab != last_ab:
        transition = (last_ab << 2) | current_ab

        # Valid quadrature transitions only
        if transition in (0b0001, 0b0111, 0b1110, 0b1000):
            encoder_accum += 1
        elif transition in (0b0010, 0b1011, 0b1101, 0b0100):
            encoder_accum -= 1

        last_ab = current_ab

        direction = 0
        if encoder_accum >= 4:
            direction = 1
            encoder_accum = 0
        elif encoder_accum <= -4:
            direction = -1
            encoder_accum = 0

        if direction != 0:
            mark_activity()

            if scale_mode:
                active_scale_index = (active_scale_index + direction) % len(SCALE_ORDER)
                print("ACTIVE_SCALE =", active_scale_name())
                mark_settings_dirty()
                update_display()

            elif octave_adjust_active:
                TRANSPOSE = clamp(TRANSPOSE + direction, -12, 12)
                print("TRANSPOSE =", TRANSPOSE)
                mark_settings_dirty()
                update_display()

            elif sw_pressed:
                encoder_rotated_while_pressed = True
                octave_adjust_active = True
                TRANSPOSE = clamp(TRANSPOSE + direction, -12, 12)
                print("TRANSPOSE =", TRANSPOSE)
                mark_settings_dirty()
                update_display()

            else:
                OCTAVE_SHIFT = clamp(OCTAVE_SHIFT + direction, -2, 2)
                transpose_indicator_until = now + 0.35
                print("OCTAVE_SHIFT =", OCTAVE_SHIFT)
                mark_settings_dirty()
                update_display()

    # ---- Matrix scan ----

    if not scale_mode:
        for col_index, col in enumerate(cols):
            col.value = False
            time.sleep(0.0005)

            for row_index, row in enumerate(rows):
                pressed = not row.value
                notes = current_notes(row_index, col_index)

                if pressed and not last_states[row_index][col_index]:
                    mark_activity()
                    for note in notes:
                        midi.send(NoteOn(note, 100))
                        print("NOTE ON", note)
                    active_notes[row_index][col_index] = notes
                    note_index = (row_index * 4) + col_index
                    led_on(note_index)

                elif not pressed and last_states[row_index][col_index]:
                    notes_off = active_notes[row_index][col_index]
                    for note in notes_off:
                        midi.send(NoteOff(note, 0))
                        print("NOTE OFF", note)
                    active_notes[row_index][col_index] = []

                    note_index = (row_index * 4) + col_index
                    led_off(note_index) 

                last_states[row_index][col_index] = pressed

            col.value = True

    else:
        for col_index, col in enumerate(cols):
            col.value = False
            time.sleep(0.0005)

            for row_index, row in enumerate(rows):
                pressed = not row.value

                is_root_down_key = (row_index == 0 and col_index == 0)
                is_root_up_key = (row_index == 0 and col_index == 3)
                is_reset_key = (row_index == 3 and col_index == 0)
                is_chord_key = (row_index == 3 and col_index == 3)

                if is_root_down_key or is_root_up_key or is_reset_key or is_chord_key:
                    if pressed and not last_states[row_index][col_index]:
                        mark_activity()

                        if is_root_down_key and not root_down_latched:
                            shift_root(-1)
                            root_down_latched = True

                        elif is_root_up_key and not root_up_latched:
                            shift_root(1)
                            root_up_latched = True

                        elif is_reset_key and not reset_latched:
                            reset_to_defaults()
                            reset_latched = True

                        elif is_chord_key and not chord_latched:
                            toggle_chord_mode()
                            chord_latched = True

                    elif not pressed and last_states[row_index][col_index]:
                        if is_root_down_key:
                            root_down_latched = False
                        elif is_root_up_key:
                            root_up_latched = False
                        elif is_reset_key:
                            reset_latched = False
                        elif is_chord_key:
                            chord_latched = False

                    active_notes[row_index][col_index] = None
                    last_states[row_index][col_index] = pressed
                    continue

                # In scale/root session, all note keys are suppressed
                if not pressed and last_states[row_index][col_index]:
                    note_off = active_notes[row_index][col_index]
                    if note_off is not None:
                        midi.send(NoteOff(note_off, 0))
                        print("NOTE OFF", note_off)
                    active_notes[row_index][col_index] = None

                last_states[row_index][col_index] = pressed

            col.value = True

    if settings_dirty and now >= settings_save_at:
        save_settings()

    check_idle()
    update_display()
    time.sleep(0.001)