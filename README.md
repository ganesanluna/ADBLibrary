ADBLibrary for Robot Framework
==============================

ADBLibrary is a custom Robot Framework library that provides Android Debug Bridge (ADB) functionalities such as:

- Executing 'adb' commands
- Running 'adb shell' commands
- Managing connected Android devices
- Capturing outputs from Android devices

This library is useful for Android client testing and automation scenarios involving ADB.

-------------------------------------------------------------------------------

PREREQUISITES
=============

Before using this library, ensure the following are installed on your system:

1. ADB (Android Debug Bridge)
   ---------------------------------

   ADB is required to communicate with Android devices.

   On Ubuntu/Debian systems:
   ``` sh
       $ sudo apt-get update
       $ sudo apt-get install adb
    ```
   On macOS using Homebrew:
   ```
       $ brew install android-platform-tools
    ```
   Alternatively, download ADB tools from:
       https://developer.android.com/studio/releases/platform-tools

2. Root Access (IMPORTANT)
   ---------------------------------

   If you want to access the **full set of functionalities** provided by ADBLibrary,
   your Android device must be connected with **root access enabled**.

-------------------------------------------------------------------------------

INSTALLATION
============

1. Clone the repository (if not already):

       $ git clone https://github.com/yourusername/ADBLibrary.git
       $ cd ADBLibrary

2. Install Python dependencies:

       $ pip install -r requirements.txt

   Note: It is recommended to use a virtual environment.

3. (Optional) Reload your profile if 'adb' is not recognized:

       $ source ~/.profile

-------------------------------------------------------------------------------

SETUP
=====

Refer to the following setup diagram to connect your Android device and verify ADB:

![Setup](doc/IMAGE1.png)

-------------------------------------------------------------------------------

EXAMPLE USAGE IN ROBOT FRAMEWORK
================================
``` robot
*** Settings ***
Library    ADBLibrary


*** Variables ***
${ANDROID_VERSION}   14

*** Test Cases ***
TC001: Get Serial Number
    ${output}  Execute Adb Command    command=adb get-serialno
    Log    Android version is ${output}

TC002: Get Android Version
    ${output}  Get Android Version
    Should Be Equal As Integers  ${output}  ${ANDROID_VERSION}

TC003: Wake Up Screen
    ${stdout}  Get State
    Should Be Equal  ${stdout}  device
    Execute Adb Shell Command    command=input keyevent 224
```
-------------------------------------------------------------------------------

PROJECT STRUCTURE
=================
``` sh
ADBLibrary/
├── src/
│   └── ADBLibrary.py         --> Main Robot Framework library
├── doc/
│   └── images/
│       └── IMAGE1.png        --> Setup diagram
├── test/
|   └── sample.robot          --> Sample robot file.
├── requirements.txt          --> Python dependencies
├── README.md                 --> Project description
├── LICENSE.txt               --> Apache License 2.0
├── setup.py                  --> Python packageing file
```
-------------------------------------------------------------------------------
DOCUMENTATIONS
==============

Refer to the following file for help with the available functionalities in the ADBLibrary:

[ADBLibrary Keyword Reference](doc/ADBLibrary.html)

-------------------------------------------------------------------------------
LICENSE
=======

This project is licensed under the Apache License 2.0.
https://www.apache.org/licenses/LICENSE-2.0

-------------------------------------------------------------------------------

CONTRIBUTIONS
=============

Contributions are welcome! Feel free to open issues or submit pull requests.
