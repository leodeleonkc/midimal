# MIDIMAL 🎹

MIDIMAL is a compact, instrument-first MIDI controller that lives on your desk and calls you to play. Whether it’s a quick escape between tasks or a full creative session, it turns idle moments into musical ideas.

Built around a 4x4 grid of mechanical switches, MIDIMAL prioritizes simplicity, playability, and immediate feedback.

---

## ✨ Vision

MIDIMAL is designed to be:

* 🎵 **Instrument-first** — not a tool, something you *play*
* ⚡ **Instant-on** — plug in and start creating
* 🧠 **Simple but powerful** — minimal friction, deep capability
* 🖐️ **Tactile and satisfying** — like a musical fidget device

---

## 🚧 Project Status

**Current Stage:** Firmware + Hardware Prototyping (Active Breadboard Build)


### Completed

* [x] CircuitPython setup on KB2040
* [x] USB MIDI output working
* [x] Single input → MIDI note
* [x] Multi-input (4 direct pins)
* [x] Matrix scanning (2x2 test)
* [x] Full 4x4 matrix wiring (16 keys)
* [x] Hardware-validated matrix scanning (no ghosting)
* [x] Working MIDI output from full matrix

### Accomplished today (4/4/26)
- [x] Verified KB2040 setup with CircuitPython
- [x] Confirmed USB MIDI output into a software synth
- [x] Tested single-input note triggering
- [x] Tested 4 direct inputs with clean note triggering
- [x] Built and validated 2x2 matrix scan logic
- [x] Added scale-based note mapping
- [x] Added transpose and octave shift logic
- [x] Simulated encoder interaction logic before testing with real hardware

### Accomplished today (4/7/26)

- [x] Built full 4x4 key matrix (16 switches + diodes)
- [x] Validated matrix scanning across all rows and columns
- [x] Confirmed multi-key input behavior (no ghosting)
- [x] Debugged and resolved CircuitPython library dependency issues
- [x] Established reliable firmware sync workflow (repo → board)
- [x] Identified and corrected diode orientation behavior in hardware
- [x] Implemented alternate scan logic to match current wiring
- [x] Fully playable MIDI grid confirmed (tested with Vital 🎛️)

Part II

- [x] Integrated and tuned **rotary encoder behavior** (transpose, octave shift, scale select)  
- [x] Implemented **long-press scale selection mode** with smooth interaction flow  
- [x] Fully wired and configured **SH1106 OLED (SPI)** display  
- [x] Resolved OLED alignment issues using correct **132px width configuration**  
- [x] Designed and implemented **startup splash screen** with animated mascot (blinking stars)  
- [x] Created and refined **MIDIMAL mascot** (pixel-art keyboard character)  
- [x] Built custom **HUD interface** with:  
  - scale display  
  - transpose and octave sections  
  - divider layout and border system  
