import sys
import time
from enum import Enum

import numpy as np
import serial
from tqdm import tqdm

SLEEP = 0.4  # sleep 0.4sec for each read/write


class MARS_FRS(Enum):
    _10 = "010%"  # frame rate = 10%
    _25 = "025%"  # frame rate = 25%
    _50 = "050%"  # frame rate = 50%
    _100 = "100%"  # frame rate = 100%


class MARS_FMS(Enum):
    SKIP = "SKIP"  # frame reduce mode = skip
    AVGE = "AVGE"  # frame reduce mode = average


class MARS_SMS(Enum):
    OPEN = "OPEN"  # Shutter open
    CLOS = "CLOS"  # Shutter close


class MARS_VZF(Enum):
    X1 = "1X"  # Video zoom factor = 1x
    X2 = "2X"  # Video zoom factor = 2x
    X4 = "4X"  # Video zoom factor = 4x
    X8 = "8X"  # Video zoom factor = 8x


class MARS_SFD(Enum):
    NONE = "NONE"  # Sensor flip direction = none
    HORI = "HORI"  # Sensor flip direction = horizontal flip
    VERT = "VERT"  # Sensor flip direction = vertical flip


class MARS_TUS(Enum):
    KELV = "KELV"  # HUD temperature unit = Kelvin
    CELS = "CELS"  # HUD temperature unit = Celsius
    FAHR = "FAHR"  # HUD temperature unit = Fahrenheit


class MARS_PLS(Enum):
    WH = "WH"  # Palette selection = white hot
    BH = "BH"  # Palette selection = black hot
    RB = "RB"  # Palette selection = rainbow
    RH = "RH"  # Palette selection = rainHC
    IB = "IB"  # Palette selection = ironbow
    LV = "LV"  # Palette selection = lave
    AT = "AT"  # Palette selection = arctic
    GB = "GB"  # Palette selection = glowbow
    GF = "GF"  # Palette selection = graded fire
    HT = "HT"  # Palette selection = hottest


class MARS_VOM(Enum):
    TV1 = "TV1"  #  TV NTSC mode (BT.656 via COMS)
    PCO = "PCO"  #  PC-OSD mode (UVC-H.264)
    PCR = "PCR"  #  PC-RAW mode (UVC-RGB)
    SCO = "SCO"  #  SOC-OSD mode (BT.656 via CMOS)
    SCR = "SCR"  #  SOC-RAW mode (RGB via CMOS)
    DUA = "DUA"  #  SOC-DUAL-A mode (BT.656 via CMOS, UVC-RGB)
    DUB = "DUB"  #  SOC-DUAL-B mode (RGB via CMOS, UVC-H.264)
    DUC = "DUC"  #  SOC-DUAL-C mode (BT.656 via CMOS, UVC-H.264)
    DUD = "DUD"  #  SOC-DUAL-D mode (RGB via CMOS, UVC-RGB)
    NVO = "NVO"  #  NVR-OSD
    NVR = "NVR"  #  NVR-RAW
    TV2 = "TV2"  #  TV PAL mode (BT.656 via COMS)
    MPR = "MPR"  #  MIPI mode (RGB via CMOS to MIPI board)
    PCY = "PCY"  #  PC-OSD mode (UVC-YUV)


class MARS_OTS(Enum):
    NORM = "NORM"  # Over Temperature Status = normal
    OVER = "OVER"  # Over Temperature Status = Over Temperature


class MARS_LPS(Enum):
    NORM = "NORM"  # Low Power Status = normal
    LOWP = "LOWP"  # Low Power Status = Low power


class MARS_CMD(Enum):
    N = "N"  # CMD = N
    Y = "Y"  # CMD = Y


class MARS_ALT(Enum):
    ONE = 0  # AGC linear type = one linear
    MULTI = 1  # AGC linear type = multiple linear


class MARS_GMS(Enum):
    X1 = "1"  # gain mode = 1
    X2 = "2"  # gain mode = 2
    X3 = "3"  # gain mode = 3
    X4 = "4"  # gain mode = 4
    X5 = "5"  # gain mode = 5


class MARS_CCI(Enum):
    _1 = "1"  # continue caputre interval 1 sec
    _2 = "2"  # continue caputre interval 2 sec
    _3 = "3"  # continue caputre interval 3 sec


class MARS_ABW(Enum):
    _5 = "5"  # Adaptive AGC block width number = 5
    _8 = "8"  # Adaptive AGC block width number = 8
    _10 = "10"  # Adaptive AGC block width number = 10


class MARS_ABH(Enum):
    _4 = "4"  # Adaptive AGC block height number = 4
    _6 = "6"  # Adaptive AGC block height number = 6
    _8 = "8"  # Adaptive AGC block height number = 8


class MARS_ENB(Enum):
    _14 = "14"  # Effective Number of Bits = 14
    _13 = "13"  # Effective Number of Bits = 13
    _12 = "12"  # Effective Number of Bits = 12
    _11 = "11"  # Effective Number of Bits = 11
    _10 = "10"  # Effective Number of Bits = 10


###########################################


def wait_ack(serial, wait_sec, ack_value="OK?"):
    retry_times = int(wait_sec / serial.timeout) + 1
    for _ in range(retry_times):
        ack = serial.read(len(ack_value)).decode("ascii")
        if ack == ack_value:
            return
    raise ValueError("ack != OK?")


###########################################


class CMD:
    def __init__(self, serial: serial):
        self.cmd = __class__.__name__
        self.dtype = np.str_
        self.byteSize = 4
        self.endian = "big"
        self.value = None
        self.serial = serial
        self.enum = None

    def decode_ascii(self, data):
        return data.decode("ascii")

    def decode_number(self, data, dtype=None, endian=None):
        if dtype is None:
            dtype = self.dtype
        if endian is None:
            endian = self.endian

        value = np.frombuffer(data, dtype)
        if sys.byteorder != endian:
            return value.copy().byteswap(inplace=True)
        else:
            return value

    def value_to_enum(self, value, enum):
        for i in enum:
            if value == self.dtype(i.value):
                return i
        return None

    def read(self):
        write_cmd = f"{self.cmd}=?".encode("ascii")
        self.serial.write(write_cmd)
        read_data = self.serial.read(self.byteSize)
        #
        if len(read_data) < self.byteSize:
            return None
        #
        if self.dtype == np.str_:
            self.value = self.decode_ascii(read_data)
        else:
            self.value = self.decode_number(read_data)
        time.sleep(SLEEP)
        # output
        if self.enum is None:
            return self.value
        else:
            return self.value_to_enum(self.value, self.enum)

    def write(self, inputs):
        if self.dtype == np.str_:
            write_data = inputs.encode("ascii")
        else:
            self.value = np.array(inputs).astype(self.dtype)
            if sys.byteorder != self.endian:
                self.value = self.value.byteswap(inplace=True)
            write_data = self.value.tobytes()
        write_head = f"{self.cmd}=".encode("ascii")
        write_tail = "?".encode("ascii")
        write_cmd = write_head + write_data + write_tail
        self.serial.write(write_cmd)
        time.sleep(SLEEP)


class CMD_YN(CMD):
    def __init__(self, serial: serial):
        super().__init__(serial)
        self.dtype = np.str_
        self.byteSize = 1
        self.enum = MARS_CMD

    def write_Y(self):
        self.write(self.enum.Y.value)

    def write_N(self):
        self.write(self.enum.N.value)


