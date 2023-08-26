import struct

from enum import Enum

class Header(Enum):
    START = b'\x5A'
    IDLE = b'\x01'
    OPEN = b'\x02'
    PRESSURE = b'\x11'
    PID = b'\x12'

class DecodeFormatType(Enum):
    PRESSURE = '>Hii'
    PID = '>H2h'
    IDLE = '>Hi'

# IDLE      : TIME(H) ANG_POS(i)
# PID       : TIME(H) SPEED(h)       VOLTAGE_CMD(h)
# PRESSURE  : TIME(H) TEMPERATURE(i) PRESSURE(i)

class DecodeFormatLength(Enum):
    PRESSURE = 10
    PID = 6
    IDLE = 6

class message_decoder:

    def __init__(self):
        self.state = None
        self.last_state = None
        self.data = b''
        self.message = None

    def decode(self,byte):

        if self.state == None:
            if byte == Header.START.value:
                self.state = Header.START
        elif self.state == Header.START:
            if byte == Header.PRESSURE.value:
                self.state = Header.PRESSURE
            elif byte == Header.PID.value:
                self.state = Header.PID
            elif byte == Header.IDLE.value:
                self.state = Header.IDLE
            else:
                self.state = None
        elif self.state == Header.PRESSURE:
            self.data += byte
            if len(self.data) == DecodeFormatLength.PRESSURE.value:
                self.message = struct.unpack(DecodeFormatType.PRESSURE.value, self.data)
                self.data = b''
                self.last_state = self.state
                self.state = None
                return True
        elif self.state == Header.PID:
            self.data += byte
            if len(self.data) == DecodeFormatLength.PID.value:
                self.message = struct.unpack(DecodeFormatType.PID.value, self.data)
                self.data = b''
                self.last_state = self.state
                self.state = None
                return True
        elif self.state == Header.IDLE:
            self.data += byte
            if len(self.data) == DecodeFormatLength.IDLE.value:
                self.message = struct.unpack(DecodeFormatType.IDLE.value, self.data)
                self.data = b''
                self.last_state = self.state
                self.state = None
                return True
        else:
            self.state = None
            self.data = b''
        return False

    def get_message(self):
        return [self.last_state, self.message]


if __name__ == '__main__':

    import serial

    ser_itf = serial.Serial(port='/dev/ttyUSB0',baudrate=460800,timeout=1)
    
    decoder = message_decoder()

    ser_itf.flush()
    byte = ser_itf.read(1)

    while(byte):
        if(decoder.decode(byte)):
            msg_type, msg_data = decoder.get_message()
            if msg_type == Header.PRESSURE:
                print("Pressure")
                print(msg_data)
            elif msg_type == Header.PID:
                print("PID")
                print(msg_data)
            elif msg_type == Header.IDLE:
                print("IDLE")
                print(msg_data)
        byte = ser_itf.read(1)


