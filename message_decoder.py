import struct

from enum import Enum

class Header(Enum):
    START = b'\x5A'
    PRESSURE = b'\x11'
    PID = b'\x12'

class DecodeFormatType(Enum):
    PRESSURE = '>ii'
    PID = 'hh'

class DecodeFormatLength(Enum):
    PRESSURE = 8
    PID = 4

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
            else:
                self.state = None

        elif self.state == Header.START:
            if byte == Header.PID.value:
                self.state = Header.PID
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
        else:
            self.state = None
            self.data = b''
        return False

    def get_message(self):
        return [self.last_state, self.message]


if __name__ == '__main__':

    import serial

    ser_itf = serial.Serial(port='/dev/ttyUSB0',baudrate=460800,timeout=1)
    header = b''
    byte = b''
    while(1):
        header = ser_itf.read(1)
        if header == b'\x5A':
            header = ser_itf.read(1)
            if header == b'\x11':
                print(ser_itf.read(9))
            header = b''