class FRS(CMD):
    """
    Write/Read frame rate

    Attributes
    ----------
    serial : serial port object

    Methods
    -------
    read()
        read value
        MARS_FRS._10 = 10%
        MARS_FRS._25 = 25%
        MARS_FRS._50 = 50%
        MARS_FRS._100 = 100%
    write_10()
        write 10%
    write_25()
        write 25%
    write_50()
        write 50%
    write_10()
        write 100%
    """

    def __init__(self, serial: serial):
        super().__init__(serial)
        self.cmd = __class__.__name__
        self.dtype = np.str_
        self.byteSize = 4
        self.enum = MARS_FRS

    def write_10(self):
        self.write(self.enum._10.value)

    def write_25(self):
        self.write(self.enum._25.value)

    def write_50(self):
        self.write(self.enum._50.value)

    def write_100(self):
        self.write(self.enum._100.value)


class FMS(CMD):
    """
    Write/Read frame reduce mode

    Attributes
    ----------
    serial : serial port object

    Methods
    -------
    read()
        read value
        MARS_FMS.SKIP = skip mode
        MARS_FMS.AVGE = average mode
    write_SKIP()
        write skip mode
    write_AVGE()
        write average mode
    """

    def __init__(self, serial: serial):
        super().__init__(serial)
        self.cmd = __class__.__name__
        self.dtype = np.str_
        self.byteSize = 4
        self.enum = MARS_FMS

    def write_SKIP(self):
        self.write(self.enum.SKIP.value)

    def write_AVGE(self):
        self.write(self.enum.AVGE.value)


class GMS(CMD):
    """
    Write/Read gain mode

    Attributes
    ----------
    serial : serial port object

    Methods
    -------
    read()
        read value
        MARS_GMS._1 = gain mode 1
        MARS_GMS._2 = gain mode 2
        MARS_GMS._3 = gain mode 3
        MARS_GMS._4 = gain mode 4
        MARS_GMS._5 = gain mode 5
    write_1()
        write gain mode 1
    write_2()
        write gain mode 2
    write_3()
        write gain mode 3
    write_4()
        write gain mode 4
    write_5()
        write gain mode 5
    """

    def __init__(self, serial: serial):
        super().__init__(serial)
        self.cmd = __class__.__name__
        self.dtype = np.str_
        self.byteSize = 1
        self.enum = MARS_GMS

    def write_1(self):
        self.write(self.enum._1.value)

    def write_2(self):
        self.write(self.enum._2.value)

    def write_3(self):
        self.write(self.enum._3.value)

    def write_4(self):
        self.write(self.enum._4.value)

    def write_5(self):
        self.write(self.enum._5.value)


class GML(CMD):
    """
    Write/Read gain mode limited Vtemp

    Attributes
    ----------
    serial : serial port object

    Methods
    -------
    read()
        read value
    write()
        write value
    """

    def __init__(self, serial: serial):
        super().__init__(serial)
        self.cmd = __class__.__name__
        self.dtype = np.int16
        self.byteSize = 2


class GMA(CMD_YN):
    """
    Set gain mode auto

    Attributes
    ----------
    serial : serial port object

    Methods
    -------
    read()
        read value
        MARS_CMD.Y = Enable
        MARS_CMD.N = Disable
    write_Y()
        write Enable
    write_N()
        write Disable
    """

    def __init__(self, serial: serial):
        super().__init__(serial)
        self.cmd = __class__.__name__
        self.dtype = np.str_
        self.byteSize = 1
        self.enum = MARS_CMD


class SMS(CMD):
    """
    Write/Read shutter status

    Attributes
    ----------
    serial : serial port object

    Methods
    -------
    read()
        read value
        MARS_SMS.OPEN = Shutter open
        MARS_SMS.CLOS = Shutter close
    write_CLOS()
        write shutter close
    write_OPEN()
        write shutter open
    """

    def __init__(self, serial: serial):
        super().__init__(serial)
        self.cmd = __class__.__name__
        self.dtype = np.str_
        self.byteSize = 4
        self.enum = MARS_SMS

    def write_CLOS(self):
        self.write(self.enum.CLOS.value)

    def write_OPEN(self):
        self.write(self.enum.OPEN.value)


class STP(CMD):
    """
    Read SoC Temperature

    Attributes
    ----------
    serial : serial port object

    Methods
    -------
    read()
        read value
    """

    def __init__(self, serial: serial):
        super().__init__(serial)
        self.cmd = __class__.__name__
        self.dtype = np.int16
        self.byteSize = 2


class VTP(CMD):
    """
    Read vtemp

    Attributes
    ----------
    serial : serial port object

    Methods
    -------
    read()
        read value
    """

    def __init__(self, serial: serial):
        super().__init__(serial)
        self.cmd = __class__.__name__
        self.dtype = np.int16
        self.byteSize = 2


class VZF(CMD):
    """
    Write/Read video zoom factor

    Attributes
    ----------
    serial : serial port object

    Methods
    -------
    read()
        read value
        MARS_VZF.X1 = zoom in 1x
        MARS_VZF.X2 = zoom in 2x
        MARS_VZF.X4 = zoom in 4x
        MARS_VZF.X8 = zoom in 8x
    write_1x()
        zoom in 1x
    write_2x()
        zoom in 2x
    write_4x()
        zoom in 4x
    write_8x()
        zoom in 8x
    """

    def __init__(self, serial: serial):
        super().__init__(serial)
        self.cmd = __class__.__name__
        self.dtype = np.str_
        self.byteSize = 2
        self.enum = MARS_VZF

    def write_1x(self):
        self.write(self.enum.X1.value)

    def write_2x(self):
        self.write(self.enum.X2.value)

    def write_4x(self):
        self.write(self.enum.X4.value)

    def write_8x(self):
        self.write(self.enum.X8.value)


class SFD(CMD):
    """
    Write/Read sensor flip direnction

    Attributes
    ----------
    serial : serial port object

    Methods
    -------
    read()
        read value
        MARS_SFD.NONE = None
        MARS_SFD.HORI = Horizontal flip
        MARS_SFD.VERT = Vertical flip
    write_NONE()
        None
    write_HORI()
        Horizontal flip
    write_VERT()
        Vertical flip
    """

    def __init__(self, serial: serial):
        super().__init__(serial)
        self.cmd = __class__.__name__
        self.dtype = np.str_
        self.byteSize = 4
        self.enum = MARS_SFD

    def write_NONE(self):
        self.write(self.enum.NONE.value)

    def write_HORI(self):
        self.write(self.enum.HORI.value)

    def write_VERT(self):
        self.write(self.enum.VERT.value)


class HUP(CMD_YN):
    """
    Write/Read HUD present

    Attributes
    ----------
    serial : serial port object

    Methods
    -------
    read()
        read value
        MARS_CMD.Y = Enable
        MARS_CMD.N = Disable
    write_Y()
        write Enable
    write_N()
        write Disable
    """

    def __init__(self, serial: serial):
        super().__init__(serial)
        self.cmd = __class__.__name__
        self.dtype = np.str_
        self.byteSize = 1
        self.enum = MARS_CMD


class PLP(CMD_YN):
    """
    Write/Read palette present

    Attributes
    ----------
    serial : serial port object

    Methods
    -------
    read()
        read value
        MARS_CMD.Y = Enable
        MARS_CMD.N = Disable
    write_Y()
        write Enable
    write_N()
        write Disable
    """

    def __init__(self, serial: serial):
        super().__init__(serial)
        self.cmd = __class__.__name__
        self.dtype = np.str_
        self.byteSize = 1
        self.enum = MARS_CMD


class LGP(CMD_YN):
    """
    Write/Read logo present

    Attributes
    ----------
    serial : serial port object

    Methods
    -------
    read()
        read value
        MARS_CMD.Y = Enable
        MARS_CMD.N = Disable
    write_Y()
        write Enable
    write_N()
        write Disable
    """

    def __init__(self, serial: serial):
        super().__init__(serial)
        self.cmd = __class__.__name__
        self.dtype = np.str_
        self.byteSize = 1
        self.enum = MARS_CMD


