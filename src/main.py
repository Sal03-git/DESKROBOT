import os
import sys
import time
import logging
import multiprocessing
from random import randint

from board import SCL, SDA
import busio
import spidev as SPI
import RPi.GPIO as GPIO
from adafruit_servokit import ServoKit
from PIL import Image, ImageDraw, ImageFont

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))
from LCD_2inch import LCD_2inch

# ── Paths ─────────────────────────────────────────────────────────────────────
REPO_ROOT    = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
EMOTIONS_DIR = os.path.join(REPO_ROOT, 'emotions')

# ── Pin configurations ────────────────────────────────────────────────────────
TOUCH_PIN     = 17   # GPIO 17 (BCM) — touch sensor on head
VIBRATION_PIN = 22   # GPIO 22 (BCM) — vibration sensor in base

GPIO.setmode(GPIO.BCM)
GPIO.setup(TOUCH_PIN,     GPIO.IN)
GPIO.setup(VIBRATION_PIN, GPIO.IN)

# ── LCD configuration ─────────────────────────────────────────────────────────
RST    = 27
DC     = 25
BL     = 18
bus    = 0
device = 0

# ── Servo setup ───────────────────────────────────────────────────────────────
kit    = ServoKit(channels=16)
servoR = kit.servo[5]   # Right arm  — PCA9685 channel 5
servoL = kit.servo[11]  # Left arm   — PCA9685 channel 11
servoB = kit.servo[13]  # Body rotate — PCA9685 channel 13

# ── Emotion frame counts ──────────────────────────────────────────────────────
frame_count = {
    'blink':   39,
    'happy':   60,
    'sad':     47,
    'dizzy':   67,
    'excited': 24,
    'neutral': 61,
    'happy2':  20,
    'angry':   20,
    'happy3':  26,
    'bootup3': 124,
    'blink2':  20,
}

VIBRATION_EMOTIONS = ['angry', 'sad', 'excited']
IDLE_EMOTIONS      = ['neutral', 'blink2']

# Shared IPC primitives
q     = multiprocessing.Queue()
event = multiprocessing.Event()


# ── Sensor polling process ────────────────────────────────────────────────────
def check_sensor():
    """Runs as a background process. Pushes emotion names onto the queue."""
    previous_touch = 1
    current_touch  = 0

    while True:
        # Touch sensor
        if GPIO.input(TOUCH_PIN) == GPIO.HIGH:
            if previous_touch != current_touch:
                if q.qsize() == 0:
                    event.set()
                    q.put('happy')
            current_touch  = 1
        else:
            current_touch  = 0

        # Vibration sensor
        if GPIO.input(VIBRATION_PIN) == 1:
            print('Vibration detected')
            if q.qsize() == 0:
                event.set()
                q.put(VIBRATION_EMOTIONS[randint(0, 2)])

        time.sleep(0.05)


# ── Servo movement helpers ────────────────────────────────────────────────────
def servoMed():
    servoR.angle = 90
    servoL.angle = 90
    servoB.angle = 90


def servoDown():
    servoR.angle = 0
    servoL.angle = 180
    servoB.angle = 90


def baserotate(reference, change, timedelay):
    for i in range(reference, reference + change, 1):
        servoB.angle = i
        time.sleep(timedelay)
    for j in range(reference + change, reference - change, -1):
        servoB.angle = j
        time.sleep(timedelay)
    for k in range(reference - change, reference, 1):
        servoB.angle = k
        time.sleep(timedelay)


def HandDownToUp(start, end, timedelay):
    for i, j in zip(range(start, end, 1), range((180 - start), (180 - end), -1)):
        servoR.angle = i
        servoL.angle = j
        time.sleep(timedelay)


def HandUpToDown(start, end, timedelay):
    for i, j in zip(range(start, end, -1), range((180 - start), (180 - end), 1)):
        servoR.angle = i
        servoL.angle = j
        time.sleep(timedelay)


# ── Emotion servo sequences ───────────────────────────────────────────────────
def happy():
    servoMed()
    for _ in range(5):
        for i in range(0, 120):
            if i <= 30:
                servoR.angle = 90 + i
                servoL.angle = 90 - i
                servoB.angle = 90 - i
            elif 30 < i <= 90:
                servoR.angle = 150 - i
                servoL.angle = i + 30
                servoB.angle = i + 30
            else:
                servoR.angle = i - 30
                servoL.angle = 210 - i
                servoB.angle = 210 - i
            time.sleep(0.004)


def sad():
    servoDown()
    for i in range(0, 60):
        if i <= 15:
            servoB.angle = 90 - i
        elif 15 < i <= 45:
            servoB.angle = 60 + i
        else:
            servoB.angle = 150 - i
        time.sleep(0.09)


def excited():
    servoDown()
    for i in range(0, 120):
        if i <= 30:
            servoB.angle = 90 - i
        elif 30 < i <= 90:
            servoB.angle = i + 30
        else:
            servoB.angle = 210 - i
        time.sleep(0.01)


# ── LCD animation ─────────────────────────────────────────────────────────────
def show(emotion_name, count):
    """Display the PNG frame animation for an emotion on the LCD."""
    for _ in range(count):
        try:
            disp = LCD_2inch()
            disp.Init()
            for i in range(frame_count[emotion_name]):
                frame_path = os.path.join(EMOTIONS_DIR, emotion_name, f'frame{i}.png')
                image = Image.open(frame_path)
                disp.ShowImage(image)
        except IOError as e:
            logging.info(e)
        except KeyboardInterrupt:
            disp.module_exit()
            servoDown()
            logging.info("Interrupted — exiting.")
            exit()


def bootup():
    show('bootup3', 1)
    p2 = multiprocessing.Process(target=show,       args=('blink2', 3))
    p3 = multiprocessing.Process(target=baserotate, args=(90, 45, 0.01))
    p2.start()
    p3.start()
    p3.join()
    p2.join()


# ── Main loop ─────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    # Sensor process runs for the entire lifetime of the program
    p1 = multiprocessing.Process(target=check_sensor, name='p1')
    p1.start()

    bootup()

    while True:
        if event.is_set():
            # Kill the idle animation if it's running
            if 'p5' in locals():
                p5.terminate()

            event.clear()
            current_emotion = q.get()
            q.empty()
            print(f'Emotion triggered: {current_emotion}')

            p2 = multiprocessing.Process(target=show, args=(current_emotion, 4))

            if current_emotion == 'happy':
                p4 = multiprocessing.Process(target=happy)
            elif current_emotion == 'sad':
                p4 = multiprocessing.Process(target=sad)
            elif current_emotion == 'excited':
                p4 = multiprocessing.Process(target=excited)
            else:
                continue

            p2.start()
            p4.start()
            p2.join()
            p4.join()

        else:
            # Terminate any stale children (except sensor p1 and idle p5)
            for child in multiprocessing.active_children():
                if child.name not in ['p1', 'p5']:
                    child.terminate()

            # Idle animation + gentle body sway
            p5 = multiprocessing.Process(target=show,       args=('neutral', 4), name='p5')
            p6 = multiprocessing.Process(target=baserotate, args=(90, 60, 0.02), name='p6')
            p5.start()
            p6.start()
            p6.join()
            p5.join()
