"""AdbInterface is an abstract method in ADBLibrary for the Robot Framework."""

# standard library
from abc import ABC, abstractmethod

class AdbInterface(ABC):
    """ADBInterface is an abstract method in ADBLibrary for the Robot Framework."""
    @abstractmethod
    def create_connection(self,
                          connection_type="usb",
                          **kwargs):
        """
        Abstract method to connect device over wifi
        """
        raise NotImplementedError("Subclass must implement the create_connection()")

    @abstractmethod
    def get_connection(self):
        """
        Abstract method to get current connections.
        """
        raise NotImplementedError("Subclass must implement the get_connection()")

    @abstractmethod
    def execute_shell_command(self,
                              command: str,
                              return_stdout: bool,
                              return_rc: bool,
                              return_stderr: bool):
        """
        Abstract method to execute shell command
        """
        raise NotImplementedError("Subclass must implement the execute_shell_command()")

    @abstractmethod
    def execute_command(self,
                        command: str,
                        return_stdout: bool,
                        return_rc: bool,
                        return_stderr:bool):
        """
        Abstract method to execute command
        """
        raise NotImplementedError("Subclass must implement the execute_command()")

    @abstractmethod
    def disconnect_device(self):
        """
        Abstract method to disconnect sepecified device
        """
        raise NotImplementedError("Subclass must implement the disconnect_device()")

    @abstractmethod
    def get_hardware_name(self):
        """
        Abstract method to get hardware name
        """
        raise NotImplementedError("Subclass must implement the get_hardware_name()")

    @abstractmethod
    def switch_connection(self,
                          device_id: str):
        """
        Abstract method to switch connection
        """
        raise NotImplementedError("Subclass must implement the switch_connection()")

    @abstractmethod
    def send_file(self,
                  src_file: str,
                  dst_file: str):
        """
        Abstract method to close connection
        """
        raise NotImplementedError("Subclass must implement the send_file()")

    @abstractmethod
    def receive_file(self,
                     src_file: str,
                     dst_file: str):
        """
        Abstract method to close connection
        """
        raise NotImplementedError("Subclass must implement the receive_file()")

    @abstractmethod
    def reboot_device(self,
                      mode: str):
        """
        Abstract method to reboot device
        """
        raise NotImplementedError("Subclass must implement the reboot_device()")

    @abstractmethod
    def get_screen_size(self):
        """
        Abstract method to get screen size
        """
        raise NotImplementedError("Subclass must implement the get_screen_size()")

    @abstractmethod
    def get_android_version(self):
        """
        Abstract method to get android version
        """
        raise NotImplementedError("Subclass must implement the get_android_version()")

    @abstractmethod
    def start_adb_server(self,
                         port: int):
        """
        Abstract method to start adb server
        """
        raise NotImplementedError("Subclass must implement the start_adb_server()")

    @abstractmethod
    def kill_adb_server(self,
                        port: int):
        """
        Abstract method to kill adb server
        """
        raise NotImplementedError("Subclass must implement the kill_adb_server()")

    @abstractmethod
    def get_state(self):
        """
        Abstract method to get state
        """
        raise NotImplementedError("Subclass must implement the get_state()")

    @abstractmethod
    def get_serial_number(self):
        """
        Abstract method to get serial number
        """
        raise NotImplementedError("Subclass must implement the get_serial_number()")

    @abstractmethod
    def switch_to_usb_mode(self,
                           device_id: str):
        """
        Abstract method to switch to usb mode
        """
        raise NotImplementedError("Subclass must implement the switch_to_usb_mode()")

    @abstractmethod
    def close_connection(self):
        """
        Abstract method to close connection
        """
        raise NotImplementedError("Subclass must implement the close_connection()")

    @abstractmethod
    def close_all_connections(self):
        """
        Abstract method to close all connections
        """
        raise NotImplementedError("Subclass must implement the close_all_connections()")

    @abstractmethod
    def set_root_access(self):
        """
        Abstract method to set root access
        """
        raise NotImplementedError("Subclass must implement the set_root_access()")

    @abstractmethod
    def set_unroot_access(self):
        """
        Abstract method to set unroot access
        """
        raise NotImplementedError("Subclass must implement the set_unroot_access()")

    @abstractmethod
    def install_apk(self,
                    apk_file: str):
        """
        Abstract method to install apk
        """
        raise NotImplementedError("Subclass must implement the install_apk()")

    @abstractmethod
    def uninstall_apk(self,
                      apk_package: str):
        """
        Abstract method to uninstall apk
        """
        raise NotImplementedError("Subclass must implement the uninstall_apk()")

    @abstractmethod
    def get_build_product(self) -> str:
        """
        Abstract method to get build product
        """
        raise NotImplementedError("Subclass must implement the get_build_product()")

    @abstractmethod
    def enable_tcpip_mode(self,
                          port: int):
        """
        Abstract method to enable tcpip mode
        """
        raise NotImplementedError("Subclass must implement the enable_tcpip_mode()")

    @abstractmethod
    def get_interface_ipv4(self,
                           interface: str) -> str:
        """
        Abstract method to get interface ipv4
        """
        raise NotImplementedError("Subclass must implement the get_interface_ipv4()")

    @abstractmethod
    def get_installed_packages(self,
                               device_id: str) -> list:
        """
        Abstract method to get installed packages
        """
        raise NotImplementedError("Subclass must implement the get_installed_packages()")

    @abstractmethod
    def package_should_exist(self,
                             package_name: str):
        """
        Abstract method to package should exist
        """
        raise NotImplementedError("Subclass must implement the package_should_exist()")

    @abstractmethod
    def package_should_not_exist(self,
                                 package_name: str):
        """
        Abstract method to package should not exist
        """
        raise NotImplementedError("Subclass must implement the package_should_not_exist()")

    @abstractmethod
    def take_screenshot(self,
                        filename: str):
        """
        Abstract method to take screenshot
        """
        raise NotImplementedError("Subclass must implement the take_screenshot()")

    @abstractmethod
    def wake_up_screen(self):
        """
        Abstract method to wake up screen
        """
        raise NotImplementedError("Subclass must implement the wake_up_screen()")

    @abstractmethod
    def sleep_screen(self):
        """
        Abstract method to sleep screen
        """
        raise NotImplementedError("Subclass must implement the sleep_screen()")

    @abstractmethod
    def get_apk_path(self,
                     package_name: str):
        """
        Abstract method to get apk path
        """
        raise NotImplementedError("Subclass must implement the get_apk_path()")

    @abstractmethod
    def clear_app_data(self,
                       package_name: str):
        """
        Abstract method to clear app data
        """
        raise NotImplementedError("Subclass must implement the clear_app_data()")

    @abstractmethod
    def get_package_info(self,
                         package_name: str):
        """
        Abstract method to get package info
        """
        raise NotImplementedError("Subclass must implement the get_package_info()")

    @abstractmethod
    def send_keyevent(self,
                      value: int):
        """
        Abstract method to send input keyevent
        """
        raise NotImplementedError("Subclass must implement the send_keyevent()")

    @abstractmethod
    def set_screen_size(self,
                        width: int,
                        height: int):
        """
        Abstract method to set screen size
        """
        raise NotImplementedError("Subclass must implement the set_screen_size()")

    @abstractmethod
    def get_running_processes(self):
        """
        Abstract method to get running processes
        """
        raise NotImplementedError("Subclass must implement the get_running_processes()")

    @abstractmethod
    def get_all_services(self):
        """
        Abstract method to get all services
        """
        raise NotImplementedError("Subclass must implement the get_all_sercices()")

    @abstractmethod
    def open_default_browser(self):
        """
        Abstract method to open default browser
        """
        raise NotImplementedError("Subclass must implement the open_default_browser()")

    @abstractmethod
    def send_text(self,
                  text: str):
        """
        Abstract method to send input text
        """
        raise NotImplementedError("Subclass must implement the send_text()")

    @abstractmethod
    def get_device_log(self,
                       log_name: str,
                       timeout: int):
        """
        Abstract method to get device log
        """
        raise NotImplementedError("Subclass must implement the get_device_log()")
