ADBLibrary for Robot Framework
==============================

**ADBLibrary** is a custom Robot Framework library that provides Android Debug Bridge (ADB) functionalities for automated testing and device control.

It enables seamless interaction with Android devices through ADB commands, making it ideal for client-side testing, device orchestration.

---

## Features

- Execute `adb` and `adb shell` commands
- Manage multiple connected Android devices
- Switch between USB and TCP/IP connection
- Install, uninstall, and inspect APKs
- Capture logs, screenshots, and device metadata
- Simulate input events and browser interactions
- Push/pull files between host and device
- Root/unroot access control
- Built on a proxy design pattern for scalable multi-device support

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
## Supported Devices

| Device Type | Supported Features                                      |
|-------------|----------------------------------------------------------|
| Rooted      | Full access to all keywords                             |
| Unrooted    | Limited access: connection, shell commands, metadata queries |

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
Library           ADBLibrary


*** Variables ***
${ADB_DEVICE}           10000000cd0c07a6
${DEVICE_IP}            192.168.1.103
${PORT}                 5555
${ADB_NETWORK_DEVICE}   ${DEVICE_IP}:${PORT}
${INTERFACE}            wlan0
${PACKAGE}              com.joeykrim.rootcheck
${TIMEOUT}              ${5}


*** Test Cases ***
TC001 - Basic ADB Operations
    [Documentation]  Verifies core ADB operations including starting the ADB server, creating a USB connection,
    ...              executing shell and ADB commands, and disconnecting the device.
    Start Adb Server
    Create Connection  type=usb  device_id=${ADB_DEVICE}
    ${model}  Execute Shell Command  getprop ro.product.model
    Log To Console  \nModel: ${model}
    ${version}  Execute Command  adb shell getprop ro.build.version.release
    Log To Console  \nAndroid Version: ${version}
    Disconnect Device

TC002 - Network Connection and Device Metadata
    [Documentation]  Verifies network-based ADB connection setup. Includes enabling TCP/IP mode, creating a
    ...              network connection, retrieving Android version, switching between devices, and fetching
    ...              device metadata such as build product, hardware name, state, and serial number.
    Create Connection  type=usb  device_id=${ADB_DEVICE}
    Enable Tcpip Mode  port=${PORT}
    Create Connection  type=network  device_ip=${DEVICE_IP}  port=${PORT}
    ${version}  Get Android Version
    Log To Console    \nAndroid Version: ${version}
    Switch Connection  device_id=${ADB_DEVICE}
    ${connection}  Get Connection
    Log To Console  \nCurrent Connection: ${connection}
    ${product}  Get Build Product
    Log To Console  \nBuild Product: ${product}
    ${hardware}  Get Hardware Name
    Log To Console  \nHardware Name: ${hardware}
    ${state}  Get State
    Should Be Equal  ${state}  device
    ${serial_number}  Get Serial Number
    Should Be Equal  ${serial_number}  ${ADB_DEVICE}
    Close All Connections
```
-------------------------------------------------------------------------------

PROJECT STRUCTURE
=================
``` sh
ADBLibrary/
├── doc/
│   ├── ADBLibrary.html       # Auto-generated keyword documentation (via libdoc)
│   └── IMAGE1.png            # Optional setup or architecture diagram
├── LICENSE.txt               # Apache License 2.0
├── README.md                 # Project overview and usage instructions
├── requirements.txt          # Python dependencies
├── setup.py                  # Packaging and distribution configuration
├── src/
│   ├── ADBLibrary/
│   │   ├── adb_library.py    # Main Robot Framework library class (with @library decorator)
│   │   └── __init__.py       # Entry point for libdoc and version declaration
│   └── core/
│       ├── adb_connection.py # Low-level ADB connection handling
│       ├── adb_interface.py  # Interface definitions and command abstractions
│       ├── adb_proxy.py      # Proxy design pattern for multi-device orchestration
│       └── __init__.py       # Core module initializer
└── test/
    └── test.robot            # Sample Robot Framework test suite using ADBLibrary

```
-------------------------------------------------------------------------------
DOCUMENTATIONS
==============

Refer to the following file for help with the available functionalities in the ADBLibrary:

[ADBLibrary Keyword Reference](doc/ADBLibrary.html)

You Can regenerate this using:
``` sh
$ libdoc ADBLibrary ADBLibrary.html
```
-------------------------------------------------------------------------------
LICENSE
=======

This project is licensed under the Apache License 2.0.
https://www.apache.org/licenses/LICENSE-2.0

-------------------------------------------------------------------------------

CONTRIBUTIONS
=============

Contributions are welcome! Feel free to:
- Submit pull requests
- Open issues
- Suggest new keywords or enhancements

Let’s build a powerful ADB automation ecosystem together.
