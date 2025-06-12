import struct


class RootNode():
    def __init__(self, data):
        if len(data) < 74:
            raise ValueError("Not enough data to parse RootNode")
        self.index = None
        (
        self.size,
        *self.pointer_array,
        self.levels,
        self.mode
        ) = struct.unpack("<Q16IBB", data[:74]) # Q = 8 bytes, I = 4 bytes, B = 1 byte

        # convert from tuple to list
        self.pointer_array = list(self.pointer_array)
        # anything left in spare
        self.spare = data[74:]

    def __repr__(self):
        return (
            f"<RootNode size={self.size}, levels={self.levels}, mode={self.mode}, "
            f"pointers={self.pointer_array}>"
        )