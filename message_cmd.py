from enum import Enum
import struct

class CmdId(Enum):
    HEADER = 0xAB
    JUNK = 0x00
    IDLE = 0x00
    OPEN_LOOP = 0x01
    OFFSET_TUNE = 0x04
    RESET = 0x05
    PID_SET_PTS = 0x06
    PID_P = 0x07
    PID_I = 0x08
    PID_D = 0x09
    PID_FF = 0x0A

class CmdFormatType(Enum):
    HEADER_STATE = '>2B'
    JUNK = '>I'
    OPEN_LOOP = '>b'
    PID_SET_PTS = '>f'
    PID_P = '>f'
    PID_I = '>f'
    PID_D = '>f'
    PID_FF = '>f'

# Here is a list of the commands that can be sent with the arguments and the type of the argument
# IDLE : 
# OPEN_LOOP : VOLTAGE_AMP(int8)
# OFFSET_TUNE : 
# RESET :
# PID_SET_PTS : SET_PTS(float32)
# PID_P : P(float32)
# PID_I : I(float32)
# PID_D : D(float32)
# PID_FF : FF(float32)
 
# On a unspecified command the state will go to IDLE

class message_cmd:
    
    def __init__(self,ser_itf):
        self.ser_itf = ser_itf

    def idle(self):
        self.send_no_param(CmdId.IDLE.value)

    def reset(self):
        self.send_no_param(CmdId.RESET.value)

    def offset_tune(self):
        self.send_no_param(CmdId.OFFSET_TUNE.value)

    def open_loop(self,p_value):
        self.send_param(p_value, CmdId.OPEN_LOOP.value, CmdFormatType.OPEN_LOOP.value)

    def pid_setpoint(self,setpoint):
        self.send_param(setpoint, CmdId.PID_SET_PTS.value, CmdFormatType.PID_SET_PTS.value)

    def pid_p(self,p_value):
        self.send_param(p_value, CmdId.PID_P.value, CmdFormatType.PID_P.value)

    def pid_i(self,i_value):
        self.send_param(i_value, CmdId.PID_I.value, CmdFormatType.PID_I.value)

    def pid_d(self,d_value):
        self.send_param(d_value, CmdId.PID_D.value, CmdFormatType.PID_D.value)

    def pid_ff(self,ff_value):
        self.send_param(ff_value, CmdId.PID_FF.value, CmdFormatType.PID_FF.value)

    def send_param(self,param,cmd_id,format_type):
        data1 = struct.pack(CmdFormatType.HEADER_STATE.value, CmdId.HEADER.value, cmd_id)
        data2 = struct.pack(format_type, param)
        while (len(data1) + len(data2) != 6):
            data2 = data2 + struct.pack('>b',0)
        self.ser_itf.write(data1+data2)

    def send_no_param(self,cmd_id):
        self.send_param(CmdId.JUNK.value,cmd_id,CmdFormatType.JUNK.value)


def test_decode(ser_itf,decoder):
    byte = ser_itf.read(1)
    a = datetime.datetime.now()
    b = datetime.datetime.now()
    c = b - a
    while(c.seconds < 2):
        b = datetime.datetime.now()
        c = b - a
        if(decoder.decode(byte)):
            msg_type, msg_data = decoder.get_message()
            if msg_type == Header.PRESSURE:
                print(f"Pressure {msg_data[1]} {msg_data[2]/100}")
            elif msg_type == Header.PID:
                print("PID")
                print(msg_data)
            elif msg_type == Header.IDLE:
                print("IDLE")
                print(msg_data)
            elif msg_type == Header.OPEN:
                print("OPEN_LOOP")
                print(msg_data)
        byte = ser_itf.read(1)


if __name__ == '__main__':

    import serial, time, datetime
    from message_decoder import * 

    ser_itf = serial.Serial(port='/dev/ttyUSB0',baudrate=460800,timeout=1)

    cmd = message_cmd(ser_itf)

    decoder = message_decoder()

    ser_itf.flush()

    #cmd.idle()
    #test_decode(ser_itf,decoder)

    #cmd.offset_tune()
    #test_decode(ser_itf,decoder)
    cmd.open_loop(4)
    
    time.sleep(1)

    cmd.open_loop(7)
    test_decode(ser_itf,decoder)

    ser_itf.close()