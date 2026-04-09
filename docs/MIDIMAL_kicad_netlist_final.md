# MIDIMAL — KiCad Netlist + PCB Checklist (Final)

## 1. Top-Level Net Summary

### KB2040 → Matrix
- ROW0 → D2
- ROW1 → D3
- ROW2 → D4
- ROW3 → D5
- COL0 → D6
- COL1 → D7
- COL2 → D8
- COL3 → D9

### KB2040 → OLED (SPI)
- 3V → VCC
- G → GND
- SCK → CLK
- MOSI → MOSI
- D0 → DC
- D1 → CS
- D10 → RES

### KB2040 → Encoder
- A0 → ENC_A
- A1 → ENC_B
- A2 → ENC_SW
- G → GND

### KB2040 → LED Subsystem
- A3 → U1 pin 2 (1A)
- 5V_RAW → U1 pin 14 (VCC)
- 5V_RAW → LED VDD
- G → U1 pin 7 (GND)
- G → LED GND

---

## 2. U1 — SN74AHCT125 (DIP-14)

| Pin | Name |       Net       |   Connection   |
|-----|------|-----------------|----------------|
| 1   | 1OE  | GND             | Enable         |
| 2   | 1A   | LED_DATA_3V3    | From KB2040 A3 |
| 3   | 1Y   | LED_DATA_5V     | To R1          |
| 7   | GND  | GND             | Ground         |
| 14  | VCC  | 5V_RAW          | Power          |

Unused channels:
- Tie OE HIGH

Pin 4 (2OE) → 5V
Pin 5 (2A)  → GND

Pin 10 (3OE) → 5V
Pin 9 (3A)   → GND

Pin 13 (4OE) → 5V
Pin 12 (4A)  → GND

Pin 6, 8, 11 → Unconnected

---

## 3. LED Path

- U1 pin 3 → R1 (220Ω)
- R1 → LED DIN
- LED chain via DOUT → next DIN

Capacitors:
- C1 = 1000µF (bulk)
- C2 = 100nF (0.1µF) ceramic / monolithic decoupling capacitor
- Place C2 directly between U1 pin 14 (VCC) and U1 pin 7 (GND)
- Ensure first LED orientation is correct (DIN vs DOUT)
- Place R1 (220Ω) as close as possible to U1 pin 3 (1Y)

---

## 4. Matrix Key Mapping

Rule:
ROW → switch → diode → COLUMN

Diode direction:
Cathode → column

Example:
K12 = D2 → SW → diode → D6

---

## 5. Reference Designators

|    Ref   |      Part      |
|----------|----------------|
| U1       | SN74AHCT125    |
| R1       | 220Ω           |
| C1       | 1000µF         |
| C2       | 100 nF (0.1µF) |
| SW1–SW16 | Key switches   |
| DM1–DM16 | Diodes         |
| J1       | OLED header    |
| J2       | Encoder        |
| J3       | LED            |
| U2       | KB2040         |

---

## 6. PCB Checklist

### Power
- 5V_RAW → LED + Shifter
- 3V → OLED
- Shared ground everywhere

### Placement
- Matrix = grid aligned
- OLED = edge header
- Encoder = top-right
- U1 + R1 close together
- C1 bulk capacitor near first LED power entry
- C2 directly next to U1

### Routing
- Keep LED data short
- Keep SPI clean
- Group rows/cols cleanly

### Test Points (IMPORTANT)
- ROW0–ROW3
- COL0–COL3
- LED_DATA_3V3
- LED_DATA_5V
- 5V_RAW
- 3V3
- GND

---

## 7. Final Notes

- This matches firmware exactly
- Safe for PCB prototyping
- LEDs verified working
- No hardware changes expected
