import json
import os
import time

import board  # pyright: ignore[reportMissingImports]
import neopixel  # pyright: ignore[reportMissingImports]
import digitalio  # pyright: ignore[reportMissingImports]
import usb_midi  # pyright: ignore[reportMissingImports]
import adafruit_midi  # pyright: ignore[reportMissingImports]
import displayio  # pyright: ignore[reportMissingImports]
import terminalio  # pyright: ignore[reportMissingImports]
from fourwire import FourWire  # pyright: ignore[reportMissingImports]
from adafruit_display_text import label  # pyright: ignore[reportMissingImports]
import adafruit_displayio_sh1106  # pyright: ignore[reportMissingImports]
from adafruit_midi.note_on import NoteOn  # pyright: ignore[reportMissingImports]
from adafruit_midi.note_off import NoteOff  # pyright: ignore[reportMissingImports]

midi = adafruit_midi.MIDI(midi_out=usb_midi.ports[1], out_channel=0)

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
    "major": [0, 2, 4, 5, 7, 9, 11],
    "minor": [0, 2, 3, 5, 7, 8, 10],
    "pentatonic": [0, 2, 4, 7, 9],
    "blues": [0, 3, 5, 6, 7, 10],
}

DISPLAY_SCALE_NAMES = {
    "major": "Major",
    "minor": "Minor",
    "pentatonic": "Pentatonic",
    "blues": "Blues",
}

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

SETTINGS_FILE = "/midimal_settings.json"
SETTINGS_SAVE_DELAY = 0.4

PRESETS_FILE = "/midimal_presets.json"
PRESET_HOLD_TIME = 0.65
MESSAGE_HOLD_TIME = 0.55
BROWSE_HOLD_TIME = 0.5

settings_dirty = False
settings_save_at = 0

message_text = ""
message_until = 0.0

active_scale_index = 2  # pentatonic default

# ---------------------------------
# Browse mode state
# ---------------------------------
browse_mode_active = False
browse_arm_pending = False
browse_click_pending = False

browse_root_note = ROOT_NOTE
browse_scale_index = active_scale_index

# ---------------------------------
# Encoder / command state
# ---------------------------------
button_press_time = None
hold_command_used = False
transpose_adjust_active = False

scale_down_latched = False
scale_up_latched = False
reset_latched = False
chord_latched = False

preset_press_time = [None, None, None, None]
preset_save_triggered = [False, False, False, False]

octave_indicator_until = 0.0


def clamp(value, min_value, max_value):
    return max(min_value, min(max_value, value))


def note_name_from_midi(note):
    return NOTE_NAMES[note % 12]


def root_note_name():
    return note_name_from_midi(ROOT_NOTE)


def active_scale_name():
    return SCALE_ORDER[active_scale_index]


def displayed_root_note():
    return browse_root_note if browse_mode_active else ROOT_NOTE


def displayed_scale_index():
    return browse_scale_index if browse_mode_active else active_scale_index


def displayed_root_name():
    return note_name_from_midi(displayed_root_note())


def displayed_scale_name():
    return SCALE_ORDER[displayed_scale_index()]


def browse_indicator_visible():
    return browse_arm_pending or browse_mode_active


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
        active_scale_index = clamp(
            int(data.get("scale_index", 2)), 0, len(SCALE_ORDER) - 1
        )
        TRANSPOSE = clamp(int(data.get("transpose", 0)), -12, 12)
        OCTAVE_SHIFT = clamp(int(data.get("octave_shift", 0)), -2, 2)
        chord_mode = bool(data.get("chord_mode", False))

        print("SETTINGS LOADED")
    except OSError:
        print("No saved settings found, using defaults")
    except Exception as e:
        print("LOAD SETTINGS ERROR:", e)


def default_presets_data():
    return {"slots": [None, None, None, None]}


