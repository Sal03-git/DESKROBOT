import time
from board import SCL, SDA
import busio
from adafruit_servokit import ServoKit
import RPi.GPIO as GPIO
from lib import LCD_2inch
from PIL import Image

# Pin configurations
touch_pin = 17
vibration_pin = 22

GPIO.setmode(GPIO.BCM)
GPIO.setup(touch_pin, GPIO.IN)
GPIO.setup(vibration_pin, GPIO.IN)

# PCA9685 configuration
kit = ServoKit(channels=16)

# Servo declarations
servoR = kit.servo[0]  # Right arm servo
servoL = kit.servo[1]  # Left arm servo
servoB = kit.servo[2]  # Body rotation servo

# LCD configuration
disp = LCD_2inch.LCD_2inch()
try:
    disp.Init()
    print("LCD initialized successfully.")
except Exception as e:
    print(f"LCD initialization failed: {e}")

def servoMed():
    """Set all servos to the middle position."""
    print("Setting servos to neutral positions...")
    servoR.angle = 90
    servoL.angle = 90
    servoB.angle = 90
    print("Servos set to neutral positions.")

def check_sensors():
    """Check touch and vibration sensors."""
    print("Starting sensor monitoring...")
    while True:
        if GPIO.input(touch_pin) == GPIO.HIGH:
            print("Touch sensor triggered.")
            servoMed()
        if GPIO.input(vibration_pin) == GPIO.HIGH:
            print("Vibration sensor triggered.")
            servoB.angle = 180  # Example action for vibration
        time.sleep(0.05)

if __name__ == "__main__":
    try:
        servoMed()  # Initialize servos to neutral position

        # Test LCD display with a blank image
        image = Image.new("RGB", (320, 240), "blue")  # Replace with your resolution
        disp.ShowImage(image)
        print("Test image displayed on LCD.")

        check_sensors()  # Start sensor monitoring
    except KeyboardInterrupt:
        GPIO.cleanup()
        print("Program terminated.")