- [x] Optimized HUD rendering for **performance (eliminated slow redraw/wipe effects)**  
- [x] Implemented clean **scale-select visual feedback** (arrow indicator)  
- [x] Fixed **UI alignment and spacing issues** across all elements  
- [x] Implemented **display idle sleep system** with instant wake on interaction  
- [x] Improved development workflow by updating **sync script to include asset files (BMPs)**  
- [x] Recovered and stabilized board behavior after firmware/reset issues  
- [x] Achieved fully playable, responsive **instrument prototype with visual feedback**
- [x] Refactored encoder logic into **state-based interaction model** (eliminated timing conflicts)  
- [x] Implemented **latched octave adjustment session** (hold + rotate behaves consistently)  
- [x] Replaced native encoder handling with **quadrature edge filtering** (stable, jitter-free input)  
- [x] Removed blocking delays and improved **input responsiveness and reliability**  
- [x] Added **contextual UI indicators** for active controls (transpose + octave arrows)  
- [x] Implemented **time-based transpose indicator** with automatic fade-out  
- [x] Improved display update system to respond to **state + time changes (not just input events)**  
- [x] Added **root note system** with dynamic key shifting (C → C# → D, etc.)  
- [x] Integrated root display into HUD (`C PENTATONIC`, etc.) for immediate feedback  
- [x] Implemented **gesture-based root shifting** (hold encoder + corner keys)  
- [x] Merged scale + root into unified **held edit session (intent-based interaction model)**  
- [x] Replaced long-press timing dependency with **action-driven mode switching**  
- [x] Designed and implemented **dual-mode encoder behavior**:  
  - quick twist → octave  
  - slight hold → scale/root session  
- [x] Eliminated interaction conflicts between **scale, root, and octave controls**  
- [x] Validated real-world use case: **play-along workflow (find root + jam instantly)**

### Accomplished today (4/8/26)

[x] Implemented full **state persistence system**
- [x] Save and restore root note, scale, transpose, octave, and chord mode
- [x] Added delayed write system to prevent excessive file writes
- [x] Implemented safe fallback for read-only filesystem (dev mode compatibility)
- [x] Confirmed persistence works across power cycles

[x] Built **reset-to-defaults gesture**
- [x] Encoder hold + key press resets:
  - root → C
  - scale → pentatonic
  - transpose → 0
  - octave → 0
  - chord mode → OFF
- [x] Integrated reset into scale/root session workflow

[x] Implemented **chord mode system**
- [x] Added chord mode toggle via encoder + key press
- [x] Built chord engine using stacked scale degrees (1–3–5)
- [x] Ensured compatibility across all scales (major, minor, pentatonic, blues)
- [x] Updated MIDI engine to support multi-note output per pad
- [x] Added proper NoteOn/NoteOff handling for chord playback

[x] Designed and integrated **chord mode UI indicator**
- [x] Added highlighted "c" badge with inverted colors (white background, black text)
- [x] Positioned dynamically relative to scale label
- [x] Ensured UI updates correctly with state changes
- [x] Included chord mode in persistence system

[x] Refined **interaction model and UX consistency**
- [x] Unified scale + root + chord interactions under a single session model
- [x] Maintained intuitive, non-menu-based control philosophy
- [x] Ensured all advanced features are intentional and discoverable

[x] Validated **real-world musical usability**
- [x] Successfully played along with external music (Spotify testing)
- [x] Verified intuitive workflow for finding root and improvising
- [x] Confirmed chord mode enhances musical exploration without added complexity

[x] Implemented **LED underglow hardware system**
- [x] Wired WS2812B LED chain with proper power distribution (5V RAW)
- [x] Integrated SN74AHCT125 level shifter for 3.3V → 5V data conversion
- [x] Added 220Ω series resistor on LED data line
- [x] Added 1000µF bulk capacitor across LED power rails
- [x] Added 100nF decoupling capacitor across level shifter VCC/GND
- [x] Properly configured unused buffer channels (OE high, inputs grounded)
- [x] Verified stable LED operation on breadboard prototype

[x] Integrated **LED system into firmware**
- [x] Installed and configured NeoPixel library for CircuitPython
- [x] Initialized LED system with correct pin (A3) and pixel order
- [x] Implemented note-triggered LED feedback system
- [x] Built scalable LED indexing model (pad → LED mapping ready)
- [x] Verified LED + MIDI + matrix coexist without timing issues

[x] Built **matrix diagnostic system**
- [x] Created isolated scan test to validate row/column behavior
- [x] Verified hardware matrix integrity independent of MIDI logic
- [x] Used diagnostic output to distinguish hardware vs software faults

[x] Identified and resolved **critical matrix scanning bug**
- [x] Discovered duplicate scan loop causing multiple columns to remain active
- [x] Diagnosed issue via mismatch between diagnostic test and runtime behavior
- [x] Removed redundant scan block to restore proper column isolation
- [x] Confirmed fix eliminated multi-note triggering issue

[x] Finalized **PCB-ready electrical architecture**
- [x] Completed precise KiCad-style netlist with exact pin mappings
- [x] Defined LED driver stage with explicit IC pin assignments
- [x] Standardized power nets (5V_RAW, 3V3, GND)
- [x] Added proper decoupling and bulk capacitance strategy
- [x] Defined clean reference designator system (DM vs D conflict resolved)
- [x] Created PCB placement and routing guidelines
- [x] Confirmed system is ready for schematic capture and PCB layout

### Accomplished since 4/8/26 and as of 4/15/26

[x] Implemented **LED underglow system (WS2812 / NeoPixel)**
- [x] Integrated LED control into matrix note system
- [x] Mapped pad presses to LED indices
- [x] Implemented NoteOn/NoteOff LED behavior
- [x] Verified hardware signal integrity via level shifter (SN74AHCT125)
- [x] Added brightness control and color configuration
- [x] Confirmed scalability from single LED → multi-LED chain

[x] Designed and finalized **LED hardware subsystem**
- [x] Implemented proper 5V power routing for LEDs
- [x] Integrated level shifting (3.3V → 5V data)
- [x] Added bulk capacitor (1000µF) for power stability
- [x] Added decoupling capacitor (0.1µF) at IC
- [x] Validated safe and stable operation on KB2040

[x] Built **preset save/load system (4 slots)**
- [x] Assigned presets to second row keys (4–7)
- [x] Implemented hold-to-save interaction (encoder + hold key)
- [x] Implemented tap-to-load interaction (encoder + tap key)
- [x] Added persistent preset storage via JSON
- [x] Supports saving:
  - root note
  - scale
  - transpose
  - octave
  - chord mode
- [x] Ensured non-destructive workflow (no auto-overwrite)

[x] Designed **OLED feedback system for presets**
- [x] Fullscreen message overlay system (no HUD redraw)
- [x] Instant display of:
  - SAVED > P1
  - LOADED > P1
  - EMPTY
- [x] Eliminated flicker, overlap, and redraw artifacts
- [x] Implemented atomic rendering (no visual jump)
- [x] Optimized timing for fast, non-blocking UX

[x] Refined **display architecture (major improvement)**
- [x] Separated HUD rendering from overlay rendering
- [x] Eliminated full bitmap redraws during interaction
- [x] Prevented border/divider “wipe” artifacts
- [x] Implemented layered display system using groups
- [x] Improved perceived performance and responsiveness

[x] Fixed **matrix input ghosting / multi-trigger bug**
- [x] Identified column-related triggering issue
- [x] Verified hardware vs software root cause
- [x] Corrected scanning logic for reliable input detection
- [x] Restored accurate 1:1 key press behavior

[x] Improved **encoder interaction model**
- [x] Refined session-based control logic
- [x] Swapped root note and scale interaction:
  - encoder rotate (held) → root note
  - top keys (held) → scale selection
- [x] Maintained intuitive, performance-friendly UX

[x] Built **maintenance boot mode (via encoder)**
- [x] Hold encoder during boot to enable dev mode
- [x] Normal boot:
  - HID/MIDI-only behavior
  - USB storage disabled
- [x] Dev mode:
  - CIRCUITPY drive enabled
  - Serial enabled
- [x] Eliminates need for physical boot button access

[x] Improved **USB device identity**
- [x] Set custom USB name: "MIDIMAL"
- [x] Clean device recognition on macOS / iOS

[x] Enhanced **development workflow**
- [x] Implemented file-level sync strategy (faster iteration)
- [x] Integrated formatting workflow (Black / auto-format)
- [x] Improved debugging and recovery flow

[x] Finalized **hardware readiness for PCB**
- [x] Validated full wiring stack:
  - matrix
  - OLED (SPI)
  - encoder
  - LED subsystem
- [x] Confirmed firmware/hardware alignment
- [x] Prepared for PCB design and enclosure integration

[x] Completed **functional prototype build**
- [x] 3D printed custom enclosure
- [x] Designed custom keycaps
- [x] Designed encoder knob
- [x] Assembled working physical MIDIMAL unit

[x] Achieved **product-level usability milestone**
- [x] Fast, responsive, real-time playability
- [x] Reliable state + preset system
- [x] Clean, intentional interaction model
- [x] Stable performance across extended use

### In Progress

* [ ] Real life use case testing
* [ ] LED underglow system
* [ ] Custom PCB

### Planned

* [ ] Create a build guide for anyone who wants to build their own MIDIMAL


---

## 🧠 Core Features (In-Progress)

* 4x4 pad grid (16 keys)
* Scale-based play mode (default)
* Chord mode
* Transpose + octave shift
* Select root note play mode
* MIDI channel selection <-- removed feature
* OLED interface
* Rotary encoder control
* LED underglow feedback

---

## 🧰 Hardware (Bill of Materials)

| Component       | Description              |
| --------------- | ------------------------ |
| Microcontroller | Adafruit KB2040 x1       |
| Switches        | Cherry MX / Gateron  x16 |
| Diodes          | 1N4148 x16               |
| Display         | 128x64 SH1106 OLED (SPI) |
| Encoder         | EC11 rotary encoder x1   |
| LEDs            | WS2812B x4 (pixels)      |
| Level Shifter   | 74AHCT125  x1            |
| Capacitor       | 1000µF electrolytic  x1  |
| Capacitor       | 100nF ceramic x1         |
---

## 💻 Firmware

Current firmware development is focused on validating the musical interaction model before full hardware assembly.

* Language: CircuitPython
* MIDI: USB class-compliant MIDI
* Architecture:

  * Matrix scanning
  * Event-based MIDI triggering
  * Scale-aware note mapping (WIP)

---

## Hardware Reference

Current wiring references for the prototype:

- [Connection schematic](docs/MIDIMAL_clean_schematic.png)
- [KiCad-style netlist draft](docs/MIDIMAL_kicad_netlist_final.md)

> Note: These are current prototype references and may change as the breadboard build is tested and refined before PCB design.

## 🔌 Getting Started (WIP)

Instructions coming soon for:

* flashing CircuitPython
* uploading firmware
* wiring prototype

---

## 📁 Repository Structure

```text
MIDIMAL/
  firmware/
  hardware/
  docs/
```

---

## 🎯 Design Philosophy

MIDIMAL is built around one idea:

> **Remove friction between you and making music**

Every design decision prioritizes:

* speed
* feel
* clarity
* creativity

---

## 🛠️ Development Workflow

* Firmware developed locally and synced to board
* CircuitPython auto-reloads on save
* Git used for version control

---

## 🚀 Roadmap

* [ ] Complete firmware v1
* [ ] Build working prototype
* [ ] Design PCB
* [ ] Design enclosure
* [ ] Release build guide

---

## 🤝 Contributing

This project is in early development, but ideas and feedback are welcome.

---

## 📜 License

TBD