def load_presets_data():
    try:
        with open(PRESETS_FILE, "r") as f:
            data = json.load(f)

        slots = data.get("slots", [None, None, None, None])
        if len(slots) < 4:
            slots = slots + [None] * (4 - len(slots))
        elif len(slots) > 4:
            slots = slots[:4]

        return {"slots": slots}
    except OSError:
        return default_presets_data()
    except Exception as e:
        print("LOAD PRESETS ERROR:", e)
        return default_presets_data()


def save_presets_data(data):
    try:
        with open(PRESETS_FILE, "w") as f:
            json.dump(data, f)
    except OSError as e:
        print("SAVE PRESETS DISABLED:", e)
    except Exception as e:
        print("SAVE PRESETS ERROR:", e)


def show_message(text, duration=MESSAGE_HOLD_TIME):
    global message_text, message_until
    message_text = text
    message_until = time.monotonic() + duration


def message_visible():
    return time.monotonic() < message_until


def save_preset_slot(slot_index):
    data = load_presets_data()
    data["slots"][slot_index] = {
        "root_note": ROOT_NOTE,
        "scale_index": active_scale_index,
        "transpose": TRANSPOSE,
        "octave_shift": OCTAVE_SHIFT,
        "chord_mode": chord_mode,
    }
    save_presets_data(data)
    show_message(f"SAVED > P{slot_index + 1}")


def load_preset_slot(slot_index):
    global ROOT_NOTE, active_scale_index, TRANSPOSE, OCTAVE_SHIFT, chord_mode

    data = load_presets_data()
    preset = data["slots"][slot_index]

    if preset is None:
        show_message("EMPTY")
        return

    ROOT_NOTE = int(preset.get("root_note", 60))
    active_scale_index = clamp(
        int(preset.get("scale_index", 2)), 0, len(SCALE_ORDER) - 1
    )
    TRANSPOSE = clamp(int(preset.get("transpose", 0)), -12, 12)
    OCTAVE_SHIFT = clamp(int(preset.get("octave_shift", 0)), -2, 2)
    chord_mode = bool(preset.get("chord_mode", False))

    mark_settings_dirty()
    show_message(f"LOADED > P{slot_index + 1}")
    update_display()


def reset_hold_command_latches():
    global scale_down_latched
    global scale_up_latched
    global reset_latched
    global chord_latched
    global preset_press_time
    global preset_save_triggered

    scale_down_latched = False
    scale_up_latched = False
    reset_latched = False
    chord_latched = False
    preset_press_time = [None, None, None, None]
    preset_save_triggered = [False, False, False, False]


def clear_hold_state():
    global button_press_time
    global hold_command_used
    global browse_arm_pending
    global transpose_adjust_active

    button_press_time = None
    hold_command_used = False
    browse_arm_pending = False
    transpose_adjust_active = False
    reset_hold_command_latches()


def cancel_browse_arm():
    global browse_arm_pending
    browse_arm_pending = False


def register_hold_command():
    global hold_command_used
    hold_command_used = True
    cancel_browse_arm()


def arm_browse_mode():
    global browse_arm_pending
    global browse_root_note
    global browse_scale_index

    if browse_arm_pending:
        return

    browse_arm_pending = True
    browse_root_note = ROOT_NOTE
    browse_scale_index = active_scale_index
    print("BROWSE ARMED")
    update_display()


def enter_browse_mode():
    global browse_mode_active
    global browse_arm_pending
    global browse_click_pending

    browse_mode_active = True
    browse_arm_pending = False
    browse_click_pending = False
    reset_hold_command_latches()

    print("BROWSE MODE:", displayed_scale_name(), displayed_root_name())
    update_display()


def commit_browse_selection():
    global ROOT_NOTE, active_scale_index

    changed = False

    if ROOT_NOTE != browse_root_note:
        ROOT_NOTE = browse_root_note
        changed = True

    if active_scale_index != browse_scale_index:
        active_scale_index = browse_scale_index
        changed = True

    if changed:
        print("BROWSE SET:", root_note_name(), active_scale_name())
        mark_settings_dirty()


def exit_browse_mode():
    global browse_mode_active
    global browse_click_pending

    browse_mode_active = False
    browse_click_pending = False
    clear_hold_state()
    update_display()


