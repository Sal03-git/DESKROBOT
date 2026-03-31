import time
import os
from PIL import Image
import RPi.GPIO as GPIO
from lib import LCD_2inch  # Adjust based on your library location and installation

# GPIO setup for Touch Sensor
touch_pin = 17  # GPIO 17, change if your physical wiring differs
GPIO.setmode(GPIO.BCM)
GPIO.setup(touch_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# Initialize the LCD
disp = LCD_2inch.LCD_2inch()  # Assumes this constructor initializes SPI and GPIO
disp.Init()
disp.clear()

# Define paths to the emotion directories
emotion_paths = {
    "bootup": "/home/user/Desktop/Emo-main/Code/emotions/bootup",
    "happy": "/home/user/Desktop/Emo-main/Code/emotions/happy",
    "neutral": "/home/user/Desktop/Emo-main/Code/emotions/neutral"
}

def display_frames(emotion_path):
    """Display frames from the emotion directory"""
    frames = sorted([f for f in os.listdir(emotion_path) if f.endswith('.png')])
    images = [Image.open(os.path.join(emotion_path, frame)) for frame in frames]
    for image in images:
        disp.ShowImage(image)  # Display image on the LCD
        time.sleep(0.05)  # Shorten display time to 0.05s per frame

def lcd_test():
    try:
        # Start with bootup emotion
        print("Displaying bootup emotion...")
        display_frames(emotion_paths["bootup"])

        # Display emotions based on touch
        print("Displaying neutral emotion...")
        while True:
            if GPIO.input(touch_pin):
                print("Touch detected! Displaying happy emotion...")
                display_frames(emotion_paths["happy"])
            else:
                display_frames(emotion_paths["neutral"])

    except KeyboardInterrupt:
        print("Test interrupted")
        disp.module_exit()  # Graceful exit
    except IOError as e:
        print(f"Error: {e}")
    finally:
        GPIO.cleanup()  # Clean up GPIO to ensure we leave them in a safe state

if __name__ == "__main__":
    lcd_test()
