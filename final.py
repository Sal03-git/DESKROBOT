import time
from board import SCL, SDA
import busio
from adafruit_servokit import ServoKit
import multiprocessing
import RPi.GPIO as GPIO
import os
import sys
import logging
import spidev as SPI
sys.path.append("..")
from lib import LCD_2inch
from PIL import Image, ImageDraw, ImageFont
from random import randint

# Pin configurations
touch_pin = 17
vibration_pin = 22

GPIO.setmode(GPIO.BCM)
GPIO.setup(touch_pin, GPIO.IN)
GPIO.setup(vibration_pin, GPIO.IN)

# LCD configuration
RST = 27
DC = 25
BL = 18
bus = 0
device = 0

kit = ServoKit(channels=16)

# Servo declarations
servoR = kit.servo[5]  # Right arm servo
servoL = kit.servo[11]  # Left arm servo
servoB = kit.servo[13]  # Body rotation servo

frame_count = {'blink': 39, 'happy': 60, 'sad': 47, 'dizzy': 67, 'excited': 24, 'neutral': 61, 'happy2': 20,
               'angry': 20, 'happy3': 26, 'bootup3': 124, 'blink2': 20}

emotion = ['angry', 'sad', 'excited']
normal = ['neutral', 'blink2']

q = multiprocessing.Queue()
event = multiprocessing.Event()

# Sensor check process
def check_sensor():
    previous_state = 1
    current_state = 0
    while True:
        if GPIO.input(touch_pin) == GPIO.HIGH:
            if previous_state != current_state:
                if q.qsize() == 0:
                    event.set()
                    q.put('happy')
                current_state = 1
            else:
                current_state = 0
        if GPIO.input(vibration_pin) == 1:
            print('vibration detected')
            if q.qsize() == 0:
                event.set()
                q.put(emotion[randint(0, 2)])
        time.sleep(0.05)

# Servo control functions
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

def happy():
    servoMed()
    for n in range(5):
        for i in range(0, 120):
            if i <= 30:
                servoR.angle = 90 + i
                servoL.angle = 90 - i
                servoB.angle = 90 - i
            if 30 < i <= 90:
                servoR.angle = 150 - i
                servoL.angle = i + 30
                servoB.angle = i + 30
            if i > 90:
                servoR.angle = i - 30
                servoL.angle = 210 - i
                servoB.angle = 210 - i
            time.sleep(0.004)

def sad():
    servoDown()
    for i in range(0, 60):
        if i <= 15:
            servoB.angle = 90 - i
        if 15 < i <= 45:
            servoB.angle = 60 + i
        if i > 45:
            servoB.angle = 150 - i
        time.sleep(0.09)

def excited():
    servoDown()
    for i in range(0, 120):
        if i <= 30:
            servoB.angle = 90 - i
        if 30 < i <= 90:
            servoB.angle = i + 30
        if i > 90:
            servoB.angle = 210 - i
        time.sleep(0.01)

def show(emotion, count):
    for _ in range(count):
        try:
            disp = LCD_2inch.LCD_2inch()
            disp.Init()
            for i in range(frame_count[emotion]):
                image = Image.open(f'/home/pi/Desktop/EmoBot/emotions/{emotion}/frame{i}.png')
                disp.ShowImage(image)
        except IOError as e:
            logging.info(e)
        except KeyboardInterrupt:
            disp.module_exit()
            servoDown()
            logging.info("quit:")
            exit()

def bootup():
    show('bootup3', 1)
    for _ in range(1):
        p2 = multiprocessing.Process(target=show, args=('blink2', 3))
        p3 = multiprocessing.Process(target=baserotate, args=(90, 45, 0.01))
        p2.start()
        p3.start()
        p3.join()
        p2.join()

if __name__ == '__main__':
    p1 = multiprocessing.Process(target=check_sensor, name='p1')
    p1.start()
    bootup()
    while True:
        if event.is_set():
            if 'p5' in locals():
                p5.terminate()
            
            event.clear()
            current_emotion = q.get()
            q.empty()
            print(current_emotion)

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
            p = multiprocessing.active_children()
            for i in p:
                if i.name not in ['p1', 'p5']:
                    i.terminate()

            neutral = normal[0]
            p5 = multiprocessing.Process(target=show, args=(neutral, 4), name='p5')  # Initialize here
            p6 = multiprocessing.Process(target=baserotate, args=(90, 60, 0.02), name='p6')
            p5.start()
            p6.start()
            p6.join()
            p5.join()
