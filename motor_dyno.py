#!/usr/bin/env python3

import serial
import struct
import argparse
import sys
import termios
import tty
import select
import matplotlib.pyplot as plt
import numpy as np 
import threading
import time

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Read UART data on Linux.')
parser.add_argument('uart_port_serial', help='UART Serial device path')
parser.add_argument('baud_rate_serial', type=int, help='UART Serial baud rate')
parser.add_argument('uart_port_modbus', help='UART ModBus device path')
parser.add_argument('baud_rate_modbus', type=int, help='UART ModBus baud rate')
args = parser.parse_args()

# Open the UART port
uart_serial = serial.Serial(args.uart_port_serial, args.baud_rate_serial,timeout = 0)
uart_modbus = serial.Serial(args.uart_port_modbus, args.baud_rate_modbus,timeout = 0)

# Set terminal settings for detecting key presses
old_settings = termios.tcgetattr(sys.stdin)
tty.setcbreak(sys.stdin.fileno())

# Data storage
received_data = []
data_lock = threading.Lock()
run_thread = True

# Function to read UART data
def read_uart_serial_data():

    print("Start read serial data")

    while True:
        # Wait for the header byte (0xAB)
        header = uart_serial.read(1)
        if header == b'\xAB':
            # Read the 3 half words (6 bytes)
            data = uart_serial.read(6)
            if len(data) == 6:
                # Unpack the half words using little-endian format
                half_words = struct.unpack('>3h', data)
                received_data.append(half_words)

        with data_lock:
            if run_thread == False:
                print("End read uart data")
                break

def read_uart_modbus_data():

    print("Start read modbus data")
    # Modbus function code (03H) to read holding registers
    function_code = 0x03

    # Slave device address
    slave_address = 1  # Replace with the appropriate slave address

    # Build the Modbus request frame
    request_frame = bytearray([slave_address, function_code, 0x00, 0x00, 0x00, 0x02])

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

    uart_modbus.flush()
    
    while True:
        # Send the request
        uart_modbus.write(request_frame)
        
        time.sleep(1)
        # Read the response
        response = uart_modbus.read(12)  # 5 bytes for address, function code, byte count, and CRC, plus 2 bytes per register
        uart_modbus.flush()

        print(response)

        with data_lock:
            if run_thread == False:
                print("End read modbus data")
                break


# Function to handle key presses
def handle_key_press():
    global run_thread
    while True:
        # Check if 'q' key is pressed
        if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
            key = sys.stdin.read(1)
            if key == 'q':
                print("q pressed")
                with data_lock:
                    run_thread = False
                    print(run_thread)
                break

# Start the UART data reading thread
uart_serial_thread = threading.Thread(target=read_uart_serial_data)
uart_modbus_thread = threading.Thread(target=read_uart_modbus_data)
key_thread = threading.Thread(target=handle_key_press)

key_thread.start()
uart_serial_thread.start()
uart_modbus_thread.start()

# Wait for the threads to finish
uart_serial_thread.join()
uart_modbus_thread.join()
key_thread.join()

# Close the UART port
uart_serial.close()
uart_modbus.close()

# Convert data to NumPy array
received_array = np.array(received_data)

# Prepare data for plotting
x = np.array(range(len(received_array)))/5000
y1 = received_array[:, 0]
y2 = received_array[:, 1]
y3 = received_array[:, 2]

# Create the plot
plt.plot(x, y1, label='Curve 1')
plt.plot(x, y2, label='Curve 2')
plt.plot(x, y3, label='Curve 3')
#plt.plot(x, (y1 + y2 + y3)/3, label='Curve 3')
plt.xlabel('Sample')
plt.ylabel('Value')
plt.title('Received Data')
plt.legend()
plt.grid(True)
# Display the plot
plt.show()


# Create the plot
fig, axs = plt.subplots(2, 1, figsize=(8, 8))

# Plot the curves
axs[0].plot(x, y1, label='Curve 1')
axs[0].plot(x, y2, label='Curve 2')
axs[0].plot(x, y3, label='Curve 3')
axs[0].set_xlabel('Sample')
axs[0].set_ylabel('Value')
axs[0].set_title('Received Data')
axs[0].legend()
axs[0].grid(True)

# Perform FFT on each signal
fs = 5000  # Sample rate
freqs = np.fft.fftfreq(len(received_array), 1/fs)
fft1 = np.abs(np.fft.fft(y1))
fft2 = np.abs(np.fft.fft(y2))
fft3 = np.abs(np.fft.fft(y3))

max_peak1 = np.max(fft1)
max_peak2 = np.max(fft2)
max_peak3 = np.max(fft3)

fft1 = fft1 / max_peak1
fft2 = fft2 / max_peak2
fft3 = fft3 / max_peak3

# Plot the FFTs
axs[1].plot(freqs, fft1, label='FFT 1')
axs[1].plot(freqs, fft2, label='FFT 2')
axs[1].plot(freqs, fft3, label='FFT 3')
axs[1].set_xlabel('Frequency (Hz)')
axs[1].set_ylabel('Amplitude')
axs[1].set_title('FFT of Received Data')
axs[1].legend()
axs[1].grid(True)
axs[1].set_xlim(0, 1000) 

# Adjust the spacing between subplots
plt.tight_layout()

# Display the plot
plt.show()