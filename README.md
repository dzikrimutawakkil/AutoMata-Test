# NO CODE AUTOMATED TESTING TOOLS

## Introduction
This repository contains an automation testing tools using Python and Appium to test Flutter Android applications. The tools enables automated UI testing to ensure the correctness, realibility, and usability of mobile applications.

## Prerequisites
Before running the tests, ensure you have the following installed:
- [Python](https://www.python.org/downloads/) (Recommended: 3.8+)
- [Appium](http://appium.io/) (Latest version)
- [Appium] Flutter Driver (Installation Key : "--source=npm appium-flutter-driver")
- Android SDK & ADB tools
- Node.js (Required for Appium)
- Java JDK (for Android development)
- [Appium-Python-Client](https://github.com/appium/python-client)

## Installation
1. Clone this repository:
   ```sh
   git clone https://github.com/dzikrimutawakkil/AutoMata-Test.git
   cd your-repo
   ```

## Using AutoMata Test App
This project includes the **AutoMata Test App**, a GUI tool for running automation tests efficiently. Below are the main features and usage guide:

1. **Run Automated Test Tools**: Open the execute file inside dist folder
2. **Upload Test File**: First select and upload your test scripts.
3. **App Installation Options**: Choose an app installation options.
    1. **App already installed**: Requires the package name (e.g., `com.appname`).
    2. **App not installed**: Requires an APK debug file to be uploaded before running tests.
4. **Device List**: A dropdown that displays all connected devices. (If your device not displayed click sync to redetect the devices)
6. **Run Appium Test**: Starts the automated test execution.
7. **Stop Button**: Halts ongoing tests.
7. **Automation Status**: Check the automation test status on the buttom field.

## License
This project is licensed under the MIT License.