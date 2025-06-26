#!/usr/bin/env python3
"""ADBLibrary is a library for the Robot Framework that provides ADB-related functionalities."""
# Standard libraries
import os
import subprocess
import re
from typing import Optional

# Third party libraries
from robot.api.deco import keyword

class ADBLibrary:
    """
    ADBLibrary is a custom Robot Framework library designed to facilitate automated interactions
    with Android devices via the Android Debug Bridge (ADB).

    This library provides a wide range of functionalities to automate and control Android devices
    through both generic ADB commands and shell-specific operations. It is especially useful in
    testing, debugging, device management, and continuous integration environments.

    Features:
        - Support for multiple connected Android devices.
        - Execute ADB and ADB shell commands with flexible return options.
        - Screen control commands (wake, sleep, reboot, screen resolution, screenshots).
        - Application management (install, uninstall, find package, clear data).
        - Device information retrieval (serial number, hardware name, build product, version).
        - File transfers (push/pull) between host and device.
        - Debug and diagnostic utilities (bug report generation, process/service listing).
        - Root and unroot device access control.
        - Text input simulation and browser interaction.

    Attributes:
        ROBOT_LIBRARY_SCOPE (str): Defines the library scope as 'Global'.
        _connected_devices (dict): Stores connected device aliases and their corresponding IDs.

    Example usage in Robot Framework:
        *** Settings ***
        Library    ADBLibrary

        *** Test Cases ***
        Wake Up All Screens
            Wake Up Screens

        Install App
            Install Apk    apk_file=/home/user/app.apk

        Generate Bug Report
            ${report_path}=    Generate Bug Report    directory_path=/tmp/reports

    Note:
        - Commands may require root access depending on the device state or command type.
        - Device connection validation is performed before each operation.

    For detailed documentation of each keyword, refer to individual method docstrings or
    generate HTML documentation using `libdoc`.
    """

    ROBOT_AUTO_KEYWORDS = False
    ROBOT_LIBRARY_SCOPE = 'Global'

    _connected_devices = {}

    @classmethod
    def _ensure_device_connected(cls, device_id: Optional[str] = None):
        """
        Ensure the device is connect or not.

        :param device_id: Specified a device id. default option is None.
        """
        cls._get_connected_devices()

        if not cls._connected_devices:
            raise ConnectionError("No connected ADB devices found.")

        if device_id and device_id not in cls._connected_devices.values():
            raise ValueError(f"Invalid ADB device: '{device_id}' not in connected list.")


    @classmethod
    def _get_connected_devices(cls):
        """
        Retrieve all connected ADB device IDs and store them with aliases.

        ``Returns:``
            A dictionary mapping aliases (e.g., 'device_0') to device IDs,
            stored in the _connected_devices attribute.

        ``Raises:``
            - ``ConnectionError``: If no devices are found.
        """
        try:
            result = subprocess.run(["adb", "devices"],
                                    capture_output=True,
                                    text=True,
                                    check=True)
            lines = result.stdout.strip().split("\n")[1:]
            devices = [line.split("\t")[0] for line in lines if "\tdevice" in line]

            if not devices:
                raise ConnectionError("No connected devices found!")

            cls._connected_devices = {f"device_{i}":
                                      device for i, device in enumerate(devices)}
            return cls._connected_devices

        except subprocess.CalledProcessError as err:
            raise RuntimeError(f"Failed to run adb devices: {err}") from err

    @classmethod
    def __is_valid_device(cls, device_id: str) -> bool:
        """
        Validate whether the given ADB device ID exists in the connected devices list.

        ``Args:``
            - ``device_id(str)``: The ADB device ID to validate.

        ``Returns:``
            - ``bool:`` True if the device ID exists in the connected devices list.

        ``Raises:``
            - ``ValueError:`` If the device ID is not found in the connected devices list.
        """
        cls._get_connected_devices()
        if device_id not in cls._connected_devices.values():
            raise ValueError(f"Invalid ADB device: '{device_id}' not in the connected list.")
        return True

    @classmethod
    def __is_valid_adb_command(cls, command: str) -> bool:
        """
        Check If command startswith adb.

        ``Args:``
            -``command(str)``: The command string to validate.

        ``Returns:``
            - ``bool:`` True if the command starts with 'adb', otherwise False.
        """
        if not command:
            raise ValueError("Command string is empty")

        pattern = r"^adb\b"
        return bool(re.match(pattern, command))

    @classmethod
    def __is_valid_adb_shell_command(cls, command: str) -> bool:
        """
        Check If command not startswith adb.

        ``Args:``
            - ``command(str)``: The command string to validate.

        ``Returns:``
            - ``bool:`` True if the command not starts with 'adb', otherwise False.
        """
        if not command:
            raise ValueError("Command string is empty")

        pattern = "^(?!adb\b)"
        return bool(re.match(pattern, command))

    @classmethod
    @keyword("Execute Adb Shell Command")
    def execute_adb_shell_command(cls,
                                  device_id: Optional[str] = None,
                                  command: str = "",
                                  return_stdout=True,
                                  return_rc=False,
                                  return_stderr=False):
        """
        Execute a shell command on an ADB-connected device.
        The `adb shell` command does not need to be passed.

        ``Args``:
            - ``device_id(str)``: Specific device ID (optional).
            - ``command(str)``: Shell command that must NOT start with 'adb'.
            - ``return_stdout(bool)``: If True, includes stdout.
            - ``return_rc(bool)``: If True, includes return code.
            - ``return_stderr(bool)``: If True, includes stderr.

        ``Returns``:
            - Output based on return_* flags.

        ``Raises``:
            - ``ValueError``: If the command is not valid.
            - ``RuntimeError``: If the command is not running properly.

        Example:
        | Execute Adb Shell Command | XXRZXXT81F | input keyevent 224 |
        | ${out}  Execute Adb Shell Command | device_id=XXRZXXT81F | command=input keyevent 224 |
        """
        cls._ensure_device_connected(device_id)

        if not cls.__is_valid_adb_shell_command(command):
            raise ValueError(f"Invalid ADB command: '{command}'. Must not start with 'adb'.")

        full_command = (
            f"adb -s {device_id} shell {command}" if device_id
            else f"adb shell {command}")

        try:
            with subprocess.Popen(full_command,
                                       shell=True,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE,
                                       encoding='UTF-8') as process:
                stdout, stderr = process.communicate()

            response = []
            if return_stdout:
                response.append(stdout.strip())
            if return_rc:
                response.append(process.returncode)
            if return_stderr:
                response.append(stderr.strip())

            return response if len(response) > 1 else response[0] if response else None

        except Exception as err:
            raise RuntimeError(f"ADB command execution failed: {err}") from err

    @classmethod
    @keyword("Execute Adb Command")
    def execute_adb_command(cls,
                            device_id: Optional[str]=None,
                            command: str = "",
                            return_stdout=True,
                            return_rc=False,
                            return_stderr=False):
        """
        Execute a generic ADB command (supports all adb commands) using subprocess.

        ``Args:``
            - ``device_id(str):`` Specific device ID (optional).
            - ``command(str):`` ADB command starting with 'adb'.
            - ``return_stdout(bool):`` If True, includes stdout in return.
            - ``return_rc(bool):`` If True, includes return code in return.
            - ``return_stderr(bool):`` If True, includes stderr in return.

        ``Returns:``
            - Output based on return_* flags.

        ``Raises:``
            - ``ValueError:`` If the command is not valid.
            - ``RuntimeError:`` If the command is not running properly.

        Example:
        | Execute Adb Command | XXRZXXCT81F | adb shell input keyevent 224 |
        | ${stdout}  Execute Adb Command | device_id=XXRZXXCT81F | command=adb devices -l |
        | ${stdout}  Execute Adb Command | command=adb get-state | #state of default adb device |
        | ${stdout}  Execute Adb Command | command=adb -s XXRZXXCT81F get-state |
        | ${stdout}  Execute Adb Command | device_id=XXRZXXCT81F | command=adb get-state |
        """
        cls._ensure_device_connected(device_id)

        if not cls.__is_valid_adb_command(command):
            raise ValueError(f"Invalid ADB command: '{command}'. Must start with 'adb'.")

        if device_id:
            if f"-s {device_id}" in command:
                full_command = command
            else:
                if command.strip().startswith("adb "):
                    full_command = command.replace("adb", f"adb -s {device_id}", 1)
                else:
                    full_command = f"adb -s {device_id} {command}"
        else:
            full_command = command

        try:
            with subprocess.Popen(full_command,
                                       shell=True,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE,
                                       encoding='UTF-8') as process:
                stdout, stderr = process.communicate()

            response = []
            if return_stdout:
                response.append(stdout.strip())
            if return_rc:
                response.append(process.returncode)
            if return_stderr:
                response.append(stderr.strip())

            return response if len(response) > 1 else response[0] if response else None

        except Exception as err:
            raise RuntimeError(f"ADB command execution failed: {err}") from err

    @classmethod
    @keyword("Wake Up Screens")
    def wake_up_screens(cls):
        """
        Wake up all connected devices

        ``Raises:``
            - ``RuntimeError:`` If the command is not running properly and no devices are connected

        Example:
        | Wake Up Screens | # wake up all adb screens |
        """
        cls._get_connected_devices()

        if not cls._connected_devices:
            raise RuntimeError("No devices connected.")

        for _, device_id in cls._connected_devices.items():
            return_code = cls.execute_adb_shell_command(device_id=device_id,
                                               command="input keyevent 224",
                                               return_stdout=False,
                                               return_rc=True)
            if return_code != 0:
                raise RuntimeError(
                    f"Invalid command on {device_id}: input keyevent 224 is not supported")

    @classmethod
    @keyword("Sleep Screens")
    def sleep_screens(cls):
        """
        Put all connected devices to sleep

        ``Raises:``
            - ``RuntimeError:`` If the command is not running properly and no devices are connected

        Example:
        | Sleep Screens | # sleep all adb screens |
        """
        cls._get_connected_devices()
        if not cls._connected_devices:
            raise RuntimeError("No devices connected.")

        for _, device_id in cls._connected_devices.items():
            return_code = cls.execute_adb_shell_command(device_id=device_id,
                                               command="input keyevent 223",
                                               return_stdout=False,
                                               return_rc=True)
            if return_code != 0:
                raise RuntimeError(
                    f"Invalid command on {device_id}: input keyevent 223 is not supported")

    @classmethod
    @keyword("Wake Up Screen")
    def wake_up_screen(cls, device_id: Optional[str] = None):
        """
        Wake up screen on specifieid device

        ``Args:``
            - ``device_id(str)``: Specific device ID.

        ``Raises:``
            - ``ValueError:`` Invalid device id
            - ``RuntimeError:`` If the command is not running properly.

        Example:
        | Wake Up Screen | XXRZXXCT81F |
        | Wake Up Screen | device_id=XXRZXXCT81F |
        """
        cls._ensure_device_connected(device_id)

        if device_id and not cls.__is_valid_device(device_id):
            raise ValueError(f"No device found. Invalid {device_id} device.")

        return_code = cls.execute_adb_shell_command(command="input keyevent 224",
                                           device_id=device_id,
                                           return_stdout=False,
                                           return_rc=True)
        if return_code != 0:
            raise RuntimeError(
                f"Invalid command on {device_id}: input keyevent 224 is not supported")

    @classmethod
    @keyword("Sleep Screen")
    def sleep_screen(cls, device_id: Optional[str] = None):
        """
        Put particular connected device to sleep

        ``Args:``
            - ``device_id(str):`` Specific device ID.

        ``Raises:``
            - ``ValueError:`` Invalid device id
            - ``RuntimeError:`` If the command is not running properly.

        Example:
        | Sleep Screen | XXRZXXCT81F |
        | Sleep Screen | device_id=XXRZXXCT81F |
        """
        cls._ensure_device_connected(device_id)

        if device_id and not cls.__is_valid_device(device_id):
            raise ValueError(f"No device found. Invalid {device_id} device.")

        return_code = cls.execute_adb_shell_command(command="input keyevent 223",
                                           device_id=device_id,
                                           return_stdout=False,
                                           return_rc=True)
        if return_code != 0:
            raise RuntimeError(
                f"Invalid command on {device_id}: input keyevent 223 is not supported")

    @classmethod
    @keyword("Reboot Device")
    def reboot_device(cls, device_id: Optional[str] = None, mode: str = "normal"):
        """
        Reboot the ADB device into a specified mode.

        ``Args:``
            - ``device_id(str):`` The device ID to reboot.
            - ``mode(str):`` Reboot mode - consists of normal, bootloader, recovery.
                    Default is 'normal'.

        ``Raises:``
            - ``ValueError:`` If an invalid mode is provided.
            - ``RuntimeError:`` If the reboot command fails.

        Example:
        | Reboot Device | # Default adb device reboot. |
        | Reboot Device | device_id=XXRZXXCT81F |
        | Reboot Device | device_id=XXRZXXCT81F | mode=normal |
        | Reboot Device | device_id=XXRZXXCT81F | mode=bootloader | # root required |
        | Reboot Device | device_id=XXRZXXCT81F | mode=recovery | # root required. |
        """
        cls._ensure_device_connected(device_id)

        valid_modes = ["normal", "bootloader", "recovery"]

        if device_id and not cls.__is_valid_device(device_id):
            raise RuntimeError(f"No device found. Invalid {device_id} device.")

        if mode not in valid_modes:
            raise ValueError(f"Invalid reboot mode: {mode}. Choose from {valid_modes}.")

        if mode == "normal":
            command = "reboot"
        elif mode == "bootloader":
            command = "reboot bootloader"
        elif mode == "recovery":
            command = "reboot recovery"

        return_code = cls.execute_adb_shell_command(device_id=device_id,
                                           command=command,
                                           return_stdout=False,
                                           return_rc=True)
        if return_code != 0:
            raise RuntimeError(
                f"Failed to reboot device {device_id} into {mode} mode.")

    @classmethod
    @keyword("Get Screen Size")
    def get_screen_size(cls, device_id: Optional[str]=None):
        """
        Get screen size for a specific device

        ``Args:``
            - ``device_id(str):`` Specific device id.

        ``Returns:``
            - Returns the screen size of given device.
              For Example: 1920x1080

        ``Raises:``
            - ``RuntimeError:`` Invalid device id

        Example:
        | ${stdout} = | Get Screen Size | # ${stdout}=1080x2400 |
        | ${stdout} = | Get Screen Size | device_id=XXRZXXCT81F |
        """
        cls._ensure_device_connected(device_id)

        if device_id and not cls.__is_valid_device(device_id):
            raise RuntimeError(f"No device found. Invalid {device_id} device.")

        cmd = "wm size"
        output = cls.execute_adb_shell_command(device_id=device_id, command=cmd)
        match = re.search(r'(\d+x\d+)', output)
        if not match:
            return None
        return match.group(1)

    @classmethod
    @keyword("Get Android Version")
    def get_android_version(cls, device_id: Optional[str]=None) -> int:
        """
        Retrieve the android version of given or specific device.

        ``Args:``
            - ``device_id(str):`` Specific device id.

        ``Returns:``
            - Returns the android version of given device.
              For Example: 15

        ``Raises:``
            - ``RuntimeError:`` Invalid device id

        Example:
        | ${stdout} = | Get Android Version | # ${stdout} = 13 |
        | ${stdout} = | Get Android Version | XXRZXXCT81F |
        | ${stdout} = | Get Android Version | device_id=XXRZXXCT81F |
        """
        cls._ensure_device_connected(device_id)

        if device_id and not cls.__is_valid_device(device_id):
            raise RuntimeError(f"No device found. Invalid {device_id} device.")

        cmd = "getprop ro.build.version.release"
        result = cls.execute_adb_shell_command(command=cmd, device_id=device_id)
        return int(result)

    @classmethod
    @keyword("Start Adb Server")
    def start_adb_server(cls, port:int=5037):
        """Start the ADB server with specified or default port.

        ``Args``:
            - ``port:`` Set the adb server port. By default sever port is 5037.

        ``Raises:``
            - ``RuntimeError:`` If the ADB server fails to start.

        Example:
        | Start Adb Server | # start adb server with default port |
        | Start Adb Server | port=5038 | # Adb server running into the port 5038. |
        """
        cmd =  f"adb start-server -p {port}"

        return_code = cls.execute_adb_command(command=cmd, return_stdout=False, return_rc=True)
        if return_code != 0:
            raise RuntimeError(f"Command execution failed: {cmd}")

    @classmethod
    @keyword("Kill Adb Server")
    def kill_adb_server(cls, port:int=5037):
        """kill the ADB server with specified port or default port.

        ``Args``:
            - ``port:`` Set the adb server port. By default sever port is 5037.

        ``Raises:``
            - ``RuntimeError:`` If the ADB server fails to kill.

        Example:
        | Kill Adb server | # kill adb server |
        """
        cmd = f"adb kill-server -p {port}"
        return_code = cls.execute_adb_command(command=cmd, return_stdout=False, return_rc=True)
        if return_code != 0:
            raise RuntimeError(f"Command execution failed: {cmd}")

    @classmethod
    @keyword("Get State")
    def get_state(cls, device_id: Optional[str]=None) -> str:
        """
        Retrive the current adb device state. Returns state of device, offline, unauthorized.

        ``Args:``
            - ``device_id(str):`` Specific device id.

        ``Returns:``
            - Returns the state of given device.
            - states are consists of device, offline, unauthorized.
            - For Example: device

        ``Raises:``
            - ``RuntimeError:`` Invalid device id and command execution failed.

        Example:
        | ${stdout} = | Get State | # ${stdout} = device |
        | ${stdout} = | Get State | XXRZXXCT81F |
        | ${stdout} = | Get State | device_id=XXRZXXCT81F |

        """
        cls._ensure_device_connected(device_id)

        if device_id and not cls.__is_valid_device(device_id):
            raise RuntimeError(f"No device found. Invalid {device_id} device.")

        cmd = "adb get-state"

        return_stdout, return_code = cls.execute_adb_command(device_id=device_id,
                                             command=cmd, return_rc=True)
        if return_code != 0:
            raise RuntimeError(f"Command execution failed: {cmd}")
        return return_stdout

    @classmethod
    @keyword("Get Serial No")
    def get_serial_no(cls, device_id: None) -> str:
        """
        Retrive the current adb device serial number. Returns device serial number.

        ``Args:``
            - ``device_id(str):`` Specific device id.

        ``Returns:``
            - Returns the serial number of given device.
            For Example: XXRZXXCT81F

        ``Raises:``
            - ``RuntimeError:`` Invalid device id and command execution failed.

        Example:
        | ${stdout} = | Get Serial No | # ${stdout} = device |
        | ${stdout} = | Get State | device_id=XXRZXXCT81F |
        """
        cls._ensure_device_connected(device_id)

        if device_id and not cls.__is_valid_device(device_id):
            raise RuntimeError(f"No device found. Invalid {device_id} device.")

        cmd = "adb get-serialno"

        stdout, return_code = cls.execute_adb_command(device_id=device_id,
                                             command=cmd,
                                             return_rc=True)
        if return_code != 0:
            raise RuntimeError(f"Command execution failed: {cmd}")
        return stdout

    @classmethod
    @keyword("Switch To Usb Mode")
    def switch_to_usb_mode(cls, device_id: Optional[str]=None):
        """
        Switch a device's ADB connection back to USB mode.

        ``Args:``
            - ``device_id(str):`` Specific device id.

        ``Raises:``
            - ``RuntimeError:`` command execution failed.

        Example:
        | ${stdout} = | Switch To Usb Mode | # ${stdout} = device |
        | ${stdout} = | Switch To Usb Mode | device_id=XXRZXXCT81F |
        """
        if device_id and not cls.__is_valid_device(device_id):
            raise RuntimeError(f"No device found. Invalid {device_id} device.")

        cmd = "adb usb"
        return_code, return_err = cls.execute_adb_command(device_id=device_id,
                                          command=cmd,
                                          return_stdout=False,
                                          return_rc=True,
                                          return_stderr=True)
        if return_code != 0:
            raise RuntimeError(f"Command execution failed: {return_err}")

    @classmethod
    @keyword("Reconnect Adb Device")
    def reconnect_adb_device(cls, device_id:Optional[str] = None):
        """
        Reconnect an ADB device.

        ``Args:``
            - ``device_id(str):`` Specific device id.

        ``Raises:``
            - ``RuntimeError``: If the reconnect command fails

        Example:
        | Reconnect Adb Device |
        | Reconnect Adb Device | XXRZXXCT81F |
        | Reconnect Adb Device | device_id=XXRZXXCT81F |
        """
        command = "adb reconnect"

        return_code = cls.execute_adb_command(device_id=device_id,
                                     command=command,
                                     return_stdout=False,
                                     return_rc=True)
        if return_code != 0:
            raise RuntimeError("Failed to reconnect the adb device.")

    @classmethod
    @keyword("Close All Adb Connections")
    def close_adb_connections(cls):
        """
        Close all adb connections.

        ``Raises:``
            - ``RuntimeError:`` command execution failed.

        Example:
        | Close All Adb Connections | # Close all adb related connections |
        """
        command = "adb disconnect"

        return_code = cls.execute_adb_command(command=command,
                                      return_stdout=False,
                                      return_rc=True)
        if return_code != 0:
            raise RuntimeError("Failed to disconnect on all adb device.")

    @classmethod
    @keyword("Close Adb Connection")
    def close_adb_connection(cls, device_id: Optional[str]=None):
        """
        Close specific or current adb connection.

        ``Raises:``
            - ``RuntimeError:`` command execution failed.

        Example:
        | Close Adb Connection |
        | Close Adb Connection | XXRZXXCT81F |
        | Close Adb Connection | device_id=XXRZXXCT81F |
        """
        command = "adb disconnect"

        return_code = cls.execute_adb_command(device_id=device_id,
                                     command=command,
                                     return_stdout=False,
                                     return_rc=True)
        if return_code != 0:
            raise RuntimeError("Failed to disconnect on all adb device.")

    @classmethod
    @keyword("Push File")
    def push_file(cls, device_id: Optional[str]=None, src: str="", dest: str=""):
        """
        File[s] Copy From Source pc to ADB device. Root access required.

        ``Args:``
            - ``device_id(str):`` Specific device id.
            - ``src(str):`` Specific file or directory in pc
            - ``dest(str):`` Specific path of adb device in adb device.

        ``Raises:``
            - ``RuntimeError``: If the reconnect command fails

        Example:
        | Push File | src=file.txt | dest=/storage/downloads/file.txt | # file |
        | Push File | device_id=XXRZXXCT81F | file.txt | /storage/downloads/file.txt |
        | Push File | src=/tmp/file | dest=/storage/downloads| # directory |
        | Push File | device_id=XXRZXXCT81F | /tmp/ | /storage/downloads |

        """
        cls._ensure_device_connected(device_id)

        if not os.path.exists(src):
            raise FileNotFoundError(f"Invalid filepath '{src}'")

        if device_id and not cls.__is_valid_device(device_id):
            raise RuntimeError(f"No device found. Invalid {device_id} device.")

        cmd = f"adb push {src} {dest}"
        return_code = cls.execute_adb_command(device_id=device_id,
                                     command=cmd,
                                     return_stdout=False,
                                     return_rc=True)
        if return_code != 0:
            raise RuntimeError(f"Command execution failed: {cmd}")

    @classmethod
    @keyword("Pull File")
    def pull_file(cls, device_id: Optional[str]=None, src: str="", dest: str=""):
        """
        File[s] Copy From ADB device to pc. Root access required.

        ``Args:``
            - ``device_id(str):`` Specific device id.
            - ``src(str):`` Specific file or directory in adb device
            - ``dest(str):`` Specific path of adb device in pc.

        ``Raises:``
            - ``RuntimeError``: If the reconnect command fails

        Example:
        | Pull File | src=/storage/downloads/file.txt | dest=file.txt | # file |
        | Pull File | device_id=XXRZXXCT81F | /storage/downloads/file.txt | file.txt |
        | Pull File | src=/storage/downloads | dest=/tmp/ | # directory |
        | Pull File | device_id=XXRZXXCT81F | /storage/downloads | /tmp/ |
        """
        cls._ensure_device_connected(device_id)

        if not os.path.exists(src):
            raise FileNotFoundError(f"Invalid filepath '{src}'")

        if device_id and not cls.__is_valid_device(device_id):
            raise RuntimeError(f"No device found. Invalid {device_id} device.")

        cmd = f"adb pull {src} {dest}"
        return_code = cls.execute_adb_command(device_id=device_id,
                                     command=cmd,
                                     return_stdout=False,
                                     return_rc=True)
        if return_code != 0:
            raise RuntimeError(f"Command execution failed: {cmd}")

    @classmethod
    @keyword("Set Root Access")
    def set_root_access(cls, device_id: Optional[str]=None):
        """
        If your device/device build should be rooted.

        ``Args:``
            - ``device_id(str):`` Specific device id.

        ``Raises:``
            - ``RuntimeError:`` command execution failed.

        Example:
        | Set Root Access | # Set root |
        | Set Root Access | device_id=XXRZXXCT81F |
        """
        cls._ensure_device_connected(device_id)

        if device_id and not cls.__is_valid_device(device_id):
            raise RuntimeError(f"No device found. Invalid {device_id} device.")

        cmd = "adb root"
        err = cls.execute_adb_command(device_id=device_id,
                                      command=cmd,
                                      return_stdout=False,
                                      return_stderr=True)
        if err:
            raise RuntimeError(f"Command execution failed, Error: {err}")

    @classmethod
    @keyword("Set Unroot Access")
    def set_unroot_access(cls, device_id: Optional[str]=None):
        """
        If your device/device build should be rooted.

        ``Args:``
            - ``device_id(str):`` Specific device id.

        ``Raises:``
            - ``RuntimeError:`` command execution failed.

        Example:
        | Set Unroot Access | # Set unroot |
        | Set Unroot Access | device_id=XXRZXXCT81F |
        """
        cls._ensure_device_connected(device_id)

        if device_id and not cls.__is_valid_device(device_id):
            raise RuntimeError(f"No device found. Invalid {device_id} device.")

        cmd = "adb unroot"
        err = cls.execute_adb_command(device_id=device_id,
                                      command=cmd,
                                      return_stdout=False,
                                      return_stderr=True)
        if err:
            raise RuntimeError(f"Command execution failed, Error: {err}")

    @classmethod
    @keyword("Install Apk")
    def install_apk(cls, device_id:Optional[str]=None, apk_file: str=""):
        """
        Installs the apk file from pc to given specified adb device.

        ``Args:``
            - ``device_id(str):`` Specified device id.
            - ``apk_file(str):`` Specific apk file in pc

        ``Raises:``
            - ``RuntimeError:`` command execution failed.

        Example:
        | Install Apk | apk_file=/home/user/Downloads/demo_calculator-1-0.apk |
        | Install Apk | device_id=XXRZXXCT81F | apk_file=~/Downloads/demo_calculator-1-0.apk |
        """
        cls._ensure_device_connected(device_id)

        if not os.path.exists(apk_file):
            raise FileNotFoundError(f"Invalid filepath '{apk_file}'")

        cmd = f"adb install {apk_file}"
        err = cls.execute_adb_command(device_id=device_id,
                                      command=cmd,
                                      return_stdout=False,
                                      return_stderr=True)
        if err:
            raise RuntimeError(f"Command execution failed, Error: {err}")

    @classmethod
    @keyword("Uninstall Apk")
    def uninstall_apk(cls, device_id:Optional[str]=None, apk_package: str=""):
        """
        Uninstalls the specified APK package from the connected ADB device.

        The APK package should be provided in the standard format, such as:
        `com.android.calculator2`

        If you're unsure about the package name, use the `Find Package` keyword to locate it.

        ``Args``:
            - ``device_id(str)``: The specific device ID to run the command on.
            - ``apk_package(str)``: The package name of the APK to uninstall
                (e.g., com.android.calculator2).

        ``Raises:``
            - ``RuntimeError:`` command execution failed.

        Example:
        | Uninstall Apk | apk_package=com.android.calculator2 |
        | UnInstall Apk | device_id=XXRZXXCT81F | apk_package=com.android.calculator2 |
        """
        cls._ensure_device_connected(device_id)

        cmd = f"adb uninstall {apk_package}"
        err = cls.execute_adb_command(device_id=device_id,
                                      command=cmd,
                                      return_stdout=False,
                                      return_stderr=True)
        if err:
            raise RuntimeError(f"Command execution failed, Error: {err}"
                               f"{apk_package} package not remove/uninstall")

    @classmethod
    @keyword("Find Apk Package")
    def find_apk_package(cls, device_id:Optional[str]=None, package_name: str="") -> bool:
        """
        Finds the package name inside of given specified device.

        ``Args:``
            - ``device_id(str):`` Specified a given adb device id.
            - ``package_name(str):`` Mention installed package name.
                                    (e.g., com.android.calculator2)

        ``Returns:``
            - ``bool:`` True if the package is available, otherwise False.

        Example:
        | ${stdout} | Find Apk | package_name=com.android.calculator2 |
        | ${stdout} | Find Apk | device_id=XXRZXXCT81F | com.android.calculator2 |
        """
        cls._ensure_device_connected(device_id)

        cmd = "pm list packages"
        output, err = cls.execute_adb_shell_command(device_id=device_id,
                                                    command=cmd,
                                                    return_stdout=True,
                                                    return_stderr=True)
        if err:
            raise RuntimeError(f"Command execution failed, Error: {err}")

        installed_packages = [
            line.replace("package:", "").strip() for line in output.splitlines()
            ]
        return package_name in installed_packages

    @classmethod
    @keyword("Get Build Product")
    def get_build_product(cls, device_id:Optional[str]=None) -> str:
        """
        Retrieve the build product.

        ``Args:``
            - ``device_id(str):`` Specified a given adb device id.

        ``Returns:``
            - ``Return(str)``: return the build produt.
        ``Raises:``
            - ``RuntimeError:`` command execution failed.

        Example:
        | ${stdout} | Get Build Product |   # ${stdout}=rpi4   |
        | ${stdout} | Get Build Product | device_id=XXRZXXCT81F |
        """
        cls._ensure_device_connected(device_id)

        cmd = "getprop ro.build.product"
        output, err = cls.execute_adb_shell_command(device_id=device_id,
                                                    command=cmd,
                                                    return_stdout=True,
                                                    return_stderr=True)
        if err:
            raise RuntimeError(f"Command execution failed, Error: {err}")

        return output

    @classmethod
    @keyword("Get Hardware Name")
    def get_hardware_name(cls, device_id:Optional[str]=None) -> str:
        """
        Retrieve the hardware name

        ``Args:``
            - ``device_id(str):`` Specified a given adb device id.

        ``Returns:``
            - ``Return(str)``: return the adb device hardware name.
        ``Raises:``
            - ``RuntimeError:`` command execution failed.

        Example:
        | ${stdout} | Get Hardware Name |   # ${stdout}=rpi4   |
        | ${stdout} | Get Hardware Name | device_id=XXRZXXCT81F |
        """
        cls._ensure_device_connected(device_id)

        cmd = "getprop ro.hardware"
        output, err = cls.execute_adb_shell_command(device_id=device_id,
                                                    command=cmd,
                                                    return_stdout=True,
                                                    return_stderr=True)
        if err:
            raise RuntimeError(f"Command execution failed, Error: {err}")

        return output

    @classmethod
    @keyword("Take Screenshot")
    def take_screenshot(cls, device_id:Optional[str]=None, filename:str='screenshot.png'):
        """
        Takes a screenshot from the specified ADB device (or the current device
        if none is specified) and saves it to the given file path.

        ``Args``:
            - ``device_id(Optional[str]):`` The ID of the ADB device.
                If None, uses the current device.
            - ``filename(str):`` The name (or path) of the file to save the screenshot.
                Defaults to 'screenshot.png'.

        ``Return:``
            - ``returns:`` Noe

        ``Raises:``
            - ``RuntimeError:`` command execution failed.
            - ``FileNotFoundError:`` File not found or file not exists.

        Example:
        | Take Screenshot |   # Default device and default filename |
        | Take Screenshot | device_id=XXRZXXCT81F | # Specified device and default filename |
        | Take Screenshot | device_id=XXRZXXCT81F | filename='/tmp/screen1.png' |

        """
        cls._ensure_device_connected(device_id)

        cmd = f"adb exec-out screencap -p > {filename}"
        err = cls.execute_adb_command(device_id=device_id,
                                      command=cmd,
                                      return_stdout=False,
                                      return_stderr=True)
        if err:
            raise RuntimeError(f"Command execution failed, Error: {err}")

        if not os.path.exists(filename):
            raise FileNotFoundError(f"File not exists/found, Check filepath: {filename}")

    @classmethod
    @keyword("Get Apk Path")
    def get_apk_path(cls, device_id:Optional[str]=None, package_name: str="") -> str:
        """
        Retrieves the full file path of the installed APK on the device.

        ``Args:``
            - ``device_id(Optional[str]):`` The ID of the ADB device.
                If None, uses the current device.
            - ``package_name:`` Specified a installed package name,
                                (e.g., com.android.calculator2).

        ``Return:``
            - ``returns:`` Retrives the full file path of the installed APK.

        ``Raises:``
            - ``RuntimeError:`` command execution failed.

        Example:
        | ${out} | Get Apk Path | package_name=com.android.calculator2 |
        | ${out} | Get Apk Path | device_id=XXRZXXCT81F | package_name=com.android.calculator2 |

        """
        cls._ensure_device_connected(device_id)

        cmd = f"pm path {package_name}"
        output, err = cls.execute_adb_shell_command(device_id=device_id,
                                            command=cmd,
                                            return_stdout=True,
                                            return_stderr=True)
        if err:
            raise RuntimeError(f"Command execution failed, Error: {err}")

        return output

    @classmethod
    @keyword("Clear App Data")
    def clear_app_data(cls, device_id:Optional[str]=None, package_name: str=""):
        """
        Resets the app by clearing all stored data of the installed APK.

        ``Args:``
            - ``device_id(Optional[str]):`` The ID of the ADB device.
                If None, uses the current device.
            - ``package_name:`` Specified a installed package name,
                                (e.g., com.android.calculator2).

        ``Raises:``
            - ``RuntimeError:`` command execution failed.

        Example:
        | Clear App Data | package_name=com.android.calculator2 |
        | Clear App Data | device_id=XXRZXXCT81F | package_name=com.android.calculator2 |
        """
        cls._ensure_device_connected(device_id)

        cmd = f"pm clear {package_name}"
        err = cls.execute_adb_shell_command(device_id=device_id,
                                      command=cmd,
                                      return_stdout=False,
                                      return_stderr=True)
        if err:
            raise RuntimeError(f"Command execution failed, Error: {err}")

    @classmethod
    @keyword("Get Package Info")
    def get_package_info(cls, device_id:Optional[str]=None, package_name: str="") -> str:
        """
        Retrieves the details about the installed package on the device.

        ``Args:``
            - ``device_id(Optional[str]):`` The ID of the ADB device.
                If None, uses the current device.
            - ``package_name:`` Specified a installed package name,
                                (e.g., com.android.calculator2).

        ``Return:``
            - ``returns:`` Retrives the full file path of the installed APK.

        ``Raises:``
            - ``RuntimeError:`` command execution failed.

        Example:
        | ${out} | Get Package Info | package_name=com.android.calculator2 |
        | ${out} | Get Package Info | device_id=XXRZXCT81F | package_name=com.android.calculator2 |

        """
        cls._ensure_device_connected(device_id)

        cmd = f"dumpsys package {package_name}"
        output, err = cls.execute_adb_shell_command(device_id=device_id,
                                            command=cmd,
                                            return_stdout=True,
                                            return_stderr=True)
        if err:
            raise RuntimeError(f"Command execution failed, Error: {err}")

        return output

    @classmethod
    @keyword("Set Keyevent Input")
    def set_keyevent_input(cls, device_id: Optional[str] = None, value: int = None) -> str:
        """
        Sends a keyevent input command to the connected Android device using ADB.

        ``Args:``
            - ``device_id(Optional[str])``: The ID of the ADB device. If None, 
                                            the default device is used.
            - ``value(int):`` The keyevent code to send (e.g., 223 for sleep screen).

        ``Returns:``
            The standard output from the executed ADB shell command.

        ``Raises:``
            - RuntimeError: If the ADB shell command fails and returns an error.

        Example:
            | ${output} | Set Keyevent Input | value=223 |
            | ${output} | Set Keyevent Input | device_id=XXRZXXCT81F | value=223 |
        """
        cls._ensure_device_connected(device_id)

        cmd = f"input keyevent {value}"
        output, err = cls.execute_adb_shell_command(
            device_id=device_id,
            command=cmd,
            return_stdout=True,
            return_stderr=True
        )

        if err:
            raise RuntimeError(f"Command execution failed. Error: {err}")

        return output

    @classmethod
    @keyword("Set Keyevent Input")
    def set_keyevent_input(cls, device_id: Optional[str] = None, value: int = None) -> str:
        """
        Sends a keyevent input command to the connected Android device using ADB.

        ``Args:``
            - ``device_id (Optional[str]):`` The ID of the ADB device. 
                                             If None, the default device is used.
            - ``value (int):`` The keyevent code to send (e.g., 223 for sleep screen).

        ``Returns:``
            - ``str:`` The standard output from the executed ADB shell command.

        ``Raises:``
            - ``RuntimeError:`` If the ADB shell command fails and returns an error.

        Example:
            | ${output} | Set Keyevent Input | value=223 |
            | ${output} | Set Keyevent Input | device_id=XXRZXXCT81F | value=223 |
        """
        cls._ensure_device_connected(device_id)

        cmd = f"input keyevent {value}"
        output, err = cls.execute_adb_shell_command(
            device_id=device_id,
            command=cmd,
            return_stdout=True,
            return_stderr=True
        )

        if err:
            raise RuntimeError(f"Command execution failed. Error: {err}")

        return output

    @classmethod
    @keyword("Set Screen Size")
    def set_screen_size(cls,
                        device_id: Optional[str] = None, 
                        width: int = None, 
                        height: int = None) -> None:
        """
        Sets the screen resolution (width x height) on an Android device using ADB.

        ``Args:``
            - ``device_id (Optional[str]):`` The unique ID of the ADB device. 
                                            If None, uses the currently connected/default device.
            - ``width (int):`` The desired screen width in pixels.
            - ``height (int):`` The desired screen height in pixels.
        ``Raises:``
            - ``RuntimeError:`` If the command to set screen size fails
                                or if width/height is not provided.
            
        Example:
            | Set Screen Size | width=1920 | height=1080 |
            | Set Screen Size | device_id=XXRZXXCT81F | width=1920 | height=1080 |
        """
        cls._ensure_device_connected(device_id)

        if width is None or height is None:
            raise ValueError("Both width and height must be specified.")

        cmd = f"wm size {width}x{height}"

        err = cls.execute_adb_shell_command(
            device_id=device_id,
            command=cmd,
            return_stdout=False,
            return_stderr=True
        )

        if err:
            raise RuntimeError(f"Command execution failed. Error: {err}")

    @classmethod
    @keyword("Get Running Processes")
    def get_running_processes(cls, device_id: Optional[str] = None) -> str:
        """
        Retrieves the list of currently running processes on the connected Android device.

        ``Args:``
            - ``device_id (Optional[str]):`` The unique ID of the ADB device.
                                    If None, the default connected device is used.
        ``Returns:``
            - ``str:`` A string containing the list of running processes.
        ``Raises:``
            - ``RuntimeError:`` If the command to retrieve running processes fails.
        
        Example:
            | ${output} | Get Running Processes |
            | ${output} | Get Running Processes | device_id=XXRZXXCT81F |
        """
        cls._ensure_device_connected(device_id)

        cmd = "ps"
        output, err = cls.execute_adb_shell_command(
            device_id=device_id,
            command=cmd,
            return_stdout=True,
            return_stderr=True
        )

        if err:
            raise RuntimeError(f"Command execution failed. Error: {err}")

        return output

    @classmethod
    @keyword("Get All Services")
    def get_all_services(cls, device_id: Optional[str] = None) -> str:
        """
        Retrieves the list of all services available on the connected Android device.

        ``Args:``
            - ``device_id (Optional[str]):`` The unique ID of the ADB device.
                                    If None, the default connected device is used.

        ``Returns:``
            - ``str:`` A string containing the list of all system services.

        ``Raises:``
            - ``RuntimeError:`` If the command to retrieve services fails.
        
        Example:
            | ${output} | Get All Services |
            | ${output} | Get All Services | device_id=XXRZXXCT81F |
        """
        cls._ensure_device_connected(device_id)

        cmd = "service list"
        output, err = cls.execute_adb_shell_command(
            device_id=device_id,
            command=cmd,
            return_stdout=True,
            return_stderr=True
        )

        if err:
            raise RuntimeError(f"Command execution failed. Error: {err}")

        return output

    @classmethod
    @keyword("Open Default Browser")
    def open_default_browser(cls, device_id: Optional[str] = None) -> None:
        """
        Opens the default web browser on the connected Android device using a key event.

        ``Args:``
            - ``device_id (Optional[str]):`` The unique ID of the ADB device.
                                    If None, the default connected device is used.

        ``Raises:``
            - ``RuntimeError:`` If the command to open the browser fails.
        
        Example:
        | Open Default Browser |
        | Open Default Browser | device_id=XXRZXXCT81F |
        """
        cls._ensure_device_connected(device_id)

        cmd = "input keyevent 64"  # KEYCODE_BROWSER
        output, err = cls.execute_adb_shell_command(
            device_id=device_id,
            command=cmd,
            return_stdout=False,
            return_stderr=True
        )

        if err:
            raise RuntimeError(f"Command execution failed. Error: {err}")

    @classmethod
    @keyword("Set Input Text")
    def set_input_text(cls, device_id: Optional[str] = None, text: str = None):
        """
        Sends a text input to the connected Android device via ADB.

        This keyword simulates typing the specified text on the device using the ADB input command.

        ``Args:``
            - ``device_id (Optional[str]):`` The ID of the connected Android device.
                If not provided, the default connected device will be used.
            - ``text (str):`` The text to input into the device.

        ``Raises:``
            - ``RuntimeError:`` If the ADB command execution fails.

        Example:
        | Set Input Text | text=Hi Adb |
        | Set Input Text | device_id=XXRZXXCT81F | text=Hi adb |
        """
        cls._ensure_device_connected(device_id)

        cmd = f'input text "{text}"'
        err = cls.execute_adb_shell_command(
            device_id=device_id,
            command=cmd,
            return_stdout=False,
            return_stderr=True
        )

        if err:
            raise RuntimeError(f"Command execution failed. Error: {err}")
        
    @classmethod
    @keyword("Generate Bug Report")
    def generate_bug_report(cls,
                            device_id: Optional[str] = None,
                            directory_path: Optional[str] = None):
        
        """
        Generates a bug report from the connected ADB device and saves it to the specified local directory.
        
        This method performs the following steps:
        1. Executes 'adb bugreport' to generate a bug report on the device.
        2. Locates the generated ZIP file in the device's internal bugreport directory.
        3. Pulls the ZIP file from the device to the specified local directory.
        4. Validates the presence of the file locally and returns its path.

        Args:
            device_id (Optional[str]): The ID of the ADB device. If None, the default connected device is used.
            directory_path (Optional[str]): The local directory where the bug report ZIP file will be saved.

        Returns:
            str: Full path to the bug report ZIP file saved on the local system.

        Raises:
            NotADirectoryError: If the given local directory path does not exist.
            FileNotFoundError: If the bug report file is not found on the device or not copied successfully.
            RuntimeError: If any ADB command fails during execution.
        """

        cls._ensure_device_connected(device_id)

        if not os.path.isdir(directory_path):
            raise NotADirectoryError(f"{directory_path}: Directory not found")

        cmd = "adb bugreport"
        cls.execute_adb_command(
            device_id=device_id,
            command=cmd,
            return_stdout=False,
            return_stderr=False
        )

        remote_path = "/data/user_de/0/com.android.shell/files/bugreports"
        file_list = cls.execute_adb_shell_command(
            device_id=device_id,
            command=f"ls {remote_path}",
            return_stdout=True
        ).splitlines()

        bugreport_file = next((f for f in file_list if f.endswith(".zip")), None)

        if not bugreport_file:
            raise FileNotFoundError("Bugreport zip file not found on device.")

        remote_file_path = f"{remote_path}/{bugreport_file}"
        pull_cmd = f"adb pull {remote_file_path} {directory_path}"

        cls.execute_adb_command(
            device_id=device_id,
            command=pull_cmd,
            return_stdout=False,
            return_stderr=False
        )

        local_file = os.path.join(directory_path, bugreport_file)

        if not os.path.isfile(local_file):
            raise FileNotFoundError("Bugreport file not copied to local directory.")

        return local_file