class SMP(CMD_YN):
    """
    Write/Read spot meter present

    Attributes
    ----------
    serial : serial port object

    Methods
    -------
    read()
        read value
        MARS_CMD.Y = Enable
        MARS_CMD.N = Disable
    write_Y()
        write Enable
    write_N()
        write Disable
    """

    def __init__(self, serial: serial):
        super().__init__(serial)
        self.cmd = __class__.__name__
        self.dtype = np.str_
        self.byteSize = 1
        self.enum = MARS_CMD


class HTC(CMD):
    """
    Write/Read HUD background color
    value : color value, 8 char
        example : "FFFFFFFF" (Red, Green, Blue, Alpha)

    Attributes
    ----------
    serial : serial port object

    Methods
    -------
    read()
        read value
    write()
        write value
    """

    def __init__(self, serial: serial):
        super().__init__(serial)
        self.cmd = __class__.__name__
        self.dtype = np.str_
        self.byteSize = 8


class HBC(CMD):
    """
    Write/Read HUD background color
    value : color value, 8 char
        example : "FFFFFFFF" (Red, Green, Blue, Alpha)

    Attributes
    ----------
    serial : serial port object

    Methods
    -------
    read()
        read value
    write()
        write value
    """

    def __init__(self, serial: serial):
        super().__init__(serial)
        self.cmd = __class__.__name__
        self.dtype = np.str_
        self.byteSize = 8


class TUS(CMD):
    """
    Write/Read temperature unit selection

    Attributes
    ----------
    serial : serial port object

    Methods
    -------
    read()
        read value
        MARS_TUS.CELS = Celsius
        MARS_TUS.FAHR = Fahrenheit
        MARS_TUS.KELV = Kelvin
    write_CELS()
        write Celsius
    write_FAHR()
        write Fahrenheit
    write_KELV()
        write Kelvin
    """

    def __init__(self, serial: serial):
        super().__init__(serial)
        self.cmd = __class__.__name__
        self.dtype = np.str_
        self.byteSize = 4
        self.enum = MARS_TUS

    def write_CELS(self):
        self.write(self.enum.CELS.value)

    def write_FAHR(self):
        self.write(self.enum.FAHR.value)

    def write_KELV(self):
        self.write(self.enum.KELV.value)


class LGR(CMD):
    """
    Write/Read logo replacement
    value : width * height * channel = 320 * 40 * 4 byte (channel = ARGB)
        arrary = [ARGBARGB...ARGB]

    Attributes
    ----------
    serial : serial port object

    Methods
    -------
    read()
        read value
    write()
        write value
    """

    def __init__(self, serial: serial):
        super().__init__(serial)
        self.cmd = __class__.__name__
        self.dtype = np.uint8
        self.byteSize = 320 * 40 * 4


class A11(CMD):
    """
    Write/Read non uniformity calibration Weights (~5 minutes to read/write)
    value : 2457600 byte

    Attributes
    ----------
    serial : serial port object

    Methods
    -------
    read()
        read value
    write()
        write value
    """

    def __init__(self, serial: serial):
        super().__init__(serial)
        self.cmd = __class__.__name__
        self.dtype = np.int8
        self.byteSize = 2457600

    def read(self):
        buffer = []
        for i in tqdm(range(0, 2457600, 24576)):
            write_head = f"{self.cmd}=".encode("ascii")
            # write_addr = np.array(i).copy().byteswap(inplace=True).tobytes()
            write_addr = np.array(i)
            if sys.byteorder != self.endian:
                write_addr = write_addr.copy().byteswap(inplace=True)
            write_addr = write_addr.tobytes()
            write_tail = "?".encode("ascii")
            write_cmd = write_head + write_addr + write_tail
            self.serial.write(write_cmd)
            read_data = self.serial.read(24576)
            if len(read_data) != 24576:
                return None
            value = np.frombuffer(read_data, dtype=self.dtype)
            buffer.append(value)
            time.sleep(SLEEP)
        self.value = np.concatenate(buffer)
        return self.value

    def write(self, inputs):
        self.value = np.array(inputs).astype(self.dtype)
        # if sys.byteorder != self.endian:
        #     self.value = self.value.byteswap(inplace=True)
        data = self.value.tobytes()
        for i in tqdm(range(0, 2457600, 24576)):
            # write_addr = np.array(i).copy().byteswap(inplace=True).tobytes()
            write_addr = np.array(i)
            if sys.byteorder != self.endian:
                write_addr = write_addr.copy().byteswap(inplace=True)
            write_addr = write_addr.tobytes()
            write_data = data[i : i + 24576]
            write_head = f"{self.cmd}=".encode("ascii")
            write_tail = "?".encode("ascii")
            write_cmd = write_head + write_addr + write_data + write_tail
            self.serial.write(write_cmd)
            # wait OK?
            wait_ack(self.serial, 10, ack_value="OK?")
            time.sleep(SLEEP)


