import struct

class LongDirEntry():
    def __init__(self, data):
        if len(data) < 10:
            raise ValueError("LongDirEntry data must be at least 10 bytes")
        self.parent_inode = None
        (
            self.inode_number,
            self.size,
            self.long_file_inumber,
            self.checksum
        ) = struct.unpack("<IIIB", data[:13])  # > = big-endian

    def __repr__(self):
        return (
            f"<LongDirEntry inode_number={self.inode_number}, size={self.size}, "
            f"long_file_inumber={self.long_file_inumber}, checksum=0x{self.checksum:02X}>"
        )