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

**Current Stage:** Firmware + Prototyping

### Completed

* [x] CircuitPython setup on KB2040
* [x] USB MIDI output working
* [x] Single input → MIDI note
* [x] Multi-input (4 direct pins)
* [x] Matrix scanning (2x2 test)

### Accomplished today (4/4/26)
- [x] Verified KB2040 setup with CircuitPython
- [x] Confirmed USB MIDI output into a software synth
- [x] Tested single-input note triggering
- [x] Tested 4 direct inputs with clean note triggering
- [x] Built and validated 2x2 matrix scan logic
- [x] Added scale-based note mapping
- [x] Added transpose and octave shift logic
- [x] Simulated encoder interaction logic before testing with real hardware

### In Progress

* [ ] Full 4x4 matrix implementation
* [ ] Scale + note mapping system
* [ ] Encoder integration
* [ ] OLED UI system

### Planned

* [ ] Custom PCB
* [ ] Enclosure design (.STL)
* [ ] LED underglow system
* [ ] Preset storage
* [ ] Full menu system

---

## 🧠 Core Features (Planned)

* 4x4 pad grid (16 keys)
* Scale-based play mode (default)
* Chromatic mode
* Chord mode
* Transpose + octave shift
* MIDI channel selection
* OLED menu interface
* Rotary encoder control
* LED underglow feedback

---

## 🧰 Hardware (Bill of Materials)

| Component       | Description              |
| --------------- | ------------------------ |
| Microcontroller | Adafruit KB2040          |
| Switches        | Cherry MX / Gateron      |
| Diodes          | 1N4148                   |
| Display         | 128x64 SH1106 OLED (SPI) |
| Encoder         | EC11 rotary encoder      |
| LEDs            | WS2812B (NeoPixel strip) |
| Level Shifter   | 74AHCT125                |
| Capacitor       | 1000µF electrolytic      |

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

- [Connection schematic](docs/midimal_connection_schematic.png)
- [KiCad-style netlist draft](docs/midimal_kicad_netlist.md)

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
