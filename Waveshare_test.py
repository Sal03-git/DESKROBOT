import spidev
import RPi.GPIO as GPIO
from PIL import Image, ImageDraw, ImageFont
import time

# GPIO pin definitions
DC = 25   # Data/Command pin
RST = 24  # Reset pin
BL = 18   # Backlight pin (optional)

# Screen resolution
SCREEN_WIDTH = 240
SCREEN_HEIGHT = 240

# SPI setup
spi = spidev.SpiDev(0, 0)  # SPI bus 0, device 0
spi.max_speed_hz = 4000000  # 4 MHz

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(DC, GPIO.OUT)
GPIO.setup(RST, GPIO.OUT)
GPIO.setup(BL, GPIO.OUT)
GPIO.output(BL, GPIO.HIGH)  # Turn on backlight

# LCD commands
LCD_INIT_COMMANDS = [
    # Add specific initialization commands for your LCD model here.
]

def lcd_command(cmd):
    GPIO.output(DC, GPIO.LOW)  # Command mode
    spi.xfer([cmd])

def lcd_data(data):
    GPIO.output(DC, GPIO.HIGH)  # Data mode
    spi.xfer([data])

def lcd_reset():
    GPIO.output(RST, GPIO.LOW)
    time.sleep(0.1)
    GPIO.output(RST, GPIO.HIGH)
    time.sleep(0.1)

def lcd_init():
    lcd_reset()
    for cmd in LCD_INIT_COMMANDS:
        lcd_command(cmd[0])
        for data in cmd[1:]:
            lcd_data(data)
    print("LCD initialized.")

def draw_test_pattern():
    image = Image.new("RGB", (SCREEN_WIDTH, SCREEN_HEIGHT), "black")
    draw = ImageDraw.Draw(image)

    # Draw a red rectangle
    draw.rectangle((10, 10, 100, 100), fill="red")

    # Draw a green circle
    draw.ellipse((120, 120, 180, 180), fill="green")

    # Draw text
    font = ImageFont.load_default()
    draw.text((50, 200), "Hello, LCD!", font=font, fill="white")

    # Convert image to raw RGB data
    raw_data = image.tobytes()
    lcd_display_raw(raw_data)

def lcd_display_raw(data):
    for i in range(0, len(data), 4096):
        lcd_data(data[i:i+4096])

# Main program
try:
    spi.open(0, 0)
    lcd_init()
    draw_test_pattern()
    print("Test pattern displayed.")
except KeyboardInterrupt:
    print("Exiting.")
finally:
    spi.close()
    GPIO.cleanup()
