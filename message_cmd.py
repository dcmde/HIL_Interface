from enum import Enum

class CmdId(Enum):
    HEADER = 0xAB
    IDLE = 0x00
    OPEN_LOOP = 0x01
    OFFSET_TUNE = 0x04
    RESET = 0x05
    PID_SET_PTS = 0x06
    PID_P = 0x07
    PID_I = 0x08
    PID_D = 0x09
    PID_FF = 0x0A

# IDLE : 
# OPEN_LOOP : VOLTAGE_AMP(int8)
# OFFSET_TUNE : 
# RESET :
# PID_SET_PTS : SET_PTS(float32)
# PID_P : P(float32)
# PID_I : I(float32)
# PID_D : D(float32)
# PID_FF : FF(float32)
 
# On error IDLE