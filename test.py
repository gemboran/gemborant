import time
import serial
import serial.tools.list_ports

port = next((port for port in serial.tools.list_ports.comports() if "SERIAL" in port.description), None)

serial = serial.Serial()
serial.baudrate = 115200
serial.timeout = 1
serial.port = port.device

serial.open()

for i in range(10):
    serial.write(b"M" + bytes([10,10]))
    time.sleep(0.2)

serial.close()
