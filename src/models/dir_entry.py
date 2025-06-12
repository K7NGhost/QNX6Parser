import struct

class DirEntry():
    def __init__(self, data):
        self.parent_inode = None
        (
            self.inode_number,
            self.name_length,
        ) = struct.unpack("<IB", data[:5])

        self.name = data[5:5 + self.name_length].decode('utf-8', errors='replace')

    def __repr__(self):
        return f"<dir_entry parent_inode={self.parent_inode} inode_id={self.inode_number}, length='{self.name_length}', name='{self.name}'>"