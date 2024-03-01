#!/usr/bin/env python3

import serial
import time
import struct

# Configure serial port
ser = serial.Serial(
    port='/dev/ttyUSB0',  # Replace with the appropriate serial port
    baudrate=115200,
    bytesize=8,
    parity='N',
    stopbits=1,
    timeout=1
)

# Modbus function code (03H) to read holding registers
function_code = 0x03

# Slave device address
slave_address = 1  # Replace with the appropriate slave address

# Register address to read from
register_address = 0x02  # Replace with the appropriate register address

# Number of registers to read
num_registers = 0  # Replace with the appropriate number of registers

# Build the Modbus request frame
request_frame = bytearray([slave_address, function_code, 0x00, 0x00, 0x00, 0x02])

print("Request Frame:", request_frame.hex())

# Calculate CRC
crc = 0xFFFF
for byte in request_frame:
    crc ^= byte
    for _ in range(8):
        if crc & 0x0001:
            crc >>= 1
            crc ^= 0xA001
        else:
            crc >>= 1

# Add CRC to the request frame
request_frame += bytearray([crc & 0xFF, (crc >> 8) & 0xFF])

print(request_frame)

while(1):
    # Send the request
    #if val == b'$':
    # Read the response
    # 5 bytes for address, function code, byte count, and CRC, plus 2 bytes per register
    print(ser.read(6))


while(1):
    # Send the request
    #if val == b'$':
    # Read the response
    response = bytearray(ser.read(6))  # 5 bytes for address, function code, byte count, and CRC, plus 2 bytes per register
    temp = response
    print(temp)

    if response[2] & 0x80:
        sign_ = -1
        response[2] = response[2] & ~0x80
    else :
        sign_ = 1

    torque = (struct.unpack('>H',response[0:2]))
    bof = (struct.unpack('>H',response[4:6]))

    print(torque[0]*sign_, " ", bof[0])


# Close the serial port
ser.close()

