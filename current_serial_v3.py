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
import datetime
import csv

def compute_crc(data):
    crc = 0x00  # Initial CRC value

    for byte in data:
        crc ^= byte  # XOR the current data byte with the CRC value
    return crc  # The final CRC value

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Read UART data on Linux.')
parser.add_argument('uart_port', help='UART device path')
parser.add_argument('baud_rate', type=int, help='UART baud rate')
parser.add_argument('--fft', type=bool, nargs='?', help='FFT Display')
parser.add_argument('--save', type=bool, nargs='?', help='Save to file')
args = parser.parse_args()

# Open the UART port
uart = serial.Serial(args.uart_port, args.baud_rate)

# Set terminal settings for detecting key presses
old_settings = termios.tcgetattr(sys.stdin)
tty.setcbreak(sys.stdin.fileno())

# Data storage
received_data = []

try:
    # Read data continuously
    while True:
        # Wait for the header byte (0xAB)
        header = uart.read(1)
        if header == b'\xAB':
            data = uart.read(9)
            if len(data) == 9:
                crc = compute_crc(b'\xAB' + data[0:8])
            
                # Unpack the half words using little-endian format
                half_words = list(struct.unpack('>4hB', data))
                check = 1
                if(crc != data[8]):
                    print("CRC Failed : ", crc , " ", data[8])
                    check = 0
                half_words.append(check)
                print("Received data:", half_words)
                received_data.append(half_words)
        
        # Check if 'q' key is pressed
        if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
            key = sys.stdin.read(1)
            if key == 'q':
                break

finally:
    # Restore terminal settings
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

# Close the UART port
uart.close()

# Convert data to NumPy array
received_array = np.array(received_data)

# Prepare data for plotting
x = np.array(range(len(received_array)))/5000
y1 = received_array[:, 0]
y2 = received_array[:, 1]
y3 = received_array[:, 2]
y4 = received_array[:, 3]
check = received_array[:, 5]

# Create the plot
fig, axs = plt.subplots(5, 1, figsize=(8, 8), sharex=True)
# Plot the curves
axs[0].plot(y1, label='Curve 1')
axs[0].grid(True)
axs[1].plot(y2, label='Curve 2')
axs[1].grid(True)
axs[2].plot(y3, label='Curve 3')
axs[2].grid(True)
axs[3].plot(y4, label='Curve 3')
axs[3].grid(True)
# Plot the check
axs[4].plot(check)
axs[4].grid(True)

# Adjust the spacing between subplots
plt.tight_layout()

# Display the plot
plt.show()

print(args.fft)
print(args.save)

if args.fft is not None:
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

if args.save is not None:
    current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_name = f"file_{current_time}.txt"  # Adjust the file extension as needed
    headers = ['data1', 'data2', 'data3', 'crc', 'crc_valid']
    # Perform your file-saving operations
    with open(file_name, "w") as file:
        writer = csv.writer(file)
        writer.writerows(received_array)

    print(f"File '{file_name}' has been saved.")