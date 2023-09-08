from serial_scanner.scanner import SerialPortScanner, SerialDeviceInfo

dev_info = SerialDeviceInfo(vid=0x0403,
                            pid=0x6014,
                            serial_number="1234")

sps = SerialPortScanner()
print(sps.find_ports(dev_info))