def shift_root(direction):
    global ROOT_NOTE, browse_root_note

    if browse_mode_active:
        browse_root_note = 60 + ((browse_root_note - 60 + direction) % 12)
        print("ROOT PREVIEW =", note_name_from_midi(browse_root_note), browse_root_note)
    else:
        ROOT_NOTE = 60 + ((ROOT_NOTE - 60 + direction) % 12)
        print("ROOT_NOTE =", root_note_name(), ROOT_NOTE)
        mark_settings_dirty()

    update_display()


def shift_scale(direction):
    global active_scale_index, browse_scale_index

    if browse_mode_active:
        browse_scale_index = (browse_scale_index + direction) % len(SCALE_ORDER)
        print("SCALE PREVIEW =", SCALE_ORDER[browse_scale_index])
    else:
        active_scale_index = (active_scale_index + direction) % len(SCALE_ORDER)
        print("ACTIVE_SCALE =", active_scale_name())
        mark_settings_dirty()

    update_display()


def reset_to_defaults():
    global ROOT_NOTE, active_scale_index, TRANSPOSE, OCTAVE_SHIFT, chord_mode

    ROOT_NOTE = 60
    active_scale_index = 2
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


def get_scale_note(index, root_note=None, scale_index=None):
    if root_note is None:
        root_note = displayed_root_note()
    if scale_index is None:
        scale_index = displayed_scale_index()

    scale = SCALES[SCALE_ORDER[scale_index]]
    scale_len = len(scale)
    octave = index // scale_len
    degree = index % scale_len
    return root_note + scale[degree] + (octave * 12) + TRANSPOSE + (OCTAVE_SHIFT * 12)


def get_chord_notes(index, root_note=None, scale_index=None):
    return [
        get_scale_note(index, root_note, scale_index),
        get_scale_note(index + 2, root_note, scale_index),
        get_scale_note(index + 4, root_note, scale_index),
    ]


def current_notes(row, col):
    note_index = (row * 4) + col

    if browse_mode_active:
        root_note = browse_root_note
        scale_index = browse_scale_index
    else:
        root_note = ROOT_NOTE
        scale_index = active_scale_index

    if chord_mode:
        return get_chord_notes(note_index, root_note, scale_index)

    return [get_scale_note(note_index, root_note, scale_index)]


def release_notes_for_key(row_index, col_index):
    notes_off = active_notes[row_index][col_index]

    if notes_off:
        for note in notes_off:
            midi.send(NoteOff(note, 0))
        active_notes[row_index][col_index] = []

    note_index = (row_index * 4) + col_index
    led_off(note_index)


def note_on_for_key(row_index, col_index):
    notes = current_notes(row_index, col_index)

    for note in notes:
        midi.send(NoteOn(note, 100))

    active_notes[row_index][col_index] = notes

    note_index = (row_index * 4) + col_index
    led_on(note_index)


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
    command=board.D0,
    chip_select=board.D1,
    reset=board.D10,
    baudrate=1000000,
)

display = adafruit_displayio_sh1106.SH1106(
    display_bus, width=132, height=64, rotation=0
)


def show_startup_splash():
    if not (
        "midimal_splash_a.bmp" in os.listdir("/")
        and "midimal_splash_b.bmp" in os.listdir("/")
    ):
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

hud_bitmap = displayio.Bitmap(132, 64, 2)
hud_palette = displayio.Palette(2)
hud_palette[0] = 0x000000
hud_palette[1] = 0xFFFFFF

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

    left = 2
    top = 2
    right = 125
    bottom = 61

    draw_hline(hud_bitmap, left, top, right - left + 1, 1)
    draw_hline(hud_bitmap, left, bottom, right - left + 1, 1)
    draw_vline(hud_bitmap, left, top, bottom - top + 1, 1)
    draw_vline(hud_bitmap, right, top, bottom - top + 1, 1)

    draw_hline(hud_bitmap, 10, 24, 108, 1, dotted=True)
    draw_vline(hud_bitmap, 57, 30, 24, 1, dotted=True)


