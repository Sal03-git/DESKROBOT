from adafruit_servokit import ServoKit
import time

# Initialize PCA9685 with 16 channels
kit = ServoKit(channels=16)

def test_two_servos():
    print("Starting servo test for 2 servos...")
    while True:
        try:
            # Move Servo 1 (Channel 0) to different angles
            print("Moving Servo 1 (Channel 0) to 0°")
            kit.servo[0].angle = 0
            time.sleep(1)

            print("Moving Servo 1 (Channel 0) to 90°")
            kit.servo[0].angle = 90
            time.sleep(1)

            print("Moving Servo 1 (Channel 0) to 180°")
            kit.servo[0].angle = 180
            time.sleep(1)

            # Move Servo 2 (Channel 1) to different angles
            print("Moving Servo 2 (Channel 1) to 0°")
            kit.servo[1].angle = 0
            time.sleep(1)

            print("Moving Servo 2 (Channel 1) to 90°")
            kit.servo[1].angle = 90
            time.sleep(1)

            print("Moving Servo 2 (Channel 1) to 180°")
            kit.servo[1].angle = 180
            time.sleep(1)
        except KeyboardInterrupt:
            print("\nServo test stopped.")
            break

# Run the servo test function
test_two_servos()
