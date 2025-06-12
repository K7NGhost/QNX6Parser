import struct

class LongNameiNode():
    def __init__(self, data):
        self.index = None
        # Read first 2 bytes as unsigned short (little endian)
        self.name_length = struct.unpack("<H", data[:2])[0]

        # Sanity check
        # if self.name_length > 510:
        #     raise ValueError(f"Name length too large: {self.name_length}")

        # Read the filename
        name_bytes = data[2:2 + self.name_length]
        self.name = name_bytes.decode("utf-8", errors="replace")
        
        def __repr__(self):
            return f"<LongNameiNode name_length={self.name_length} file_name='{self.name}'>"