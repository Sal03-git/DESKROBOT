import RPi.GPIO as GPIO
import time
import os
from PIL import Image
from lib import LCD_2inch  # Import the LCD library (adjust based on your folder structure)

# Initialize GPIO for touch sensor
touch_pin = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(touch_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# Initialize LCD
def lcd_test():
    try:
        # Create LCD object
        disp = LCD_2inch.LCD_2inch()
        disp.Init()
        disp.clear()  # Clear the screen to start fresh

        # Define the paths to the emotion directories
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
                time.sleep(0.05)  # Shorten display time to 0.05s per frame (faster transition)

        # Start with bootup emotion
        print("Displaying bootup emotion...")
        display_frames(emotion_paths["bootup"])

        # Display neutral emotion, but check touch sensor for changes to happy
        print("Displaying neutral emotion...")
        while True:
            if GPIO.input(touch_pin) == GPIO.HIGH:
                print("Touch detected! Displaying happy emotion...")
                display_frames(emotion_paths["happy"])
                time.sleep(0.5)  # Pause after displaying happy emotion
                print("Returning to neutral emotion...")
            display_frames(emotion_paths["neutral"])

    except KeyboardInterrupt:
        print("Test interrupted")
        disp.module_exit()  # Graceful exit
    except IOError as e:
        print(f"Error: {e}")
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    lcd_test()
