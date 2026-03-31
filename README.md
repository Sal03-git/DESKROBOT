# 🤖 EMO — Emotion-Expressive Desk Robot

<p align="center">
  <img src="docs/assets/emo_preview.png" alt="EMO Desk Robot" width="300"/>
</p>

A Raspberry Pi-powered desk companion robot that expresses emotions through an LCD display and reacts to physical interactions via touch and vibration sensors. Built for the **Automatic Control** course at the Arab Academy for Science, Technology and Maritime Transport (AASTMT), December 2024.

---

## Table of Contents

- [Overview](#overview)
- [Hardware](#hardware)
  - [Components](#components)
  - [Wiring Summary](#wiring-summary)
- [Software Architecture](#software-architecture)
- [Repository Structure](#repository-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Running EMO](#running-emo)
  - [Autostart on Boot](#autostart-on-boot)
- [Emotions & Behaviors](#emotions--behaviors)
- [Testing Individual Components](#testing-individual-components)
- [Authors](#authors)

---

## Overview

EMO is a 3D-printed desk robot with a three-part chassis (base, body, head). It uses a **Raspberry Pi 3** as its central processing unit and coordinates three subsystems in parallel using Python's `multiprocessing` module:

- **Sensors** — A touch sensor on the head and a vibration sensor in the base continuously poll for user interaction.
- **Servos** — Three SG90 servo motors (right arm, left arm, body rotation) produce synchronized movement sequences matched to each emotion.
- **LCD Display** — A Waveshare 2-inch SPI LCD renders animated PNG frame sequences to express a range of facial emotions.

When idle, EMO plays a looping neutral animation while slowly rotating its body. Touching the head triggers a happy response; knocking or vibrating the base triggers a random emotion (angry, sad, or excited).

---

## Hardware

### Components

| Component | Model | Qty | Notes |
|-----------|-------|-----|-------|
| Microcontroller | Raspberry Pi 3 Model B | 1 | Powered via fast-charging 5 V micro-USB |
| Servo Driver | PCA9685 (16-channel PWM) | 1 | Powered by stepped-down battery supply |
| Servo Motors | SG90 | 3 | Right arm (ch 5), Left arm (ch 11), Body (ch 13) |
| LCD Display | Waveshare 2-inch SPI LCD | 1 | SPI bus 0, device 0 |
| Touch Sensor | TTP223B capacitive | 1 | GPIO 17 (BCM), mounted on head |
| Vibration Sensor | SW-18020P | 1 | GPIO 22 (BCM), mounted in base |
| Batteries | 3.7 V Li-ion × 2 | 2 | Series = 7.4 V input to step-down |
| Voltage Regulator | DC-DC step-down | 1 | 7.4 V → 5 V for PCA9685 |
| Chassis | PLA+ 3D print | — | Base / Body / Head |

### Wiring Summary

```
Raspberry Pi 3
├── I²C (SDA GPIO2, SCL GPIO3)  →  PCA9685
│   ├── Channel  5              →  Right Arm Servo (servoR)
│   ├── Channel 11              →  Left Arm Servo  (servoL)
│   └── Channel 13              →  Body Servo      (servoB)
│
├── SPI (bus 0, device 0)       →  Waveshare 2" LCD
│   ├── RST  GPIO 27
│   ├── DC   GPIO 25
│   └── BL   GPIO 18
│
├── GPIO 17 (BCM, INPUT)        →  Touch Sensor
└── GPIO 22 (BCM, INPUT)        →  Vibration Sensor
```

---

## Software Architecture

`src/main.py` spawns three concurrent processes:

```
main
├── p1  check_sensor()       — polls touch & vibration GPIOs, pushes emotion events to Queue
├── p5  show(neutral, ...)   — idle LCD animation loop (runs when no event pending)
├── p6  baserotate(...)      — idle body sway (runs alongside p5)
└── On event:
    ├── p2  show(emotion, 4) — plays emotion animation on LCD
    └── p4  happy/sad/excited() — drives servos for matching movement
```

Emotion names map to subdirectories under `emotions/`, each containing sequentially numbered PNG frames (`frame0.png`, `frame1.png`, …). The `frame_count` dictionary in `main.py` defines the total frame count per emotion.

---

## Repository Structure

```
DESKROBOT/
│
├── src/
│   └── main.py                      # Entry point — full integrated robot firmware
│
├── tests/
│   ├── test_servo.py                # Standalone servo sweep test
│   ├── test_servo_with_driver.py    # PCA9685 driver + servo test
│   ├── test_servo_touch.py          # Servo response to touch sensor
│   ├── test_touch_sensor.py         # Touch sensor GPIO read test
│   ├── test_vibration_sensor.py     # Vibration sensor GPIO read test
│   ├── test_lcd.py                  # LCD initialization and display test
│   ├── test_emotions.py             # Emotion animation playback test
│   ├── test_touch_emotions.py       # Touch sensor + LCD emotion test
│   └── test_waveshare.py            # Waveshare display driver test
│
├── emotions/
│   ├── angry/      frame0.png … frameN.png
│   ├── blink/      frame0.png … frameN.png
│   ├── blink2/     frame0.png … frameN.png
│   ├── bootup3/    frame0.png … frameN.png
│   ├── dizzy/      frame0.png … frameN.png
│   ├── excited/    frame0.png … frameN.png
│   ├── happy/      frame0.png … frameN.png
│   ├── happy2/     frame0.png … frameN.png
│   ├── happy3/     frame0.png … frameN.png
│   ├── neutral/    frame0.png … frameN.png
│   └── sad/        frame0.png … frameN.png
│
├── lib/
│   └── LCD_2inch.py                 # Waveshare 2" SPI LCD driver
│
├── docs/
│   └── autostart.md                 # How to make EMO launch on Raspberry Pi boot
│
├── requirements.txt
└── README.md
```

> **Note on `emotions/`:** The PNG frame assets are large and are not tracked in this repository by default. Place the emotion folders (sourced from the [original Emo project](https://github.com/CodersCafeTech/Emo)) at `emotions/` relative to the repo root, then update the path in `src/main.py` accordingly (see [Getting Started](#getting-started)).

---

## Getting Started

### Prerequisites

- Raspberry Pi 3 (or later) running **Raspberry Pi OS (Bullseye or later)**
- Python 3.7+
- I²C enabled (`sudo raspi-config` → Interface Options → I2C → Enable)
- SPI enabled (`sudo raspi-config` → Interface Options → SPI → Enable)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/Sal03-git/DESKROBOT.git
cd DESKROBOT

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Place your emotion PNG assets
#    Copy each emotion folder into emotions/
#    e.g. emotions/happy/frame0.png … frame59.png

# 4. Update the emotions path in src/main.py if needed
#    Default path: emotions/ (relative to repo root)
```

### Running EMO

```bash
python src/main.py
```

EMO will play the boot animation, then enter the idle loop. Touch the sensor on the head or tap the base to trigger emotional responses.

### Autostart on Boot

To have EMO start automatically when the Raspberry Pi powers on, see [`docs/autostart.md`](docs/autostart.md).

The short version:

```bash
# Edit the crontab
crontab -e

# Add this line (adjust path as needed)
@reboot python /home/user/DESKROBOT/src/main.py &
```

---

## Emotions & Behaviors

| Trigger | Emotion | Servo Behavior | Frame Count |
|---------|---------|----------------|-------------|
| Boot | `bootup3` | Idle sway | 124 |
| Idle | `neutral` | Slow body rotation | 61 |
| Idle blink | `blink2` | Slow body rotation | 20 |
| Touch sensor | `happy` | Arms wave up/down, body oscillates | 60 |
| Vibration (random) | `angry` | — | 20 |
| Vibration (random) | `sad` | Arms down, body rocks side to side | 47 |
| Vibration (random) | `excited` | Arms down, body fast oscillation | 24 |

Additional emotion assets available: `blink` (39 frames), `dizzy` (67), `happy2` (20), `happy3` (26).

---

## Testing Individual Components

Use the scripts in `tests/` to validate each subsystem independently before running the full firmware.

```bash
# Test servos via PCA9685 driver
python tests/test_servo_with_driver.py

# Test touch sensor GPIO reading
python tests/test_touch_sensor.py

# Test vibration sensor GPIO reading
python tests/test_vibration_sensor.py

# Test LCD display initialization
python tests/test_lcd.py

# Test emotion animation playback on LCD
python tests/test_emotions.py

# Test touch → emotion response (no servos)
python tests/test_touch_emotions.py

# Test servos responding to touch
python tests/test_servo_touch.py
```

---

## Authors

**Salaheldeen Abdelmoneim** — [github.com/Sal03-git](https://github.com/Sal03-git)  
**Galaleldeen Abdelmoneim**

Arab Academy for Science, Technology and Maritime Transport — Electronics & Communications Engineering, 2024

Emotion PNG assets adapted from [CodersCafeTech/Emo](https://github.com/CodersCafeTech/Emo).
