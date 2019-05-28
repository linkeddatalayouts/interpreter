class Offset(object):
    def __init__(self, bit_offset = None, byte_offset=None):
        self.bit_offset_relative = bit_offset
        self.byte_offset_relative = byte_offset
        self.absolute_bit_offset = None
        self.absolute_byte_offset = None