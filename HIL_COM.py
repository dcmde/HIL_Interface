# HIL_COM.py

import serial
import time
import numpy as np
from message_decoder import *

PRBS_POLYNOMIALS = {
    "L15": {"polynomial": 0b11001, "length": 15},
    "L31": {"polynomial": 0b101001, "length": 31},
    "L63": {"polynomial": 0b1100001, "length": 63},
    "L127": {"polynomial": 0b11000001, "length": 63},
    "L511": {"polynomial": 0b1000100001, "length": 511}
}

def prbs_one_shot(ser,amplitude,delay):
    with open('output.txt','w') as f:
        identification_sequence(ser,f,amplitude,delay)

def prbs_sequence(ser,amplitude,delay):
    with open('output.txt','w') as f:
        f.write("mcu_time;theta;u;cmd;current1;current2;current3\n")
        for amp in amplitude:
            identification_sequence(ser,f,amp,delay)

def identification_sequence(ser,file,amplitude=10,delay=100):
    start_time = time.time()

    header = b''
    data = b''
    state = 0

    ser.flush()
    print("Start receiving and sending data")

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
                if len(data) == 14:
                    mcu_time, theta, u, cur1, cur2, cur3 = struct.unpack('>Hihhhh', data)
                    file.write(f"{mcu_time};{theta};{u};{int(amplitude)};{int(cur1)};{int(cur2)};{int(cur3)}\n")
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
    data = struct.pack('Bbhbb', 0xAB, STATE, FREQ, AMP, 0)
    # open the serial port
    ser = serial.Serial('/dev/ttyUSB2', 230400)
    # send the data
    ser.write(data)
    # close the serial port
    ser.close()

def send_data_1(ser, STATE, FREQ, AMP):
    # pack the data into a byte string
    data = struct.pack('Bbhbb', 0xAB, STATE, FREQ, AMP, 0)
    # send the data
    ser.write(data)

def set_pid_val(ser,STATE,val):
    data1 = struct.pack('Bb', 0xAB, STATE)
    data2 = struct.pack('f', val)
    ser.write(data1+data2)

def set_pid_p(ser,val):
    set_pid_val(ser,7,val);

def set_pid_i(ser,val):
    set_pid_val(ser,8,val);

def set_pid_d(ser,val):
    set_pid_val(ser,9,val);

def set_pid_ff(ser,val):
    set_pid_val(ser,0x0A,val);

def set_pid(ser,val):
    set_pid_val(ser,6,val);

def reset(ser):
    send_data_1(ser, 0x05, 0, 0)

def pid_interface(ser,file,ref_speed,pid_p,pid_ff):
    start_time = time.time()

    header = b''
    data = b''
    state = 0

    ser.flush()
    print("Start receiving and sending data")

    step_time = 0
    amplitude = 0

    set_pid_p(ser,pid_p)
    set_pid_ff(ser,pid_ff)
    set_pid(ser,ref_speed)

    end_time = time.perf_counter()*1000 + 1000

    ser.flush()

    while time.perf_counter()*1000 < end_time:
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
                if len(data) == 4:
                    omega, u = struct.unpack('hh', data)
                    file.write(f"{omega};{u}\n")
                    header = b''
                    data = b''
                    state = 0
            else:
                state = 0
                header = b''
                data = b''

    print("Finished receiving and sending data")


def pid_sequence(ser,ref_speed,pid_p,pid_ff):
    with open('output_pid.txt','w') as file:
        file.write("omega;theta;u\n")
        pid_interface(ser,file,ref_speed,pid_p,pid_ff)
