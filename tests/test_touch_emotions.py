import time
import RPi.GPIO as GPIO
from adafruit_servokit import ServoKit

# Pin configurations
touch_pin = 17

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(touch_pin, GPIO.IN)

# Initialize the PCA9685 Servo Driver
kit = ServoKit(channels=16)

# Assign servos to channels
servoR = kit.servo[0]  # Right arm servo on channel 0
servoL = kit.servo[1]  # Left arm servo on channel 1

def move_servos():
    servoR.angle = 0  # Move right arm to 0 degrees
    servoL.angle = 180  # Move left arm to 180 degrees
    time.sleep(1)
    servoR.angle = 90  # Reset right arm to 90 degrees
    servoL.angle = 90  # Reset left arm to 90 degrees

try:
    print("Touch sensor test. Press the touch sensor to move servos.")
    while True:
        if GPIO.input(touch_pin) == GPIO.HIGH:  # If touch sensor is pressed
            print("Touch detected!")
            move_servos()
        time.sleep(0.1)
except KeyboardInterrupt:
    print("Exiting program.")
finally:
    GPIO.cleanup()
