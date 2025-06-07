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
