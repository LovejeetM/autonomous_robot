# Autonomous Garden Monitoring Robot

This project details the construction and operation of an autonomous robot designed for garden monitoring. The robot navigates the garden, captures images of plants, and analyzes them using AI.

## Description

The robot utilizes a LiDAR sensor for environmental mapping and obstacle avoidance.  It navigates to identified plant locations, captures images using a Raspberry Pi camera, and leverages AI (specifically, Google's Generative AI API is implied) to analyze the images and provide information about the plants (e.g., health, species). The robot is controlled by a Raspberry Pi Zero 2 W and powered by a combination of a power bank and 18650 batteries.  Movement is achieved using BO motors, and camera orientation is controlled by servo motors.

## Hardware

The following hardware components are used:

*   **Microcontroller:** Raspberry Pi Zero 2 W
*   **Camera:** Raspberry Pi Camera
*   **Drive Motors:** 2 x BO Motors
*   **Camera Positioning:** 2 x Servo Motors
*   **LiDAR Sensor:** VL53L0x
*   **Power:**
    *   Powerbank
    *   2 x 18650 Batteries
*   **Motor Driver:** L298 Motor Driver

## Software Requirements & Libraries

This project relies on the following Python libraries.  It is highly recommended to use a virtual environment (e.g., `venv` or `conda`) to manage these dependencies.
Use code with caution.
Markdown
Adafruit-Blinka==8.45.2
adafruit-circuitpython-busdevice==5.2.9
adafruit-circuitpython-connectionmanager==3.1.1
adafruit-circuitpython-requests==4.1.3
adafruit-circuitpython-typing==1.10.3
adafruit-circuitpython-vl53l0x==3.6.11
Adafruit-PlatformDetect==3.71.0
Adafruit-PureIO==1.1.11
adafruit-python-shell==1.8.1
annotated-types==0.7.0
args==0.1.0
beautifulsoup4==4.12.3
binho-host-adapter==0.1.6
blinker==1.8.2
cachetools==5.3.3
certifi==2020.6.20
chardet==4.0.0
click==8.1.7
clint==0.5.1
colorama==0.4.4
colorzero==1.1
cryptography==3.3.2
distro==1.5.0
flask==3.0.3
google-ai-generativelanguage==0.6.4
google-api-core==2.19.0
google-api-python-client==2.131.0
google-auth==2.29.0
google-auth-httplib2==0.2.0
google-generativeai==0.6.0
googleapis-common-protos==1.63.1
gpiozero==1.6.2
grpcio==1.64.1
grpcio-status==1.62.2
httplib2==0.22.0
idna==2.10
importlib-metadata==7.1.0
itsdangerous==2.2.0
jinja2==3.1.4
Markdown==3.6
markdownify==0.13.1
MarkupSafe==2.1.5
numpy==2.0.0
pathfinding==1.0.10
picamera2==0.3.12
pidng==4.0.9
piexif==1.1.3
Pillow==8.1.2
proto-plus==1.23.0
protobuf==4.25.3
pyasn1==0.6.0
pyasn1-modules==0.4.0
pydantic==2.7.3
pydantic-core==2.18.4
pyftdi==0.55.4
pygame==2.6.0
pyinotify==0.9.6
pyOpenSSL==20.0.1
pyparsing==3.1.2
pyserial==3.5
python-apt==2.2.1
python-prctl==1.7
pyusb==1.2.1
pyxattr==0.7.2
requests==2.25.1
rpi-ws281x==5.0.0
RPi.GPIO==0.7.1
rsa==4.9
simplejpeg==1.7.4
simplejson==3.17.2
six==1.16.0
soupsieve==2.5
spidev==3.5
ssh-import-id==5.10
sysv-ipc==1.1.0
toml==0.10.1
tqdm==4.66.4
typing-extensions==4.12.1
uritemplate==4.1.1
urllib3==1.26.5
v4l2-python3==0.3.2
werkzeug==3.0.3
youtube-dl==2021.6.6
zipp==3.19.1

To install these dependencies, use pip:

```bash
pip install -r requirements.txt
Use code with caution.
(You should create a requirements.txt file and paste the above list into it.)

Software Installation:

Install a compatible operating system on your Raspberry Pi Zero 2 W (e.g., Raspberry Pi OS Lite).

Enable I2C and camera interfaces using raspi-config.

Clone this repository to your Raspberry Pi:

git clone https://github.com/LovejeetM/autonomous_robot/

Bash
Install the required Python libraries (as described in the "requirements.txt" section).

Configuration:

You will likely need to configure your AI API credentials. Store API key in a secure manner (e.g., environment variables) and load them into your Python script. Do not hardcode your API key directly into the code.

Adjust any necessary parameters within the code, such as motor speeds, turning angles, camera resolution, and AI model settings, specific pins for connection.

Usage
Power On: Ensure the batteries are charged and the powerbank is connected. Power on the robot.

Start the Program: Run the main Python script:

python ai.py 

Bash
Monitoring: The robot will begin autonomously exploring the garden, scanning the environment, and analyzing plants.

Troubleshooting
Robot not moving: Check motor connections, motor driver power, and the L298 Motor Driver configuration. Verify that the gpiozero library is correctly installed and that the correct GPIO pins are being used in your code.

LiDAR sensor not working: Ensure the I2C interface is enabled and the sensor is correctly wired. Test the sensor with a simple I2C scanning script to confirm it's detected. Verify the adafruit-circuitpython-vl53l0x library is installed.

Camera not working: Check the camera connection and ensure the camera interface is enabled. Use libcamera-still or libcamera-vid to test basic camera functionality.

AI analysis errors: Verify your API key is correct and you have sufficient API usage credits. Check the API documentation for error codes and troubleshooting tips. Double-check the data format being sent to the API. Consider adding error handling (try-except blocks) around your API calls to gracefully handle potential issues.

Dependencies error: If you encounter an error related to a missing library, double-check that you have installed all dependencies correctly using pip install -r requirements.txt. If the error persists, try creating a fresh virtual environment and reinstalling the dependencies.

Future Improvements
Object Detection: Implement more sophisticated object detection to identify specific plant types or diseases.

Mapping and Localization: Integrate SLAM (Simultaneous Localization and Mapping) for more accurate navigation and map creation.

Web Interface: Create a web interface for remote control, monitoring, and data visualization.

Obstacle Avoidance: Enhance obstacle avoidance using the LiDAR data to navigate complex garden layouts.

Watering System: Add automatic watering system to it.

Contributing
Contributions to this project are welcome! Please follow these guidelines:

Fork the repository.

Create a new branch for your feature/fix.

Commit your changes with clear commit messages.

Submit a pull request.