class A11_shutterless(A11):
    """
    Write/Read non uniformity calibration Weights (~5 minutes to read/write)
    value : 2457600 byte

    Attributes
    ----------
    serial : serial port object

    Methods
    -------
    read()
        read value
    write()
        write value
    """

    def __init__(self, serial: serial):
        super().__init__(serial)
        self.cmd = __class__.__name__
        self.dtype = np.int8
        self.byteSize = 2457600
        self.cmd = "A11"

    def read(self):
        buffer = []
        for i in tqdm(range(0, 2457600, 24576)):
            write_head = f"{self.cmd}=".encode("ascii")
            # write_addr = np.array(i).copy().byteswap(inplace=True).tobytes()
            write_addr = np.array(i)
            if sys.byteorder != self.endian:
                write_addr = write_addr.copy().byteswap(inplace=True)
            write_addr = write_addr.tobytes()
            write_tail = "?".encode("ascii")
            write_cmd = write_head + write_addr + write_tail
            self.serial.write(write_cmd)
            read_data = self.serial.read(24576)
            if len(read_data) != 24576:
                return None
            value = np.frombuffer(read_data, dtype=self.dtype)
            buffer.append(value)
            time.sleep(SLEEP)
        self.value = np.concatenate(buffer)
        return self.value

    def read_nuc(self):
        return super().read()

    def read_bp(self, size=640 * 480 // 8):
        write_head = f"{self.cmd}=".encode("ascii")
        # write_addr = np.array(i).copy().byteswap(inplace=True).tobytes()
        write_addr = np.array(~0)
        if sys.byteorder != self.endian:
            write_addr = write_addr.copy().byteswap(inplace=True)
        write_addr = write_addr.tobytes()
        write_tail = "?".encode("ascii")
        write_cmd = write_head + write_addr + write_tail
        self.serial.write(write_cmd)
        read_data = self.serial.read(size)
        if len(read_data) != size:
            return None
        self.value = np.frombuffer(read_data, dtype=self.dtype)
        time.sleep(SLEEP)
        return self.value

    def write_nuc(self, nuc):
        self.write(nuc)

    def write_bp(self, bp):
        #
        self.value = np.array(bp).astype(self.dtype)
        # if sys.byteorder != self.endian:
        #     self.value = self.value.byteswap(inplace=True)
        data = self.value.tobytes()

        write_head = f"{self.cmd}=".encode("ascii")
        write_data = data
        write_tail = "?".encode("ascii")
        write_cmd = write_head + write_data + write_tail
        self.serial.write(write_cmd)
        # wait OK?
        wait_ack(self.serial, 10, ack_value="OK?")
        time.sleep(SLEEP)


class A12(CMD):
    """
    Write/Read temperature calibration Weights
    value : 40 byte

    Attributes
    ----------
    serial : serial port object

    Methods
    -------
    read()
        read value
    write()
        write value
    """

    def __init__(self, serial: serial):
        super().__init__(serial)
        self.cmd = __class__.__name__
        self.dtype = np.int8
        self.byteSize = 40


class TCG(CMD):
    """
    Write/Read temperature gain

    Attributes
    ----------
    serial : serial port object

    Methods
    -------
    read()
        read value
    write()
        write value
    """

    def __init__(self, serial: serial):
        super().__init__(serial)
        self.cmd = __class__.__name__
        self.dtype = np.float32
        self.byteSize = 4


class TCO(CMD):
    """
    Write/Read temperature offset

    Attributes
    ----------
    serial : serial port object

    Methods
    -------
    read()
        read value
    write()
        write value
    """

    def __init__(self, serial: serial):
        super().__init__(serial)
        self.cmd = __class__.__name__
        self.dtype = np.float32
        self.byteSize = 4


class A1B_nuc_bypass(CMD_YN):
    """
    Write/Read non uniformity calibration bypass

    Attributes
    ----------
    serial : serial port object

    Methods
    -------
    read()
        read value
        MARS_CMD.Y = Bypass
        MARS_CMD.N = NO Bypass
    write_Y()
        write Bypass
    write_N()
        write NO Bypass
    """

    def __init__(self, serial: serial):
        super().__init__(serial)
        self.cmd = "A1B"
        self.dtype = np.str_
        self.byteSize = 1
        self.enum = MARS_CMD


class A23_equalizer(CMD):
    """
    Write/Read AGC equalizer value

    Attributes
    ----------
    serial : serial port object

    Methods
    -------
    read()
        read value
    write()
        write value
    """

    def __init__(self, serial: serial):
        super().__init__(serial)
        self.cmd = "A23"
        self.dtype = np.float32
        self.byteSize = 4


class A25_gamma(CMD):
    """
    Write/Read AGC gamma value

    Attributes
    ----------
    serial : serial port object

    Methods
    -------
    read()
        read value
    write()
        write value
    """

    def __init__(self, serial: serial):
        super().__init__(serial)
        self.cmd = "A25"
        self.dtype = np.float32
        self.byteSize = 4


class A26_contrast(CMD):
    """
    Write/Read AGC contrast value

    Attributes
    ----------
    serial : serial port object

    Methods
    -------
    read()
        read value
    write()
        write value
    """

    def __init__(self, serial: serial):
        super().__init__(serial)
        self.cmd = "A26"
        self.dtype = np.float32
        self.byteSize = 4


class A27_stablizer(CMD):
    """
    Write/Read AGC stablizer value

    Attributes
    ----------
    serial : serial port object

    Methods
    -------
    read()
        read value
    write()
        write value
    """

    def __init__(self, serial: serial):
        super().__init__(serial)
        self.cmd = "A27"
        self.dtype = np.float32
        self.byteSize = 4


class A28_contrast_limit(CMD):
    """
    Write/Read AGC contrast_limit value

    Attributes
    ----------
    serial : serial port object

    Methods
    -------
    read()
        read value
    write()
        write value
    """

    def __init__(self, serial: serial):
        super().__init__(serial)
        self.cmd = "A28"
        self.dtype = np.float32
        self.byteSize = 4


class A29_brightness(CMD):
    """
    Write/Read AGC brightness value

    Attributes
    ----------
    serial : serial port object

    Methods
    -------
    read()
        read value
    write()
        write value
    """

    def __init__(self, serial: serial):
        super().__init__(serial)
        self.cmd = "A29"
        self.dtype = np.float32
        self.byteSize = 4


class A2B_AGC_bypass(CMD_YN):
    """
    Write/Read automatic gain control bypass

    Attributes
    ----------
    serial : serial port object

    Methods
    -------
    read()
        read value
        MARS_CMD.Y = Bypass
        MARS_CMD.N = NO Bypass
    write_Y()
        write Bypass
    write_N()
        write NO Bypass
    """

    def __init__(self, serial: serial):
        super().__init__(serial)
        self.cmd = "A2B"
        self.dtype = np.str_
        self.byteSize = 1
        self.enum = MARS_CMD


class A33_dde(CMD):
    """
    Write/Read digital detail enhance value

    Attributes
    ----------
    serial : serial port object

    Methods
    -------
    read()
        read value
    write()
        write value
    """

    def __init__(self, serial: serial):
        super().__init__(serial)
        self.cmd = "A33"
        self.dtype = np.float32
        self.byteSize = 4


class A3B_dde_bypass(CMD_YN):
    """
    Write/Read digital detail enhance bypass

    Attributes
    ----------
    serial : serial port object

    Methods
    -------
    read()
        read value
        MARS_CMD.Y = Bypass
        MARS_CMD.N = NO Bypass
    write_Y()
        write Bypass
    write_N()
        write NO Bypass
    """

    def __init__(self, serial: serial):
        super().__init__(serial)
        self.cmd = "A3B"
        self.dtype = np.str_
        self.byteSize = 1
        self.enum = MARS_CMD


class PLS(CMD):
    """
    Write/Read palette selection

    Attributes
    ----------
    serial : serial port object

    Methods
    -------
    read()
        read value
        MARS_PLS.WH = white hot
        MARS_PLS.BH = black hot
        MARS_PLS.RB = rainbow
        MARS_PLS.RH = rainHC
        MARS_PLS.IB = ironbow
        MARS_PLS.LV = lave
        MARS_PLS.AT = arctic
        MARS_PLS.GB = glowbow
        MARS_PLS.GF = graded fire
        MARS_PLS.HT = hottest
    write_WH()
        write white hot
    write_BH()
        write black hot
    write_RB()
        write rainbow
    write_RH()
        write rainHC
    write_IB()
        write ironbow
    write_LV()
        write lave
    write_AT()
        write arctic
    write_GB()
        write glowbow
    write_GF()
        write graded fire
    write_HT()
        write hottest
    """

    def __init__(self, serial: serial):
        super().__init__(serial)
        self.cmd = __class__.__name__
        self.dtype = np.str_
        self.byteSize = 2
        self.enum = MARS_PLS

    def write_WH(self):
        self.write(self.enum.WH.value)

    def write_BH(self):
        self.write(self.enum.BH.value)

    def write_RB(self):
        self.write(self.enum.RB.value)

    def write_RH(self):
        self.write(self.enum.RH.value)

    def write_IB(self):
        self.write(self.enum.IB.value)

    def write_LV(self):
        self.write(self.enum.LV.value)

    def write_AT(self):
        self.write(self.enum.AT.value)

    def write_GB(self):
        self.write(self.enum.GB.value)

    def write_GF(self):
        self.write(self.enum.GF.value)

    def write_HT(self):
        self.write(self.enum.HT.value)


class CFG:
    """
    Save/load manufacture/user config

    Attributes
    ----------
    serial : serial port object

    Methods
    -------
    write_manufacture_save()
        manufacture cofig save
    write_manufacture_load()
        manufacture cofig load
    write_user_save()
        manufacture cofig save
    write_user_save()
        user cofig load
    """

    def __init__(self, serial: serial):
        self.cmd = __class__.__name__
        self.dtype = np.str_
        self.byteSize = 4
        self.endian = "big"
        self.value = []
        self.serial = serial
        self.enum = None
        self.wait_sec = 60

    def write_manufacture_save(self):
        write_cmd = f"{self.cmd}=MSAVE?".encode("ascii")
        self.serial.write(write_cmd)
        # wait OK?
        wait_ack(self.serial, self.wait_sec, ack_value="OK?")
        time.sleep(SLEEP)

    def write_manufacture_load(self):
        write_cmd = f"{self.cmd}=MLOAD?".encode("ascii")
        self.serial.write(write_cmd)
        # wait OK?
        wait_ack(self.serial, self.wait_sec, ack_value="OK?")
        time.sleep(SLEEP)

    def write_user_save(self):
        write_cmd = f"{self.cmd}=USAVE?".encode("ascii")
        self.serial.write(write_cmd)
        # wait OK?
        wait_ack(self.serial, self.wait_sec, ack_value="OK?")
        time.sleep(SLEEP)

    def write_user_load(self):
        write_cmd = f"{self.cmd}=ULOAD?".encode("ascii")
        self.serial.write(write_cmd)
        # wait OK?
        wait_ack(self.serial, self.wait_sec, ack_value="OK?")
        time.sleep(SLEEP)


class VOM(CMD):
    """
    Write/Read output mode

    Attributes
    ----------
    serial : serial port object

    Methods
    -------
    read()
        read value
        MARS_VOM.TV1 = TV NTSC mode (BT.656 via COMS)
        MARS_VOM.PCO = PC-OSD mode (UVC-H.264)
        MARS_VOM.PCR = PC-RAW mode (UVC-RGB)
        MARS_VOM.SCO = SOC-OSD mode (BT.656 via CMOS)
        MARS_VOM.SCR = SOC-RAW mode (RGB via CMOS)
        MARS_VOM.DUA = SOC-DUAL-A mode (BT.656 via CMOS, UVC-RGB)
        MARS_VOM.DUB = SOC-DUAL-B mode (RGB via CMOS, UVC-H.264)
        MARS_VOM.DUC = SOC-DUAL-C mode (BT.656 via CMOS, UVC-H.264)
        MARS_VOM.DUD = SOC-DUAL-D mode (RGB via CMOS, UVC-RGB)
        MARS_VOM.NVO = NVR-OSD
        MARS_VOM.NVR = NVR-RAW
        MARS_VOM.TV2 = TV PAL mode (BT.656 via COMS)
        MARS_VOM.MPR = MIPI mode (RGB via CMOS to MIPI board)
        MARS_VOM.PCY = PC-OSD mode (UVC-YUV)
    write_TV1()
        TV NTSC mode (BT.656 via COMS)
    write_PCO()
        PC-OSD mode (UVC-H.264)
    write_PCR()
        PC-RAW mode (UVC-RGB)
    write_SCO()
        SOC-OSD mode (BT.656 via CMOS)
    write_SCR()
        SOC-RAW mode (RGB via CMOS)
    write_DUA()
        SOC-DUAL-A mode (BT.656 via CMOS, UVC-RGB)
    write_DUB()
        SOC-DUAL-B mode (RGB via CMOS, UVC-H.264)
    write_DUC()
        SOC-DUAL-C mode (BT.656 via CMOS, UVC-H.264)
    write_DUD()
        SOC-DUAL-D mode (RGB via CMOS, UVC-RGB)
    write_NVO()
        NVR-OSD
    write_NVR()
        NVR-RAW
    write_TV2()
        TV PAL mode (BT.656 via COMS)
    write_MPR()
        MIPI mode (RGB via CMOS to MIPI board)
    write_PCY()
        PC-OSD mode (UVC-YUV)
    """

    def __init__(self, serial: serial):
        super().__init__(serial)
        self.cmd = __class__.__name__
        self.dtype = np.str_
        self.byteSize = 3
        self.enum = MARS_VOM

    def write_TV1(self):
        self.write(self.enum.TV1.value)

    def write_PCO(self):
        self.write(self.enum.PCO.value)

    def write_PCR(self):
        self.write(self.enum.PCR.value)

    def write_SCO(self):
        self.write(self.enum.SCO.value)

    def write_SCR(self):
        self.write(self.enum.SCR.value)

    def write_DUA(self):
        self.write(self.enum.DUA.value)

    def write_DUB(self):
        self.write(self.enum.DUB.value)

    def write_DUC(self):
        self.write(self.enum.DUC.value)

    def write_DUD(self):
        self.write(self.enum.DUD.value)

    def write_NVO(self):
        self.write(self.enum.NVO.value)

    def write_NVR(self):
        self.write(self.enum.NVR.value)

    def write_TV2(self):
        self.write(self.enum.TV2.value)

    def write_MPR(self):
        self.write(self.enum.MPR.value)

    def write_PCY(self):
        self.write(self.enum.PCY.value)


class RTC(CMD):
    """
    Write/Read Real-time clock
    value : "YYYYMMDDhhmmss", 14 char

    Attributes
    ----------
    serial : serial port object

    Methods
    -------
    read()
        read value
    write()
        write value
    """

    def __init__(self, serial: serial):
        super().__init__(serial)
        self.cmd = __class__.__name__
        self.dtype = np.str_
        self.byteSize = 14


class FWV(CMD):
    """
    Read Firmware version
    value : "X.XX", 4 char

    Attributes
    ----------
    serial : serial port object

    Methods
    -------
    read()
        read value
    """

    def __init__(self, serial: serial):
        super().__init__(serial)
        self.cmd = __class__.__name__
        self.dtype = np.str_
        self.byteSize = 4


class GFD(CMD):
    """
    Write/Read sensor gfid at chosen gain mode (gms)

    Attributes
    ----------
    serial : serial port object

    Methods
    -------
    read()
        read value
    write()
        write value
    """

    def __init__(self, serial: serial):
        super().__init__(serial)
        self.cmd = __class__.__name__
        self.dtype = np.uint8
        self.byteSize = 1


class GSK(CMD):
    """
    Write/Read sensor gsk at chosen gain mode (gms)

    Attributes
    ----------
    serial : serial port object

    Methods
    -------
    read()
        read value
    write()
        write value
    """

    def __init__(self, serial: serial):
        super().__init__(serial)
        self.cmd = __class__.__name__
        self.dtype = np.uint16
        self.byteSize = 2


class TIN(CMD):
    """
    Write/Read sensor tint at chosen gain mode (gms)

    Attributes
    ----------
    serial : serial port object

    Methods
    -------
    read()
        read value
    write()
        write value
    """

    def __init__(self, serial: serial):
        super().__init__(serial)
        self.cmd = __class__.__name__
        self.dtype = np.uint16
        self.byteSize = 2


class CIN(CMD):
    """
    Write/Read sensor cint at chosen gain mode (gms)

    Attributes
    ----------
    serial : serial port object

    Methods
    -------
    read()
        read value
    write()
        write value
    """

    def __init__(self, serial: serial):
        super().__init__(serial)
        self.cmd = __class__.__name__
        self.dtype = np.uint8
        self.byteSize = 1


class A0B(CMD_YN):
    """
    Write/Read algorithm 0 bypass

    Attributes
    ----------
    serial : serial port object

    Methods
    -------
    read()
        read value
        MARS_CMD.Y = Bypass
        MARS_CMD.N = NO Bypass
    write_Y()
        write Bypass
    write_N()
        write NO Bypass
    """

    def __init__(self, serial: serial):
        super().__init__(serial)
        self.cmd = __class__.__name__
        self.dtype = np.str_
        self.byteSize = 1
        self.enum = MARS_CMD


class DNB(CMD_YN):
    """
    Write/Read algorithm 0 bypass

    Attributes
    ----------
    serial : serial port object

    Methods
    -------
    read()
        read value
        MARS_CMD.Y = Bypass
        MARS_CMD.N = NO Bypass
    write_Y()
        write Bypass
    write_N()
        write NO Bypass
    """

    def __init__(self, serial: serial):
        super().__init__(serial)
        self.cmd = __class__.__name__
        self.dtype = np.str_
        self.byteSize = 1
        self.enum = MARS_CMD


class ENB(CMD):
    """
    Write/Read Effective Number of Bits

    Attributes
    ----------
    serial : serial port object

    Methods
    -------
    read()
        read value
        MARS_ENB_14,  // Effective Number of Bits = 14
        MARS_ENB_13,  // Effective Number of Bits = 13
        MARS_ENB_12,  // Effective Number of Bits = 12
        MARS_ENB_11,  // Effective Number of Bits = 11
        MARS_ENB_10,  // Effective Number of Bits = 10
    write_14()
        Effective Number of Bits = 14
    write_13()
        Effective Number of Bits = 13
    write_12()
        Effective Number of Bits = 12
    write_11()
        Effective Number of Bits = 11
    write_10()
        Effective Number of Bits = 10
    """

    def __init__(self, serial: serial):
        super().__init__(serial)
        self.cmd = __class__.__name__
        self.dtype = np.str_
        self.byteSize = 2
        self.enum = MARS_ENB

    def write_14(self):
        self.write(self.enum._14.value)

    def write_13(self):
        self.write(self.enum._13.value)

    def write_12(self):
        self.write(self.enum._12.value)

    def write_11(self):
        self.write(self.enum._11.value)

    def write_10(self):
        self.write(self.enum._10.value)


class DSC(CMD):
    """
    Do shutter calibration one time

    Attributes
    ----------
    serial : serial port object

    Methods
    -------
    write()
        Do shutter calibration one time
    """

    def __init__(self, serial: serial):
        super().__init__(serial)
        self.cmd = __class__.__name__
        self.dtype = np.uint8
        self.byteSize = 1

    def write(self):
        super().write(1)


class TCB(CMD_YN):
    """
    Write/Read algorithm 0 bypass

    Attributes
    ----------
    serial : serial port object

    Methods
    -------
    read()
        read value
        MARS_CMD.Y = Bypass
        MARS_CMD.N = NO Bypass
    write_Y()
        write Bypass
    write_N()
        write NO Bypass
    """

    def __init__(self, serial: serial):
        super().__init__(serial)
        self.cmd = __class__.__name__
        self.dtype = np.str_
        self.byteSize = 1
        self.enum = MARS_CMD


class SFC(CMD):
    """
    Write/Read external supplemental flat field calibration enable/disable

    Attributes
    ----------
    serial : serial port object

    Methods
    -------
    write_1()
        Enable
    write_0()
        Disable
    """

    def __init__(self, serial: serial):
        super().__init__(serial)
        self.cmd = __class__.__name__
        self.dtype = np.uint8
        self.byteSize = 1

    def write_1(self):
        super().write(1)

    def write_0(self):
        super().write(0)


class SFS(CMD):
    """
    Set external supplemental flat field calibration image

    Attributes
    ----------
    serial : serial port object

    Methods
    -------
    write_1()
        Set calibration image
    """

    def __init__(self, serial: serial):
        super().__init__(serial)
        self.cmd = __class__.__name__
        self.dtype = np.uint8
        self.byteSize = 1

    def write(self):
        super().write(1)


class SR1(CMD):
    """
    Write/Read Flash Status Register 1 value

    Attributes
    ----------
    serial : serial port object

    Methods
    -------
    read()
        read value
    write()
        write value
    """

    def __init__(self, serial: serial):
        super().__init__(serial)
        self.cmd = __class__.__name__
        self.dtype = np.uint8
        self.byteSize = 1


class SR2(CMD):
    """
    Write/Read Flash Status Register 2 value

    Attributes
    ----------
    serial : serial port object

    Methods
    -------
    read()
        read value
    write()
        write value
    """

    def __init__(self, serial: serial):
        super().__init__(serial)
        self.cmd = __class__.__name__
        self.dtype = np.uint8
        self.byteSize = 1


class SR3(CMD):
    """
    Write/Read Flash Status Register 3 value

    Attributes
    ----------
    serial : serial port object

    Methods
    -------
    read()
        read value
    write()
        write value
    """

    def __init__(self, serial: serial):
        super().__init__(serial)
        self.cmd = __class__.__name__
        self.dtype = np.uint8
        self.byteSize = 1


class WPC(CMD):
    """
    Write Flash WP control value

    Attributes
    ----------
    serial : serial port object

    Methods
    -------
    write()
        write value
    """

    def __init__(self, serial: serial):
        super().__init__(serial)
        self.cmd = __class__.__name__
        self.dtype = np.uint8
        self.byteSize = 1


class ALT(CMD):
    """
    Write/Read AGC linear type

    Attributes
    ----------
    serial : serial port object

    Methods
    -------
    read()
        read value
        MARS_ALT.ONE    = one linear
        MARS_ALT.MULTI  = multiple linear
    write_one()
        one linear
    write_multi()
        multiple linear
    """

    def __init__(self, serial: serial):
        super().__init__(serial)
        self.cmd = __class__.__name__
        self.dtype = np.uint8
        self.byteSize = 1
        self.enum = MARS_ALT

    def write_one(self):
        self.write(MARS_ALT.ONE)

    def write_multi(self):
        self.write(MARS_ALT.MULTI)


class AHS(CMD):
    """
    Write/Read AGC histogram stride value

    Attributes
    ----------
    serial : serial port object

    Methods
    -------
    read()
        read value
    write()
        write value
    """

    def __init__(self, serial: serial):
        super().__init__(serial)
        self.cmd = __class__.__name__
        self.dtype = np.uint8
        self.byteSize = 1


class SCT(CMD):
    """
    Write/Read Shutter NUC vtemp difference threshold value

    Attributes
    ----------
    serial : serial port object

    Methods
    -------
    read()
        read value
    write()
        write value
    """

    def __init__(self, serial: serial):
        super().__init__(serial)
        self.cmd = __class__.__name__
        self.dtype = np.float32
        self.byteSize = 4


class ASC(CMD):
    """
    Write/Read Auto Shutter Calibration enable/disable

    Attributes
    ----------
    serial : serial port object

    Methods
    -------
    read()
        read value
        1 = Enable
        0 = Disable
    write_0()
        Disable
    write_1()
        Enable
    """

    def __init__(self, serial: serial):
        super().__init__(serial)
        self.cmd = __class__.__name__
        self.dtype = np.uint8
        self.byteSize = 1

    def write_0(self):
        self.write(0)

    def write_1(self):
        self.write(1)


class SCP(CMD):
    """
    Write/Read Shutter NUC calibration period value (sec)

    Attributes
    ----------
    serial : serial port object

    Methods
    -------
    read()
        read value
    write()
        write value
    """

    def __init__(self, serial: serial):
        super().__init__(serial)
        self.cmd = __class__.__name__
        self.dtype = np.float32
        self.byteSize = 4


class SCI(CMD):
    """
    Write/Read Shutter NUC calibration, shutter image integral number

    Attributes
    ----------
    serial : serial port object

    Methods
    -------
    read()
        read value
    write()
        write value
    """

    def __init__(self, serial: serial):
        super().__init__(serial)
        self.cmd = __class__.__name__
        self.dtype = np.uint8
        self.byteSize = 1


class DIA(CMD):
    """
    Read diagnosis information

    Attributes
    ----------
    serial : serial port object

    Methods
    -------
    read()
        read info
    """

    def __init__(self, serial: serial):
        super().__init__(serial)
        self.cmd = __class__.__name__
        self.dtype = np.str_
        self.byteSize = 41 + 6 + 1 + 4 + 64

    def read(self):
        write_cmd = f"{self.cmd}=?".encode("ascii")
        self.serial.write(write_cmd)
        read_data = self.serial.read(self.byteSize)
        #  *          SMS : 4 * char      4byte
        #  *          A1B : 1 * char      1byte
        #  *          VTP : 1 * int16     2byte
        #  *          CTP : 1 * float32   4byte
        #  *          SR1 : 1 * uint8     1byte
        #  *          SR2 : 1 * uint8     1byte
        #  *          SR3 : 1 * uint8     1byte
        #  *          SSN : 9 * char      9byte
        #  *          OTT : 1 * float     4byte
        #  *          OTS : 4 * char      4byte
        #  *          LPS : 4 * char      4byte
        #  *          GFD : 1 * uint8     1byte
        #  *          GSK : 2 * uint16    2byte
        #  *          TIN : 2 * uint16    2byte
        #  *          CIN : 1 * uint8     1byte
        ###
        #  *          dbg_cnt : 6 * char      6byte
        #  *          dbg_flag: 1 * char      1byte
        ###
        #  *          FPS : 1 * float32   4byte
        ###
        #  *          FW_info : 64 * char 64byte

        sms = self.decode_ascii(read_data[0:4])
        a1b = self.decode_ascii(read_data[4:5])
        vtp = self.decode_number(read_data[5:7], np.int16, "big")
        ctp = self.decode_number(read_data[7:11], np.float32, "big")
        sr1 = self.decode_number(read_data[11:12], np.int8, "big")
        sr2 = self.decode_number(read_data[12:13], np.int8, "big")
        sr3 = self.decode_number(read_data[13:14], np.int8, "big")
        ssn = self.decode_ascii(read_data[14:23])
        ott = self.decode_number(read_data[23:27], np.float32, "big")
        ots = self.decode_ascii(read_data[27:31])
        lps = self.decode_ascii(read_data[31:35])
        #
        GFD = self.decode_number(read_data[35:36], np.uint8, "big")
        GSK = self.decode_number(read_data[36:38], np.uint16, "big")
        TIN = self.decode_number(read_data[38:40], np.uint16, "big")
        CIN = self.decode_number(read_data[40:41], np.uint8, "big")
        #
        dbg_cnt = self.decode_ascii(read_data[41:47])
        dbg_flag = self.decode_number(read_data[47:48], np.int8, "big")
        #
        fps = self.decode_number(read_data[48:52], np.float32, "big")
        #
        firmware_info = self.decode_ascii(read_data[52:116])
        return {
            "SMS": sms,
            "A1B": a1b,
            "VTP": vtp,
            "CTP": ctp,
            "SR1": sr1,
            "SR2": sr2,
            "SR3": sr3,
            "SSN": ssn,
            "OTT": ott,
            "OTS": ots,
            "LPS": lps,
            "GFD": GFD,
            "GSK": GSK,
            "TIN": TIN,
            "CIN": CIN,
            "DEBUG_CNT": dbg_cnt,
            "DEBUG_FLAG": dbg_flag,
            "FPS": fps,
            "firmware_info": firmware_info,
        }


class CTP(CMD):
    """
    Read diagnosis information

    Attributes
    ----------
    serial : serial port object

    Methods
    -------
    read()
        read info
    """

    def __init__(self, serial: serial):
        super().__init__(serial)
        self.cmd = __class__.__name__
        self.dtype = np.float32
        self.byteSize = 4


class OTT(CMD):
    """
    Write/Read Over temperature threshold (Celsius)

    Attributes
    ----------
    serial : serial port object

    Methods
    -------
    read()
        read value
    write()
        write value
    """

    def __init__(self, serial: serial):
        super().__init__(serial)
        self.cmd = __class__.__name__
        self.dtype = np.float32
        self.byteSize = 4


class OTB(CMD_YN):
    """
    Write/Read Over temperature function bypass

    Attributes
    ----------
    serial : serial port object

    Methods
    -------
    read()
        read value
        MARS_CMD.Y = Bypass
        MARS_CMD.N = NO Bypass
    write_Y()
        write Bypass
    write_N()
        write NO Bypass
    """

    def __init__(self, serial: serial):
        super().__init__(serial)
        self.cmd = __class__.__name__
        self.dtype = np.str_
        self.byteSize = 1
        self.enum = MARS_CMD


class OTS(CMD):
    """
    Write/Read Over temperature status

    Attributes
    ----------
    serial : serial port object

    Methods
    -------
    read()
        read value
        MARS_OTS.NORM = Normal status
        MARS_OTS.OVER = Over temperature status
    """

    def __init__(self, serial: serial):
        super().__init__(serial)
        self.cmd = __class__.__name__
        self.dtype = np.str_
        self.byteSize = 4
        self.enum = MARS_OTS


class LPS(CMD):
    """
    Write/Read Over temperature status

    Attributes
    ----------
    serial : serial port object

    Methods
    -------
    read()
        read value
        MARS_LPS.NORM = Normal status
        MARS_LPS.LOWP = Low power status
    write_LOWP()
        Low power status
    write_NORM()
        Normal status
    """

    def __init__(self, serial: serial):
        super().__init__(serial)
        self.cmd = __class__.__name__
        self.dtype = np.str_
        self.byteSize = 4
        self.enum = MARS_LPS

    def write_LOWP(self):
        self.write(self.enum.LOWP.value)

    def write_NORM(self):
        self.write(self.enum.NORM.value)


class SSN(CMD):
    """
    Read Sensor serial number (works only when video is streaming)

    Attributes
    ----------
    serial : serial port object

    Methods
    -------
    read()
        read value
    """

    def __init__(self, serial: serial):
        super().__init__(serial)
        self.cmd = __class__.__name__
        self.dtype = np.str_
        self.byteSize = 9


class VZC(CMD):
    """
    Write/Read Video zoom center

    Attributes
    ----------
    serial : serial port object

    Methods
    -------
    read()
        read value
    write()
        write value
    """

    def __init__(self, serial: serial):
        super().__init__(serial)
        self.cmd = __class__.__name__
        self.dtype = np.uint32
        self.byteSize = 4

    def read(self):
        write_cmd = f"{self.cmd}=?".encode("ascii")
        self.serial.write(write_cmd)
        read_data = self.serial.read(self.byteSize)
        value = self.decode_number(read_data)
        ratio_x = value // 10000 / 1000
        ratio_y = value % 10000 / 1000
        time.sleep(SLEEP)
        return ratio_x, ratio_y

    def write(self, ratio_x, ratio_y):
        value = (ratio_x * 10000 + ratio_y) * 1000
        self.value = np.array(value).astype(self.dtype)
        if sys.byteorder != self.endian:
            self.value = self.value.byteswap(inplace=True)
        write_data = self.value.tobytes()
        write_head = f"{self.cmd}=".encode("ascii")
        write_tail = "?".encode("ascii")
        # print(write_data)
        write_cmd = write_head + write_data + write_tail
        self.serial.write(write_cmd)
        time.sleep(SLEEP)


class FTG(CMD_YN):
    """
    Write/Read frame trigger enable/disable

    Attributes
    ----------
    serial : serial port object

    Methods
    -------
    read()
        read value
        MARS_CMD.Y = Enable
        MARS_CMD.N = Disable
    write_Y()
        Enable
    write_N()
        Disable
    """

    def __init__(self, serial: serial):
        super().__init__(serial)
        self.cmd = __class__.__name__
        self.dtype = np.str_
        self.byteSize = 1
        self.enum = MARS_CMD


class UGM(CMD):
    """
    Start firmware upgrade

    Attributes
    ----------
    serial : serial port object

    Methods
    -------
    write()
        Start firmware upgrade
    """

    def __init__(self, serial: serial):
        super().__init__(serial)
        self.cmd = __class__.__name__
        self.dtype = np.str_
        self.byteSize = 0
        self.wait_sec = 10

    def write(self):
        write_cmd = f"{self.cmd}=?".encode("ascii")
        self.serial.write(write_cmd)
        # wait OK?
        wait_ack(self.serial, self.wait_sec, ack_value="OK?")
        time.sleep(SLEEP)


class UGR(CMD):
    """
    Firmware update

    Attributes
    ----------
    serial : serial port object

    Methods
    -------
    write()
        addr: Raw data address in firmware file
        data: Raw data, length 24576 bytes (If there is not enough data, buffer should be filled with 0)
    """

    def __init__(self, serial: serial):
        super().__init__(serial)
        self.cmd = __class__.__name__
        self.dtype = np.str_
        self.byteSize = 24576
        self.wait_sec = 20

    def write(self, addr, data):
        # write_head
        write_head = f"{self.cmd}=".encode("ascii")
        self.serial.write(write_head)
        # wirte_addr
        write_addr = addr
        if sys.byteorder != self.endian:
            write_addr = write_addr.byteswap(inplace=True)
        write_addr = write_addr.tobytes()
        self.serial.write(write_addr)
        # write_data
        write_data = np.zeros(24576, dtype=np.uint8)
        write_data[: data.shape[0]] = data.astype(np.uint8)
        write_data = write_data.tobytes()
        self.serial.write(write_data)
        # write_tail
        write_tail = "?".encode("ascii")
        self.serial.write(write_tail)
        # wait OK?
        wait_ack(self.serial, self.wait_sec, ack_value="OK?")
        time.sleep(SLEEP)


class UGD(CMD):
    """
    End firmware upgrade

    Attributes
    ----------
    serial : serial port object

    Methods
    -------
    write()
        End firmware upgrade
    """

    def __init__(self, serial: serial):
        super().__init__(serial)
        self.cmd = __class__.__name__
        self.dtype = np.str_
        self.byteSize = 0
        self.wait_sec = 20

    def write(self):
        write_cmd = f"{self.cmd}=?".encode("ascii")
        self.serial.write(write_cmd)
        # wait OK?
        wait_ack(self.serial, self.wait_sec, ack_value="OK?")
        time.sleep(SLEEP)


class RIP(CMD):
    """
    Write/Read Ethernet IP
    value : ip[4] = {192,168,0,6}

    Attributes
    ----------
    serial : serial port object

    Methods
    -------
    read()
        read value
    write()
        write value
    """

    def __init__(self, serial: serial):
        super().__init__(serial)
        self.cmd = __class__.__name__
        self.dtype = np.uint8
        self.byteSize = 4


class RGW(CMD):
    """
    Write/Read Ethernet gateway
    value : gateway[4] = {192,168,0,6}

    Attributes
    ----------
    serial : serial port object

    Methods
    -------
    read()
        read value
    write()
        write value
    """

    def __init__(self, serial: serial):
        super().__init__(serial)
        self.cmd = __class__.__name__
        self.dtype = np.uint8
        self.byteSize = 4


class RNM(CMD):
    """
    Write/Read Ethernet netmask
    value : netmask[4] = {255,255,255,0}

    Attributes
    ----------
    serial : serial port object

    Methods
    -------
    read()
        read value
    write()
        write value
    """

    def __init__(self, serial: serial):
        super().__init__(serial)
        self.cmd = __class__.__name__
        self.dtype = np.uint8
        self.byteSize = 4


class BPA(CMD):
    """
    Add bad pixel index
    value : 256 1d index (h*width+w). Not used index should be filled with -1.

    Attributes
    ----------
    serial : serial port object

    Methods
    -------
    read()
        read value
    write()
        write value
    """

    def __init__(self, serial: serial):
        super().__init__(serial)
        self.cmd = __class__.__name__
        self.dtype = np.uint32
        self.byteSize = 1024
        self.dataNum = 256
        self.wait_sec = 10

    def read(self):
        return

    def write(self, inputs):
        self.value = np.zeros(self.dataNum, dtype=self.dtype) + 4294967295
        for i, inp in enumerate(inputs):
            self.value[i] = inp
        self.value = self.value.astype(self.dtype)

        # head
        write_head = f"{self.cmd}=".encode("ascii")
        self.serial.write(write_head)
        # value
        for value in self.value:
            value = np.array(value)
            if sys.byteorder != self.endian:
                write_data = value.byteswap(inplace=True)
            write_data = write_data.tobytes()
            self.serial.write(write_data)

        # tail
        write_tail = "?".encode("ascii")
        self.serial.write(write_tail)

        # print(self.serial.read(1000).decode("ascii"))

        # wait OK?
        wait_ack(self.serial, self.wait_sec, ack_value="OK?")
        time.sleep(SLEEP)


class BPR(BPA):
    """
    Remove bad pixel index
    value : 256 1d index (h*width+w). Not used index should be filled with -1.

    Attributes
    ----------
    serial : serial port object

    Methods
    -------
    read()
        read value
    write()
        write value
    """

    def __init__(self, serial: serial):
        super().__init__(serial)
        self.cmd = __class__.__name__


class CCE(CMD_YN):
    """
    Write/Read continue capture enable

    Attributes
    ----------
    serial : serial port object

    Methods
    -------
    read()
        read value
        MARS_CMD.Y = Enable
        MARS_CMD.N = Disable
    write_Y()
        Enable
    write_N()
        Disable
    """

    def __init__(self, serial: serial):
        super().__init__(serial)
        self.cmd = __class__.__name__
        self.dtype = np.str_
        self.byteSize = 1
        self.enum = MARS_CMD


class CCI(CMD):
    """
    Write/Read continue capture interval

    Attributes
    ----------
    serial : serial port object

    Methods
    -------
    read()
        read value
        MARS_CCI._1 = 1 sec
        MARS_CCI._2 = 2 sec
        MARS_CCI._3 = 3 sec
    write_1sec()
        write 1 sec
    write_2sec()
        write 2 sec
    write_3sec()
        write 3 sec
    """

    def __init__(self, serial: serial):
        super().__init__(serial)
        self.cmd = __class__.__name__
        self.dtype = np.str_
        self.byteSize = 1
        self.enum = MARS_CCI

    def write_1sec(self):
        self.write(self.enum._1.value)

    def write_2sec(self):
        self.write(self.enum._2.value)

    def write_3sec(self):
        self.write(self.enum._3.value)


class VRE(CMD_YN):
    """
    Write/Read video record enable

    Attributes
    ----------
    serial : serial port object

    Methods
    -------
    read()
        read value
        MARS_CMD.Y = Enable
        MARS_CMD.N = Disable
    write_Y()
        Enable
    write_N()
        Disable
    """

    def __init__(self, serial: serial):
        super().__init__(serial)
        self.cmd = __class__.__name__
        self.dtype = np.str_
        self.byteSize = 1
        self.enum = MARS_CMD


class GSH(CMD):
    """
    Write/Read Gray Scale High threshold (0~255)

    Attributes
    ----------
    serial : serial port object

    Methods
    -------
    read()
        read value
    write()
        write value
    """

    def __init__(self, serial: serial):
        super().__init__(serial)
        self.cmd = __class__.__name__
        self.dtype = np.uint8
        self.byteSize = 1


class GSL(CMD):
    """
    Write/Read Gray Scale Low threshold (0~255)

    Attributes
    ----------
    serial : serial port object

    Methods
    -------
    read()
        read value
    write()
        write value
    """

    def __init__(self, serial: serial):
        super().__init__(serial)
        self.cmd = __class__.__name__
        self.dtype = np.uint8
        self.byteSize = 1


class RCH(CMD):
    """
    Write/Read Raw Count High threshold (0~16383)

    Attributes
    ----------
    serial : serial port object

    Methods
    -------
    read()
        read value
    write()
        write value
    """

    def __init__(self, serial: serial):
        super().__init__(serial)
        self.cmd = __class__.__name__
        self.dtype = np.uint16
        self.byteSize = 2


class RCL(CMD):
    """
    Write/Read Raw Count Low threshold (0~16383)

    Attributes
    ----------
    serial : serial port object

    Methods
    -------
    read()
        read value
    write()
        write value
    """

    def __init__(self, serial: serial):
        super().__init__(serial)
        self.cmd = __class__.__name__
        self.dtype = np.uint16
        self.byteSize = 2


class FBR(CMD):
    """
    Write/Read Flat Bias Ratio (0.0~1.0)

    Attributes
    ----------
    serial : serial port object

    Methods
    -------
    read()
        read value
    write()
        write value
    """

    def __init__(self, serial: serial):
        super().__init__(serial)
        self.cmd = __class__.__name__
        self.dtype = np.float32
        self.byteSize = 4