draw_static_hud()

scale_label = label.Label(terminalio.FONT, text="PENTATONIC", color=0xFFFFFF)
splash.append(scale_label)

scale_arrow = label.Label(terminalio.FONT, text="", color=0xFFFFFF, x=12, y=14)
splash.append(scale_arrow)

chord_label = label.Label(
    terminalio.FONT, text=" c ", color=0x000000, x=0, y=12, background_color=0xFFFFFF
)
splash.append(chord_label)

octave_title = label.Label(terminalio.FONT, text="OCTAVE", color=0xFFFFFF, x=14, y=35)
splash.append(octave_title)

transpose_title = label.Label(
    terminalio.FONT, text="TRANSPOSE", color=0xFFFFFF, x=65, y=35
)
splash.append(transpose_title)

octave_value = label.Label(terminalio.FONT, text="+0", color=0xFFFFFF, x=20, y=49)
splash.append(octave_value)

octave_arrow = label.Label(terminalio.FONT, text="", color=0xFFFFFF, x=10, y=49)
splash.append(octave_arrow)

transpose_value = label.Label(terminalio.FONT, text="+0", color=0xFFFFFF, x=72, y=49)
splash.append(transpose_value)

transpose_arrow = label.Label(terminalio.FONT, text="", color=0xFFFFFF, x=60, y=49)
splash.append(transpose_arrow)

message_group = displayio.Group()
message_group.hidden = True

message_bg_bitmap = displayio.Bitmap(132, 64, 2)
message_bg_palette = displayio.Palette(2)
message_bg_palette[0] = 0x000000
message_bg_palette[1] = 0xFFFFFF

message_bg = displayio.TileGrid(message_bg_bitmap, pixel_shader=message_bg_palette)
message_group.append(message_bg)

message_label = label.Label(
    terminalio.FONT, text="SAVED > P1", color=0xFFFFFF, x=0, y=32
)
message_group.append(message_label)

splash.append(message_group)

draw_rect(message_bg_bitmap, 0, 0, 132, 64, 0)

last_display_scale = None
last_display_transpose = None
last_display_octave = None
last_display_browse_indicator = None
last_display_browse_mode = None
last_display_octave_active = None
last_display_transpose_active = None
last_display_chord_mode = None
last_display_message_text = None
last_display_message_visible = None


def update_display(force=False):
    global last_display_scale
    global last_display_transpose
    global last_display_octave
    global last_display_browse_indicator
    global last_display_browse_mode
    global last_display_octave_active
    global last_display_transpose_active
    global last_display_chord_mode
    global last_display_message_text
    global last_display_message_visible

    scale_text = (
        f"{displayed_root_name()} "
        f"{DISPLAY_SCALE_NAMES[displayed_scale_name()].upper()}"
    )
    transpose_text = f"{TRANSPOSE:+d}"
    octave_text = f"{OCTAVE_SHIFT:+d}"

    octave_active = time.monotonic() < octave_indicator_until
    transpose_active = transpose_adjust_active
    browse_indicator = browse_indicator_visible()

    current_message_visible = message_visible()
    current_message_text = message_text

    if (
        force
        or scale_text != last_display_scale
        or TRANSPOSE != last_display_transpose
        or OCTAVE_SHIFT != last_display_octave
        or browse_indicator != last_display_browse_indicator
        or browse_mode_active != last_display_browse_mode
        or octave_active != last_display_octave_active
        or transpose_active != last_display_transpose_active
        or chord_mode != last_display_chord_mode
        or current_message_visible != last_display_message_visible
        or current_message_text != last_display_message_text
    ):
        if current_message_visible:
            message_label.text = current_message_text
            message_label.x = (VISIBLE_W - (len(current_message_text) * 6)) // 2
            message_label.y = 32

            message_group.hidden = False

            scale_label.hidden = True
            scale_arrow.hidden = True
            chord_label.hidden = True
            octave_title.hidden = True
            transpose_title.hidden = True
            octave_value.hidden = True
            transpose_value.hidden = True
            octave_arrow.hidden = True
            transpose_arrow.hidden = True

        else:
            message_group.hidden = True

            scale_label.hidden = False
            scale_label.text = scale_text
            scale_label.x = (VISIBLE_W - (len(scale_text) * 6)) // 2
            scale_label.y = 14

            scale_arrow.hidden = False
            scale_arrow.text = ">" if browse_indicator else ""
            scale_arrow.x = scale_label.x - 10
            scale_arrow.y = 14

            octave_title.hidden = False
            transpose_title.hidden = False
            octave_value.hidden = False
            transpose_value.hidden = False
            octave_arrow.hidden = False
            transpose_arrow.hidden = False

            if chord_mode:
                chord_label.hidden = False
                chord_label.x = scale_label.x + (len(scale_label.text) * 6) + 4
                chord_label.y = 14
            else:
                chord_label.hidden = True

            octave_value.text = octave_text
            octave_value.x = 25
            octave_value.y = 49

            if octave_active:
                octave_arrow.text = ">"
                octave_arrow.x = octave_value.x - 10
                octave_arrow.y = octave_value.y
            else:
                octave_arrow.text = ""

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
        last_display_browse_indicator = browse_indicator
        last_display_browse_mode = browse_mode_active
        last_display_octave_active = octave_active
        last_display_transpose_active = transpose_active
        last_display_chord_mode = chord_mode
        last_display_message_text = current_message_text
        last_display_message_visible = current_message_visible


