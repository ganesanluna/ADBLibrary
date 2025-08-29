"""
adb_proxy.py
------------
Implements the Proxy Design Pattern for managing multiple ADB device connections.
This class acts as a proxy/facade on top of `AdbConnection`.

Responsibilities:
- Manage multiple ADB device connections (USB & Network)
- Route commands to the correct ADB client
- Provide a single access point (proxy) for higher-level libraries (Robot Framework)
"""

# standard libraries
import threading
import logging
import time
import subprocess

# Local Libraries
from .adb_connection import AdbConnection

# Ensure logs
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s.%(funcName)s: %(message)s")

class AdbProxy:
    _cache = {}
    _lock = threading.Lock()
    _thread_local = threading.local()

    def __init__(self, device_id=None):
        self.device_id = device_id
        if device_id:
            self._real = self._get_or_create(device_id)
        else:
            self._real = None

    def _get_or_create(self, device_id):
        with self._lock:
            if device_id in self._cache:
                conn = self._cache[device_id]
                logger.debug("Using cached connection for %s", device_id)
            else:
                conn = AdbConnection()
                conn.create_connection(connection_type="usb", device_id=device_id)
                self._cache[device_id] = conn
                logger.debug("Created new connection for %s", device_id)
        self._thread_local.conn = conn
        return conn

    def create_connection(self, connection_type="usb", **kwargs):
        """
        Create a new ADB connection (USB or network).
        """
        if connection_type == "usb":
            device_id = kwargs.get("device_id")
            if not device_id:
                raise ValueError("Missing 'device_id' for USB connection")

            conn = AdbConnection()
            conn.create_connection(connection_type="usb", device_id=device_id)

            with self._lock:
                self._cache[device_id] = conn

            self.device_id = device_id
            self._thread_local.conn = conn
            self._real = conn

        elif connection_type == "network":
            device_ip = kwargs.get("device_ip")
            port = kwargs.get("port", 5555)
            if not device_ip:
                raise ValueError("Missing 'device_ip' for network connection")

            device_id = f"{device_ip}:{port}"
            conn = AdbConnection()
            conn.create_connection(connection_type="network", device_ip=device_ip, port=port, device_id=device_id)

            with self._lock:
                self._cache[device_id] = conn

            self.device_id = device_id
            self._thread_local.conn = conn
            self._real = conn

        else:
            raise ValueError(f"Unsupported connection type: {connection_type}")

    def get_connection(self):
        """
        Returns the current active ADB connection instance.
        """
        if not hasattr(self._thread_local, "conn") or not self._thread_local.conn:
            raise RuntimeError("No active ADB connection. Use create_connection or switch_connection first.")
        return self._thread_local.conn

    def switch_connection(self, device_id):
        """
        Switch to another already connected device, or create a new one if not in cache.
        """
        logger.info("Switching to device: %s", device_id)
        conn = self._cache.get(device_id)

        if not conn:
            conn = AdbConnection()
            self._cache[device_id] = conn

        try:
            conn.switch_connection(device_id)
        except RuntimeError:
            logger.warning(f"Device {device_id} not reachable. Attempting USB recovery...")
            subprocess.call("adb usb", shell=True)
            time.sleep(2)
            try:
                conn.switch_connection(device_id)
            except RuntimeError:
                raise RuntimeError(f"Failed to recover USB device: {device_id}")

        self.device_id = device_id
        self._thread_local.conn = conn
        self._real = conn

    def disconnect(self):
        """
        Disconnect only the current device.
        """
        if self.device_id in self._cache:
            self._cache[self.device_id].disconnect_device()
            logger.info("Disconnected device: %s", self.device_id)
            self._thread_local.conn = None
            self._real = None

    def __getattr__(self, name):
        """
        Forward attribute/method calls to the active AdbConnection.
        """
        if not hasattr(self._thread_local, "conn") or not self._thread_local.conn:
            raise RuntimeError("No active ADB connection. Use create_connection or switch_connection first.")
        return getattr(self._thread_local.conn, name)

    def close_connection(self):
        """
        Closes the current active ADB connection.
        """
        if hasattr(self._thread_local, "conn") and self._thread_local.conn:
            try:
                self._thread_local.conn.disconnect_device()
                logger.info("Closed current connection: %s", self.device_id)
            except Exception as e:
                logger.warning(f"Failed to close current connection: {e}")
            finally:
                self._thread_local.conn = None
                self._real = None
                self.device_id = None

    def close_all_connections(self):
        """
        Clears all cached ADB connections and resets internal state.
        """
        with self._lock:
            for dev, conn in self._cache.items():
                try:
                    conn.disconnect_device()
                except Exception as e:
                    logger.warning(f"Failed to disconnect {dev}: {e}")
            self._cache.clear()
            self._thread_local.conn = None
            self._real = None
            self.device_id = None
            logger.info("Cleared all ADB connections.")

    def start_adb_server(self, port: int = 5037):
        """
        Start the ADB server without requiring an active device connection.
        """
        conn = AdbConnection()
        conn.start_adb_server(port=port)
        logger.info("ADB server started on port %s", port)
        return True

    def kill_adb_server(self, port: int = 5037):
        """
        Kill the ADB server without requiring an active device connection.
        """
        conn = AdbConnection()
        conn.kill_adb_server(port=port)
        logger.info("ADB server killed on port %s", port)
        return True


if __name__ == "__main__":
    adb = AdbProxy()

    adb.start_adb_server(port=5222)
    adb.create_connection(connection_type="usb", device_id="10000000cd0c07a6")
    print(f"Current conn (USB): {adb.device_id}")
    print("Screen size:", adb.get_screen_size())
    adb.enable_tcpip_mode()
    adb.create_connection(connection_type="network", device_ip="192.168.1.103")
    print(f"Current conn (Network): {adb.device_id}")
    adb.switch_connection("10000000cd0c07a6")
    print(f"Switched back to: {adb.device_id}")
