import spidev
import RPi.GPIO as GPIO
import time

# GPIO Pins
DC = 25
RST = 24
BL = 18

# SPI Setup
spi = spidev.SpiDev(0, 0)
spi.max_speed_hz = 1000000  # 1 MHz

# GPIO Setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(DC, GPIO.OUT)
GPIO.setup(RST, GPIO.OUT)
GPIO.setup(BL, GPIO.OUT)
GPIO.output(BL, GPIO.HIGH)  # Turn on backlight

def lcd_reset():
    GPIO.output(RST, GPIO.LOW)
    time.sleep(0.1)
    GPIO.output(RST, GPIO.HIGH)
    time.sleep(0.1)

try:
    spi.open(0, 0)  # Open SPI bus
    lcd_reset()
    GPIO.output(DC, GPIO.LOW)  # Command mode
    spi.xfer([0x29])  # Display ON command
    print("Sent Display ON command.")
except Exception as e:
    print(f"Error: {e}")
finally:
    spi.close()
    GPIO.cleanup()
