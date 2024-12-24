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

# LCD commands (Replace with actual commands for your model)
LCD_INIT_COMMANDS = [
    # Add your LCD-specific initialization commands here
]

# Functions for SPI communication and control
def lcd_command(cmd):
    """Send a command to the LCD."""
    GPIO.output(DC, GPIO.LOW)  # Command mode
    spi.xfer([cmd])

def lcd_data(data):
    """Send data to the LCD."""
    GPIO.output(DC, GPIO.HIGH)  # Data mode
    if isinstance(data, int):  # Single byte
        spi.xfer([data])
    elif isinstance(data, (bytes, bytearray, list)):  # Multiple bytes
        spi.xfer(list(data))
    else:
        raise ValueError("Unsupported data type in lcd_data")

def lcd_reset():
    """Reset the LCD."""
    GPIO.output(RST, GPIO.LOW)
    time.sleep(0.1)
    GPIO.output(RST, GPIO.HIGH)
    time.sleep(0.1)

def lcd_init():
    """Initialize the LCD."""
    lcd_reset()
    for cmd in LCD_INIT_COMMANDS:
        lcd_command(cmd[0])
        for data in cmd[1:]:
            lcd_data(data)
    print("LCD initialized.")

def lcd_display_raw(data):
    """Send raw data to the LCD."""
    if isinstance(data, (bytes, bytearray)):
        data = list(data)
    lcd_data(data)

# Test pattern display
def draw_test_pattern():
    """Draw and display a test pattern on the LCD."""
    # Create a blank image
    image = Image.new("RGB", (SCREEN_WIDTH, SCREEN_HEIGHT), "black")
    draw = ImageDraw.Draw(image)

    # Draw a red rectangle
    draw.rectangle((10, 10, 100, 100), fill="red")

    # Draw a green circle
    draw.ellipse((120, 120, 180, 180), fill="green")

    # Draw some text
    font = ImageFont.load_default()
    draw.text((50, 200), "Hello, LCD!", font=font, fill="white")

    # Convert image to raw RGB data
    raw_data = image.convert("RGB").tobytes()
    lcd_display_raw(raw_data)

# Main program
try:
    spi.open(0, 0)  # Open SPI bus
    lcd_init()      # Initialize the LCD
    draw_test_pattern()  # Draw and display a test pattern
    print("Test pattern displayed.")
except KeyboardInterrupt:
    print("\nExiting.")
finally:
    spi.close()  # Close SPI bus
    GPIO.cleanup()  # Reset GPIO pins
