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
    ...              executing shell and ADB commands the device.
    Create Connection  type=usb  device_id=${ADB_DEVICE}
    ${model}  Execute Shell Command  getprop ro.product.model
    Log To Console  \nModel: ${model}
    ${version}  Execute Command  adb shell getprop ro.build.version.release
    Log To Console  \nAndroid Version: ${version}
    Close Connection

TC002 - Network Connection and Device Metadata
    [Documentation]  Verifies network-based ADB connection setup. Includes enabling TCP/IP mode, creating a
    ...              network connection, retrieving Android version, and fetching device metadata such as 
    ...              build product, hardware name, state, and serial number.
    Create Connection  type=usb  device_id=${ADB_DEVICE}
    Enable Tcpip Mode  port=${PORT}
    Create Connection  type=network  device_ip=${DEVICE_IP}  port=${PORT}
    ${version}  Get Android Version
    Log To Console    \nAndroid Version: ${version}
    ${connection}  Get Connection
    Log To Console  \nCurrent Connection: ${connection}
    ${product}  Get Build Product
    Log To Console  \nBuild Product: ${product}
    ${hardware}  Get Hardware Name
    Log To Console  \nHardware Name: ${hardware}
    ${state}  Get State
    Should Be Equal  ${state}  device
    ${serial_number}  Get Serial Number
    Should Be Equal  ${serial_number}  ${ADB_NETWORK_DEVICE}
    Close All Connections

TC003 - Access Control and Diagnostics
    [Documentation]  Verifies access control and diagnostic utilities. Includes switching to USB mode, toggling
    ...              root/unroot access, retrieving system services and running processes, and closing the connection.
    Create Connection  type=usb  device_id=${ADB_DEVICE}
    Switch To Usb Mode
    Sleep  ${TIMEOUT}
    Set Root Access
    Sleep  ${TIMEOUT}
    ${services}  Get All Services
    Log To Console  \nServices: ${services}
    ${processes}=  Get Running Processes
    Log To Console  \nProcesses: ${processes}
    Close Connection

TC004 - APK Lifecycle Operations
    [Documentation]  Verifies APK-related operations including installation in test mode, retrieving APK path,
    ...              clearing app data, fetching package info, validating package existence, and uninstalling the app.
    Create Connection  type=usb  device_id=${ADB_DEVICE}
    Install Apk  apk_file=install.apk  mode=test
    Sleep  ${TIMEOUT}
    ${path}  Get Apk Path  package_name=${PACKAGE}
    Log To Console  \nAPK Path: ${path}
    Clear App Data  package_name=${PACKAGE}
    ${info}  Get Package Info  package_name=${PACKAGE}
    Log To Console  \nPackage Info: ${info}
    Package Should Exist  ${PACKAGE}
    Uninstall Apk  ${PACKAGE}
    Sleep  ${TIMEOUT}
    Package Should Not Exist  ${PACKAGE}
    Close Connection

TC005 - Device Interaction and Reboot
    [Documentation]  Verifies device interaction commands including screen sleep/wake, retrieving IPv4 address,
    ...              sending keyevents, launching the default browser, sending text input, and rebooting the device.
    Create Connection  type=usb  device_id=${ADB_DEVICE}
    Sleep Screen
    Sleep  ${TIMEOUT}
    Wake Up Screen
    Sleep  ${TIMEOUT}
    Send Keyevent  value=223
    Sleep  ${TIMEOUT}
    Send Keyevent  value=224
    Sleep  ${TIMEOUT}
    Open Default Browser
    Sleep  ${TIMEOUT}
    Send Text  google
    Sleep  ${TIMEOUT}
    Reboot Device

    
