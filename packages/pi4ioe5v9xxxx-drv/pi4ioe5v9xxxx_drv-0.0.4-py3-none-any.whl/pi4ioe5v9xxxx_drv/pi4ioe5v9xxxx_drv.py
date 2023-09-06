from smbus2 import SMBus
from smbus2 import i2c_msg

_BITS = 24
_I2C_ADDR = 0x20
_BUS = None
_PORT_VALUE = [0xFF]
_READMODE = False
_INVERT = False


def setup(i2c_bus=1, i2c_addr=0x20, bits=24, read_mode=False, invert=False):
    """Set up the IO expander devices."""
    global _I2C_ADDR
    global _BITS
    global _BUS
    global _PORT_VALUE
    global _READMODE
    global _INVERT
    _I2C_ADDR = i2c_addr
    _BITS = bits
    _READMODE = read_mode
    _INVERT = invert
    # Make 8-bits (can be 2- or 4-bits, but should always pack in a 8-bit msg)
    while bits % 8:
        bits += 1
    # Increase array size
    _PORT_VALUE = [0xFF] * int(bits / 8)
    # Set up I2C bus connectivity
    _BUS = SMBus(i2c_bus)
    # Write 1 to all pins to prepaire them for reading, or bring hardware in a defined state
    msg = i2c_msg.write(_I2C_ADDR, _PORT_VALUE)
    if _BUS:
        _BUS.i2c_rdwr(msg)
    else:
        raise ReferenceError("I2C bus was not created, please check I2C address!")
    # If in read mode: do first hw read to have memory ready
    if read_mode:
        hw_to_memory()


def hw_to_memory():
    """Read pin data from hardware and write to memory."""
    global _BUS
    global _PORT_VALUE
    global _I2C_ADDR
    global _READMODE
    if not _READMODE:
        raise ValueError("You cannot read from the hardware as it is in write mode!")
    msg = i2c_msg.read(_I2C_ADDR, len(_PORT_VALUE))
    if _BUS:
        _BUS.i2c_rdwr(msg)
        for k in range(msg.len):
            _PORT_VALUE[k] = int(msg.buf[k].hex(), 16)
    else:
        raise ReferenceError("I2C bus was not created, did you run setup?")


def memory_to_hw():
    """Write values stored in memory to hardware"""
    global _BUS
    global _PORT_VALUE
    global _I2C_ADDR
    if _READMODE:
        raise ValueError("You cannot write to hardware as it is in read mode!")
    msg = i2c_msg.write(_I2C_ADDR, _PORT_VALUE)
    if _BUS:
        _BUS.i2c_rdwr(msg)
    else:
        raise ValueError("I2C bus not available, did you run setup?")


def pin_from_memory(pin: int):
    """Read pin value from memory and return its value"""
    global _BITS
    global _READMODE
    global _PORT_VALUE
    global _INVERT
    if pin > _BITS:
        raise ValueError("Pin number is larger than number of bits available!")
    byte_nr = int((pin - 1) / 8)
    bit_nr = int((pin - 1) - (byte_nr * 8))
    mask = 0x01 << bit_nr
    if (_PORT_VALUE[byte_nr] & mask) != 0:
        return not _INVERT
    else:
        return _INVERT


def pin_to_memory(pin: int, value: bool):
    """Write pin value to memory"""
    global _PORT_VALUE
    global _BITS
    if pin > _BITS:
        raise ValueError("Pin number is larger than number of bits available!")
    local_value = value
    if _INVERT:
        local_value = not local_value
    byte_nr = int((pin - 1) / 8)
    bit_nr = int((pin - 1) - (byte_nr * 8))
    if byte_nr < len(_PORT_VALUE):
        mask = 0x1 << bit_nr
        # First remove the bit
        _PORT_VALUE[byte_nr] &= ~mask
        # If value set the correponding bit
        if local_value:
            _PORT_VALUE[byte_nr] |= mask
    else:
        raise ValueError(
            "Writing pin %d to  bit %d of port %d while IO-expander has only %d ports (%d bits)!"
            % (pin, bit_nr, byte_nr, len(_PORT_VALUE), len(PORT_VALUE) * 8)
        )
