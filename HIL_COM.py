# HIL_COM.py

import threading
import struct
import serial
import time
import numpy as np

PRBS_POLYNOMIALS = {
    "L15": {"polynomial": 0b11001, "length": 15},
    "L31": {"polynomial": 0b101001, "length": 31},
    "L63": {"polynomial": 0b1100001, "length": 63},
    "L127": {"polynomial": 0b11000001, "length": 63},
    "L511": {"polynomial": 0b1000100001, "length": 511}
}

def read_write_serial(ser,amplitude=10,delay=100):
    start_time = time.time()

    header = b''
    data = b''
    state = 0

    ser.flush()
    print("Start receiving and sending data")

    with open('output.txt','w') as f:
        f.write("mcu_time;theta;u;cmd\n")

        prbs = (np.array(generate_prbs("L31")) - 0.5) * amplitude * 2
        end_time = 0

        end_time = time.perf_counter()*1000 + delay*31
        step_time = 0
        amplitude = 0

        while time.perf_counter()*1000 < end_time:

            # Non-blocking delay
            if time.perf_counter()*1000-step_time > delay:
                amplitude = prbs[0]
                prbs = np.delete(prbs,0)
                step_time = time.perf_counter()*1000
                send_data_1(ser, 1, 0, int(amplitude))

            byte = ser.read(1)
            if byte:
                if state == 0:
                    header += byte
                    if header == b'\x5A':
                        state = 1
                    else:
                        header = b''
                elif state == 1:
                    header += byte
                    if header == b'\x5A\xA5':
                        state = 2
                    else:
                        state = 0
                        header = b''
                elif state == 2:
                    data += byte
                    if len(data) == 8:
                        mcu_time, theta, u = struct.unpack('>HIh', data)  
                        f.write(f"{mcu_time};{theta};{u};{int(amplitude)}\n")
                        data = b''
                        state = 0
                else:
                    state = 0
                    header = b''
                    data = b''

        # Send a final value of 0 to signal the end of the PRBS sequence
        send_data_1(ser, 1, 0, 0)

    print("Finished receiving and sending data")

def prbs_test(ser,amplitude,delay):
    ser = ser
    def read_serial():
        start_time = time.time()
        header = b''
        data = b''
        state = 0
        print("Start receiving data")
        with open('output.txt','w') as f:
            f.write("mcu_time;theta;cmd\n")
            while time.time() - start_time < 10:
                byte = ser.read(1)
                if byte:
                    if state == 0:
                        header += byte
                        if header == b'\x5A':
                            state = 1
                        else:
                            header = b''
                    elif state == 1:
                        header += byte
                        if header == b'\x5A\xA5':
                            state = 2
                        else:
                            state = 0
                            header =b''
                    elif state == 2:
                        data += byte
                        if len(data) == 6:
                            mcu_time, theta = struct.unpack('>HI', data)  
                            f.write(f"{mcu_time};{theta};{cmd}\n")
                            data = b''
                            state = 0
                    else:
                        state = 0
                        header = b''
                        data = b''
        print("Finished receiving data")

    def write_serial():
        print("Start sending PRBS")
        send_prbs_1(ser,"L31",amplitude,delay)
        print("Finished sending PRBS")

    read_thread = threading.Thread(target=read_serial)
    read_thread.daemon = True
    read_thread.start()

    write_thread = threading.Thread(target=write_serial)
    write_thread.daemon = True
    write_thread.start()

    while True:
        if input("Press q to quit: ") == "q":
            break

    #stop threads
    read_thread.join()
    write_thread.join()

def send_prbs_1(ser, generator, amplitude=10, delay=0.1):
    prbs = (np.array(generate_prbs(generator))-0.5)*amplitude*2
    for amplitude in prbs:
        send_data_1(ser,1,0,int(amplitude))
        time.sleep(delay)
    send_data_1(ser,1,0,0)

def send_prbs(generator, amplitude=10, delay=0.3):
    prbs = (np.array(generate_prbs(generator))-0.5)*amplitude*2
    for amplitude in prbs:
        send_data(1,0,int(amplitude))
        time.sleep(delay)
    send_data(1,0,0)

def generate_prbs(length_str):
    # look up the polynomial and length for the specified PRBS length
    polynomial = PRBS_POLYNOMIALS[length_str]["polynomial"]
    length = PRBS_POLYNOMIALS[length_str]["length"]
    # determine the number of bits in the LFSR
    n = polynomial.bit_length() - 1
    # initialize the shift register with all ones
    sr = [1] * n
    # initialize the output list with zeros
    prbs = [0] * length
    # iterate over the shift register
    for i in range(length):
        # calculate the next output bit
        prbs[i] = sr[0]
        # calculate the feedback bit using the polynomial
        fb = sum([sr[j] for j in range(n) if polynomial & (1 << j)]) % 2
        # shift the register and insert the feedback bit at the end
        sr = sr[1:] + [fb]
    return prbs

def send_data(STATE, FREQ, AMP):
    # pack the data into a byte string
    data = struct.pack('Bbhb', 0xAB, STATE, FREQ, AMP)
    # open the serial port
    ser = serial.Serial('/dev/ttyUSB2', 230400)
    # send the data
    ser.write(data)
    # close the serial port
    ser.close()

def send_data_1(ser, STATE, FREQ, AMP):
    # pack the data into a byte string
    data = struct.pack('Bbhb', 0xAB, STATE, FREQ, AMP)
    # send the data
    ser.write(data)
