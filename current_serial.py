#!/usr/bin/env python3

import serial
import struct
import argparse

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Read UART data on Linux.')
parser.add_argument('uart_port', help='UART device path')
parser.add_argument('baud_rate', type=int, help='UART baud rate')
args = parser.parse_args()

# Open the UART port
uart = serial.Serial(args.uart_port, args.baud_rate)

# Read data continuously
while True:
    # Wait for the header byte (0xAB)
    header = uart.read(1)
    if header == b'\xAB':
        # Read the 3 half words (6 bytes)
        data = uart.read(6)
        if len(data) == 6:
            # Unpack the half words using little-endian format
            half_words = struct.unpack('>3h', data)
            
            print("Received data:", half_words)

# Close the UART port
uart.close()