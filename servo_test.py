from adafruit_servokit import ServoKit
import time

# Initialize the ServoKit for a 16-channel PCA9685
kit = ServoKit(channels=16)

# Function to test servos
def test_servos():
    print("Testing servo movement...")
    while True:
        try:
            # Move servo on channel 0
            print("Moving servo on channel 0 to 0 degrees")
            kit.servo[0].angle = 0
            time.sleep(1)

            print("Moving servo on channel 0 to 90 degrees")
            kit.servo[0].angle = 90
            time.sleep(1)

            print("Moving servo on channel 0 to 180 degrees")
            kit.servo[0].angle = 180
            time.sleep(1)

            # Move servo on channel 1
            print("Moving servo on channel 1 to 0 degrees")
            kit.servo[1].angle = 0
            time.sleep(1)

            print("Moving servo on channel 1 to 90 degrees")
            kit.servo[1].angle = 90
            time.sleep(1)

            print("Moving servo on channel 1 to 180 degrees")
            kit.servo[1].angle = 180
            time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping servo test.")
            break

# Run the test function
test_servos()
