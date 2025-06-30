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

To install these dependencies, use pip:

```bash
pip install -r requirements.txt

```

## Software Installation:

Install a compatible operating system on your Raspberry Pi Zero 2 W (e.g., Raspberry Pi OS Lite).

Enable I2C and camera interfaces using raspi-config.

Clone this repository to your Raspberry Pi:

git clone https://github.com/LovejeetM/autonomous_robot/


Install the required Python libraries (as described in the "requirements.txt" section).

## Configuration:

You will likely need to configure your AI API credentials. Store API key in a secure manner (e.g., environment variables) and load them into your Python script. Do not hardcode your API key directly into the code.

Adjust any necessary parameters within the code, such as motor speeds, turning angles, camera resolution, and AI model settings, specific pins for connection.

## Usage

Power On: Ensure the batteries are charged and the powerbank is connected. Power on the robot.

Start the Program: Run the main Python script:

python ai.py 


Monitoring: The robot will begin autonomously exploring the garden, scanning the environment, and analyzing plants.

## Troubleshooting

Robot not moving: Check motor connections, motor driver power, and the L298 Motor Driver configuration. Verify that the gpiozero library is correctly installed and that the correct GPIO pins are being used in your code.

LiDAR sensor not working: Ensure the I2C interface is enabled and the sensor is correctly wired. Test the sensor with a simple I2C scanning script to confirm it's detected. Verify the adafruit-circuitpython-vl53l0x library is installed.

Camera not working: Check the camera connection and ensure the camera interface is enabled. Use libcamera-still or libcamera-vid to test basic camera functionality.

AI analysis errors: Verify your API key is correct and you have sufficient API usage credits. Check the API documentation for error codes and troubleshooting tips. Double-check the data format being sent to the API. Consider adding error handling (try-except blocks) around your API calls to gracefully handle potential issues.

Dependencies error: If you encounter an error related to a missing library, double-check that you have installed all dependencies correctly using pip install -r requirements.txt. If the error persists, try creating a fresh virtual environment and reinstalling the dependencies.

## Future Improvements

Object Detection: Implement more sophisticated object detection to identify specific plant types or diseases.

Mapping and Localization: Integrate SLAM (Simultaneous Localization and Mapping) for more accurate navigation and map creation.

Web Interface: Create a web interface for remote control, monitoring, and data visualization.

Obstacle Avoidance: Enhance obstacle avoidance using the LiDAR data to navigate complex garden layouts.

Watering System: Add automatic watering system to it.

## Contributing

Contributions to this project are welcome! Please follow these guidelines:

Fork the repository.

Create a new branch for your feature/fix.

Commit your changes with clear commit messages.

Submit a pull request.