show_startup_splash()
load_settings()
browse_root_note = ROOT_NOTE
browse_scale_index = active_scale_index
update_display(force=True)
display.root_group = splash

# ---------------------------------
# LED setup
# ---------------------------------
LED_PIN = board.A3
NUM_PIXELS = 6
LED_BRIGHTNESS = 1.00

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
        pixels[index] = (76, 153, 255)


def led_off(index):
    if index < NUM_PIXELS:
        pixels[index] = (0, 0, 0)


# ---------------------------------
# Matrix setup
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

last_sw = enc_sw.value
last_ab = (int(enc_a.value) << 1) | int(enc_b.value)
encoder_accum = 0

mark_activity()

print("MIDIMAL boot")
print("ACTIVE_SCALE =", active_scale_name())

while True:
    now = time.monotonic()
    sw_pressed = not enc_sw.value

    # ---------------------------------
    # Encoder button edge handling
    # ---------------------------------
    if sw_pressed and last_sw:
        mark_activity()

        if browse_mode_active:
            browse_click_pending = True
        else:
            button_press_time = now
            hold_command_used = False
            browse_arm_pending = False
            transpose_adjust_active = False
            reset_hold_command_latches()

    elif not sw_pressed and not last_sw:
        if browse_mode_active:
            if browse_click_pending:
                browse_click_pending = False
                commit_browse_selection()
                exit_browse_mode()
        else:
            if browse_arm_pending and not hold_command_used:
                enter_browse_mode()
            else:
                clear_hold_state()
                update_display()

            if settings_dirty:
                save_settings()

    last_sw = enc_sw.value

    # ---------------------------------
    # Hold-to-arm browse (but do not enter yet)
    # ---------------------------------
    if (
        sw_pressed
        and not browse_mode_active
        and button_press_time is not None
        and not hold_command_used
        and (now - button_press_time) >= BROWSE_HOLD_TIME
    ):
        arm_browse_mode()

    # ---------------------------------
    # Encoder rotation handling
    # ---------------------------------
    current_ab = (int(enc_a.value) << 1) | int(enc_b.value)

    if current_ab != last_ab:
        transition = (last_ab << 2) | current_ab

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

            if browse_mode_active:
                shift_root(direction)

            elif sw_pressed:
                register_hold_command()
                transpose_adjust_active = True
                TRANSPOSE = clamp(TRANSPOSE + direction, -12, 12)
                print("TRANSPOSE =", TRANSPOSE)
                mark_settings_dirty()
                update_display()

            else:
                OCTAVE_SHIFT = clamp(OCTAVE_SHIFT + direction, -2, 2)
                octave_indicator_until = now + 0.35
                print("OCTAVE_SHIFT =", OCTAVE_SHIFT)
                mark_settings_dirty()
                update_display()

    # ---------------------------------
    # Matrix scan
    # ---------------------------------
    for col_index, col in enumerate(cols):
        col.value = False
        time.sleep(0.0005)

        for row_index, row in enumerate(rows):
            pressed = not row.value
            was_pressed = last_states[row_index][col_index]

            is_browse_scale_down_key = (
                browse_mode_active and row_index == 0 and col_index == 0
            )
            is_browse_scale_up_key = (
                browse_mode_active and row_index == 0 and col_index == 3
            )

            is_hold_preset_key = (
                sw_pressed and not browse_mode_active and row_index == 1
            )
            is_hold_chord_key = (
                sw_pressed
                and not browse_mode_active
                and row_index == 3
                and col_index == 0
            )  # bottom left = chord
            is_hold_reset_key = (
                sw_pressed
                and not browse_mode_active
                and row_index == 3
                and col_index == 3
            )  # bottom right = reset

            if browse_mode_active:
                key_is_playable = (
                    not is_browse_scale_down_key and not is_browse_scale_up_key
                )
            else:
                key_is_playable = not sw_pressed

            if key_is_playable:
                if pressed and not was_pressed:
                    mark_activity()
                    note_on_for_key(row_index, col_index)

                elif not pressed and was_pressed:
                    release_notes_for_key(row_index, col_index)

                last_states[row_index][col_index] = pressed
                continue

            if not pressed and was_pressed:
                release_notes_for_key(row_index, col_index)

            # ---- Browse mode scale preview keys ----
            if is_browse_scale_down_key or is_browse_scale_up_key:
                if pressed and not was_pressed:
                    mark_activity()

                    if is_browse_scale_down_key and not scale_down_latched:
                        shift_scale(-1)
                        scale_down_latched = True

                    elif is_browse_scale_up_key and not scale_up_latched:
                        shift_scale(1)
                        scale_up_latched = True

                elif not pressed and was_pressed:
                    if is_browse_scale_down_key:
                        scale_down_latched = False
                    elif is_browse_scale_up_key:
                        scale_up_latched = False

                last_states[row_index][col_index] = pressed
                continue

            # ---- Hold-command preset keys ----
            if is_hold_preset_key:
                slot_index = 3 - col_index

                if pressed and not was_pressed:
                    mark_activity()
                    register_hold_command()
                    preset_press_time[slot_index] = now
                    preset_save_triggered[slot_index] = False

                elif pressed and was_pressed:
                    if (
                        preset_press_time[slot_index] is not None
                        and not preset_save_triggered[slot_index]
                        and (now - preset_press_time[slot_index]) >= PRESET_HOLD_TIME
                    ):
                        save_preset_slot(slot_index)
                        preset_save_triggered[slot_index] = True

                elif not pressed and was_pressed:
                    if not preset_save_triggered[slot_index]:
                        load_preset_slot(slot_index)

                    preset_press_time[slot_index] = None
                    preset_save_triggered[slot_index] = False

                last_states[row_index][col_index] = pressed
                continue

            # ---- Hold-command bottom row shortcuts ----
            if is_hold_chord_key or is_hold_reset_key:
                if pressed and not was_pressed:
                    mark_activity()
                    register_hold_command()

                    if is_hold_chord_key and not chord_latched:
                        toggle_chord_mode()
                        chord_latched = True

                    elif is_hold_reset_key and not reset_latched:
                        reset_to_defaults()
                        reset_latched = True

                elif not pressed and was_pressed:
                    if is_hold_chord_key:
                        chord_latched = False
                    elif is_hold_reset_key:
                        reset_latched = False

                last_states[row_index][col_index] = pressed
                continue

            last_states[row_index][col_index] = pressed

        col.value = True

    if settings_dirty and now >= settings_save_at:
        save_settings()

    check_idle()
    update_display()
    time.sleep(0.001)
