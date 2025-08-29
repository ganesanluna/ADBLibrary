"""AdbConnection is an intermediate layer in ADBLibrary for the Robot Framework."""
# standard library
import os
import re
import subprocess
import logging
import time
import ipaddress
from typing import Optional, Union, Tuple

# Local library
from .adb_interface import AdbInterface

# debugging
logger = logging.getLogger(__name__)


class AdbConnection(AdbInterface):
    """
    Adb connection is a core module of this library.
    """
    def __init__(self):
        self.device_id = None
        self.connected = False
        self.server_port = 5037
        self.tcpip_port = 5555

    def _Get_the_devices(self) -> list:
        """
        Get the list of connected adb devices.
        """
        try:
            output = subprocess.check_output(["adb", "devices"], text=True)
            connected_devices = [line.split("\t")[0] for line in output.strip().splitlines()[1:]]
            return connected_devices
        except subprocess.CalledProcessError:
            return []

    def _is_device_connected(self,
                             device_id: Optional[str] = None) -> bool:
        """
        Checks if the given device_id is listed in adb devices.
        """
        devices = self._Get_the_devices()
        logger.info("Current connected devices: %s", devices)

        if not device_id:
            return len(devices) == 1

        return device_id in devices

    def start_adb_server(self,
                        port: Optional[int] = None) -> None:
        """
        Start the ADB server.
        """
        port = port or self.server_port
        self.server_port = port

        cmd = f"adb start-server -p {port}"
        logger.info("Starting ADB server on port %s ... ", port)
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                logger.error("ADB server failed to start: %s",result.stderr.strip())
                raise RuntimeError(f"Failed to start ADB server on port {port}")
            logger.info("ADB server started successfully.")
        except subprocess.SubprocessError as err:
            logger.exception("Exception occurred while starting ADB server.")
            raise RuntimeError("ADB server start failed") from err

    def kill_adb_server(self,
                        port: Optional[int] = None) -> None:
        """
        Kill the ADB server.
        """
        port = port or self.server_port
        self.server_port = port

        env = os.environ.copy()
        env["ANDROID_ADB_SERVER_PORT"] = str(port)

        cmd = "adb kill-server"
        logger.info("Stopping ADB server on port %s ...", port)
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, env=env)
            if result.returncode != 0:
                logger.error("ADB server failed to stop: %s", result.stderr.strip())
                raise RuntimeError(f"Failed to stop ADB server on port {port}")
            logger.info("ADB server stopped successfully.")
        except subprocess.SubprocessError as err:
            logger.exception("Exception occurred while stopping ADB server.")
            raise RuntimeError("ADB server stop failed") from err

    def get_interface_ipv4(self,
                           interface: Optional[str]=None) -> str:
        """
        Retrieve the IPv4 address of given interface
        """
        if not(self.device_id or self.connected):
            raise ValueError(
                "No ADB device Found. Use create_connection keyword. "
                f"device_id:{self.device_id}, connected:{self.connected}"
                )

        if not interface:
            raise ValueError("Interface still Empty, Pass the valid interface")

        cmd = (f"adb -s {self.device_id} shell ifconfig {interface} | grep 'inet addr' |"
              f"awk '{{print $2}}' | cut -d: -f2")

        logger.info("Execute this command: %s ...", cmd)
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                logger.error("Failed to execute command: %s", result.stderr.strip())
                raise RuntimeError(f"Failed to execute command: {cmd}")
            logger.debug("IPv4 Address: %s",result.stdout.strip())
            return result.stdout.strip()
        except subprocess.SubprocessError as err:
            logger.exception("Exception occurred while stopping ADB server.")
            raise RuntimeError("ADB server stop failed") from err

    def enable_tcpip_mode(self,
                          port: Optional[int] = None) -> None:
        """
        Enable tcpip mode in specified device_id
        """
        if ":" in str(self.device_id):
            raise ValueError(
                f"Current device is '{self.device_id}'.\n"
                "Must switch to or create a USB-connected device.\n"
                "TCP/IP mode can only be enabled on USB-connected devices."
            )

        port = port or self.tcpip_port
        self.tcpip_port = port
        cmd = f"adb -s {self.device_id} tcpip {port}"
        logger.info("Executing the command: %s", cmd)
        result = subprocess.call(cmd, shell=True)
        if result != 0:
            raise RuntimeError(f"Failed to enable TCP/IP mode on {self.device_id}")
        logger.debug(f"TCP/IP mode enabled on {self.device_id}:{port}")  # pylint: disable=W1203


    def get_connection(self) -> str:
        """
        Get The current an active adb connection.
        """
        return self.device_id

    import ipaddress

    def _is_valid_ip(self,
                    ip: str) -> bool:
        """
        Check ip address
        """
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False

    def connect_net_device(self,
                           device_ip: Optional[str] = None,
                           port: Optional[int] = None,
                           timeout: int = 10) -> None:
        """
        Connects to an ADB device over Wi-Fi.
        """
        port = port or self.tcpip_port
        if not self._is_valid_ip(device_ip):
            raise ValueError(f"Invalid device_ip={device_ip}")

        device_id = f"{device_ip}:{port}"
        cmd = ["adb", "connect", device_id]

        logger.info("Connecting to device: %s", device_id)
        logger.info(f"Executing command: {' '.join(cmd)}")

        proc = None
        try:
            proc = subprocess.Popen(cmd,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    text=True)

            start_time = time.time()
            while time.time() - start_time < timeout:
                if proc.poll() is not None:
                    break
                time.sleep(0.5)

            if proc.poll() is None:
                logger.warning("Timeout reached. Terminating ADB connect for %s", device_id)
                proc.terminate()
                proc.wait(timeout=5)

            stdout, stderr = proc.communicate()
            if "connected" not in stdout.lower():
                raise RuntimeError(f"Failed to connect to {device_id}. Output: {stdout.strip()}")

            self.device_id = device_id
            self.connected = True

        except Exception as e:
            if proc:
                try:
                    proc.kill()
                except Exception:
                    pass
            raise RuntimeError(f"Error while connecting to {device_id}: {e}")

    def connect_usb_device(self,
                           device_id: str) -> None:
        """
        Connects to an ADB device over USB.
        """
        self.device_id = device_id

        if not self._is_device_connected(device_id):
            raise RuntimeError(f"ADB device: {device_id} not connected")

        self.connected = True
        logger.info("USB device connected: %s", device_id)

    def create_connection(self,
                          connection_type: str = 'usb',
                          **kwargs):
        """
        Create a connection either usb or network.
        """
        if connection_type.lower() == 'usb':
            if not kwargs.get('device_id'):
                raise NameError(f"Argument: 'device_id' is not defined")
            self.connect_usb_device(device_id=kwargs.get('device_id'))
        elif connection_type.lower() == 'network':
            if not(kwargs.get('device_ip') or kwargs.get('port')):
                raise NameError(f"Argument: 'device_ip' and 'port' is not defined")
            port = None or kwargs.get('port')
            self.connect_net_device(
                device_ip=kwargs.get('device_ip'),
                port=port)
        else:
            raise ValueError(f"Unsupported connection type: {connection_type}")

    def execute_shell_command(self,
                              command: str = "",
                              return_stdout: bool = True,
                              return_rc: bool = False,
                              return_stderr: bool = False) -> Union[str, Tuple]:
        """
        Execute a shell command on the device.
        """
        if not(self.device_id or self.connected):
            raise ValueError(
                "No ADB device Found. Use create_connection keyword. "
                f"device_id:{self.device_id}, connected:{self.connected}"
                )

        if command.startswith("adb") or command.startswith("shell"):
            raise ValueError(f"Invalid shell command: '{command}'")

        full_command = f"adb -s {self.device_id} shell {command}"
        logger.info("Executing Command: %s", full_command)
        process = subprocess.Popen(full_command, shell=True,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   encoding='UTF-8')
        stdout, stderr = process.communicate()

        logger.debug(
            f"\nResponse output: {stdout.strip()}, \nerror:{stderr.strip()}, \nrc:{process.returncode}"
            )
        response = []
        if return_stdout:
            response.append(stdout.strip())
        if return_rc:
            response.append(process.returncode)
        if return_stderr:
            response.append(stderr.strip())
        return response if len(response) > 1 else response[0] if response else None

    def execute_command(self,
                        command: str = "",
                        return_stdout: bool = True,
                        return_rc: bool = False,
                        return_stderr: bool = False) -> Union[str, Tuple]:
        """
        Execute a generic ADB command.
        """
        if not(self.device_id or self.connected):
            raise ValueError(
                "No ADB device Found. Use create_connection keyword. "
                f"device_id:{self.device_id}, connected:{self.connected}"
                )

        if not command.startswith("adb"):
            raise ValueError(f"Invalid ADB command: '{command}'")

        if self.device_id and f"-s {self.device_id}" not in command:
            command = command.replace("adb", f"adb -s {self.device_id}", 1)

        logger.info("Execute Adb Command: %s ", command)
        process = subprocess.Popen(command, shell=True,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   encoding='UTF-8')
        stdout, stderr = process.communicate()

        logger.debug(
            f"\nResponse output: {stdout.strip()}, \nerror:{stderr.strip()}, \nrc:{process.returncode}"
            )

        response = []
        if return_stdout:
            response.append(stdout.strip())
        if return_rc:
            response.append(process.returncode)
        if return_stderr:
            response.append(stderr.strip())
        return response if len(response) > 1 else response[0] if response else None

    def get_hardware_name(self) -> str:
        """
        Obtain the hardware name of the device.
        """
        if not(self.device_id or self.connected):
            raise ValueError(
                "No ADB device Found. Use create_connection keyword. "
                f"device_id:{self.device_id}, connected:{self.connected}"
                )

        cmd = f"adb -s {self.device_id} shell getprop ro.hardware"

        logger.info("Execute Command: %s ", cmd)
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        logger.debug(
            f"\nResponse output: {result.stdout.strip()},"
            f"\nerror:{result.stderr.strip()}, \nrc:{result.returncode}"
            )
        if result.returncode != 0:
            raise RuntimeError(
                f"Failed to run this get build product command in this device {self.device_id}")

        output = result.stdout.strip()
        return output

    def reboot_device(self,
                      mode: str = "normal") -> None:
        """
        Reboot the device into a specific mode
        """
        if not(self.device_id or self.connected):
            raise ValueError(
                "No ADB device Found. Use create_connection keyword. "
                f"device_id:{self.device_id}, connected:{self.connected}"
                )

        valid_modes = {
            "normal": "reboot",
            "bootloader": "reboot bootloader",
            "recovery": "reboot recovery"
            }

        if mode.lower() not in valid_modes:
            raise ValueError(f"Invalid reboot mode: {mode}")

        cmd = f"adb -s {self.device_id} shell {valid_modes[mode.lower()]}"
        logger.info("Executing Command: %s", cmd)
        result = subprocess.call(cmd, shell=True)
        logger.debug("Response output: %s", result)
        if result != 0:
            raise RuntimeError(f"Failed to reboot device {self.device_id} into {mode} mode.")

    def get_screen_size(self) -> str:
        """
        Get screen resolution of the device.
        """
        if not(self.device_id or self.connected):
            raise ValueError(
                "No ADB device Found. Use create_connection keyword. "
                f"device_id:{self.device_id}, connected:{self.connected}"
                )

        cmd = f"adb -s {self.device_id} shell wm size"
        logger.info("Executing Command: %s", cmd)
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        logger.debug(
            f"\nResponse output: {result.stdout.strip()},"
            f"\nerror:{result.stderr.strip()}, \nrc:{result.returncode}"
            )
        if result.returncode != 0:
            raise RuntimeError(
                f"Failed to run this get screen size command in this device {self.device_id}")

        output = result.stdout.strip()
        match = re.search(r'(\d+x\d+)', output)
        return match.group(1) if match else None

    def get_android_version(self) -> str:
        """
        Get Android OS version.
        """
        if not(self.device_id or self.connected):
            raise ValueError(
                "No ADB device Found. Use create_connection keyword. "
                f"device_id:{self.device_id}, connected:{self.connected}"
                )

        cmd = f"adb -s {self.device_id} shell getprop ro.build.version.release"
        logger.info("Executing Command: %s ", cmd)
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        logger.debug(
            f"\nResponse output: {result.stdout.strip()},"
            f"\nerror:{result.stderr.strip()}, \nrc:{result.returncode}"
            )
        if result.returncode != 0:
            raise RuntimeError(
                f"Failed to run this get android version command in this device {self.device_id}")

        return result.stdout.strip()

    def get_state(self) -> str:
        """
        Get the connection state of the device.
        """
        if not(self.device_id or self.connected):
            raise ValueError(
                "No ADB device Found. Use create_connection keyword. "
                f"device_id:{self.device_id}, connected:{self.connected}"
                )

        cmd = f"adb -s {self.device_id} get-state"
        logger.info("Executing Command: %s", cmd)

        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        logger.debug(
            f"\nResponse output: {result.stdout.strip()},"
            f"\nerror:{result.stderr.strip()}, \nrc:{result.returncode}"
            )

        if result.returncode != 0:
            raise RuntimeError(
                f"Failed to run this get state command in this device {self.device_id}")

        output = result.stdout.strip()
        return output

    def get_serial_number(self,
                          device_id: Optional[str] = None) -> str:
        """
        Get the serial number of the device.
        """
        if not(self.device_id or self.connected):
            raise ValueError(
                "No ADB device Found. Use create_connection keyword. "
                f"device_id:{self.device_id}, connected:{self.connected}"
                )

        cmd = f"adb -s {self.device_id} get-serialno"

        logger.info("Executing Command: %s", cmd)
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        logger.debug(
            f"\nResponse output: {result.stdout.strip()},"
            f"\nerror:{result.stderr.strip()}, \nrc:{result.returncode}"
            )

        if result.returncode != 0:
            raise RuntimeError(
                f"Failed to run this get serial command in this device {self.device_id}")

        output = result.stdout.strip()
        return output

    def switch_connection(self,
                          device_id: Optional[str]) -> None:
        """
        Switch to a different ADB device.
        """
        logger.info("Before switch connection: %s", self.device_id)
        if not self._is_device_connected(device_id):
            raise RuntimeError(f"ADB device : {device_id} not connected")
        self.device_id = device_id
        self.connected = True
        logger.info("Current connection: %s", self.device_id)

    def get_build_product(self) -> str:
        """
        Obtain the product of the device.
        """
        if not(self.device_id or self.connected):
            raise ValueError(
                "No ADB device Found. Use create_connection keyword. "
                f"device_id:{self.device_id}, connected:{self.connected}"
                )

        cmd = f"adb -s {self.device_id} shell getprop ro.build.product"

        logger.info("Executing Command: %s", cmd)

        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        logger.debug(
            f"\nResponse output: {result.stdout.strip()},"
            f"\nerror:{result.stderr.strip()}, \nrc:{result.returncode}"
            )

        if result.returncode != 0:
            raise RuntimeError(
                f"Failed to run this get build product command in this device {self.device_id}")

        output = result.stdout.strip()

        return output

    def send_file(self,
                  src_file: str = "",
                  dst_file: str = "") -> None:
        """
        Get a file from host to device.
        """
        if not(self.device_id or self.connected):
            raise ValueError(
                "No ADB device Found. Use create_connection keyword. "
                f"device_id:{self.device_id}, connected:{self.connected}"
                )

        if not os.path.exists(src_file):
            raise FileNotFoundError(f"Invalid filepath '{src_file}'")

        cmd = f"adb -s {self.device_id} push {src_file} {dst_file}"
        logger.info("Executing Command: %s", cmd)
        result = subprocess.call(cmd, shell=True)
        logger.debug("\nResponse return code: %s", result)

        if result != 0:
            raise RuntimeError(f"Failed to send file {src_file} to {self.device_id}")

        logger.debug(
            "File successfully transfer from local machine to %s", self.device_id)

    def receive_file(self,
                     src_file: str = "",
                     dst_file: str = "") -> None:
        """
        Pull a file from device to host.
        """
        if not(self.device_id or self.connected):
            raise ValueError(
                "No ADB device Found. Use create_connection keyword. "
                f"device_id:{self.device_id}, connected:{self.connected}"
                )

        cmd = f"adb -s {self.device_id} pull {src_file} {dst_file}"
        logger.info("Executing Command: %s", cmd)
        result = subprocess.call(cmd, shell=True)
        logger.debug("\nResponse return code: %s", result)

        if result != 0:
            raise RuntimeError(f"Failed to receive file {src_file} to {self.device_id}")

        if not os.path.exists(dst_file):
            raise FileNotFoundError(f"File Not Found:'{dst_file}'")
        logger.debug(
            f"File successfully transfer from {self.device_id} to local machine.")

    def set_root_access(self) -> None:
        """
        Set the root access of the device
        """
        if not(self.device_id or self.connected):
            raise ValueError(
                "No ADB device Found. Use create_connection keyword. "
                f"device_id:{self.device_id}, connected:{self.connected}"
                )

        cmd = f"adb -s {self.device_id} root"
        logger.info("Executing command: %s", cmd)
        result = subprocess.call(cmd, shell=True)
        logger.debug("\nResponse return code: %s", result)
        if result != 0:
            raise RuntimeError(f"Failed to execute the root access command")
        logger.debug(f"Successfully set root access")

    def set_unroot_access(self) -> None:
        """
        Set the unroot access of the device
        """
        if not(self.device_id or self.connected):
            raise ValueError(
                "No ADB device Found. Use create_connection keyword. "
                f"device_id:{self.device_id}, connected:{self.connected}"
                )

        cmd = f"adb -s {self.device_id} unroot"
        logger.info("Executing command: %s", cmd)
        result = subprocess.call(cmd, shell=True)
        logger.debug(f"\nResponse return code: %s", result)
        if result != 0:
            raise RuntimeError(f"Failed to execute the unroot access command")
        logger.debug("Successfully set unroot access")

    def install_apk(self,
                    apk_file: str = "",
                    mode: str = "normal") -> None:
        """
        Install the specified APK file to the device
        """
        if not(self.device_id or self.connected):
            raise ValueError(
                "No ADB device Found. Use create_connection keyword. "
                f"device_id:{self.device_id}, connected:{self.connected}"
                )

        valid_modes = {
            "normal": " ",
            "replace": " -r",
            "downgrade": " -d",
            "test": " -t"
            }

        if mode.lower() not in valid_modes:
            raise ValueError(f"Invalid installation mode: {mode}")

        if not(os.path.exists(apk_file) or apk_file.endswith(".apk")):
            raise FileNotFoundError(f"Invalid filepath '{apk_file}'")

        cmd = f"adb -s {self.device_id} install{valid_modes[mode]} {apk_file}"
        logger.info("Executing command: %s", cmd)
        result = subprocess.call(cmd, shell=True)

        logger.debug("\nResponse return code: %s", result)
        if result != 0:
            raise RuntimeError(f"Failed to execute an install apk file command")
        logger.debug("Successfully installed the %s file.", apk_file)

    def uninstall_apk(self,
                      apk_package: str = "") -> None:
        """
        Uninstall the specified package to the device
        """
        if not(self.device_id or self.connected):
            raise ValueError(
                "No ADB device Found. Use create_connection keyword. "
                f"device_id:{self.device_id}, connected:{self.connected}"
                )

        if not apk_package.startswith("com."):
            raise ValueError(f"Invalid package name: {apk_package}")

        cmd = f"adb -s {self.device_id} uninstall {apk_package}"
        logger.info(f"Executing command: %s", cmd)
        result = subprocess.call(cmd, shell=True)

        logger.debug("\nResponse return code: %s", result)
        if result != 0:
            raise RuntimeError(
                f"Failed to run an uninstall apk file command\n"
                f"Check apk package: {apk_package}. use 'find package' keyword")
        logger.debug(f"Successfully uninstalled the %s.", apk_package)

    def get_installed_packages(self) -> list:
        """
        Get list of installed packages from the device
        """
        if not(self.device_id or self.connected):
            raise ValueError(
                "No ADB device Found. Use create_connection keyword. "
                f"device_id:{self.device_id}, connected:{self.connected}"
                )

        cmd = f"adb -s {self.device_id} shell pm list packages"
        logger.info("Executing command: %s", cmd)
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        logger.debug(
            f"\nResponse output: {result.stdout.strip()},"
            f"\nerror:{result.stderr.strip()}, \nrc:{result.returncode}"
            )

        if result.returncode != 0:
            raise RuntimeError(
                f"Failed to run this get installed packages command in {self.device_id}")
        output = result.stdout.strip()
        installed = [line.replace("package:", "").strip() for line in output.splitlines()]
        logger.debug("\nlist of packages: %s", installed)
        return installed

    def package_should_exist(self,
                             package_name: str = None) -> None:
        """
        Ensure the packages is should exist.
        """
        packages = self.get_installed_packages()
        if not(package_name.startswith("package:") or package_name.startswith("com.")):
            raise ValueError(f"Invalid Package name. {package_name}")
        package_name = package_name.replace("package:", "")
        assert package_name in packages, f"Package '{package_name}' does not exist"

    def package_should_not_exist(self,
                                 package_name: Optional[str] = None) -> None:
        """
        Ensure the packages is should not exist.
        """
        packages = self.get_installed_packages()
        if not(package_name.startswith("package:") or package_name.startswith("com.")):
            raise ValueError(f"Invalid Package name. {package_name}")
        package_name = package_name.replace("package:", "")
        assert package_name not in packages, f"Package '{package_name}' exists"

    def switch_to_usb_mode(self) -> None:
        """
        Switch device back to USB mode.
        """
        if not(self.device_id or self.connected):
            raise ValueError(
                "No ADB device Found. Use create_connection keyword. "
                f"device_id:{self.device_id}, connected:{self.connected}"
                )

        cmd = f"adb -s {self.device_id} usb"
        logger.info("Executing command: %s", cmd)
        result = subprocess.call(cmd, shell=True)

        logger.debug(f"\nResponse return code: {result}")
        if result != 0:
            raise RuntimeError(f"Failed to execute the switch to usb mode command")
        logger.debug("%s back to USB mode.", self.device_id)

    def take_screenshot(self,
                        filename: str = 'screenshot.png') -> None:
        """
        Takes a screenshot from the specified ADB device.
        """
        if not(self.device_id or self.connected):
            raise ValueError(
                "No ADB device Found. Use create_connection keyword. "
                f"device_id:{self.device_id}, connected:{self.connected}"
                )

        image_formats = ["png", "jpg", "jpeg", "webp", "bmp", "gif", "heif", "heic"]
        if not filename.lower().endswith(tuple(image_formats)):
            raise ValueError(
                f"Invalid image format {filename}. Supporting format: {image_formats}")

        cmd = f"adb -s {self.device_id} exec-out screencap -p > {filename}"
        logger.info("Executing Command: %s", cmd)
        result = subprocess.call(cmd, shell=True)
        logger.debug("\nResponse return code: %s", result)

        if result != 0:
            raise RuntimeError(f"Failed to transfer {filename} from {self.device_id}")

        if not os.path.exists(filename):
            raise FileNotFoundError(f"File not exists/found, Check filepath: {filename}")

        logger.debug(
            "Screen capture successfully and transfer from %s to local machine", self.device_id)

    def get_apk_path(self,
                     package_name: str="") -> str:
        """
        Get apk file path in given package name
        """
        packages = self.get_installed_packages()
        if not(package_name.startswith("package:") or package_name.startswith("com.")):
            raise ValueError(f"Invalid Package name. {package_name}")
        package_name = package_name.replace("package:", "")

        assert package_name in packages, f"Package '{package_name}' does not exists"

        cmd = f"adb -s {self.device_id} shell pm path {package_name}"
        logger.info("Executing command: %s", cmd)
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        logger.debug(
            f"\nResponse output: {result.stdout.strip()},"
            f"\nerror:{result.stderr.strip()}, \nrc:{result.returncode}"
            )

        if result.returncode != 0:
            raise RuntimeError(
                f"Failed to run this get apk file path command in {self.device_id}")
        return result.stdout.strip()

    def get_package_info(self,
                         package_name: str="") -> str:
        """
        Retrieves the details about the installed package on the device.
        """
        packages = self.get_installed_packages()
        if not(package_name.startswith("package:") or package_name.startswith("com.")):
            raise ValueError(f"Invalid Package name. {package_name}")
        package_name = package_name.replace("package:", "")

        assert package_name in packages, f"Package '{package_name}' does not exists"

        cmd = f"adb -s {self.device_id} shell dumpsys package {package_name}"
        logger.info("Executing command: %s", cmd)
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        logger.debug(
            f"\nResponse output: {result.stdout.strip()},"
            f"\nerror:{result.stderr.strip()}, \nrc:{result.returncode}"
            )

        if result.returncode != 0:
            raise RuntimeError(
                f"Failed to run this get apk package info command in {self.device_id}")
        return result.stdout.strip()

    def clear_app_data(self,
                       package_name: str="") -> str:
        """
        Clear app data from given installed package name
        """
        packages = self.get_installed_packages()
        if not(package_name.startswith("package:") or package_name.startswith("com.")):
            raise ValueError(f"Invalid Package name. {package_name}")
        package_name = package_name.replace("package:", "")

        assert package_name in packages, f"Package '{package_name}' does not exists"

        cmd = f"adb -s {self.device_id} shell pm clear {package_name}"
        logger.info("Executing command: %s", cmd)
        result = subprocess.call(cmd, shell=True)

        logger.debug("\nResponse return code: %s", result)
        if result != 0:
            raise RuntimeError(
                f"Failed to run this clear app data command in {self.device_id}")
        logger.debug("The data has been cleared to the given %s", package_name)

    def disconnect_device(self) -> None:
        """
        Disconnect the current ADB device.
        """
        logger.info("Disconnect to Current adb device")
        self.connected = False
        logger.debug(
            "Current device_id={self.device_id}, self.connected={self.connected}")


    def open_default_browser(self) -> None:
        """
        Open the default web browser on the connected Android device using a key event.
        """
        if not(self.device_id or self.connected):
            raise ValueError(
                "No ADB device Found. Use create_connection keyword. "
                f"device_id:{self.device_id}, connected:{self.connected}"
                )

        cmd = f"adb -s {self.device_id} shell input keyevent 64"
        logger.info("Executing Command: %s", cmd)
        result = subprocess.call(cmd, shell=True)
        logger.debug("\nResponse return code: %s", result)

        if result != 0:
            raise RuntimeError(f"Failed to open the default browser from {self.device_id}")

        logger.debug(
            "Opened default browser in this device: %s", self.device_id)

    def wake_up_screen(self) -> None:
        """
        Wake up screen on specifieid device
        """
        if not(self.device_id or self.connected):
            raise ValueError(
                "No ADB device Found. Use create_connection keyword. "
                f"device_id:{self.device_id}, connected:{self.connected}"
                )

        cmd = f"adb -s {self.device_id} shell input keyevent 224"
        logger.info("Executing Command: %s", cmd)
        result = subprocess.call(cmd, shell=True)
        logger.debug("\nResponse return code: %s", result)

        if result != 0:
            raise RuntimeError(f"Failed to wake up screen command from {self.device_id}")

        logger.debug(
            "The device: %s is displayed ON", self.device_id)

    def sleep_screen(self) -> None:
        """
        Sleep screen on specifieid device
        """
        if not(self.device_id or self.connected):
            raise ValueError(
                "No ADB device Found. Use create_connection keyword. "
                f"device_id:{self.device_id}, connected:{self.connected}"
                )

        cmd = f"adb -s {self.device_id} shell input keyevent 223"
        logger.info("Executing Command: %s", cmd)
        result = subprocess.call(cmd, shell=True)
        logger.debug("\nResponse return code: %s", result)

        if result != 0:
            raise RuntimeError(f"Failed to sleep screen command from {self.device_id}")

        logger.debug(
            "The device: %s is displayed OFF", self.device_id)

    def send_keyevent(self,
                      value: int = None) -> str:
        """
        Sends a keyevent input command to the connected Android device using ADB.
        """
        if not(self.device_id or self.connected):
            raise ValueError(
                "No ADB device Found. Use create_connection keyword. "
                f"device_id:{self.device_id}, connected:{self.connected}"
                )

        if value not in range(0, 225):
            raise ValueError(
                f"Invalid keyevent input value:{value}"
                f"value supports from 0 to 224")

        cmd = f"adb -s {self.device_id} shell input keyevent {value}"
        logger.info("Executing Command: %s", cmd)
        result = subprocess.call(cmd, shell=True)
        logger.debug("\nResponse return code: %s", result)

        if result != 0:
            raise RuntimeError(f"Failed to run the send_keyevent from {self.device_id}")

        logger.debug(
            f"Triggered keyevent {value} in {self.device_id}")

    def set_screen_size(self,
                        width: Optional[int] = None,
                        height: Optional[int] = None) -> None:
        """
        Sets the screen resolution (width x height) on an Android device using ADB.
        """
        if not(self.device_id or self.connected):
            raise ValueError(
                "No ADB device Found. Use create_connection keyword. "
                f"device_id:{self.device_id}, connected:{self.connected}"
                )

        if not(isinstance(int(width), int) and isinstance(int(height), int)):
            raise ValueError(f"invalid parameters width:{width} and height:{height}")

        cmd = f"adb -s {self.device_id} shell wm size {int(width)}x{int(height)}"
        logger.info("Executing Command: %s", cmd)
        result = subprocess.call(cmd, shell=True)
        logger.debug("\nResponse return code: %s", result)
        if result != 0:
            raise RuntimeError(
                f"Failed to run this set screen size command in this device {self.device_id}")
        logger.debug(
            f"Screen resolution successfully set {width}x{height} in {self.device_id}")

    def get_running_processes(self) -> str:
        """
        Retrieves the list of currently running processes on the connected Android device.
        """
        if not(self.device_id or self.connected):
            raise ValueError(
                "No ADB device Found. Use create_connection keyword. "
                f"device_id:{self.device_id}, connected:{self.connected}"
                )

        cmd = f"adb -s {self.device_id} shell ps"
        logger.info("Executing command: %s", cmd)
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        logger.debug(
            f"\nResponse output: {result.stdout.strip()},"
            f"\nerror:{result.stderr.strip()}, \nrc:{result.returncode}"
            )

        if result.returncode != 0:
            raise RuntimeError(
                f"Failed to run this get apk package info command in {self.device_id}")
        return result.stdout.strip()

    def get_all_services(self) -> str:
        """
        Retrieves the list of all services available on the connected Android device
        """
        if not(self.device_id or self.connected):
            raise ValueError(
                "No ADB device Found. Use create_connection keyword. "
                f"device_id:{self.device_id}, connected:{self.connected}"
                )

        cmd = f"adb -s {self.device_id} shell service list"
        logger.info("Executing command: %s", cmd)
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        logger.debug(
            f"\nResponse output: {result.stdout.strip()},"
            f"\nerror:{result.stderr.strip()}, \nrc:{result.returncode}"
            )

        if result.returncode != 0:
            raise RuntimeError(
                f"Failed to run this get apk package info command in {self.device_id}")
        return result.stdout.strip()

    def send_text(self,
                  text: Optional[str] = None) -> None:
        """
        Sends a input text command to the connected Android device using ADB.
        """
        if not(self.device_id or self.connected):
            raise ValueError(
                "No ADB device Found. Use create_connection keyword. "
                f"device_id:{self.device_id}, connected:{self.connected}"
                )

        cmd = f'adb -s {self.device_id} shell input text "{str(text)}"'
        logger.info("Executing Command:%s", cmd)
        result = subprocess.call(cmd, shell=True)
        logger.debug("\nResponse return code: %s", result)

        if result != 0:
            raise RuntimeError(f"Failed to run the send_text from {self.device_id}")

        logger.debug(
            f"Triggered keyevent {text} in {self.device_id}")

    def close_connection(self) -> None:
        """
        Close connection of the device
        """
        logger.info("Close current adb connection")
        self.device_id = None
        self.connected = False
        logger.debug(
            f"Current connection:\n"
            f"device_id={self.device_id},self.connected={self.connected}"
            )

    def close_all_connections(self) -> None:
        """
        Close all adb connections
        """
        self.device_id = None
        self.connected = False

    def get_device_log(self,
                       log_name: Optional[str] = None,
                       timeout: int = 5) -> str:
        """
        Get the device log info, save file too on the connected Android device.
        """
        if not(self.device_id or self.connected):
            raise ValueError(
                "No ADB device Found. Use create_connection keyword. "
                f"device_id:{self.device_id}, connected:{self.connected}"
                )

        cmd = ["adb", "-s", self.device_id, "logcat"]
        logger.info(f"Executing command: {' '.join(cmd)}")

        try:
            proc = subprocess.Popen(cmd,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    text=True)
            output_lines = []
            start_time = time.time()

            while time.time() - start_time < timeout:
                line = proc.stdout.readline()
                if line:
                    output_lines.append(line)
            proc.terminate()
            proc.wait(timeout=5)

            log_output = ''.join(output_lines).strip()

            if log_name:
                try:
                    with open(log_name, "w", encoding="utf-8") as f:
                        f.write(log_output)
                    logger.info("Log saved to %s", log_name)
                except IOError as e:
                    logger.warning("Failed to save log to %s: %s", log_name, e)

            return log_output

        except Exception as e:
            proc.kill()
            raise RuntimeError(f"Error while capturing logcat: {e}") from e


