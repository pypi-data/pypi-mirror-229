from __future__ import annotations
import serial
from serial.tools import list_ports
import atexit


class SerialDeviceInfo:
    def __init__(self, vid=None, pid=None, serial_number=None):
        self.vid = vid
        self.pid = pid
        self.serial_number = serial_number

    def __eq__(self, other: SerialDeviceInfo):
        return self.vid == other.vid and \
            self.pid == other.pid and \
            self.serial_number == other.serial_number


class SerialPortScanner:
    def __init__(self):
        self.ports = {}  # Opened serial ports - {str(board ID): Serial object}
        self.port_names = {}  # Port names - {str(board ID): str(USB COM port names (eg COM3 or /dev/ttyACM2)}
        self.nPorts = 0  # Number of opened serial ports
        self._en_debug = True

    def enable_debug(self, en=True):
        self._en_debug = en

    # ---------------------- SERIAL ----------------------#

    def find_ports(self, target_device: SerialDeviceInfo = None):
        """
        Looks through available serial ports for a device with a particular
        VendorID and ProductID and unique ID
        Returns port string or None if not found.

        find_port(str) -> [str(port),str(SNR)] OR []
        """
        # Map devices to (VID, PID, SER) as strings
        self.port_names = {}

        if self._en_debug:
            print("Finding devices...")
        for port in list_ports.comports():  # Scan available COM ports
            # ignore devices without device info
            if (port.pid is None) or (port.vid is None):
                continue
            _id = port.serial_number
            # print(port, hex(port.vid), hex(port.pid), port.serial_number)
            if target_device is None:
                self.port_names[_id] = port.device  # Assign ID to port

            # Check VID and PID are consistent
            elif (port.vid == target_device.vid and  # VID
                  port.pid == target_device.pid):  # PID
                # FIXME - doesn't currently check for serial number

                # print('\t{:0>12x} on {}'.format(id,))
                if self._en_debug:
                    print('\t{} on {} [{}]'.format(_id, port.device, port.description))

                self.port_names[_id] = port.device  # Assign ID to port
                self.ports[_id] = None  # Assuming all ports are closed at this point.

        # if self._en_debug:
        #     print("{} device(s) found at: {}".format(len(self.port_names),
        #                                              list(self.port_names.values())))
        if len(self.port_names) == 0:
            return None
        return list(self.port_names.values())[0]  # NB only need one

    def port_is_present(self, port: str) -> bool:
        port_names = [dev.name for dev in list_ports.comports()]
        return port in port_names

    def open_serial_ports(self, baud=115200):
        print("Opening ports...")
        if len(self.port_names) == 0:
            print("No devices found!")
            raise SystemExit
        devices = self.ports.keys()
        for _id in devices:  # range(len(self.ports)): #Open serial ports
            try:
                self.ports[_id] = serial.Serial(self.port_names[_id], baud,
                                                timeout=2)  # self.ser_ports.append([ser,self.ports[i][1]])
                print("\t{}".format(self.port_names[_id]))

                atexit.register(self.close_serial_ports)  # Arrange to close ports on system exit
            except serial.serialutil.SerialException as e:
                print(e)
                raise SystemExit

        self.nPorts = len(self.ports)  # Set number of open boards

    def close_serial_ports(self):
        print("Closing serial ports...")
        # for id, port in self.ports.items():
        for port in self.ports.values():
            print("\t{}".format(port.port))
            port.close()
        self.ports = {}

        print("Done!")
