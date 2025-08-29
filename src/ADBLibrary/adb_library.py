"""ADBLibrary is a library for the Robot Framework that provides ADB-related functionalities."""
# local libraries
from robot.api.deco import keyword, library
from core.adb_proxy import AdbProxy

__version__ = "0.1.3"

@library(scope='GLOBAL', auto_keywords=False)
class ADBLibrary:
    """
    ADBLibrary is a custom Robot Framework library for automating Android device interactions
    using the Android Debug Bridge (ADB). It provides a robust and extensible interface for
    executing ADB commands, managing device state, and performing advanced operations across
    multiple connected devices.

    This library is built on the **proxy design pattern**, which abstracts and manages ADB connections
    through a centralized `AdbProxy` layer. This allows seamless switching between devices, thread-safe
    execution, and efficient reuse of established connections.

    🔹 Core Capabilities:
        - Multi-device management with dynamic switching
        - USB and TCP/IP connection support
        - Shell command execution with flexible output handling
        - Device control: wake, sleep, reboot, screen resolution, screenshots
        - App lifecycle: install, uninstall, clear data, verify packages
        - Device info: serial number, hardware name, build product, Android version
        - File transfers: push/pull between host and device
        - Debug utilities: log capture, running processes, service listing
        - Root access control: enable/disable root, test mode installation
        - Input simulation: send keyevents, text input, open browser

    🔹 Architecture:
        - Implements the **proxy design pattern** via `AdbProxy` for connection abstraction
        - Thread-local context for safe parallel execution
        - Internal caching of device connections for fast switching
        - Designed for extensibility and clean integration with other Robot Framework libraries

    🔹 Device Compatibility:
        - Most keywords require the device to be in **rooted debugging mode**.
        - On **unrooted devices**, only a subset of keywords are supported:

            Supported on unrooted devices:
                - Create Connection
                - Get Connection
                - Switch Connection
                - Execute Shell Command
                - Execute Command
                - Get Screen Size
                - Get Serial Number
                - Get State
                - Get Android Version
                - Get Installed Packages
                - Package Should Exist / Not Exist

            Root-only keywords include:
                - File transfers (Send/Receive File)
                - App data clearing
                - Test-mode APK installation
                - TCP/IP mode switching
                - Browser and input simulation
                - Screenshot and screen resolution control

    🔹 Attributes:
        ROBOT_LIBRARY_SCOPE (str): Defines the library scope as 'GLOBAL'.
        _connected_devices (dict): Stores connected device aliases and their corresponding IDs.

    🔹 Example usage in Robot Framework:
        | *** Settings ***
        | Library    ADBLibrary

        | *** Test Cases ***
        | Example Test
        |     Create Connection    type=usb    device_id=10000000cd0c07a6
        |     Enable Tcpip Mode    port=5555
        |     Create Connection    type=network    device_ip=192.168.1.103
        |     ${version}=    Get Android Version
        |     Log    Android version: ${version}

    🔹 Notes:
        - Device connection is validated before each operation.
        - Root access may be required depending on the command.
        - For full documentation, refer to individual keyword docstrings or generate HTML docs using `libdoc`.
        - Contributions, bug reports, and feature requests are welcome via GitHub.
    """
    ROBOT_LIBRARY_VERSION = __version__
    ROBOT_LIBRARY_SCOPE = "GLOBAL"

    def __init__(self):
        self.adb = AdbProxy()

    @keyword("Start Adb Server")
    def start_adb_server(self,
                         port:int=5037):
        """
        Start the ADB server with specified or default port.

        ``Args``:
            - ``port:`` Set the adb server port. By default sever port is 5037.

        ``Raises:``
            - ``RuntimeError:`` If the ADB server fails to start.

        Example:
        | Start Adb Server | # start adb server with default port |
        | Start Adb Server | port=5038 | # Adb server running into the port 5038. |
        """
        return self.adb.start_adb_server(port=port)

    @keyword("Kill Adb Server")
    def kill_adb_server(self,
                        port:int=5037):
        """kill the ADB server with specified port or default port.

        ``Args``:
            - ``port:`` Set the adb server port. By default sever port is 5037.

        ``Raises:``
            - ``RuntimeError:`` If the ADB server fails to kill.

        Example:
        | Kill Adb server | # default port |
        | Kill Adb Server | port=5038 |
        """
        return self.adb.kill_adb_server(port)

    @keyword("Enable Tcpip Mode")
    def enable_tcpip_mode(self, port: int = 5555) -> None:
        """
        Enables TCP/IP mode on the currently connected ADB device.

        This keyword is important for creating a connection based on network mode.
        It must be used before attempting to connect via IP.

        TCP/IP mode can only be enabled when the device is connected via USB.

        ``Args``:
            - ``port(int)``: The TCP/IP port to use. the default port is 5555.

        ``Raises``:
            - ``ValueError``: If the current device is already in network mode (IP:port format).
            - ``RuntimeError``: If the ADB command to enable TCP/IP mode fails.

        Example:
        | Create Connection     | type=usb | device_id=10000000cd0c07a6 |
        | Enable Tcpip Mode     | port=5555 |
        | Create Connection     | type=network | device_ip=192.168.1.103 |
        """
        self.adb.enable_tcpip_mode(port=port)


    @keyword("Create Connection")
    def create_connection(self,
                          type: str = 'usb',
                          device_id: str = None,
                          device_ip: str = None,
                          port: int = 5555):
        """
        Establishes an ADB (Android Debug Bridge) connection to a device via USB or network.

        This keyword supports two connection types:
        - 'usb': Connects to a device using its USB interface. Requires `device_id`.
        - 'network': Connects to a device over TCP/IP. Requires `device_ip` and optionally `port`.

        ``Args``:
            - ``type(str)``: Type of connection to establish.
                             Must be either 'usb' or 'network'. Defaults to 'usb'.
            - ``device_id(str, optional)``: Unique identifier of the USB-connected device.
            - ``device_ip(str, optional)``: IP address of the device for network connection.
            - ``port(int, optional)``: Port number for network connection. Defaults to 5555.

        ``Raises``:
            - ``ValueError``: If an unsupported connection type is provided.

        Example:
        | Create Connection | type=network | device_ip=192.168.0.101 | port=5555 |
        | Create Connection | type=usb     | device_id=emulator-5554 |
        """
        if type == 'usb':
            self.adb.create_connection(connection_type='usb', device_id=device_id)
        elif type == 'network':
            self.adb.create_connection(connection_type='network', device_ip=device_ip, port=port)

    @keyword("Get Connection")
    def get_connection(self) -> str:
        """
        Returns the currently active ADB connection identifier.

        Returns:
            str: The device ID or IP:port string of the active ADB connection.

        Raises:
            RuntimeError: If no ADB connection has been established.

        Example:
        | Create Connection | type=network | device_ip=192.168.0.101 | port=5555 |
        | ${stdout} | Get Connection |
        | Log  | ${stdout} | # Output: 192.168.0.101:5555 |
        | Create Connection | type=usb     | device_id=emulator-5554 |
        | ${stdout2} | Get Connection |
        | Log | ${stdout2} | # Output: emulator-5554 |
        """
        self.adb.get_connection()

    @keyword("Switch Connection")
    def switch_connection(self,
                          device_id: str):
        """
        Switches the active ADB connection to the specified device.

        ``Args``:
            - device_id(str): The target device identifier or IP:port string to switch to.
                              Must match an existing connection.

        ``Raises``:
            - ``RuntimeError``: If the specified device ID is not found among active connections.

        Example:
        | Create Connection | type=network | device_ip=192.168.0.101 | port=5555 |
        | ${stdout} | Get Connection |
        | Log | ${stout} | # Output: 192.168.0.101:5555 |
        | Create Connection | type=usb     | device_id=emulator-5554 |
        | ${stdout} | Get Connection |
        | Log | ${stdout} | # Output: emulator-5554 |
        | Switch Connection | device_id=192.168.0.101:5555 |
        | ${stdout} | Get Connection |
        | Log | ${stdout} |# Output: 192.168.0.101:5555 |
        """
        self.adb.switch_connection(device_id=device_id)

    @keyword("Execute Shell Command")
    def execute_shell_command(self,
                              command: str,
                              return_stdout=True,
                              return_rc=False,
                              return_stderr=False):
        """
        Execute a shell command on an ADB-connected device.
        The `adb shell` command does not need to be passed.

        ``Args``:
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
        | Execute Shell Command | input keyevent 224 |
        | ${out}  Execute Shell Command | command=input keyevent 224 |
        """
        return self.adb.execute_shell_command(command=command,
                                              return_stdout=return_stdout,
                                              return_rc=return_rc,
                                              return_stderr=return_stderr)

    @keyword("Execute Command")
    def execute_command(self,
                        command: str,
                        return_stdout=True,
                        return_rc=False,
                        return_stderr=False):
        """
         Execute a generic ADB command (supports all adb commands) using subprocess
         from current connected devices.

        ``Args:``
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
        | Create Adb Connection | usb | device_id=XXRZXXCT81F |
        | Execute Command | adb shell input keyevent 224 |
        | ${stdout}  Execute Command | command=adb devices -l |
        | Log | ${stdout} |
        | ${stdout2}  Execute Command | command=adb get-state |
        | Log | ${stdout2} | # state of default adb device |
        | ${stdout3}  Execute Command | command=adb -s XXRZXXCT81F get-state |
        | Log | ${stdout2} | # state of default adb device |
        | ${rc} | Execute Command | command=adb get-state | return_stdout=False | return_rc=True |
        | Should Be True | ${rc} == 0 |
        """
        return self.adb.execute_command(command=command,
                                        return_stdout=return_stdout,
                                        return_rc=return_rc,
                                        return_stderr=return_stderr)

    @keyword("Get Hardware Name")
    def get_hardware_name(self) -> str:
        """
        Retrieve the hardware name from current connected adb device.

        ``Returns:``
            - ``Return(str)``: return the adb device hardware name.
        ``Raises:``
            - ``RuntimeError:`` command execution failed.

        Example:
        | ${stdout} | Get Hardware Name |
        | Log  | ${stdout} | |${stdout}=rpi4 |
        """
        return self.adb.get_hardware_name()

    @keyword("Get State")
    def get_state(self) -> str:
        """
        Retrieve the current adb device state. Returns state of device, offline, unauthorized.

        ``Args:``
            - ``device_id(str):`` Specific device id.

        ``Returns:``
            - Returns the state of current connected device.
            - states are consists of device, offline, unauthorized.
            - For Example: device

        ``Raises:``
            - ``RuntimeError:`` Invalid device id and command execution failed.

        Example:
        | ${stdout} = | Get State |
        | Log | ${stdout} | # ${stdout} = device |
        """
        return self.adb.get_state()

    @keyword("Get Serial Number")
    def get_serial_number(self) -> str:
        """
        Retrieve the current adb device serial number. Returns device serial number.

        ``Returns:``
            The serial number of current connected device.
            For Example: XXRZXXCT81F

        ``Raises:``
            - ``RuntimeError:`` Invalid device id and command execution failed.

        Example:
        | ${stdout} = | Get Serial Number |
        | Log | ${stdout} | # ${stdout} = XXRZXXCT81F |
        """
        return self.adb.get_serial_number()

    @keyword("Disconnect Device")
    def disconnect_device(self):
        """
        Disconnects the current adb device.

        Example:
        | Create Connection | type=usb | device_id=emulator-5554 |
        | ${stdout} | Get Connection | # Output: emulator-5554 |
        | Disconnect Device |
        | ${stdout} | Get Connection | # Output: RuntimeError |
        """
        self.adb.disconnect()

    @keyword("Sleep Screen")
    def sleep_screen(self):
        """
        Put current connected device to sleep

        ``Raises:``
            - ``ValueError:`` Invalid device id
            - ``RuntimeError:`` If the command is not running properly.

        Example:
        | Sleep Screen |
        """
        self.adb.sleep_screen()

    @keyword("Wake Up Screen")
    def wake_up_screen(self):
        """
        Wake up screen on current connected device.

        ``Raises:``
            - ``ValueError:`` Invalid device id
            - ``RuntimeError:`` If the command is not running properly.

        Example:
        | Wake Up Screen |
        """
        self.adb.wake_up_screen()

    @keyword("Take Screenshot")
    def take_screenshot(self,
                        filename:str='screenshot.png'):
        """
        Takes a screenshot from the current ADB device (or the current device
        if none is specified) and saves it to the given file path.

        ``Args``:
            - ``device_id(Optional[str]):`` The ID of the ADB device.
                If None, uses the current device.
            - ``filename(str):`` The name (or path) of the file to save the screenshot.
                Defaults to 'screenshot.png'.

        ``Raises:``
            - ``RuntimeError:`` command execution failed.
            - ``FileNotFoundError:`` File not found or file not exists.

        Example:
        | Take Screenshot |   # Default device and default filename |
        | Take Screenshot | filename='/tmp/screen1.png' |

        """
        self.adb.take_screenshot(filename=filename)

    @keyword("Reboot Device")
    def reboot_device(self,
                      mode: str = "normal"):
        """
        Reboots the currently connected ADB device in the specified mode.

        ``Args``:
            mode(str): Reboot mode. Supported values are:
                - "normal" (default): Regular reboot
                - "bootloader": Reboot into bootloader (requires root)
                - "recovery": Reboot into recovery mode (requires root)

        ``Raises:``
            - ValueError: If an unsupported mode is provided.
            - RuntimeError: If the reboot command fails.

        Example:
        | Reboot Device | # Default adb device reboot. |
        | Reboot Device | mode=normal |
        | Reboot Device | mode=bootloader | # root required |
        | Reboot Device | mode=recovery | # root required. |
        """
        self.adb.reboot_device(mode=mode)

    @keyword("Get Screen Size")
    def get_screen_size(self):
        """
        Retrieve the screen size for a current connected adb device

        ``Returns``:
            Screen size in the format 'widthxheight', e.g., '1080x2400'.

        ``Raises:``
            - ``RuntimeError:`` Invalid device id or command fails.

        Example:
        | ${stdout} = | Get Screen Size |
        | Log | ${stdout} | # ${stdout} = 1080x2400 |
        """
        return self.adb.get_screen_size()

    @keyword("Get Android Version")
    def get_android_version(self) -> int:
        """
        Retrieve the android version for current connected device.

        ``Args:``
            - ``device_id(str):`` Specific device id.

        ``Returns:``
            - Returns the android version of given device.
              For Example: 15

        ``Raises:``
            - ``RuntimeError:`` Invalid device id

        Example:
        | ${stdout} = | Get Android Version |
        | Log | ${stdout} | # ${stdout} = 15 |
        """
        return self.adb.get_android_version()

    @keyword("Switch To Usb Mode")
    def switch_to_usb_mode(self):
        """
        Switches the current ADB device back to USB mode.

        ``Raises``:
            - ``RuntimeError``: If the command execution fails.

        Example:
        | Switch To Usb Mode  |
        """
        self.adb.switch_to_usb_mode()

    @keyword("Close All Connections")
    def close_all_connections(self):
        """
        Close all adb connections.

        Example:
        | Create Connection | type=network | device_ip=192.168.0.101 | port=5555 |
        | ${stdout} | Get Connection |
        | Log | ${stdout} | # Output: 192.168.0.101:5555 |
        | Create Connection | type=usb     | device_id=emulator-5554 |
        | ${stdout} | Get Connection |
        | Log | ${stdout} | # Output: emulator-5554 |
        | Close All Connections |
        """
        self.adb.close_all_connections()

    @keyword("Close Connection")
    def close_connection(self):
        """
        Close current adb connection.

        Example:
        | Create Connection | type=usb     | device_id=emulator-5554 |
        | ${stdout} | Get Connection | # Output: emulator-5554 |
        | Close Connection |
        """
        self.adb.close_connection()

    @keyword("Open Default Browser")
    def open_default_browser(self) -> None:
        """
        Opens the default web browser on the connected Android device using a key event.

        ``Raises:``
            - ``RuntimeError:`` If the command to open the browser fails.

        Example:
        | Open Default Browser |
        """
        self.adb.open_default_browser()

    @keyword("Send Text")
    def send_text(self,
                  text: str = None):
        """
        Sends a text input to the connected Android device via ADB.

        This keyword simulates typing the specified text on the device using the ADB input command.

        ``Args:``
            - ``text (str):`` The text to input into the device.

        ``Raises:``
            - ``RuntimeError:`` If the ADB send text command execution fails.

        Example:
        | Set Input Text | text=Hi Adb |
        """
        self.adb.send_text(text=text)

    @keyword("Get All Services")
    def get_all_services(self) -> str:
        """
        Retrieves the list of all services available on the connected Adb device.

        ``Returns:``
            - ``str:`` A string containing the list of all system services.

        ``Raises:``
            - ``RuntimeError:`` If the command to retrieve services fails.

        Example:
        | ${stdout} | Get All Services |
        | Log | ${stdout} |
        """
        return self.adb.get_all_services()

    @keyword("Get Running Processes")
    def get_running_processes(self) -> str:
        """
        Retrieves the list of currently running processes on the connected Adb device.

        ``Returns:``
            - ``str:`` A string containing the list of running processes.
        ``Raises:``
            - ``RuntimeError:`` If the command to retrieve running processes fails.

        Example:
        | ${stdout} | Get Running Processes |
        | Log | ${stdout} |
        """
        return self.adb.get_running_processes()

    @keyword("Get Package Info")
    def get_package_info(self,
                         package_name: str) -> str:
        """
        Retrieves the details about the installed package on the current device.

        ``Args:``
            - ``package_name:`` Specified a installed package name,
                                (e.g., com.android.calculator2).

        ``Return:``
            - ``returns:`` Retrieves the full file path of the installed APK.

        ``Raises:``
            - ``RuntimeError:`` command execution failed.

        Example:
        | ${stdout} | Get Package Info | package_name=com.android.calculator2 |
        | Log | ${stdout} |
        """
        return self.adb.get_package_info(package_name=package_name)

    @keyword("Get Apk Path")
    def get_apk_path(self,
                     package_name: str) -> str:
        """
        Retrieves the full file path of the installed APK on the device.

        ``Args:``
            - ``package_name:`` Specified a installed package name,
                                (e.g., com.android.calculator2).

        ``Return:``
            - ``returns:`` Retrieves the full file path of the installed APK.

        ``Raises:``
            - ``RuntimeError:`` command execution failed.

        Example:
        | ${stdout} | Get Apk Path | package_name=com.android.calculator2 |
        | Log | ${stdout} |
        """
        return self.adb.get_apk_path(package_name=package_name)

    @keyword("Clear App Data")
    def clear_app_data(self,
                       package_name: str= None):
        """
        Resets the app by clearing all stored data of the installed APK.

        ``Args:``
            - ``package_name:`` Specified a installed package name,
                                (e.g., com.android.calculator2).

        ``Raises:``
            - ``RuntimeError:`` command execution failed.

        Example:
        | Clear App Data | package_name=com.android.calculator2 |
        """
        self.adb.clear_app_data(package_name=package_name)

    @keyword("Send File")
    def send_file(self,
                  source_path: str, destination_path: str):
        """
        File[s] send From Source pc to ADB device. Root access required.

        ``Args:``
            - ``source_path(str):`` Specific file or directory in pc
            - ``destination_path(str):`` Specific path of adb device in adb device.

        ``Raises:``
            - ``RuntimeError``: If the send_file command fails.

        Example:
        | Send File | source_path=file.txt | destination_path=/storage/downloads/file.txt |
        | Send File | source_path=/tmp/ | destination_path=/tmp/ |
        """
        self.adb.send_file(src_file=source_path, dst_file=destination_path)

    @keyword("Receive File")
    def receive_file(self,
                     source_path: str,
                     destination_path: str):
        """
        File[s] receive from ADB device to pc. Root access required.

        ``Args:``
            - ``source_path(str):`` Specific file or directory in adb device
            - ``destination_path(str):`` Specific path of adb device in pc.

        ``Raises:``
            - ``RuntimeError``: If the reconnect command fails

        Example:
        | Receive File | source_path=/storage/downloads/file.txt | destination_path=file.txt |
        | Receive File | source_path=/storage/downloads | destination_path=/tmp/ |
        """
        self.adb.receive_file(src_file=source_path, dst_file=destination_path)

    @keyword("Set Root Access")
    def set_root_access(self):
        """
        If your current connected adb device build should be rooted.

        ``Raises:``
            - ``RuntimeError:`` command execution failed.

        Example:
        | Set Root Access |
        """
        self.adb.set_root_access()

    @keyword("Set Unroot Access")
    def set_unroot_access(self):
        """
        If your current connected adb device should be unrooted.

        ``Raises:``
            - ``RuntimeError:`` command execution failed.

        Example:
        | Set Unroot Access |
        """
        self.adb.set_unroot_access()

    @keyword("Install Apk")
    def install_apk(self,
                    apk_file: str = "",
                    mode: str = "normal"):
        """
        Installs the specified APK file to the connected ADB device using the given mode.

        ``Args``:
            - ``apk_file(str)``: Path to the APK file to be installed.
            - ``mode(str)``: Installation mode. Supported values:
                - "normal" (default): Standard installation.
                - "replace": Reinstall the existing package.
                - "downgrade": Downgrade the installed package.
                - "test": Install the package in test mode.

        ``Raises``:
            - ``ValueError``: If an unsupported mode is provided.
            - ``RuntimeError``: If the installation command fails.

        Example:
            | Install Apk | apk_file=root-checker.apk |
            | Install Apk | apk_file=app.apk | mode=replace |
        """
        self.adb.install_apk(apk_file=apk_file,
                             mode=mode)

    @keyword("Uninstall Apk")
    def uninstall_apk(self,
                      apk_package: str=""):
        """
        Uninstalls the specified APK package from the connected ADB device.

        The APK package should be provided in the standard format, such as:
        `com.android.calculator2`

        If you're unsure about the package name, use the `Find Package` keyword to locate it.

        ``Args``:
            - ``apk_package(str)``: The package name of the APK to uninstall
                (e.g., com.android.calculator2).

        ``Raises:``
            - ``RuntimeError:`` command execution failed.

        Example:
        | Uninstall Apk | apk_package=com.android.calculator2 |
        """
        self.adb.uninstall_apk(apk_package=apk_package)

    @keyword("Get Installed Packages")
    def get_installed_packages(self) -> list:
        """
        Retrieves a list of all packages installed on the currently connected ADB device.

        Returns:
            list: A list of package names (e.g., ['com.android.settings', 'com.example.app']).

        Raises:
            ValueError: If no ADB device is connected.
            RuntimeError: If the ADB command fails to execute.

        Example:
        | Create Connection | type=usb | device_id=10000000cd0c07a6 |
        | ${packages} =  | Get Installed Packages |
        | Should Contain | ${packages} | com.android.settings |
        """
        return self.adb.get_installed_packages()

    @keyword("Package Should Exist")
    def package_should_exist(self,
                             package_name: str = None) -> None:
        """
        Verifies that the specified package is installed on the connected ADB device.

        ``Args``:

            - ``package_name(str)``: The name of the package to check. Can be in the form
            'package:com.example.app' or 'com.example.app'.

        ``Raises``:
            - ``ValueError``: If the package name format is invalid.
            - ``AssertionError``: If the package is not found among installed packages.

        Example:
        | Package Should Exist | com.android.settings |
        | Package Should Exist | package:com.joeykrim.rootcheck |
        """
        self.adb.package_should_exist(package_name=package_name)

    @keyword("Package Should Not Exist")
    def package_should_not_exist(self,
                                 package_name: str = None) -> None:
        """
        Verifies that the specified package isn't installed on the connected ADB device.

        ``Args``:
            - ``package_name(str)``: The name of the package to check. Can be in the form
                                'package:com.example.app' or 'com.example.app'.

        ``Raises``:
            - ``ValueError``: If the package name format is valid.
            - ``AssertionError``: If the package is found among installed packages.

        Example:
        | Package Should Not Exist | com.android.settings |
        | Package Should Not Exist | package:com.joeykrim.rootcheck |
        """
        self.adb.package_should_not_exist(package_name=package_name)

    @keyword("Get Build Product")
    def get_build_product(self) -> str:
        """
        Retrieve the build product on the current device.

        ``Returns:``
            - ``Return(str)``: return the build product.

        ``Raises:``
            - ``RuntimeError:`` command execution failed.

        Example:
        | ${stdout} | Get Build Product |
        | Log | ${stdout} | # ${stdout}=rpi4 |
        """
        return self.adb.get_build_product()

    @keyword("Get Interface IPv4")
    def get_interface_ipv4(self,
                           interface: str = None) -> str:
        """
        Retrieves the IPv4 address of the specified network interface on the connected ADB device.

        This keyword is useful for verifying device connectivity and extracting runtime IP information
        from interfaces such as 'wlan0' or 'eth0'.

        ``Args``:
            - ``interface(str)``: The name of the network interface to query (e.g., 'wlan0')

        - ``Returns``:
            The IPv4 address assigned to the specified interface.

        ``Raises``:
            - ``ValueError``: If no ADB device is connected or if the interface name is missing.
            - ``RuntimeError``: If the ADB command fails to execute or returns an error.

        Example:
        | Create Connection | connection_type=usb | device_id=10000000cd0c07a6 |
        | ${ip} = | Get Interface IPv4   | interface=wlan0 |
        | Log | Device IP: ${ip} |
        """
        return self.adb.get_interface_ipv4(interface=interface)


    @keyword("Send Keyevent")
    def send_keyevent(self,
                      value: int = None):
        """
        Sends a keyevent input command to the connected Android device using ADB.

        ``Args:``
            - ``value(int):`` The keyevent code to send (e.g., 223 for sleep screen).
                              keyevent value supports from 0 to 224.

        ``Returns:``
            The standard output from the executed ADB shell command.

        ``Raises:``
            - RuntimeError: If the ADB shell command fails and returns an error.

        Example:
        | Send Keyevent | value=223 |
        """
        self.adb.send_keyevent(value=value)

    @keyword("Set Screen Size")
    def set_screen_size(self,
                        width: int,
                        height: int) -> None:
        """
        Sets the screen resolution (width x height) on an Android device using ADB.

        ``Args:``
            - ``width (int):`` The desired screen width in pixels.
            - ``height (int):`` The desired screen height in pixels.
        ``Raises:``
            - ``RuntimeError:`` If the command to set screen size fails
                                or if width/height is not provided.

        Example:
        | Set Screen Size | width=1920 | height=1080 |
        """
        self.adb.set_screen_size(width=width, height=height)

    @keyword("Get Device Log")
    def get_device_log(self,
                       log_name: str = None,
                       timeout: int = 10) -> str:
        """
        Captures log output from the connected Android device using `adb logcat`.

        This keyword is useful for debugging and monitoring runtime behavior. It reads logs
        for a specified duration and optionally saves them to a file on the host machine.

        ``Args``:
            - ``log_name(str)``: Filename to save the captured log output. If not provided,
                                 logs are returned but not saved.
            - ``timeout(int)``: Duration in seconds to capture logs. Default is 5 seconds.

        ``Returns``:
            The captured log output as a single string.

        ``Raises``:
            - ``ValueError``: If no ADB device is connected.
            - ``RuntimeError``: If log capture fails or the subprocess encounters an error.

        Example:
        | Create Connection | connection_type=usb | device_id=10000000cd0c07a6 |
        | ${log} | Get Device Log | log_name=device.log | timeout=10 |
        | Log | ${log} |
        """
        return self.get_device_log(log_name=log_name,
                                   timeout=timeout)