if __name__ == '__main__':
    adb = AdbConnection()
    adb.start_adb_server(port=5222)
    adb.create_connection(connection_type='usb', device_id='10000000cd0c07a6')
    print(adb.get_screen_size())
    print(adb.execute_shell_command(command="input keyevent 224"))
    time.sleep(3)
    print(adb.execute_command(command="adb shell input keyevent 223"))
    time.sleep(3)
    print(adb.execute_shell_command(command="input keyevent 224"))
    adb.set_unroot_access()
    time.sleep(5)
    adb.set_root_access()
    time.sleep(5)
    adb.enable_tcpip_mode()
    adb.create_connection(connection_type='network', device_ip='192.168.1.103')
    ip_address = adb.get_interface_ipv4(interface="wlan0")
    print(ip_address)
    adb.disconnect_device()
    time.sleep(5)
    adb.create_connection(connection_type='network', device_ip='192.168.1.103')
    print(adb.execute_command(command="adb shell input keyevent 223"))
    time.sleep(3)
    adb.switch_connection(device_id='10000000cd0c07a6')
    print(adb.execute_shell_command(command="input keyevent 224"))
    adb.switch_connection('192.168.1.103:5555')
    adb.open_default_browser()

    print(adb.get_hardware_name())  #rpi4
    print(adb.get_screen_size())   # 1920x1080
    print(adb.get_android_version())  # 15
    print(adb.get_state())  # device
    print(adb.get_serial_number())  # 10000000cd0c07a6
    print(adb.get_build_product())
    #adb.kill_adb_server()
    #adb.close_connection()
    filename = "iperf.log"
    adb.send_file(src_file=filename, dst_file="/tmp/ganesan.log")
    adb.receive_file(src_file="/tmp/ganesan.log", dst_file="/tmp/demo.log")
    install_apk = "root-checker.apk"
    adb.install_apk(apk_file=install_apk, mode="test")
    time.sleep(10)

    print(adb.get_installed_packages())
    print(adb.package_should_exist(package_name="com.android.theme.icon_pack.circular.android"))
    print(adb.package_should_not_exist(package_name="com.android.theme.icon_pack.circular.android23"))
    adb.create_connection(connection_type='usb', device_id='10000000cd0c07a6')
    adb.switch_to_usb_mode()
    time.sleep(5)
    adb.take_screenshot(filename="ganesan.jpg")
    print(adb.get_device_log(log_name='ganesan.log'))

    print(adb.get_apk_path(package_name="com.joeykrim.rootcheck"))
    adb.clear_app_data(package_name="com.joeykrim.rootcheck")
    print(adb.get_package_info(package_name="com.joeykrim.rootcheck"))

    uninstall_apk = "com.joeykrim.rootcheck"
    adb.uninstall_apk(apk_package=uninstall_apk)


    adb.send_keyevent(value=224)
    adb.set_screen_size(width='1024', height='720')
    print(adb.get_running_processes())
    print(adb.get_all_services())

    adb.send_text(text="10+54")

    mode = "bootloader"
    adb.reboot_device(mode=mode)
