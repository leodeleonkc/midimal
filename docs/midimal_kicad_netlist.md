# MIDIMAL — KiCad-Style Netlist Table (Current Draft)

This is a human-readable netlist draft based on the currently locked pin map.

## 1) Nets by subsystem

### KB2040 to key matrix
| Net | From | To |
|---|---|---|
| ROW0 | KB2040 D2 | Matrix row 0 |
| ROW1 | KB2040 D3 | Matrix row 1 |
| ROW2 | KB2040 D4 | Matrix row 2 |
| ROW3 | KB2040 D5 | Matrix row 3 |
| COL0 | KB2040 D6 | Matrix column 0 |
| COL1 | KB2040 D7 | Matrix column 1 |
| COL2 | KB2040 D8 | Matrix column 2 |
| COL3 | KB2040 D9 | Matrix column 3 |

### KB2040 to OLED
| Net | From | To |
|---|---|---|
| OLED_GND | KB2040 G | OLED GND |
| OLED_3V3 | KB2040 3V | OLED VCC |
| OLED_SCK | KB2040 CLK | OLED CLK |
| OLED_MOSI | KB2040 MOSI | OLED MOSI |
| OLED_RES | KB2040 TX | OLED RES |
| OLED_DC | KB2040 D10 | OLED DC |
| OLED_CS | KB2040 RX | OLED CS |

### KB2040 to rotary encoder
| Net | From | To |
|---|---|---|
| ENC_A | KB2040 A0 | Encoder A |
| ENC_B | KB2040 A1 | Encoder B |
| ENC_SW | KB2040 A2 | Encoder SW |
| GND | KB2040 G | Encoder GND |

### KB2040 to external LED subsystem
| Net | From | To |
|---|---|---|
| LED_DATA_3V3 | KB2040 A3 | 74AHCT125 input |
| LED_5V | KB2040 RAW | WS2812B +5V |
| GND | KB2040 G | WS2812B GND |
| SHIFTER_5V | KB2040 RAW | 74AHCT125 VCC |
| SHIFTER_GND | KB2040 G | 74AHCT125 GND |

## 2) Matrix per-key net table

**Diode rule:** `ROW -> switch -> diode -> COLUMN`  
**Diode orientation:** cathode (striped end) toward the **column** side.

| Key | Row net | Column net | Connection rule |
|---|---|---|---|
| K12 | ROW0 | COL0 | D2 -> switch -> diode -> D6 |
| K13 | ROW0 | COL1 | D2 -> switch -> diode -> D7 |
| K14 | ROW0 | COL2 | D2 -> switch -> diode -> D8 |
| K15 | ROW0 | COL3 | D2 -> switch -> diode -> D9 |
| K08 | ROW1 | COL0 | D3 -> switch -> diode -> D6 |
| K09 | ROW1 | COL1 | D3 -> switch -> diode -> D7 |
| K10 | ROW1 | COL2 | D3 -> switch -> diode -> D8 |
| K11 | ROW1 | COL3 | D3 -> switch -> diode -> D9 |
| K04 | ROW2 | COL0 | D4 -> switch -> diode -> D6 |
| K05 | ROW2 | COL1 | D4 -> switch -> diode -> D7 |
| K06 | ROW2 | COL2 | D4 -> switch -> diode -> D8 |
| K07 | ROW2 | COL3 | D4 -> switch -> diode -> D9 |
| K00 | ROW3 | COL0 | D5 -> switch -> diode -> D6 |
| K01 | ROW3 | COL1 | D5 -> switch -> diode -> D7 |
| K02 | ROW3 | COL2 | D5 -> switch -> diode -> D8 |
| K03 | ROW3 | COL3 | D5 -> switch -> diode -> D9 |

## 3) LED shifter stage

| Net | From | To |
|---|---|---|
| LED_DATA_3V3 | KB2040 A3 | 74AHCT125 input |
| LED_DATA_5V | 74AHCT125 output | 220Ω resistor input |
| LED_DATA_SERIES | 220Ω resistor output | WS2812B DIN |
| LED_5V | KB2040 RAW | WS2812B +5V |
| GND | KB2040 G | WS2812B GND |
| LED_BULK_CAP_POS | 1000µF capacitor + | WS2812B +5V |
| LED_BULK_CAP_NEG | 1000µF capacitor - | WS2812B GND |

## 4) Suggested PCB grouping

| Group | Nets / parts |
|---|---|
| Matrix zone | D2–D9, 16 switches, 16 diodes |
| Display zone | CLK, MOSI, RX, D10, TX, 3V, G |
| Encoder zone | A0, A1, A2, G |
| LED zone | A3, 74AHCT125, resistor, capacitor, RAW, G |

## 5) Notes before PCB

- Keep the matrix traces grouped and consistent by row/column.
- Keep the OLED header as a compact dedicated block.
- Place the encoder close to the top-right physical corner.
- Place the LED shifter close to the microcontroller, and the bulk capacitor close to LED power entry.
- Final PCB should still be validated against the exact KB2040 footprint and the exact OLED module footprint you receive.
